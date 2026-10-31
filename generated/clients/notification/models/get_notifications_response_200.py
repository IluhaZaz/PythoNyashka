from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.notification_get import NotificationGet


T = TypeVar("T", bound="GetNotificationsResponse200")


@_attrs_define
class GetNotificationsResponse200:
    """
    Attributes:
        notifications (list[NotificationGet]):
    """

    notifications: list[NotificationGet]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        notifications = []
        for notifications_item_data in self.notifications:
            notifications_item = notifications_item_data.to_dict()
            notifications.append(notifications_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "notifications": notifications,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.notification_get import NotificationGet  # noqa: PLC0415

        d = dict(src_dict)
        notifications = []
        _notifications = d.pop("notifications")
        for notifications_item_data in _notifications:
            notifications_item = NotificationGet.from_dict(notifications_item_data)

            notifications.append(notifications_item)

        get_notifications_response_200 = cls(
            notifications=notifications,
        )

        get_notifications_response_200.additional_properties = d
        return get_notifications_response_200

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
