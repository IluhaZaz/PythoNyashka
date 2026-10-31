from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaConfig(BaseSettings):
    bootstrap_servers: str = "localhost:9092"

    model_config = SettingsConfigDict(env_prefix="kafka_")
