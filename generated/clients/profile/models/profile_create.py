from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.profile_create_gender import ProfileCreateGender
from ..types import UNSET, Unset

T = TypeVar("T", bound="ProfileCreate")


@_attrs_define
class ProfileCreate:
    """
    Attributes:
        email (str):
        name (str):
        surname (str):
        age (int):
        bio (str):
        gender (ProfileCreateGender):
        tags (list[str]):
        avatar_id (str | Unset):
    """

    email: str
    name: str
    surname: str
    age: int
    bio: str
    gender: ProfileCreateGender
    tags: list[str]
    avatar_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        name = self.name

        surname = self.surname

        age = self.age

        bio = self.bio

        gender = self.gender.value

        tags = self.tags

        avatar_id = self.avatar_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
                "name": name,
                "surname": surname,
                "age": age,
                "bio": bio,
                "gender": gender,
                "tags": tags,
            }
        )
        if avatar_id is not UNSET:
            field_dict["avatar_id"] = avatar_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        name = d.pop("name")

        surname = d.pop("surname")

        age = d.pop("age")

        bio = d.pop("bio")

        gender = ProfileCreateGender(d.pop("gender"))

        tags = cast(list[str], d.pop("tags"))

        avatar_id = d.pop("avatar_id", UNSET)

        profile_create = cls(
            email=email,
            name=name,
            surname=surname,
            age=age,
            bio=bio,
            gender=gender,
            tags=tags,
            avatar_id=avatar_id,
        )

        profile_create.additional_properties = d
        return profile_create

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
