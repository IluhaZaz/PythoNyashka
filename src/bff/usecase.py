from asyncio import CancelledError
from http import HTTPStatus
from uuid import UUID

from fastapi import UploadFile

from generated.clients.auth.api.auth import login, logout, refresh_token, register, reset_password
from generated.clients.auth.client import AuthenticatedClient, Client
from generated.clients.auth.models.auth_tokens import AuthTokens as ClientAuthTokens
from generated.clients.auth.models.login_request import LoginRequest as ClientLoginRequest
from generated.clients.auth.models.login_response_401 import LoginResponse401
from generated.clients.auth.models.logout_response_401 import LogoutResponse401
from generated.clients.auth.models.password_reset_request import PasswordResetRequest
from generated.clients.auth.models.refresh_token_request import (
    RefreshTokenRequest as ClientRefreshTokenRequest,
)
from generated.clients.auth.models.refresh_token_response_401 import RefreshTokenResponse401
from generated.clients.auth.models.register_request import RegisterRequest
from generated.clients.auth.models.register_response_201 import RegisterResponse201
from generated.clients.auth.models.register_response_400 import RegisterResponse400
from generated.clients.auth.models.reset_password_response_400 import ResetPasswordResponse400
from generated.clients.auth.models.reset_password_response_401 import ResetPasswordResponse401
from generated.clients.media.api.media import upload_media
from generated.clients.media.client import Client as MediaClient
from generated.clients.media.models.media_create import MediaCreate
from generated.clients.media.models.upload_media_response_201 import UploadMediaResponse201
from generated.clients.media.types import File
from generated.clients.profile.api.profiles import create_profile, delete_profile
from generated.clients.profile.client import Client as ProfileClient
from generated.clients.profile.models.create_profile_response_201 import CreateProfileResponse201
from generated.clients.profile.models.create_profile_response_409 import CreateProfileResponse409
from generated.clients.profile.models.profile_create import ProfileCreate as ClientProfileCreate
from generated.clients.profile.models.profile_create_gender import ProfileCreateGender
from src.bff.domain.schemas import (
    AuthTokens,
    ChangePasswordRequest,
    ErrorResponse,
    LoginRequest,
    ProfileCreate,
    ProfileCreatedResponse,
    RefreshTokenRequest,
)


class InvalidCredentialsError(Exception):
    def __init__(self, error: str) -> None:
        self.error = error
        super().__init__(error)


class Login:
    def __init__(self, client: Client) -> None:
        self.client = client

    async def execute(self, req: LoginRequest) -> AuthTokens:
        response = await login.asyncio_detailed(
            client=self.client,
            body=ClientLoginRequest(email=str(req.email), password=req.password),
        )

        if response.status_code == HTTPStatus.OK and isinstance(
            response.parsed, ClientAuthTokens,
        ):
            return AuthTokens.model_validate(response.parsed.to_dict())

        if response.status_code == HTTPStatus.UNAUTHORIZED and isinstance(
            response.parsed, LoginResponse401,
        ):
            error = ErrorResponse.model_validate(response.parsed.to_dict())
            raise InvalidCredentialsError(error.error)

        raise RuntimeError(f"Unexpected Auth Service response: {response.status_code}")


class Refresh:
    def __init__(self, client: Client) -> None:
        self.client = client

    async def execute(self, req: RefreshTokenRequest) -> AuthTokens:
        response = await refresh_token.asyncio_detailed(
            client=self.client,
            body=ClientRefreshTokenRequest(refresh_token=req.refresh_token),
        )
        if response.status_code == HTTPStatus.OK and isinstance(
            response.parsed, ClientAuthTokens,
        ):
            return AuthTokens.model_validate(response.parsed.to_dict())
        if response.status_code == HTTPStatus.UNAUTHORIZED and isinstance(
            response.parsed, RefreshTokenResponse401,
        ):
            error = ErrorResponse.model_validate(response.parsed.to_dict())
            raise InvalidCredentialsError(error.error)

        raise RuntimeError(f"Unexpected Auth Service response: {response.status_code}")


class Logout:
    def __init__(self, client: AuthenticatedClient | None) -> None:
        self.client = client

    async def execute(self, req: RefreshTokenRequest) -> None:
        if self.client is None:
            raise InvalidCredentialsError("Невалидный токен или сессия")

        response = await logout.asyncio_detailed(
            client=self.client,
            body=ClientRefreshTokenRequest(refresh_token=req.refresh_token),
        )
        if response.status_code == HTTPStatus.NO_CONTENT:
            return
        if response.status_code == HTTPStatus.UNAUTHORIZED and isinstance(
            response.parsed, LogoutResponse401,
        ):
            error = ErrorResponse.model_validate(response.parsed.to_dict())
            raise InvalidCredentialsError(error.error)

        raise RuntimeError(f"Unexpected Auth Service response: {response.status_code}")


