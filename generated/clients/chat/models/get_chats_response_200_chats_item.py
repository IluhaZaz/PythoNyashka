from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

T = TypeVar("T", bound="GetChatsResponse200ChatsItem")


@_attrs_define
class GetChatsResponse200ChatsItem:
    """
    Attributes:
        id (UUID):
        participant_ids (list[UUID]):
    """

    id: UUID
    participant_ids: list[UUID]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        participant_ids = []
        for participant_ids_item_data in self.participant_ids:
            participant_ids_item = str(participant_ids_item_data)
            participant_ids.append(participant_ids_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "participantIds": participant_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        participant_ids = []
        _participant_ids = d.pop("participantIds")
        for participant_ids_item_data in _participant_ids:
            participant_ids_item = UUID(participant_ids_item_data)

            participant_ids.append(participant_ids_item)

        get_chats_response_200_chats_item = cls(
            id=id,
            participant_ids=participant_ids,
        )

        get_chats_response_200_chats_item.additional_properties = d
        return get_chats_response_200_chats_item

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
