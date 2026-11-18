import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.storage.postgresql.models import Base
from src.match.domain.schemas import SwipeDecision


class MatchMixin:
    __table_args__ = {"schema": "match"}


class Match(MatchMixin, Base):
    __tablename__ = "matches"

    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    initiator_profile_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    target_profile_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    decision: Mapped[str] = mapped_column(
        "status", String(20), nullable=False, default=SwipeDecision.pending.value,
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
