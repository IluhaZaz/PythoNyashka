from collections.abc import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.profile import usecase
from src.profile.infrastructure.storage.postgresql.repository import ProfileRepository
from src.infrastructure.storage.postgresql.core import DBSession


async def get_session() -> AsyncIterator[AsyncSession]:
    """Получает асинхронную сессию БД. Автоматически делает rollback при ошибке."""
    async with DBSession() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


def get_repository(
    session: AsyncSession = Depends(get_session),
) -> ProfileRepository:
    """Создает репозиторий профиля."""
    return ProfileRepository(session)


def create_profile_uc(
    repo: ProfileRepository = Depends(get_repository),
) -> usecase.CreateProfile:
    """Создает use case для создания профиля."""
    return usecase.CreateProfile(repository=repo)


def update_profile_uc(
    repo: ProfileRepository = Depends(get_repository),
) -> usecase.UpdateProfile:
    """Создает use case для обновления профиля."""
    return usecase.UpdateProfile(repository=repo)


def get_profile_uc(
    repo: ProfileRepository = Depends(get_repository),
) -> usecase.GetProfile:
    """Создает use case для получения профиля."""
    return usecase.GetProfile(repository=repo)