from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class GenderEnum(str, Enum):
    male = "male"
    female = "female"


class ProfileCreate(BaseModel):
    email: str
    name: str = Field(min_length=1, max_length=100)
    surname: str = Field(min_length=1, max_length=100)
    age: int = Field(gt=0, lt=150)
    bio: str = Field(max_length=1000)
    gender: GenderEnum
    tags: list[str] = Field(default_factory=list)
    avatar_id: Optional[str] = None


class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    surname: Optional[str] = Field(default=None, min_length=1, max_length=100)
    age: Optional[int] = Field(default=None, gt=0, lt=150)
    bio: Optional[str] = Field(default=None, max_length=1000)
    gender: Optional[GenderEnum] = None
    tags: Optional[list[str]] = None
    avatar_id: Optional[str] = None


class ProfileGet(BaseModel):
    id: str
    email: str
    name: str
    surname: str
    age: int
    bio: str
    gender: GenderEnum
    tags: list[str]
    avatar_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}