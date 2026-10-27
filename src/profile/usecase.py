from src.profile.domain.schemas import ProfileCreate, ProfileUpdate, ProfileGet
from src.profile.infrastructure.storage.postgresql.repository import ProfileRepository


class ProfileNotFoundError(Exception):
    """Выбрасывается, когда профиль с указанным ID не найден."""
    pass


class CreateProfile:
    def __init__(self, repository: ProfileRepository):
        self.repository = repository

    async def execute(self, req: ProfileCreate) -> str:
        """
        Создает новый профиль.
        Возвращает ID созданного профиля.
        """
        profile_id = await self.repository.create(req)
        return profile_id


class UpdateProfile:
    def __init__(self, repository: ProfileRepository):
        self.repository = repository

    async def execute(self, profile_id: str, req: ProfileUpdate) -> None:
        """
        Обновляет существующий профиль.
        Бросает ProfileNotFoundError, если профиль не найден.
        """
        updated = await self.repository.update(profile_id, req)
        if not updated:
            raise ProfileNotFoundError()


class GetProfile:
    def __init__(self, repository: ProfileRepository):
        self.repository = repository

    async def execute(self, profile_id: str) -> ProfileGet:
        """
        Возвращает профиль по ID.
        Бросает ProfileNotFoundError, если профиль не найден.
        """
        profile = await self.repository.get_by_id(profile_id)
        if profile is None:
            raise ProfileNotFoundError()
        
        # Маппим snake_case (БД) -> camelCase (Pydantic схема)
        return ProfileGet(
            id=profile.id,
            email=profile.email,
            avatarId=profile.avatar_id,
            name=profile.name,
            surname=profile.surname,
            age=profile.age,
            bio=profile.bio,
            gender=profile.gender,
            tags=profile.tags,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )