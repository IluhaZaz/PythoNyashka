import asyncio
import json
import logging
from abc import ABC, abstractmethod

from aiokafka import AIOKafkaConsumer, TopicPartition
from aiokafka.errors import CommitFailedError, IllegalStateError, KafkaError
from pydantic import BaseModel

logger = logging.getLogger(__name__)


def create_consumer(
    bootstrap_servers: str, topic: str, group_id: str,
) -> AIOKafkaConsumer:
    return AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        enable_auto_commit=False,
        auto_offset_reset="earliest",
    )


class BaseKafkaConsumer(ABC):
    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
        group_id: str,
        retry_backoff_seconds: float = 1.0,
        processing_timeout_seconds: float = 30.0,
    ) -> None:
        self.retry_backoff_seconds = retry_backoff_seconds
        self.processing_timeout_seconds = processing_timeout_seconds
        self.consumer = create_consumer(bootstrap_servers, topic, group_id)
        self._pending: tuple[TopicPartition, int] | None = None

    @abstractmethod
    def _transfrom(self, data: dict[str, object]) -> BaseModel:
        raise NotImplementedError

    async def start(self) -> None:
        await self.consumer.start()

    async def stop(self) -> None:
        await self.consumer.stop()

    async def run(self) -> BaseModel:
        if self._pending is not None:
            raise RuntimeError("Commit or retry the previous Kafka message before reading again")

        while True:
            try:
                record = await self.consumer.getone()
            except KafkaError:
                logger.exception("Failed to read a Kafka message")
                await asyncio.sleep(self.retry_backoff_seconds)
                continue

            partition = TopicPartition(record.topic, record.partition)
            try:
                async with asyncio.timeout(self.processing_timeout_seconds):
                    data = json.loads(record.value or b"")
                    if not isinstance(data, dict):
                        raise ValueError("Kafka message must be a JSON object")
                    message = self._transfrom(data)
            except Exception:
                logger.exception(
                    "Failed to process Kafka message at %s:%s:%s; retrying without commit",
                    record.topic, record.partition, record.offset,
                )
                self._rewind(partition, record.offset)
                await asyncio.sleep(self.retry_backoff_seconds)
                continue

            self._pending = (partition, record.offset)
            return message

    def retry(self) -> None:
        if self._pending is not None:
            partition, offset = self._pending
            self._rewind(partition, offset)
            self._pending = None

    def _rewind(self, partition: TopicPartition, offset: int) -> None:
        if partition in self.consumer.assignment():
            self.consumer.seek(partition, offset)

    async def commit(self) -> bool:
        if self._pending is None:
            raise RuntimeError("No Kafka message to commit")

        partition, offset = self._pending
        while True:
            try:
                await self.consumer.commit({partition: offset + 1})
                self._pending = None
                return True
            except (CommitFailedError, IllegalStateError):
                logger.warning("Partition assignment changed before commit for %s", partition)
                self.retry()
                return False
            except KafkaError:
                logger.exception("Failed to commit Kafka offset for %s; retrying", partition)
                await asyncio.sleep(self.retry_backoff_seconds)
