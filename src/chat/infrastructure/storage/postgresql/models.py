from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, ForeignKeyConstraint, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.storage.postgresql.models import Base


class Chat(Base):
    __tablename__ = "chats"
    __table_args__ = {"schema": "chat"}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4()),
    )


class ChatMember(Base):
    __tablename__ = "chat_members"
    __table_args__ = (
        Index("ix_chat_members_profile_id_chat_id", "profile_id", "chat_id"),
        {"schema": "chat"},
    )

    chat_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("chat.chats.id", ondelete="CASCADE"), primary_key=True,
    )
    profile_id: Mapped[str] = mapped_column(String(36), primary_key=True)


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        ForeignKeyConstraint(
            ["chat_id", "sender_id"],
            ["chat.chat_members.chat_id", "chat.chat_members.profile_id"],
            ondelete="CASCADE",
        ),
        Index("ix_messages_chat_id_sent_at_id", "chat_id", "sent_at", "id"),
        {"schema": "chat"},
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4()),
    )
    chat_id: Mapped[str] = mapped_column(String(36), nullable=False)
    sender_id: Mapped[str] = mapped_column(String(36), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    media: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
