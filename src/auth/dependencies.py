from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import usecase
from src.auth.infrastructure.messaging.kafka.publisher import NotificationPublisher
from src.auth.infrastructure.storage.postgresql.repository import AuthRepository
from src.auth.security import AuthConfig, TokenService
from src.infrastructure.storage.postgresql.core import DBSession


async def get_session() -> AsyncIterator[AsyncSession]:
    async with DBSession() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


def get_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AuthRepository:
    return AuthRepository(session)


def get_notification_publisher(request: Request) -> NotificationPublisher:
    return request.app.state.notification_publisher


def register_uc(
    repo: Annotated[AuthRepository, Depends(get_repository)],
    publisher: Annotated[NotificationPublisher, Depends(get_notification_publisher)],
) -> usecase.Register:
    return usecase.Register(repository=repo, notification_publisher=publisher)

def get_token_service() -> TokenService:
    return TokenService(AuthConfig())


def login_uc(
    repo: Annotated[AuthRepository, Depends(get_repository)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> usecase.Login:
    return usecase.Login(
        repository=repo,
        token_service=token_service,
    )

def logout_uc(
    repo: Annotated[AuthRepository, Depends(get_repository)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> usecase.Logout:
    return usecase.Logout(
        repository=repo,
        token_service=token_service,
    )

def change_password_uc(
    repo: Annotated[AuthRepository, Depends(get_repository)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
    publisher: Annotated[NotificationPublisher, Depends(get_notification_publisher)],
) -> usecase.ChangePassword:
    return usecase.ChangePassword(
        repository=repo,
        token_service=token_service,
        notification_publisher=publisher,
    )

def refresh_uc(
    repo: Annotated[AuthRepository, Depends(get_repository)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> usecase.Refresh:
    return usecase.Refresh(
        repository=repo,
        token_service=token_service,
    )
