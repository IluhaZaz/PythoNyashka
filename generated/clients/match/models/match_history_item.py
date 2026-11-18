from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from ..models.match_get_status import MatchGetStatus
from ..models.match_swipe import MatchSwipe
from ..types import UNSET, Unset

T = TypeVar("T", bound="MatchHistoryItem")


@_attrs_define
class MatchHistoryItem:
    """
    Attributes:
        my_swipe (MatchSwipe | None): The viewer's own swipe, or null if they have not swiped.
        id (UUID | Unset):
        initiator_profile_id (UUID | Unset):
        target_profile_id (UUID | Unset):
        status (MatchGetStatus | Unset): noResponse means the viewer has not swiped or is waiting for a reply. accepted
            requires two likes. rejected means the viewer has swiped and at least one profile disliked the pair.
        created_at (datetime.datetime | Unset):
    """

    my_swipe: MatchSwipe | None
    id: UUID | Unset = UNSET
    initiator_profile_id: UUID | Unset = UNSET
    target_profile_id: UUID | Unset = UNSET
    status: MatchGetStatus | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        my_swipe: None | str
        if isinstance(self.my_swipe, MatchSwipe):
            my_swipe = self.my_swipe.value
        else:
            my_swipe = self.my_swipe

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
        field_dict.update(
            {
                "mySwipe": my_swipe,
            }
        )
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
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)

        def _parse_my_swipe(data: object) -> MatchSwipe | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                my_swipe_type_0 = MatchSwipe(data)

                return my_swipe_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(MatchSwipe | None, data)

        my_swipe = _parse_my_swipe(d.pop("mySwipe"))

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

        match_history_item = cls(
            my_swipe=my_swipe,
            id=id,
            initiator_profile_id=initiator_profile_id,
            target_profile_id=target_profile_id,
            status=status,
            created_at=created_at,
        )

        match_history_item.additional_properties = d
        return match_history_item

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
