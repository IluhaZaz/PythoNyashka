import hashlib
import secrets
from datetime import datetime, timezone, timedelta

from pwdlib import PasswordHash

from src.auth.domain.schemas import RegisterRequest, LoginRequest, AuthTokens
from src.auth.infrastructure.storage.postgresql.repository import AuthRepository
from src.auth.security import password_hasher, TokenService, DUMMY_PASSWORD_HASH


class Register:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    async def execute(self, req: RegisterRequest) -> str:
        pass_hash = password_hasher.hash(req.password)

        id_ = await self.repository.register(
            email=req.email,
            profile_id=req.profile_id,
            pass_hash=pass_hash
        )

        return id_


class InvalidCredentialsError(Exception):
    pass


class Login:
    def __init__(
        self,
        repository: AuthRepository,
        token_service: TokenService,
    ):
        self.repository = repository
        self.token_service = token_service

    async def execute(self, req: LoginRequest) -> AuthTokens:
        user = await self.repository.get_user_by_email(req.email)

        if user is not None:
            stored_hash = user.password_hash
        else:
            stored_hash = DUMMY_PASSWORD_HASH

        is_valid = password_hasher.verify(req.password, stored_hash)

        if user is None or not is_valid:
            raise InvalidCredentialsError()

        now = datetime.now(timezone.utc)

        refresh_token = secrets.token_urlsafe(32)
        refresh_token_hash = hashlib.sha256(
            refresh_token.encode()
        ).hexdigest()

        access_token = self.token_service.create_access_token(
            user_id=user.id,
            profile_id=user.profile_id,
            now=now,
        )

        await self.repository.create_session(
            user_id=user.id,
            refresh_token_hash=refresh_token_hash,
            expires_at=now + timedelta(
                days=self.token_service.config.refresh_ttl_days,
            ),
            is_revoked=False
        )

        return AuthTokens(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.token_service.config.access_ttl_seconds,
        )
