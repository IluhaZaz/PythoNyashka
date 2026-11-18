from collections.abc import AsyncIterator
from http import HTTPStatus
from typing import Annotated
from uuid import UUID

import httpx
import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from generated.clients.auth.client import AuthenticatedClient, Client
from generated.clients.chat.client import Client as ChatClient
from generated.clients.match.client import Client as MatchClient
from generated.clients.media.client import Client as MediaClient
from generated.clients.notification.client import Client as NotificationClient
from generated.clients.profile.client import Client as ProfileClient
from src.bff.config import (
    AuthClientConfig,
    ChatClientConfig,
    MatchClientConfig,
    MediaClientConfig,
    NotificationClientConfig,
    ProfileClientConfig,
    TokenConfig,
)
from src.bff.security import AccessTokenVerifier
from src.bff.usecase import (
    APIRequestError,
    ChangePassword,
    Chats,
    CreateProfile,
    GetMedia,
    GetNotifications,
    GetProfile,
    Login,
    Logout,
    Matches,
    ReadNotification,
    Refresh,
    UpdateProfile,
)

bearer = HTTPBearer(auto_error=False, bearerFormat="JWT", scheme_name="BearerAuth")


def get_auth_config() -> AuthClientConfig:
    return AuthClientConfig()


async def get_auth_client(
    config: Annotated[AuthClientConfig, Depends(get_auth_config)],
) -> AsyncIterator[Client]:
    async with Client(
        base_url=config.base_url,
        timeout=httpx.Timeout(config.timeout_seconds),
    ) as client:
        yield client


def login_uc(
    client: Annotated[Client, Depends(get_auth_client)],
) -> Login:
    return Login(client=client)


def refresh_uc(
    client: Annotated[Client, Depends(get_auth_client)],
) -> Refresh:
    return Refresh(client=client)


async def get_authenticated_auth_client(
    config: Annotated[AuthClientConfig, Depends(get_auth_config)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> AsyncIterator[AuthenticatedClient | None]:
    if credentials is None:
        yield None
        return

    async with AuthenticatedClient(
        base_url=config.base_url,
        token=credentials.credentials,
        timeout=httpx.Timeout(config.timeout_seconds),
    ) as client:
        yield client


def change_password_uc(
    client: Annotated[AuthenticatedClient | None, Depends(get_authenticated_auth_client)],
) -> ChangePassword:
    return ChangePassword(client=client)


def logout_uc(
    client: Annotated[AuthenticatedClient | None, Depends(get_authenticated_auth_client)],
) -> Logout:
    return Logout(client=client)


def get_profile_config() -> ProfileClientConfig:
    return ProfileClientConfig()


def get_media_config() -> MediaClientConfig:
    return MediaClientConfig()


async def get_profile_client(
    config: Annotated[ProfileClientConfig, Depends(get_profile_config)],
) -> AsyncIterator[ProfileClient]:
    async with ProfileClient(
        base_url=config.base_url,
        timeout=httpx.Timeout(config.timeout_seconds),
    ) as client:
        yield client


async def get_media_client(
    config: Annotated[MediaClientConfig, Depends(get_media_config)],
) -> AsyncIterator[MediaClient]:
    async with MediaClient(
        base_url=config.base_url,
        timeout=httpx.Timeout(config.timeout_seconds),
    ) as client:
        yield client


def create_profile_uc(
    auth_client: Annotated[Client, Depends(get_auth_client)],
    profile_client: Annotated[ProfileClient, Depends(get_profile_client)],
    media_client: Annotated[MediaClient, Depends(get_media_client)],
) -> CreateProfile:
    return CreateProfile(
        auth_client=auth_client,
        profile_client=profile_client,
        media_client=media_client,
    )


def get_current_profile_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> UUID | None:
    if credentials is None:
        return None
    try:
        return AccessTokenVerifier(TokenConfig()).get_profile_id(credentials.credentials)
    except jwt.InvalidTokenError:
        return None


def update_profile_uc(
    profile_id: Annotated[UUID | None, Depends(get_current_profile_id)],
    profile_client: Annotated[ProfileClient, Depends(get_profile_client)],
    media_client: Annotated[MediaClient, Depends(get_media_client)],
) -> UpdateProfile:
    return UpdateProfile(
        profile_id=profile_id,
        profile_client=profile_client,
        media_client=media_client,
    )


def get_profile_uc(
    profile_id: Annotated[UUID | None, Depends(get_current_profile_id)],
    profile_client: Annotated[ProfileClient, Depends(get_profile_client)],
) -> GetProfile:
    return GetProfile(profile_id=profile_id, profile_client=profile_client)


def get_media_uc(
    profile_id: Annotated[UUID | None, Depends(get_current_profile_id)],
    client: Annotated[MediaClient, Depends(get_media_client)],
) -> GetMedia:
    return GetMedia(client=client, authenticated=profile_id is not None)


def get_notification_config() -> NotificationClientConfig:
    return NotificationClientConfig()


async def get_notification_client(
    config: Annotated[NotificationClientConfig, Depends(get_notification_config)],
) -> AsyncIterator[NotificationClient]:
    async with NotificationClient(
        base_url=config.base_url,
        timeout=httpx.Timeout(config.timeout_seconds),
    ) as client:
        yield client


def get_notifications_uc(
    profile_id: Annotated[UUID | None, Depends(get_current_profile_id)],
    client: Annotated[NotificationClient, Depends(get_notification_client)],
) -> GetNotifications:
    return GetNotifications(profile_id=profile_id, client=client)


def read_notification_uc(
    profile_id: Annotated[UUID | None, Depends(get_current_profile_id)],
    client: Annotated[NotificationClient, Depends(get_notification_client)],
) -> ReadNotification:
    return ReadNotification(profile_id=profile_id, client=client)


def get_chat_config() -> ChatClientConfig:
    return ChatClientConfig()


async def get_chat_client(
    config: Annotated[ChatClientConfig, Depends(get_chat_config)],
) -> AsyncIterator[ChatClient]:
    async with ChatClient(
        base_url=config.base_url,
        timeout=httpx.Timeout(config.timeout_seconds),
    ) as client:
        yield client


def chats_uc(
    profile_id: Annotated[UUID | None, Depends(get_current_profile_id)],
    client: Annotated[ChatClient, Depends(get_chat_client)],
    media_client: Annotated[MediaClient, Depends(get_media_client)],
) -> Chats:
    return Chats(profile_id=profile_id, client=client, media_client=media_client)


async def get_match_client() -> AsyncIterator[MatchClient]:
    config = MatchClientConfig()
    async with MatchClient(
        base_url=config.base_url,
        timeout=httpx.Timeout(config.timeout_seconds),
    ) as client:
        try:
            yield client
        except httpx.RequestError as exc:
            raise APIRequestError(HTTPStatus.BAD_GATEWAY, "Match Service unavailable") from exc


def matches_uc(
    profile_id: Annotated[UUID | None, Depends(get_current_profile_id)],
    client: Annotated[MatchClient, Depends(get_match_client)],
) -> Matches:
    return Matches(profile_id=profile_id, client=client)
