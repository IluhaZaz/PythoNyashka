from src.notification.domain.schemas import NotificationCreate
from src.notification.infrastructure.storage.postgresql.repository import NotificationRepository


class NotificationNotFoundError(Exception):
    pass


class CreateNotification:
    def __init__(self, repository: NotificationRepository) -> None:
        self.repository = repository

    async def execute(self, req: NotificationCreate) -> str:
        return await self.repository.create(req)


class ReadNotification:
    def __init__(self, repository: NotificationRepository) -> None:
        self.repository = repository

    async def execute(self, notification_id: str, profile_id: str) -> None:
        if not await self.repository.mark_as_read(notification_id, profile_id):
            raise NotificationNotFoundError()
