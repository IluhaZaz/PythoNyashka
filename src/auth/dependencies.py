from collections.abc import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import usecase
from src.auth.infrastructure.storage.postgresql.repository import AuthRepository
from src.infrastructure.storage.postgresql.core import DBSession


async def get_session() -> AsyncIterator[AsyncSession]:
    async with DBSession() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


def get_repository(
    session: AsyncSession = Depends(get_session),
) -> AuthRepository:
    return AuthRepository(session)


def register_uc(
    repo: AuthRepository = Depends(get_repository),
) -> usecase.Register:
    return usecase.Register(repository=repo)