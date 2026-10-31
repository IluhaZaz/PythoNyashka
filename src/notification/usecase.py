import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from tenacity import RetryCallState, before_sleep_log, retry, stop_after_attempt, wait_fixed

from src.infrastructure.messaging.kafka.events import NotificationEvent
from src.notification.domain.schemas import NotificationGet
from src.notification.infrastructure.messaging.kafka.consumer import NotificationConsumer
from src.notification.infrastructure.messaging.smtp.sender import SMTPSender
from src.notification.infrastructure.storage.postgresql.repository import NotificationRepository

logger = logging.getLogger(__name__)


def _email_failed(retry_state: RetryCallState) -> bool:
    logger.error("Skipping email after %s failed attempts", retry_state.attempt_number)
    return False


class NotificationNotFoundError(Exception):
    pass


class CreateNotification:
    def __init__(
        self,
        consumer: NotificationConsumer,
        repository: NotificationRepository,
        sender: SMTPSender,
    ) -> None:
        self.consumer = consumer
        self.repository = repository
        self.sender = sender

    async def execute(self) -> None:
        while True:
            message = await self.consumer.run()
            try:
                async with asyncio.timeout(self.consumer.processing_timeout_seconds):
                    event = NotificationEvent.model_validate(message)

                    notification_id = await self.repository.create(
                        profile_id=str(event.profile_id), text=event.text,
                    )
                is_sent = False
                if event.email is not None:
                    is_sent = await self._send_email(event.email, event.subject, event.text)
                    await self.repository.set_sent_status(
                        notification_id, is_sent,
                    )
            except Exception:
                logger.exception(
                    "Failed to save notification or sent status; retrying without Kafka commit",
                )
                self.consumer.retry()
                await asyncio.sleep(self.consumer.retry_backoff_seconds)
                continue

            if await self.consumer.commit():
                logger.info(
                    "Created notification %s from %s, is_sent=%s",
                    notification_id, event.source, is_sent,
                )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(1),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        retry_error_callback=_email_failed,
    )
    async def _send_email(self, email: str, subject: str, text: str) -> bool:
        async with asyncio.timeout(self.consumer.processing_timeout_seconds):
            await self.sender.send(email, subject, text)
        return True


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
