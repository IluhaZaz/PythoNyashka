from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.profile.domain.schemas import ProfileCreate, ProfileUpdate
from src.profile.infrastructure.storage.postgresql.models import Profile


class ProfileRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def create(self, profile_data: ProfileCreate) -> str:
        """Создает новый профиль и возвращает его ID."""
        data = profile_data.model_dump(mode='json')
        
        if "avatarId" in data:
            data["avatar_id"] = data.pop("avatarId")
        else:
            data["avatar_id"] = None
            
        profile = Profile(**data)
        self.session.add(profile)
        await self.session.flush()  
        await self.session.commit()
        return profile.id

    async def get_by_id(self, profile_id: str) -> Profile | None:
        """Получает профиль по ID."""
        query = select(Profile).where(Profile.id == profile_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update(self, profile_id: str, update_data: ProfileUpdate) -> bool:
        """
        Обновляет профиль. 
        Возвращает True, если профиль найден и обновлен, иначе False.
        """
        data = update_data.model_dump(mode='json', exclude_unset=True)
        
        if not data:
            return True

        if "avatarId" in data:
            data["avatar_id"] = data.pop("avatarId")

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