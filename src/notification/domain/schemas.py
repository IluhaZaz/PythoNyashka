from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class NotificationGet(BaseModel):
    id: UUID
    profile_id: UUID
    text: str
    is_read: bool
    is_sent: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationsGetResponse(BaseModel):
    notifications: list[NotificationGet]


class Error(BaseModel):
    error: str


class ValidationErrorItem(BaseModel):
    field: str
    reason: str


class ValidationErrors(BaseModel):
    errors: list[ValidationErrorItem]
