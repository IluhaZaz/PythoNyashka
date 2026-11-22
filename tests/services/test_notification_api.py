from datetime import datetime, timedelta

import pytest
from sqlalchemy.exc import DBAPIError

from src.notification import dependencies
from src.notification.infrastructure.storage.postgresql.models import Notification
from src.notification.main import app
from tests.helpers import (
    MISSING_ID,
    NOTIFICATION_ID,
    OTHER_PROFILE_ID,
    PROFILE_ID,
    TIMESTAMP,
    assert_no_content,
)

pytestmark = pytest.mark.anyio
NEWEST_NOTIFICATION_ID = "00000000-0000-4000-8000-000000000010"


class NegativePaginationReachedDatabase(Exception):
    pass


@pytest.fixture
async def client(service_client):
    async with service_client(app, dependencies) as http:
        yield http


@pytest.fixture
async def notifications(db_sessions):
    timestamp = datetime.fromisoformat(TIMESTAMP)
    async with db_sessions() as session:
        session.add_all(
            [
                Notification(
                    id=NOTIFICATION_ID,
                    profile_id=PROFILE_ID,
                    text="Welcome",
                    created_at=timestamp,
                ),
                Notification(
                    id=NEWEST_NOTIFICATION_ID,
                    profile_id=PROFILE_ID,
                    text="Password changed",
                    is_sent=True,
                    created_at=timestamp + timedelta(seconds=1),
                ),
                Notification(profile_id=OTHER_PROFILE_ID, text="Someone else's notification"),
            ]
        )
        await session.commit()


async def test_list_notifications_scopes_to_profile_and_orders_newest_first(client, notifications):
    response = await client.get(f"/notifications/{PROFILE_ID}")

    assert response.status_code == 200, response.text
    newest, oldest = response.json()["notifications"]
    assert (newest["id"], oldest["id"]) == (NEWEST_NOTIFICATION_ID, NOTIFICATION_ID)
    assert {newest["profile_id"], oldest["profile_id"]} == {PROFILE_ID}
    assert newest["is_sent"] is True
    assert oldest["text"] == "Welcome"
    assert oldest["is_read"] is False
    assert oldest["is_sent"] is False
    assert datetime.fromisoformat(oldest["created_at"]) == datetime.fromisoformat(TIMESTAMP)


@pytest.mark.parametrize(
    ("params", "expected"),
    [
        ({"limit": 1}, [NEWEST_NOTIFICATION_ID]),
        ({"limit": 1, "offset": 1}, [NOTIFICATION_ID]),
        ({"limit": 0}, []),
        ({"offset": 2}, []),
    ],
)
async def test_list_notifications_paginates(client, notifications, params, expected):
    response = await client.get(f"/notifications/{PROFILE_ID}", params=params)
    assert response.status_code == 200
    assert [item["id"] for item in response.json()["notifications"]] == expected


async def test_list_notifications_for_profile_without_events_is_empty(client, notifications):
    response = await client.get(f"/notifications/{MISSING_ID}")
    assert response.status_code == 200
    assert response.json() == {"notifications": []}


@pytest.mark.xfail(
    strict=True,
    raises=NegativePaginationReachedDatabase,
    reason="Notification passes negative pagination to PostgreSQL, which rejects it",
)
@pytest.mark.parametrize(("field", "sqlstate"), [("limit", "2201W"), ("offset", "2201X")])
async def test_list_notifications_rejects_negative_pagination_as_client_error(
    client, field, sqlstate
):
    try:
        response = await client.get(f"/notifications/{PROFILE_ID}", params={field: -1})
    except DBAPIError as exc:
        if getattr(exc.orig, "sqlstate", None) != sqlstate:
            raise
        raise NegativePaginationReachedDatabase(field) from exc
    assert response.status_code == 422, response.text
    (error,) = response.json()["errors"]
    assert error["field"] == field


async def test_read_notification_is_idempotent_and_persists_flag(client, notifications):
    path = f"/notifications/{NOTIFICATION_ID}/read"
    for _ in range(2):
        assert_no_content(await client.post(path, params={"profile_id": PROFILE_ID}))

    response = await client.get(f"/notifications/{PROFILE_ID}")
    assert response.status_code == 200
    states = {item["id"]: item["is_read"] for item in response.json()["notifications"]}
    assert states == {NOTIFICATION_ID: True, NEWEST_NOTIFICATION_ID: False}


@pytest.mark.parametrize(
    ("notification_id", "profile_id"),
    [
        (NOTIFICATION_ID, OTHER_PROFILE_ID),
        (MISSING_ID, PROFILE_ID),
    ],
)
@pytest.mark.security
async def test_read_notification_returns_not_found_for_unknown_or_unowned_event(
    client,
    notifications,
    db_sessions,
    notification_id,
    profile_id,
):
    response = await client.post(
        f"/notifications/{notification_id}/read",
        params={"profile_id": profile_id},
    )

    assert response.status_code == 404
    assert response.json() == {"error": "Notification not found for this profile"}
    async with db_sessions() as session:
        assert (await session.get(Notification, NOTIFICATION_ID)).is_read is False


@pytest.mark.parametrize(
    ("method", "path", "params", "field"),
    [
        ("GET", "/notifications/invalid", {}, "profile_id"),
        ("GET", f"/notifications/{PROFILE_ID}", {"limit": "invalid"}, "limit"),
        ("GET", f"/notifications/{PROFILE_ID}", {"offset": "invalid"}, "offset"),
        ("POST", "/notifications/invalid/read", {"profile_id": PROFILE_ID}, "notification_id"),
        ("POST", f"/notifications/{NOTIFICATION_ID}/read", {}, "profile_id"),
    ],
)
async def test_notification_validation_uses_custom_error_schema(
    client, method, path, params, field
):
    response = await client.request(method, path, params=params)
    assert response.status_code == 422
    (error,) = response.json()["errors"]
    assert error["field"] == field
    assert error["reason"]
