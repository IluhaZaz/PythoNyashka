from enum import StrEnum


class ProfileCreateGender(StrEnum):
    FEMALE = "female"
    MALE = "male"

    def __str__(self) -> str:
        return str(self.value)
