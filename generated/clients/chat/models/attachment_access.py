from enum import StrEnum


class AttachmentAccess(StrEnum):
    ALLOWED = "allowed"
    DENIED = "denied"
    UNLINKED = "unlinked"

    def __str__(self) -> str:
        return str(self.value)
