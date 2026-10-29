from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.profile_get_gender import ProfileGetGender
from ..types import UNSET, Unset

T = TypeVar("T", bound="ProfileGet")


@_attrs_define
class ProfileGet:
    """
    Attributes:
        id (str):
        name (str):
        surname (str):
        age (int):
        bio (str):
        gender (ProfileGetGender):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        tags (list[str]):
        email (str | Unset):
        avatar_id (str | Unset):
    """

    id: str
    name: str
    surname: str
    age: int
    bio: str
    gender: ProfileGetGender
    created_at: datetime.datetime
    updated_at: datetime.datetime
    tags: list[str]
    email: str | Unset = UNSET
    avatar_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        surname = self.surname

        age = self.age

        bio = self.bio

        gender = self.gender.value

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        tags = self.tags

        email = self.email

        avatar_id = self.avatar_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "surname": surname,
                "age": age,
                "bio": bio,
                "gender": gender,
                "created_at": created_at,
                "updated_at": updated_at,
                "tags": tags,
            }
        )
        if email is not UNSET:
            field_dict["email"] = email
        if avatar_id is not UNSET:
            field_dict["avatar_id"] = avatar_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        surname = d.pop("surname")

        age = d.pop("age")

        bio = d.pop("bio")

        gender = ProfileGetGender(d.pop("gender"))

        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))

        updated_at = datetime.datetime.fromisoformat(d.pop("updated_at"))

        tags = cast(list[str], d.pop("tags"))

        email = d.pop("email", UNSET)

        avatar_id = d.pop("avatar_id", UNSET)

        profile_get = cls(
            id=id,
            name=name,
            surname=surname,
            age=age,
            bio=bio,
            gender=gender,
            created_at=created_at,
            updated_at=updated_at,
            tags=tags,
            email=email,
            avatar_id=avatar_id,
        )

        profile_get.additional_properties = d
        return profile_get

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
