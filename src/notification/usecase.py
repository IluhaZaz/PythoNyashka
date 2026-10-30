from src.notification.domain.events import NotificationEvent
from src.notification.domain.schemas import NotificationGet
from src.notification.infrastructure.storage.postgresql.repository import NotificationRepository


class NotificationNotFoundError(Exception):
    pass


class CreateNotification:
    def __init__(self, repository: NotificationRepository) -> None:
        self.repository = repository

    async def execute(self, event: NotificationEvent) -> str:
        return await self.repository.create(profile_id=str(event.profile_id), text=event.text)


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
