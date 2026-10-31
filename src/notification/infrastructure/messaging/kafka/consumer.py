from src.infrastructure.messaging.kafka.config import KafkaConfig
from src.infrastructure.messaging.kafka.consumer import BaseKafkaConsumer
from src.infrastructure.messaging.kafka.events import NotificationEvent


class NotificationConsumer(BaseKafkaConsumer):
    def __init__(self, config: KafkaConfig) -> None:
        super().__init__(
            bootstrap_servers=config.bootstrap_servers,
            topic=config.notifications_topic,
            group_id=config.notifications_group_id,
            retry_backoff_seconds=config.retry_backoff_seconds,
            processing_timeout_seconds=config.processing_timeout_seconds,
        )

    def _transfrom(self, data: dict[str, object]) -> NotificationEvent:
        return NotificationEvent.model_validate(data)
