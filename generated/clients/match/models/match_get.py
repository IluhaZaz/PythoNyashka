from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.match_get_status import MatchGetStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="MatchGet")


@_attrs_define
class MatchGet:
    """
    Attributes:
        id (UUID | Unset):
        initiator_profile_id (UUID | Unset):
        target_profile_id (UUID | Unset):
        status (MatchGetStatus | Unset):
        created_at (datetime.datetime | Unset):
    """

    id: UUID | Unset = UNSET
    initiator_profile_id: UUID | Unset = UNSET
    target_profile_id: UUID | Unset = UNSET
    status: MatchGetStatus | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id: str | Unset = UNSET
        if not isinstance(self.id, Unset):
            id = str(self.id)

        initiator_profile_id: str | Unset = UNSET
        if not isinstance(self.initiator_profile_id, Unset):
            initiator_profile_id = str(self.initiator_profile_id)

        target_profile_id: str | Unset = UNSET
        if not isinstance(self.target_profile_id, Unset):
            target_profile_id = str(self.target_profile_id)

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        created_at: str | Unset = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if initiator_profile_id is not UNSET:
            field_dict["initiatorProfileId"] = initiator_profile_id
        if target_profile_id is not UNSET:
            field_dict["targetProfileId"] = target_profile_id
        if status is not UNSET:
            field_dict["status"] = status
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _id = d.pop("id", UNSET)
        id: UUID | Unset
        if isinstance(_id, Unset):
            id = UNSET
        else:
            id = UUID(_id)

        _initiator_profile_id = d.pop("initiatorProfileId", UNSET)
        initiator_profile_id: UUID | Unset
        if isinstance(_initiator_profile_id, Unset):
            initiator_profile_id = UNSET
        else:
            initiator_profile_id = UUID(_initiator_profile_id)

        _target_profile_id = d.pop("targetProfileId", UNSET)
        target_profile_id: UUID | Unset
        if isinstance(_target_profile_id, Unset):
            target_profile_id = UNSET
        else:
            target_profile_id = UUID(_target_profile_id)

        _status = d.pop("status", UNSET)
        status: MatchGetStatus | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = MatchGetStatus(_status)

        _created_at = d.pop("createdAt", UNSET)
        created_at: datetime.datetime | Unset
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = datetime.datetime.fromisoformat(_created_at)

        match_get = cls(
            id=id,
            initiator_profile_id=initiator_profile_id,
            target_profile_id=target_profile_id,
            status=status,
            created_at=created_at,
        )

        match_get.additional_properties = d
        return match_get

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
