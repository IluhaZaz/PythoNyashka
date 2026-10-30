from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.storage.postgresql.core import DBSession
from src.notification import usecase
from src.notification.infrastructure.storage.postgresql.repository import NotificationRepository


async def get_session() -> AsyncIterator[AsyncSession]:
    async with DBSession() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


def get_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> NotificationRepository:
    return NotificationRepository(session)


def create_notification_uc(
    repo: Annotated[NotificationRepository, Depends(get_repository)],
) -> usecase.CreateNotification:
    return usecase.CreateNotification(repository=repo)


def get_notifications_uc(
    repo: Annotated[NotificationRepository, Depends(get_repository)],
) -> usecase.GetNotifications:
    return usecase.GetNotifications(repository=repo)


def read_notification_uc(
    repo: Annotated[NotificationRepository, Depends(get_repository)],
) -> usecase.ReadNotification:
    return usecase.ReadNotification(repository=repo)
