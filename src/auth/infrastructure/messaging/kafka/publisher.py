import asyncio
import logging
from uuid import UUID

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from src.infrastructure.messaging.kafka.events import NotificationEvent

logger = logging.getLogger(__name__)


class NotificationPublisher:
    def __init__(self, producer: AIOKafkaProducer) -> None:
        self.producer = producer

    async def publish(
        self, profile_id: str, text: str, *,
        email: str | None = None, subject: str = "PythoNyashka",
    ) -> None:
        try:
            event = NotificationEvent(
                source="auth", profile_id=UUID(profile_id), text=text,
                email=email, subject=subject,
            )
            await asyncio.wait_for(
                self.producer.send_and_wait(
                    "notification.events",
                    value=event.model_dump_json().encode("utf-8"),
                    key=str(event.profile_id).encode("utf-8"),
                ),
                timeout=5.0,
            )
        except (KafkaError, TimeoutError, ValueError):
            logger.exception(
                "Failed to publish Auth notification for profile %s; Auth changes remain committed",
                profile_id,
            )
