from enum import StrEnum


class MatchGetStatus(StrEnum):
    ACCEPTED = "accepted"
    NORESPONSE = "noResponse"
    REJECTED = "rejected"

    def __str__(self) -> str:
        return str(self.value)
