from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaConfig(BaseSettings):
    bootstrap_servers: str = "localhost:9092"
    notifications_topic: str = "notification.events"
    notifications_group_id: str = "notification-service"
    retry_backoff_seconds: float = Field(default=1.0, gt=0)
    processing_timeout_seconds: float = Field(default=30.0, gt=0)

    model_config = SettingsConfigDict(env_prefix="kafka_")
