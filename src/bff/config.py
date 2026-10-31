from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthClientConfig(BaseSettings):
    base_url: str = "http://localhost:8000"
    timeout_seconds: float = Field(default=10.0, gt=0)

    model_config = SettingsConfigDict(env_prefix="bff_auth_")


class TokenConfig(BaseSettings):
    jwt_secret: SecretStr = Field(min_length=32, init=False)

    model_config = SettingsConfigDict(env_prefix="auth_")


class ProfileClientConfig(BaseSettings):
    base_url: str = "http://localhost:8001"
    timeout_seconds: float = Field(default=10.0, gt=0)

    model_config = SettingsConfigDict(env_prefix="bff_profile_")


class MediaClientConfig(BaseSettings):
    base_url: str = "http://localhost:8002"
    timeout_seconds: float = Field(default=10.0, gt=0)

    model_config = SettingsConfigDict(env_prefix="bff_media_")


class NotificationClientConfig(BaseSettings):
    base_url: str = "http://localhost:8004"
    timeout_seconds: float = Field(default=10.0, gt=0)

    model_config = SettingsConfigDict(env_prefix="bff_notification_")
