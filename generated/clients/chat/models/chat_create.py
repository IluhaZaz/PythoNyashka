from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

T = TypeVar("T", bound="ChatCreate")


@_attrs_define
class ChatCreate:
    """
    Attributes:
        contact_ids (list[UUID]):
    """

    contact_ids: list[UUID]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        contact_ids = []
        for contact_ids_item_data in self.contact_ids:
            contact_ids_item = str(contact_ids_item_data)
            contact_ids.append(contact_ids_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "contactIds": contact_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        contact_ids = []
        _contact_ids = d.pop("contactIds")
        for contact_ids_item_data in _contact_ids:
            contact_ids_item = UUID(contact_ids_item_data)

            contact_ids.append(contact_ids_item)

        chat_create = cls(
            contact_ids=contact_ids,
        )

        chat_create.additional_properties = d
        return chat_create

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
