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
from generated.clients.media.api.media import get_media_by_id, upload_media
from generated.clients.media.client import Client as MediaClient
from generated.clients.media.models.media_create import MediaCreate
from generated.clients.media.models.upload_media_response_201 import UploadMediaResponse201
from generated.clients.media.types import File
from generated.clients.profile.api.profiles import (
    create_profile,
    delete_profile,
    get_profile_by_id,
    update_profile,
)
from generated.clients.profile.client import Client as ProfileClient
from generated.clients.profile.models.create_profile_response_201 import CreateProfileResponse201
from generated.clients.profile.models.create_profile_response_409 import CreateProfileResponse409
from generated.clients.profile.models.get_profile_by_id_response_200 import (
    GetProfileByIdResponse200,
)
from generated.clients.profile.models.profile_create import ProfileCreate as ClientProfileCreate
from generated.clients.profile.models.profile_create_gender import ProfileCreateGender
from generated.clients.profile.models.profile_update import ProfileUpdate as ClientProfileUpdate
from src.bff.domain.schemas import (
    AuthTokens,
    ChangePasswordRequest,
    ErrorResponse,
    LoginRequest,
    ProfileCreate,
    ProfileCreatedResponse,
    ProfileGetResponse,
    ProfileUpdate,
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
        if req.avatar is not None:
            body.avatar_id = str(await self._upload_avatar(req.avatar))

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
            await self._register_user(req, profile.id)
        except (Exception, CancelledError):
            await self._delete_profile(profile.id)
            raise

        return profile

    async def _upload_avatar(self, avatar: UploadFile) -> UUID:
        return await _upload_avatar(avatar, self.media_client)

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


class MediaNotFoundError(Exception):
    pass


class GetMedia:
    def __init__(self, client: MediaClient, authenticated: bool) -> None:
        self.client = client
        self.authenticated = authenticated

    async def execute(self, media_id: UUID) -> tuple[bytes, str, str | None]:
        if not self.authenticated:
            raise InvalidCredentialsError("Невалидный access-токен")

        response = await get_media_by_id.asyncio_detailed(media_id, client=self.client)
        if response.status_code == HTTPStatus.OK and isinstance(response.parsed, File):
            return (
                response.content,
                response.headers.get("content-type", "application/octet-stream"),
                response.headers.get("content-disposition"),
            )
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise MediaNotFoundError()

        raise RuntimeError(f"Unexpected Media Service response: {response.status_code}")


class ProfileNotFoundError(Exception):
    def __init__(self, error: str) -> None:
        self.error = error
        super().__init__(error)


class GetProfile:
    def __init__(self, profile_id: UUID | None, profile_client: ProfileClient) -> None:
        self.profile_id = profile_id
        self.profile_client = profile_client

    async def execute(self) -> ProfileGetResponse:
        if self.profile_id is None:
            raise InvalidCredentialsError("Невалидный access-токен")

        response = await get_profile_by_id.asyncio_detailed(
            str(self.profile_id), client=self.profile_client,
        )
        if response.status_code == HTTPStatus.OK and isinstance(
            response.parsed, GetProfileByIdResponse200,
        ):
            return ProfileGetResponse.model_validate_json(response.content)
        if response.status_code == HTTPStatus.NOT_FOUND:
            error = ErrorResponse.model_validate_json(response.content)
            raise ProfileNotFoundError(error.error)

        raise RuntimeError(f"Unexpected Profile Service response: {response.status_code}")


class UpdateProfile:
    def __init__(
        self,
        profile_id: UUID | None,
        profile_client: ProfileClient,
        media_client: MediaClient,
    ) -> None:
        self.profile_id = profile_id
        self.profile_client = profile_client
        self.media_client = media_client

    async def execute(self, req: ProfileUpdate) -> None:
        if self.profile_id is None:
            raise InvalidCredentialsError("Невалидный access-токен")

        profile_id = str(self.profile_id)
        profile = await get_profile_by_id.asyncio_detailed(profile_id, client=self.profile_client)
        if profile.status_code == HTTPStatus.NOT_FOUND:
            error = ErrorResponse.model_validate_json(profile.content)
            raise ProfileNotFoundError(error.error)
        if profile.status_code != HTTPStatus.OK:
            raise RuntimeError(f"Unexpected Profile Service response: {profile.status_code}")

        body = ClientProfileUpdate.from_dict(
            req.model_dump(exclude_none=True, exclude={"avatar"}),
        )
        if req.avatar is not None:
            body.avatar_id = str(await _upload_avatar(req.avatar, self.media_client))
        if not body.to_dict():
            return

        response = await update_profile.asyncio_detailed(
            profile_id=profile_id,
            client=self.profile_client,
            body=body,
        )
        if response.status_code == HTTPStatus.NO_CONTENT:
            return
        if response.status_code == HTTPStatus.NOT_FOUND:
            error = ErrorResponse.model_validate_json(response.content)
            raise ProfileNotFoundError(error.error)

        raise RuntimeError(f"Unexpected Profile Service response: {response.status_code}")


async def _upload_avatar(avatar: UploadFile, client: MediaClient) -> UUID:
    response = await upload_media.asyncio_detailed(
        client=client,
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
