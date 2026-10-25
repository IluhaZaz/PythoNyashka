import hashlib
import secrets
from datetime import datetime, timezone, timedelta

import jwt
from pwdlib import PasswordHash

from src.auth.domain.schemas import RegisterRequest, LoginRequest, AuthTokens, RefreshTokenRequest, \
    ChangePasswordRequest
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

class InvalidSessionError(Exception):
    pass


class Logout:
    def __init__(
        self,
        repository: AuthRepository,
        token_service: TokenService,
    ):
        self.repository = repository
        self.token_service = token_service

    async def execute(
        self,
        req: RefreshTokenRequest,
        access_token: str,
    ) -> None:
        try:
            payload = self.token_service.verify_access_token(
                access_token,
            )
        except jwt.InvalidTokenError as exc:
            raise InvalidSessionError() from exc

        refresh_token_hash = hashlib.sha256(
            req.refresh_token.encode()
        ).hexdigest()

        session_found = await self.repository.revoke_session(
            user_id=payload["sub"],
            refresh_token_hash=refresh_token_hash,
        )

        if not session_found:
            raise InvalidSessionError()

class InvalidOldPasswordError(Exception):
    pass

class ChangePassword:
    def __init__(
            self,
            repository: AuthRepository,
            token_service: TokenService,
    ):
        self.repository = repository
        self.token_service = token_service
        self.password_hasher = PasswordHash.recommended()

    async def execute(
            self,
            req: ChangePasswordRequest,
            access_token: str,
    ) -> None:
        try:
            payload = self.token_service.verify_access_token(
                access_token,
            )
        except jwt.InvalidTokenError as exc:
            raise InvalidCredentialsError() from exc

        user = await self.repository.get_user_by_id(
            payload["sub"],
        )

        if user is None:
            raise InvalidCredentialsError()

        previous_hash = user.password_hash

        is_valid = password_hasher.verify(req.old_password, previous_hash)

        if not is_valid:
            raise InvalidOldPasswordError()

        new_hash = self.password_hasher.hash(req.new_password)

        changed = await self.repository.change_password(
            user_id=user.id,
            previous_password_hash=previous_hash,
            new_password_hash=new_hash,
        )

        if not changed:
            raise InvalidOldPasswordError()


class InvalidRefreshTokenError(Exception):
    pass


class Refresh:
    def __init__(
        self,
        repository: AuthRepository,
        token_service: TokenService,
    ):
        self.repository = repository
        self.token_service = token_service

    async def execute(self, req: RefreshTokenRequest) -> AuthTokens:
        old_hash = hashlib.sha256(
            req.refresh_token.encode()
        ).hexdigest()

        user = await self.repository.get_user_by_refresh_hash(old_hash)

        if user is None:
            raise InvalidRefreshTokenError()

        new_refresh_token = secrets.token_urlsafe(32)
        new_hash = hashlib.sha256(
            new_refresh_token.encode()
        ).hexdigest()

        access_token = self.token_service.create_access_token(
            user_id=user.id,
            profile_id=user.profile_id,
            now=datetime.now(timezone.utc),
        )

        rotated = await self.repository.rotate_refresh_token(
            old_hash=old_hash,
            new_hash=new_hash,
        )

        if not rotated:
            raise InvalidRefreshTokenError()

        return AuthTokens(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=self.token_service.config.access_ttl_seconds,
        )