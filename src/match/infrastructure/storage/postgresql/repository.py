from sqlalchemy import and_, or_, select
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

    async def get_pending_match(self, profile_id: str) -> MatchGet | None:
        query = (
            select(Match)
            .join(Profile, Profile.id == Match.target_profile_id)
            .where(
                Match.initiator_profile_id == profile_id,
                Match.decision == SwipeDecision.pending.value,
            )
            .order_by(Match.created_at, Match.id)
            .limit(1)
        )
        match = await self.session.scalar(query)
        if match is None:
            return None
        return self._to_response(match, other_decision=None)

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
        if not await self.lock_profile(profile_id):
            return False

        match = await self.session.get(Match, match_id)
        if match is None:
            return False

        if match.initiator_profile_id == profile_id:
            match.decision = decision.value
        elif match.target_profile_id == profile_id and match.decision == SwipeDecision.like:
            if not await self._answer_incoming(profile_id, match.initiator_profile_id, decision):
                return False
        else:
            return False

        await self.session.commit()
        return True

    async def _answer_incoming(
        self, profile_id: str, sender_id: str, decision: SwipeDecision,
    ) -> bool:
        query = (
            select(Match)
            .where(
                Match.initiator_profile_id == profile_id,
                Match.target_profile_id == sender_id,
            )
            .order_by(
                (Match.decision != SwipeDecision.pending.value).desc(),
                Match.created_at.desc(),
                Match.id.desc(),
            )
            .limit(1)
        )
        answer = await self.session.scalar(query)
        if answer is None:
            self.session.add(Match(
                initiator_profile_id=profile_id,
                target_profile_id=sender_id,
                decision=decision.value,
            ))
        elif answer.decision == SwipeDecision.pending:
            answer.decision = decision.value
        else:
            return answer.decision == decision

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
            .where(or_(
                and_(
                    Match.initiator_profile_id == profile_id,
                    Match.decision != SwipeDecision.pending.value,
                ),
                and_(
                    Match.target_profile_id == profile_id,
                    Match.decision == SwipeDecision.like.value,
                    other_decision.is_(None),
                ),
            ))
            .order_by(Match.created_at.desc(), Match.id.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return [
            MatchHistoryItem(
                **self._to_response(match, other_decision).model_dump(),
                my_swipe=(
                    SWIPE_BY_DECISION.get(match.decision)
                    if match.initiator_profile_id == profile_id else None
                ),
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
