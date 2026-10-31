from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import UploadFile
from pydantic import AliasChoices, BaseModel, ConfigDict, EmailStr, Field

from src.bff.domain.tags import ProfileTag


class LoginRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    email: EmailStr
    password: str


class AuthTokens(BaseModel):
    model_config = ConfigDict(strict=True)

    access_token: str
    refresh_token: str
    token_type: Literal["Bearer"]
    expires_in: int | None = None


class ChangePasswordRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    old_password: str = Field(repr=False, json_schema_extra={"writeOnly": True})
    new_password: str = Field(repr=False, json_schema_extra={"writeOnly": True})


class RefreshTokenRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    refresh_token: str = Field(repr=False, json_schema_extra={"writeOnly": True})


class ErrorResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    error: str


class NotificationGet(BaseModel):
    model_config = ConfigDict(strict=True)

    id: UUID
    profile_id: UUID
    text: str
    is_read: bool
    is_sent: bool
    created_at: datetime


class NotificationsGetResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    notifications: list[NotificationGet]


class ProfileCreate(BaseModel):
    model_config = ConfigDict(strict=True)

    email: EmailStr
    password: str = Field(repr=False, json_schema_extra={"writeOnly": True})
    name: str = Field(min_length=1, max_length=100)
    surname: str = Field(min_length=1, max_length=100)
    age: int = Field(strict=False, gt=0, lt=150)
    bio: str = Field(max_length=1000)
    gender: Literal["male", "female"]
    tags: list[ProfileTag]
    avatar: UploadFile | None = None


class ProfileCreatedResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    id: UUID


class ProfileGet(BaseModel):
    model_config = ConfigDict(strict=True)

    id: UUID
    name: str
    surname: str
    age: int
    bio: str
    gender: Literal["male", "female"]
    tags: list[str]
    created_at: datetime
    updated_at: datetime
    email: EmailStr | None = None
    avatar: UUID | None = Field(
        default=None,
        validation_alias=AliasChoices("avatar", "avatar_id"),
    )


class ProfileGetResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    profile: ProfileGet


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str | None = Field(default=None, min_length=1, max_length=100)
    surname: str | None = Field(default=None, min_length=1, max_length=100)
    age: int | None = Field(default=None, strict=False, gt=0, lt=150)
    bio: str | None = Field(default=None, max_length=1000)
    gender: Literal["male", "female"] | None = None
    tags: list[ProfileTag] | None = None
    avatar: UploadFile | None = None
