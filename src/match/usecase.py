from src.match.domain.schemas import MatchGet
from src.match.infrastructure.storage.postgresql.repository import MatchRepository


class MatchNotFoundError(Exception):
    pass


class GetNextMatch:
    def __init__(self, repository: MatchRepository):
        self.repository = repository

    async def execute(self, profile_id: str) -> MatchGet:
        match = await self.repository.get_next_pending(profile_id)
        if not match:
            raise MatchNotFoundError("No matches available")
        return match


class AcceptMatch:
    def __init__(self, repository: MatchRepository):
        self.repository = repository

    async def execute(self, match_id: str, profile_id: str) -> None:
        updated = await self.repository.update_status(match_id, profile_id, "accepted")
        if not updated:
            raise MatchNotFoundError("Match not found or unauthorized")


class RejectMatch:
    def __init__(self, repository: MatchRepository):
        self.repository = repository

    async def execute(self, match_id: str, profile_id: str) -> None:
        updated = await self.repository.update_status(match_id, profile_id, "rejected")
        if not updated:
            raise MatchNotFoundError("Match not found or unauthorized")


class GetMatchHistory:
    def __init__(self, repository: MatchRepository):
        self.repository = repository

    async def execute(self, profile_id: str, offset: int = 0, limit: int = 10) -> list[MatchGet]:
        return await self.repository.get_history(profile_id, offset, limit)