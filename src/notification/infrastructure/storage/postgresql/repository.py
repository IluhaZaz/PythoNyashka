from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.notification.domain.schemas import NotificationCreate, NotificationGet
from src.notification.infrastructure.storage.postgresql.models import Notification


class NotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, notification_data: NotificationCreate) -> str:
        notification = Notification(**notification_data.model_dump(mode="json"))
        self.session.add(notification)
        await self.session.commit()
        return notification.id

    async def get_by_profile(
        self, profile_id: str, limit: int | None = None, offset: int = 0,
    ) -> list[NotificationGet]:
        query = (
            select(Notification)
            .where(Notification.profile_id == profile_id)
            .order_by(Notification.created_at.desc(), Notification.id.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return [NotificationGet.model_validate(row) for row in result.scalars().all()]

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
