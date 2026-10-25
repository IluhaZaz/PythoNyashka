from datetime import datetime, timedelta

import jwt
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pwdlib import PasswordHash


password_hasher = PasswordHash.recommended()

DUMMY_PASSWORD_HASH = password_hasher.hash("dummy-password")

class AuthConfig(BaseSettings):
    jwt_secret: SecretStr = Field(min_length=32)
    access_ttl_seconds: int = Field(default=900, gt=0)
    refresh_ttl_days: int = Field(default=30, gt=0)

    model_config = SettingsConfigDict(env_prefix="auth_")


class TokenService:
    def __init__(self, config: AuthConfig):
        self.config = config

    def create_access_token(
        self,
        user_id: str,
        profile_id: str,
        now: datetime,
    ) -> str:
        payload = {
            "sub": user_id,
            "profile_id": profile_id,
            "iat": now,
            "exp": now + timedelta(
                seconds=self.config.access_ttl_seconds,
            ),
            "iss": "auth",
            "aud": "bff",
            "token_use": "access",
        }

        return jwt.encode(
            payload,
            self.config.jwt_secret.get_secret_value(),
            algorithm="HS256",
        )