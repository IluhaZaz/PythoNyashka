from enum import StrEnum


class MatchSwipe(StrEnum):
    DISLIKE = "dislike"
    LIKE = "like"

    def __str__(self) -> str:
        return str(self.value)
