from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.notification.domain.schemas import NotificationCreate
from src.notification.infrastructure.storage.postgresql.models import Notification


class NotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, notification_data: NotificationCreate) -> str:
        notification = Notification(**notification_data.model_dump(mode="json"))
        self.session.add(notification)
        await self.session.commit()
        return notification.id

    async def mark_as_read(self, notification_id: str, profile_id: str) -> bool:
        query = (
            update(Notification)
            .where(Notification.id == notification_id, Notification.profile_id == profile_id)
            .values(is_read=True)
            .returning(Notification.id)
        )
        result = await self.session.execute(query)
        if result.scalar_one_or_none() is None:
            return False

        await self.session.commit()
        return True
