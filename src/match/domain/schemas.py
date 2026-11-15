from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class MatchStatusEnum(str, Enum):
    no_response = "noResponse"
    accepted = "accepted"
    rejected = "rejected"


class MatchGet(BaseModel):
    id: str
    initiator_profile_id: str = Field(
        validation_alias="initiator_profile_id",
        serialization_alias="initiatorProfileId"
    )
    target_profile_id: str = Field(
        validation_alias="target_profile_id",
        serialization_alias="targetProfileId"
    )
    status: MatchStatusEnum
    created_at: datetime = Field(
        validation_alias="created_at",
        serialization_alias="createdAt"
    )

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class MatchesGetResponse(BaseModel):
    matches: list[MatchGet]