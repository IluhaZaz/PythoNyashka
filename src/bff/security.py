from uuid import UUID

import jwt

from src.bff.config import TokenConfig


class AccessTokenVerifier:
    def __init__(self, config: TokenConfig) -> None:
        self.config = config

    def get_profile_id(self, access_token: str) -> UUID:
        payload = jwt.decode(
            access_token,
            key=self.config.jwt_secret.get_secret_value(),
            algorithms=["HS256"],
            issuer="auth",
            audience="bff",
            options={
                "require": ["exp", "iat", "sub", "iss", "aud", "token_use", "profile_id"],
            },
        )
        if payload["token_use"] != "access":
            raise jwt.InvalidTokenError("Expected access token")
        if not isinstance(payload["sub"], str) or not payload["sub"]:
            raise jwt.InvalidTokenError("Invalid user ID")

        profile_id = payload["profile_id"]
        if not isinstance(profile_id, str):
            raise jwt.InvalidTokenError("Invalid profile ID")
        try:
            return UUID(profile_id)
        except ValueError as exc:
            raise jwt.InvalidTokenError("Invalid profile ID") from exc
