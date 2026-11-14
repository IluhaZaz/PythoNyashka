from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetChatsResponse200")


@_attrs_define
class GetChatsResponse200:
    """
    Attributes:
        chat_ids (list[UUID] | Unset):
    """

    chat_ids: list[UUID] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        chat_ids: list[str] | Unset = UNSET
        if not isinstance(self.chat_ids, Unset):
            chat_ids = []
            for chat_ids_item_data in self.chat_ids:
                chat_ids_item = str(chat_ids_item_data)
                chat_ids.append(chat_ids_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if chat_ids is not UNSET:
            field_dict["chatIds"] = chat_ids

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        _chat_ids = d.pop("chatIds", UNSET)
        chat_ids: list[UUID] | Unset = UNSET
        if _chat_ids is not UNSET:
            chat_ids = []
            for chat_ids_item_data in _chat_ids:
                chat_ids_item = UUID(chat_ids_item_data)

                chat_ids.append(chat_ids_item)

        get_chats_response_200 = cls(
            chat_ids=chat_ids,
        )

        get_chats_response_200.additional_properties = d
        return get_chats_response_200

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
