import uuid
from sqlalchemy import select, update, not_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.match.domain.schemas import MatchGet
from src.match.infrastructure.storage.postgresql.models import Match


class MatchRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_active_pending(self, profile_id: str) -> MatchGet | None:
        query = (
            select(Match)
            .where(
                Match.initiator_profile_id == profile_id,
                Match.status == "noResponse"
            )
            .order_by(Match.created_at.asc())
            .limit(1)
        )
        result = await self.session.execute(query)
        match = result.scalar_one_or_none()
        if not match:
            return None
        return MatchGet.model_validate(match, from_attributes=True)

    async def get_excluded_profile_ids(self, profile_id: str) -> list[str]:
        query = select(Match.target_profile_id).where(Match.initiator_profile_id == profile_id)
        result = await self.session.execute(query)
        excluded = [row[0] for row in result.all()]
        excluded.append(profile_id)  ж# Исключаем самого себя
        return excluded

    async def create_match(self, initiator_id: str, target_id: str) -> MatchGet:
        new_match = Match(
            id=str(uuid.uuid4()),
            initiator_profile_id=initiator_id,
            target_profile_id=target_id,
            status="noResponse"
        )
        self.session.add(new_match)
        await self.session.commit()
        await self.session.refresh(new_match)
        return MatchGet.model_validate(new_match, from_attributes=True)

    async def get_by_id(self, match_id: str) -> Match | None:
        query = select(Match).where(Match.id == match_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_status(self, match_id: str, profile_id: str, new_status: str) -> bool:
        query = (
            update(Match)
            .where(
                Match.id == match_id,
                Match.initiator_profile_id == profile_id
            )
            .values(status=new_status)
            .returning(Match.id)
        )
        result = await self.session.execute(query)
        updated_id = result.scalar_one_or_none()
        if updated_id is None:
            return False
        await self.session.commit()
        return True

    async def get_history(self, profile_id: str, offset: int = 0, limit: int = 10) -> list[MatchGet]:
        query = (
            select(Match)
            .where(Match.initiator_profile_id == profile_id)
            .order_by(Match.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query.execution_options(populate_existing=True))
        matches = result.scalars().all()
        return [MatchGet.model_validate(m, from_attributes=True) for m in matches]