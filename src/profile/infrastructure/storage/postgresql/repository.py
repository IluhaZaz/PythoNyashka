from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.profile.domain.schemas import ProfileCreate, ProfileUpdate
from src.profile.infrastructure.storage.postgresql.models import Profile


class ProfileRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def create(self, profile_data: ProfileCreate) -> str:
        """Создает новый профиль и возвращает его ID."""
        # Преобразуем Pydantic модель в dict для SQLAlchemy
        # avatarId из схемы маппим в avatar_id для БД
        data = profile_data.model_dump()
        if "avatarId" in data:
            data["avatar_id"] = data.pop("avatarId")
            
        profile = Profile(**data)
        self.session.add(profile)
        await self.session.flush()  # Получаем ID до коммита
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
        Использует exclude_unset=True, чтобы обновлять только переданные поля (PATCH).
        Возвращает True, если профиль найден и обновлен, иначе False.
        """
        # Получаем только те поля, которые были явно переданы в запросе
        data = update_data.model_dump(exclude_unset=True)
        
        if not data:
            return True  # Нечего обновлять, считаем успехом

        # Маппинг avatarId -> avatar_id для БД
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