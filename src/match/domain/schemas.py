from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MatchStatusEnum(str, Enum):
    no_response = "noResponse"
    accepted = "accepted"
    rejected = "rejected"


class SwipeDecision(str, Enum):
    # Values stored in match.matches.status by earlier versions of the service.
    pending = "noResponse"
    like = "accepted"
    dislike = "rejected"


def match_status(own_decision: str, other_decision: str | None) -> MatchStatusEnum:
    if own_decision == SwipeDecision.pending:
        return MatchStatusEnum.no_response
    if SwipeDecision.dislike in (own_decision, other_decision):
        return MatchStatusEnum.rejected
    if own_decision == other_decision == SwipeDecision.like:
        return MatchStatusEnum.accepted
    return MatchStatusEnum.no_response


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


MatchSwipe = Literal["like", "dislike"]


class MatchHistoryItem(MatchGet):
    my_swipe: MatchSwipe | None = Field(
        serialization_alias="mySwipe",
        description="The viewer's own swipe, or null if they have not swiped.",
    )


class MatchesGetResponse(BaseModel):
    matches: list[MatchHistoryItem]
