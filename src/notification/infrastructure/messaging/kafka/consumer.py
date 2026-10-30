import asyncio
import logging

from aiokafka import TopicPartition
from aiokafka.errors import CommitFailedError, IllegalStateError, KafkaError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.infrastructure.messaging.kafka.config import KafkaConfig
from src.infrastructure.messaging.kafka.consumer import create_consumer
from src.notification.domain.events import NotificationEvent
from src.notification.infrastructure.storage.postgresql.repository import NotificationRepository
from src.notification.usecase import CreateNotification

logger = logging.getLogger(__name__)


class NotificationConsumer:
    def __init__(
        self,
        config: KafkaConfig,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self.config = config
        self.session_factory = session_factory
        self.consumer = create_consumer(
            bootstrap_servers=config.bootstrap_servers,
            topic=config.notifications_topic,
            group_id=config.notifications_group_id,
        )

    async def start(self) -> None:
        await self.consumer.start()

    async def stop(self) -> None:
        await self.consumer.stop()

    async def run(self) -> None:
        while True:
            try:
                record = await self.consumer.getone()
            except KafkaError:
                logger.exception("Failed to read a notification event from Kafka")
                await asyncio.sleep(self.config.retry_backoff_seconds)
                continue

            partition = TopicPartition(record.topic, record.partition)
            try:
                async with asyncio.timeout(self.config.processing_timeout_seconds):
                    event = NotificationEvent.model_validate_json(record.value or b"")
                    async with self.session_factory() as session:
                        notification_id = await CreateNotification(
                            NotificationRepository(session),
                        ).execute(event)
            except Exception:
                logger.exception(
                    "Failed to process notification event at %s:%s:%s; retrying without commit",
                    record.topic, record.partition, record.offset,
                )
                self._rewind(partition, record.offset)
                await asyncio.sleep(self.config.retry_backoff_seconds)
                continue

            if await self._commit(partition, record.offset + 1):
                logger.info(
                    "Created notification %s from %s at %s:%s:%s",
                    notification_id, event.source, record.topic, record.partition, record.offset,
                )

    def _rewind(self, partition: TopicPartition, offset: int) -> None:
        if partition in self.consumer.assignment():
            self.consumer.seek(partition, offset)

    async def _commit(self, partition: TopicPartition, offset: int) -> bool:
        while True:
            try:
                await self.consumer.commit({partition: offset})
                return True
            except (CommitFailedError, IllegalStateError):
                logger.warning("Partition assignment changed before commit for %s", partition)
                self._rewind(partition, offset - 1)
                return False
            except KafkaError:
                logger.exception("Failed to commit notification offset for %s; retrying", partition)
                await asyncio.sleep(self.config.retry_backoff_seconds)
