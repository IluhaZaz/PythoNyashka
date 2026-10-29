from enum import StrEnum


class ProfileGetGender(StrEnum):
    FEMALE = "female"
    MALE = "male"

    def __str__(self) -> str:
        return str(self.value)
