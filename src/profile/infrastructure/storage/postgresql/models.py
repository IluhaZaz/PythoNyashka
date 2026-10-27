import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column, Mapped

from src.infrastructure.storage.postgresql.models import Base


class ProfileMixin:
    __table_args__ = {"schema": "profile"}


class Profile(ProfileMixin, Base):
    __tablename__ = "profiles"

    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    avatar_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    surname: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)
    bio: Mapped[str] = mapped_column(String(1000), nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)  # "male" или "female"
    tags: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )