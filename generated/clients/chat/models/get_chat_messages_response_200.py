from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.message_get import MessageGet


T = TypeVar("T", bound="GetChatMessagesResponse200")


@_attrs_define
class GetChatMessagesResponse200:
    """
    Attributes:
        chat_id (UUID):
        messages (list[MessageGet] | Unset):
    """

    chat_id: UUID
    messages: list[MessageGet] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        chat_id = str(self.chat_id)

        messages: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.messages, Unset):
            messages = []
            for messages_item_data in self.messages:
                messages_item = messages_item_data.to_dict()
                messages.append(messages_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "chatId": chat_id,
            }
        )
        if messages is not UNSET:
            field_dict["messages"] = messages

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.message_get import MessageGet

        d = dict(src_dict)
        chat_id = UUID(d.pop("chatId"))

        _messages = d.pop("messages", UNSET)
        messages: list[MessageGet] | Unset = UNSET
        if _messages is not UNSET:
            messages = []
            for messages_item_data in _messages:
                messages_item = MessageGet.from_dict(messages_item_data)

                messages.append(messages_item)

        get_chat_messages_response_200 = cls(
            chat_id=chat_id,
            messages=messages,
        )

        get_chat_messages_response_200.additional_properties = d
        return get_chat_messages_response_200

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
