from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.storage.postgresql.core import DBSession
from src.match import usecase
from src.match.infrastructure.storage.postgresql.repository import MatchRepository
from collections.abc import AsyncIterator


async def get_session() -> AsyncIterator[AsyncSession]:
    async with DBSession() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


def get_repository(
    session: AsyncSession = Depends(get_session),
) -> MatchRepository:
    return MatchRepository(session)


def get_next_match_uc(
    repo: MatchRepository = Depends(get_repository),
) -> usecase.GetNextMatch:
    return usecase.GetNextMatch(repository=repo)


def accept_match_uc(repo: MatchRepository = Depends(get_repository)) -> usecase.AcceptMatch:
    return usecase.AcceptMatch(repository=repo)


def reject_match_uc(repo: MatchRepository = Depends(get_repository)) -> usecase.RejectMatch:
    return usecase.RejectMatch(repository=repo)


def get_match_history_uc(repo: MatchRepository = Depends(get_repository)) -> usecase.GetMatchHistory:
    return usecase.GetMatchHistory(repository=repo)
