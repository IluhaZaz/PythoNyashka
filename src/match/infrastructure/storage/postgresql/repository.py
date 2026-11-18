from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from src.match.domain.schemas import MatchGet, MatchHistoryItem, MatchSwipe, SwipeDecision, match_status
from src.match.infrastructure.storage.postgresql.models import Match
from src.profile.infrastructure.storage.postgresql.models import Profile


SWIPE_BY_DECISION: dict[str, MatchSwipe] = {
    SwipeDecision.like.value: "like",
    SwipeDecision.dislike.value: "dislike",
}


class MatchRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def lock_profile(self, profile_id: str) -> bool:
        query = select(Profile.id).where(Profile.id == profile_id).with_for_update()
        return await self.session.scalar(query) is not None

    async def find_candidate(self, profile_id: str) -> str | None:
        seen = select(Match.target_profile_id).where(Match.initiator_profile_id == profile_id)
        incoming_like = (
            select(Match.id)
            .where(
                Match.initiator_profile_id == Profile.id,
                Match.target_profile_id == profile_id,
                Match.decision == SwipeDecision.like.value,
            )
            .exists()
        )
        query = (
            select(Profile.id)
            .where(Profile.id != profile_id, Profile.id.not_in(seen))
            .order_by(incoming_like.desc(), Profile.id)
            .limit(1)
        )
        return await self.session.scalar(query)

    async def create_match(self, initiator_id: str, target_id: str) -> MatchGet:
        new_match = Match(
            initiator_profile_id=initiator_id,
            target_profile_id=target_id,
        )
        self.session.add(new_match)
        await self.session.commit()
        return self._to_response(new_match, other_decision=None)

    async def update_decision(
        self, match_id: str, profile_id: str, decision: SwipeDecision,
    ) -> bool:
        query = (
            update(Match)
            .where(
                Match.id == match_id,
                Match.initiator_profile_id == profile_id
            )
            .values(decision=decision.value)
            .returning(Match.id)
        )
        result = await self.session.execute(query)
        updated_id = result.scalar_one_or_none()
        if updated_id is None:
            return False
        await self.session.commit()
        return True

    async def get_history(
        self, profile_id: str, offset: int = 0, limit: int = 10,
    ) -> list[MatchHistoryItem]:
        reciprocal = aliased(Match)
        other_decision = (
            select(reciprocal.decision)
            .where(
                reciprocal.initiator_profile_id == Match.target_profile_id,
                reciprocal.target_profile_id == Match.initiator_profile_id,
                reciprocal.decision != SwipeDecision.pending.value,
            )
            .order_by(reciprocal.created_at.desc(), reciprocal.id.desc())
            .limit(1)
            .scalar_subquery()
        )
        query = (
            select(Match, other_decision)
            .where(Match.initiator_profile_id == profile_id)
            .order_by(Match.created_at.desc(), Match.id.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return [
            MatchHistoryItem(
                **self._to_response(match, other_decision).model_dump(),
                my_swipe=SWIPE_BY_DECISION.get(match.decision),
            )
            for match, other_decision in result
        ]

    @staticmethod
    def _to_response(match: Match, other_decision: str | None) -> MatchGet:
        return MatchGet(
            id=match.id,
            initiator_profile_id=match.initiator_profile_id,
            target_profile_id=match.target_profile_id,
            status=match_status(match.decision, other_decision),
            created_at=match.created_at,
        )
