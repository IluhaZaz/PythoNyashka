from src.infrastructure.messaging.kafka.consumer import BaseKafkaConsumer
from src.infrastructure.messaging.kafka.events import NotificationEvent


class NotificationConsumer(BaseKafkaConsumer):
    def __init__(self, bootstrap_servers: str) -> None:
        super().__init__(
            bootstrap_servers=bootstrap_servers,
            topic="notification.events",
            group_id="notification-service",
            retry_backoff_seconds=1.0,
            processing_timeout_seconds=30.0,
        )

    def _transfrom(self, data: dict[str, object]) -> NotificationEvent:
        return NotificationEvent.model_validate(data)
