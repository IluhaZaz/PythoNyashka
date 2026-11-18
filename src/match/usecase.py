from src.match.domain.schemas import MatchGet, MatchHistoryItem, SwipeDecision
from src.match.infrastructure.storage.postgresql.repository import MatchRepository


class MatchNotFoundError(Exception):
    pass


class GetNextMatch:
    def __init__(self, repository: MatchRepository):
        self.repository = repository

    async def execute(self, profile_id: str) -> MatchGet:
        if not await self.repository.lock_profile(profile_id):
            raise MatchNotFoundError("Profile not found")

        target_profile_id = await self.repository.find_candidate(profile_id)
        if target_profile_id is None:
            raise MatchNotFoundError("No more profiles available for matching")

        return await self.repository.create_match(
            initiator_id=profile_id,
            target_id=target_profile_id,
        )


class AcceptMatch:
    def __init__(self, repository: MatchRepository):
        self.repository = repository

    async def execute(self, match_id: str, profile_id: str) -> None:
        updated = await self.repository.update_decision(match_id, profile_id, SwipeDecision.like)
        if not updated:
            raise MatchNotFoundError("Match not found or unauthorized")


class RejectMatch:
    def __init__(self, repository: MatchRepository):
        self.repository = repository

    async def execute(self, match_id: str, profile_id: str) -> None:
        updated = await self.repository.update_decision(
            match_id, profile_id, SwipeDecision.dislike,
        )
        if not updated:
            raise MatchNotFoundError("Match not found or unauthorized")


class GetMatchHistory:
    def __init__(self, repository: MatchRepository):
        self.repository = repository

    async def execute(
        self, profile_id: str, offset: int = 0, limit: int = 10,
    ) -> list[MatchHistoryItem]:
        return await self.repository.get_history(profile_id, offset, limit)
