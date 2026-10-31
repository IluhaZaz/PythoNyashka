from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="NotificationGet")


@_attrs_define
class NotificationGet:
    """
    Attributes:
        id (UUID):
        profile_id (UUID):
        text (str):
        is_read (bool):
        is_sent (bool):
        created_at (datetime.datetime):
    """

    id: UUID
    profile_id: UUID
    text: str
    is_read: bool
    is_sent: bool
    created_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        profile_id = str(self.profile_id)

        text = self.text

        is_read = self.is_read

        is_sent = self.is_sent

        created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "profile_id": profile_id,
                "text": text,
                "is_read": is_read,
                "is_sent": is_sent,
                "created_at": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        profile_id = UUID(d.pop("profile_id"))

        text = d.pop("text")

        is_read = d.pop("is_read")

        is_sent = d.pop("is_sent")

        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))

        notification_get = cls(
            id=id,
            profile_id=profile_id,
            text=text,
            is_read=is_read,
            is_sent=is_sent,
            created_at=created_at,
        )

        notification_get.additional_properties = d
        return notification_get

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
