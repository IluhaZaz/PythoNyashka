import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.infrastructure.messaging.kafka.events import NotificationEvent
from src.notification.domain.schemas import NotificationGet
from src.notification.infrastructure.messaging.kafka.consumer import NotificationConsumer
from src.notification.infrastructure.messaging.smtp.sender import SMTPSender
from src.notification.infrastructure.storage.postgresql.repository import NotificationRepository

logger = logging.getLogger(__name__)


class NotificationNotFoundError(Exception):
    pass


class CreateNotification:
    def __init__(
        self,
        consumer: NotificationConsumer,
        session_factory: async_sessionmaker[AsyncSession],
        sender: SMTPSender,
    ) -> None:
        self.consumer = consumer
        self.session_factory = session_factory
        self.sender = sender

    async def execute(self) -> None:
        while True:
            message = await self.consumer.run()
            try:
                async with asyncio.timeout(self.consumer.processing_timeout_seconds):
                    event = NotificationEvent.model_validate(message)
                    async with self.session_factory() as session:
                        notification_id = await NotificationRepository(session).create(
                            profile_id=str(event.profile_id), text=event.text,
                        )
                    if event.email is not None:
                        await self.sender.send(event.email, event.subject, event.text)
            except Exception:
                logger.exception(
                    "Failed to create notification or send email; retrying without Kafka commit",
                )
                self.consumer.retry()
                await asyncio.sleep(self.consumer.retry_backoff_seconds)
                continue

            if await self.consumer.commit():
                logger.info("Created notification %s from %s", notification_id, event.source)


class GetNotifications:
    def __init__(self, repository: NotificationRepository) -> None:
        self.repository = repository

    async def execute(
        self, profile_id: str, limit: int | None = None, offset: int = 0,
    ) -> list[NotificationGet]:
        return await self.repository.get_by_profile(profile_id, limit=limit, offset=offset)


class ReadNotification:
    def __init__(self, repository: NotificationRepository) -> None:
        self.repository = repository

    async def execute(self, notification_id: str, profile_id: str) -> None:
        if not await self.repository.mark_as_read(notification_id, profile_id):
            raise NotificationNotFoundError()
