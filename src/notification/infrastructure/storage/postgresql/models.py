import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, String, Text, false, func
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.storage.postgresql.models import Base


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_profile_created_at_id", "profile_id", "created_at", "id"),
        {"schema": "notification"},
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()),
    )
    profile_id: Mapped[str] = mapped_column(String(36), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false(),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
