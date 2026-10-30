from uuid import UUID

from pydantic import BaseModel


class NotificationCreate(BaseModel):
    profile_id: UUID
    text: str


class NotificationCreatedResponse(BaseModel):
    id: UUID


class Error(BaseModel):
    error: str


class ValidationErrorItem(BaseModel):
    field: str
    reason: str


class ValidationErrors(BaseModel):
    errors: list[ValidationErrorItem]
