from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.storage.postgresql.core import DBSession
from src.profile import usecase
from src.profile.infrastructure.storage.postgresql.repository import ProfileRepository


async def get_session() -> AsyncIterator[AsyncSession]:
    async with DBSession() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


def get_repository(
    session: AsyncSession = Depends(get_session),
) -> ProfileRepository:
    return ProfileRepository(session)


def create_profile_uc(
    repo: ProfileRepository = Depends(get_repository),
) -> usecase.CreateProfile:
    return usecase.CreateProfile(repository=repo)


def update_profile_uc(
    repo: ProfileRepository = Depends(get_repository),
) -> usecase.UpdateProfile:
    return usecase.UpdateProfile(repository=repo)


def get_profile_uc(
    repo: ProfileRepository = Depends(get_repository),
) -> usecase.GetProfile:
    return usecase.GetProfile(repository=repo)


def delete_profile_uc(
    repo: Annotated[ProfileRepository, Depends(get_repository)],
) -> usecase.DeleteProfile:
    return usecase.DeleteProfile(repository=repo)
