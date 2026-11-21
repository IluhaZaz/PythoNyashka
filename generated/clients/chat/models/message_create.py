from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from ..types import UNSET, Unset

T = TypeVar("T", bound="MessageCreate")


@_attrs_define
class MessageCreate:
    """
    Attributes:
        text (str):
        media (list[UUID]):
        sender_id (UUID | Unset):
    """

    text: str
    media: list[UUID]
    sender_id: UUID | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        text = self.text

        media = []
        for media_item_data in self.media:
            media_item = str(media_item_data)
            media.append(media_item)

        sender_id: str | Unset = UNSET
        if not isinstance(self.sender_id, Unset):
            sender_id = str(self.sender_id)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "text": text,
                "media": media,
            }
        )
        if sender_id is not UNSET:
            field_dict["senderId"] = sender_id

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        text = d.pop("text")

        media = []
        _media = d.pop("media")
        for media_item_data in _media:
            media_item = UUID(media_item_data)

            media.append(media_item)

        _sender_id = d.pop("senderId", UNSET)
        sender_id: UUID | Unset
        if isinstance(_sender_id, Unset):
            sender_id = UNSET
        else:
            sender_id = UUID(_sender_id)

        message_create = cls(
            text=text,
            media=media,
            sender_id=sender_id,
        )

        message_create.additional_properties = d
        return message_create

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
