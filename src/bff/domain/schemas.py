from typing import Literal
from uuid import UUID

from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict, EmailStr, Field


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


class ErrorResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    error: str


class ProfileCreate(BaseModel):
    model_config = ConfigDict(strict=True)

    email: EmailStr
    password: str = Field(repr=False, json_schema_extra={"writeOnly": True})
    name: str = Field(min_length=1, max_length=100)
    surname: str = Field(min_length=1, max_length=100)
    age: int = Field(strict=False, gt=0, lt=150)
    bio: str = Field(max_length=1000)
    gender: Literal["male", "female"]
    tags: list[str]
    avatar: UploadFile | None = None


class ProfileCreatedResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    id: UUID