class InvalidOldPasswordError(Exception):
    def __init__(self, error: str) -> None:
        self.error = error
        super().__init__(error)


class ChangePassword:
    def __init__(self, client: AuthenticatedClient | None) -> None:
        self.client = client

    async def execute(self, req: ChangePasswordRequest) -> None:
        if self.client is None:
            raise InvalidCredentialsError("Невалидный access-токен")

        response = await reset_password.asyncio_detailed(
            client=self.client,
            body=PasswordResetRequest(
                old_password=req.old_password,
                new_password=req.new_password,
            ),
        )
        if response.status_code == HTTPStatus.NO_CONTENT:
            return
        if response.status_code == HTTPStatus.BAD_REQUEST and isinstance(
            response.parsed, ResetPasswordResponse400,
        ):
            error = ErrorResponse.model_validate(response.parsed.to_dict())
            raise InvalidOldPasswordError(error.error)
        if response.status_code == HTTPStatus.UNAUTHORIZED and isinstance(
            response.parsed, ResetPasswordResponse401,
        ):
            error = ErrorResponse.model_validate(response.parsed.to_dict())
            raise InvalidCredentialsError(error.error)

        raise RuntimeError(f"Unexpected Auth Service response: {response.status_code}")


class ProfileAlreadyExistsError(Exception):
    def __init__(self, error: str) -> None:
        self.error = error
        super().__init__(error)


class CreateProfile:
    def __init__(
        self,
        auth_client: Client,
        profile_client: ProfileClient,
        media_client: MediaClient,
    ) -> None:
        self.auth_client = auth_client
        self.profile_client = profile_client
        self.media_client = media_client

    async def execute(self, req: ProfileCreate) -> ProfileCreatedResponse:
        body = ClientProfileCreate(
            email=str(req.email),
            name=req.name,
            surname=req.surname,
            age=req.age,
            bio=req.bio,
            gender=ProfileCreateGender(req.gender),
            tags=req.tags,
        )

        response = await create_profile.asyncio_detailed(client=self.profile_client, body=body)
        if response.status_code == HTTPStatus.CONFLICT and isinstance(
            response.parsed, CreateProfileResponse409,
        ):
            error = ErrorResponse.model_validate(response.parsed.to_dict())
            raise ProfileAlreadyExistsError(error.error)

        if response.status_code != HTTPStatus.CREATED or not isinstance(
            response.parsed, CreateProfileResponse201,
        ):
            raise RuntimeError(f"Unexpected Profile Service response: {response.status_code}")

        profile = ProfileCreatedResponse(id=UUID(response.parsed.id))
        try:
            if req.avatar:
                body.avatar_id = str(await self._upload_avatar(req.avatar))
            await self._register_user(req, profile.id)
        except (Exception, CancelledError):
            await self._delete_profile(profile.id)
            raise

        return profile

    async def _upload_avatar(self, avatar: UploadFile) -> UUID:
        response = await upload_media.asyncio_detailed(
            client=self.media_client,
            body=MediaCreate(file=File(
                payload=avatar.file,
                file_name=avatar.filename,
                mime_type=avatar.content_type or "application/octet-stream",
            )),
        )
        if response.status_code != HTTPStatus.CREATED or not isinstance(
            response.parsed, UploadMediaResponse201,
        ):
            raise RuntimeError(f"Unexpected Media Service response: {response.status_code}")
        return response.parsed.id

    async def _register_user(self, req: ProfileCreate, profile_id: UUID) -> None:
        response = await register.asyncio_detailed(
            client=self.auth_client,
            body=RegisterRequest(
                email=str(req.email),
                password=req.password,
                profile_id=profile_id,
            ),
        )
        if response.status_code == HTTPStatus.BAD_REQUEST and isinstance(
            response.parsed, RegisterResponse400,
        ):
            error = ErrorResponse.model_validate(response.parsed.to_dict())
            raise ProfileAlreadyExistsError(error.error)
        if response.status_code != HTTPStatus.CREATED or not isinstance(
            response.parsed, RegisterResponse201,
        ):
            raise RuntimeError(f"Unexpected Auth Service response: {response.status_code}")

    async def _delete_profile(self, profile_id: UUID) -> None:
        response = await delete_profile.asyncio_detailed(
            str(profile_id), client=self.profile_client,
        )
        if response.status_code != HTTPStatus.NO_CONTENT:
            raise RuntimeError(f"Profile rollback failed: {response.status_code}")
