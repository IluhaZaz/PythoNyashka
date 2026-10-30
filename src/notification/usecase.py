from src.notification.domain.schemas import NotificationCreate, NotificationGet
from src.notification.infrastructure.storage.postgresql.repository import NotificationRepository


class NotificationNotFoundError(Exception):
    pass


class CreateNotification:
    def __init__(self, repository: NotificationRepository) -> None:
        self.repository = repository

    async def execute(self, req: NotificationCreate) -> str:
        return await self.repository.create(req)


class GetNotifications:
    def __init__(self, repository: NotificationRepository) -> None:
        self.repository = repository

    async def execute(
        self, profile_id: str, limit: int | None = None, offset: int = 0,
    ) -> list[NotificationGet]:
        return await self.repository.get_by_profile(profile_id, limit=limit, offset=offset)


class ReadNotification:
    def __init__(self, repository: NotificationRepository) -> None:
        self.repository = repository

    async def execute(self, notification_id: str, profile_id: str) -> None:
        if not await self.repository.mark_as_read(notification_id, profile_id):
            raise NotificationNotFoundError()
