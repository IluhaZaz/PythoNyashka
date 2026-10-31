from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr


class NotificationEvent(BaseModel):
    source: Literal["auth", "match"]
    profile_id: UUID
    text: str
    email: EmailStr | None = None
    subject: str = "PythoNyashka"
