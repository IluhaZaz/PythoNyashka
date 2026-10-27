from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class GenderEnum(str, Enum):
    male = "male"
    female = "female"


class ProfileCreate(BaseModel):
    id: UUID
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    surname: str = Field(min_length=1, max_length=100)
    age: int = Field(gt=0, lt=150)
    bio: str = Field(max_length=1000)
    gender: GenderEnum
    tags: list[str] = Field(default_factory=list)
    avatarId: Optional[UUID] = None


class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    surname: Optional[str] = Field(default=None, min_length=1, max_length=100)
    age: Optional[int] = Field(default=None, gt=0, lt=150)
    bio: Optional[str] = Field(default=None, max_length=1000)
    gender: Optional[GenderEnum] = None
    tags: Optional[list[str]] = None
    avatarId: Optional[UUID] = None


class ProfileGet(BaseModel):
    id: UUID
    email: EmailStr
    name: str
    surname: str
    age: int
    bio: str
    gender: GenderEnum
    tags: list[str]
    avatarId: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}