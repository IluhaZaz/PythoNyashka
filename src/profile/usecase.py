from sqlalchemy.exc import IntegrityError

from src.profile.domain.schemas import ProfileCreate, ProfileGet, ProfileUpdate
from src.profile.infrastructure.storage.postgresql.repository import ProfileRepository


class ProfileNotFoundError(Exception):
    pass


class ProfileAlreadyExistsError(Exception):
    pass


class CreateProfile:
    def __init__(self, repository: ProfileRepository):
        self.repository = repository

    async def execute(self, req: ProfileCreate) -> str:
        try:
            return await self.repository.create(req)
        except IntegrityError:
            raise ProfileAlreadyExistsError("email already used")


class UpdateProfile:
    def __init__(self, repository: ProfileRepository):
        self.repository = repository

    async def execute(self, profile_id: str, req: ProfileUpdate) -> None:
        updated = await self.repository.update(profile_id, req)
        if not updated:
            raise ProfileNotFoundError()


class GetProfile:
    def __init__(self, repository: ProfileRepository):
        self.repository = repository

    async def execute(self, profile_id: str) -> ProfileGet:
        profile = await self.repository.get_by_id(profile_id)
        if profile is None:
            raise ProfileNotFoundError()
        return profile