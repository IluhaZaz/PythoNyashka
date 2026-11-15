from src.match.domain.schemas import MatchGet
from src.match.infrastructure.storage.postgresql.repository import MatchRepository
from src.match.infrastructure.storage.postgresql.models import Profile  # Модель профилей из соседней схемы, если доступна, либо запрос через клиент


class MatchNotFoundError(Exception):
    pass


class GetNextMatch:
    def __init__(self, repository: MatchRepository, session):
        self.repository = repository
        self.session = session

    async def execute(self, profile_id: str) -> MatchGet:
        active_match = await self.repository.get_active_pending(profile_id)
        if active_match:
            return active_match

        excluded_ids = await self.repository.get_excluded_profile_ids(profile_id)

        from sqlalchemy import select
        from src.profile.infrastructure.storage.postgresql.models import Profile as ProfileModel

        query = (
            select(ProfileModel.id)
            .where(not_(ProfileModel.id.in_(excluded_ids)))
            .limit(1)
        )
        result = await self.session.execute(query)
        target_profile_id = result.scalar_one_or_none()

        if not target_profile_id:
            raise MatchNotFoundError("No more profiles available for matching")

        new_match = await self.repository.create_match(
            initiator_id=profile_id,
            target_id=target_profile_id
        )
        return new_match


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