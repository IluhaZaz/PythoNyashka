from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from ..types import UNSET, Unset

T = TypeVar("T", bound="MessageGet")


@_attrs_define
class MessageGet:
    """
    Attributes:
        id (UUID):
        sender_id (UUID):
        text (str):
        media (list[UUID]):
        sent_at (datetime.datetime | Unset):
    """

    id: UUID
    sender_id: UUID
    text: str
    media: list[UUID]
    sent_at: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        sender_id = str(self.sender_id)

        text = self.text

        media = []
        for media_item_data in self.media:
            media_item = str(media_item_data)
            media.append(media_item)

        sent_at: str | Unset = UNSET
        if not isinstance(self.sent_at, Unset):
            sent_at = self.sent_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "senderId": sender_id,
                "text": text,
                "media": media,
            }
        )
        if sent_at is not UNSET:
            field_dict["sentAt"] = sent_at

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        sender_id = UUID(d.pop("senderId"))

        text = d.pop("text")

        media = []
        _media = d.pop("media")
        for media_item_data in _media:
            media_item = UUID(media_item_data)

            media.append(media_item)

        _sent_at = d.pop("sentAt", UNSET)
        sent_at: datetime.datetime | Unset
        if isinstance(_sent_at, Unset):
            sent_at = UNSET
        else:
            sent_at = datetime.datetime.fromisoformat(_sent_at)

        message_get = cls(
            id=id,
            sender_id=sender_id,
            text=text,
            media=media,
            sent_at=sent_at,
        )

        message_get.additional_properties = d
        return message_get

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
