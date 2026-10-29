from collections.abc import AsyncIterator
from typing import Annotated

import httpx
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from generated.clients.auth.client import AuthenticatedClient, Client
from generated.clients.media.client import Client as MediaClient
from generated.clients.profile.client import Client as ProfileClient
from src.bff.config import AuthClientConfig, MediaClientConfig, ProfileClientConfig
from src.bff.usecase import ChangePassword, CreateProfile, Login, Logout, Refresh

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
