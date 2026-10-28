import uuid

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.profile.domain.schemas import ProfileCreate, ProfileGet, ProfileUpdate
from src.profile.infrastructure.storage.postgresql.models import Profile


class ProfileRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def create(self, profile_data: ProfileCreate) -> str:
        data = profile_data.model_dump(mode='json')
        data["id"] = str(uuid.uuid4())
        
        profile = Profile(**data)
        self.session.add(profile)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise
        return profile.id

    async def get_by_id(self, profile_id: str) -> ProfileGet | None:
        query = select(Profile).where(Profile.id == profile_id)
        result = await self.session.execute(query)
        profile = result.scalar_one_or_none()
        if profile is None:
            return None
        return ProfileGet.model_validate(profile, from_attributes=True)

    async def update(self, profile_id: str, update_data: ProfileUpdate) -> bool:
        data = update_data.model_dump(mode='json', exclude_unset=True)
        
        if not data:
            return True

        query = (
            update(Profile)
            .where(Profile.id == profile_id)
            .values(**data)
            .returning(Profile.id)
        )
        
        result = await self.session.execute(query)
        updated_id = result.scalar_one_or_none()
        
        if updated_id is None:
            return False
            
        await self.session.commit()
        return True