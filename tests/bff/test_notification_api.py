import pytest

from tests.helpers import (
    NOTIFICATION_ID,
    PROFILE_ID,
    TIMESTAMP,
    assert_no_content,
    assert_validation_error,
)

pytestmark = pytest.mark.anyio

NOTIFICATION = {
    "id": NOTIFICATION_ID,
    "profile_id": PROFILE_ID,
    "text": "Welcome",
    "created_at": TIMESTAMP,
    "is_read": False,
    "is_sent": True,
}
READ_PATH = f"/notifications/{NOTIFICATION_ID}/read"


@pytest.mark.parametrize(
    ("params", "forwarded", "items"),
    [
        ({}, {"limit": "10", "offset": "0"}, [NOTIFICATION]),
        ({"limit": 1, "offset": 2}, {"limit": "1", "offset": "2"}, [NOTIFICATION]),
        ({"limit": 0}, {"limit": "0", "offset": "0"}, []),
    ],
)
async def test_list_notifications_uses_token_profile_and_preserves_pagination(
    client,
    downstream,
    access_headers,
    params,
    forwarded,
    items,
):
    body = {"notifications": items}
    downstream.expect("GET", "notification", f"/notifications/{PROFILE_ID}", 200, json=body)

    response = await client.get("/notifications", headers=access_headers(), params=params)

    assert response.status_code == 200
    assert response.json() == body
    assert dict(downstream.requests[0].url.params) == forwarded


@pytest.mark.parametrize("field", ["limit", "offset"])
async def test_list_notifications_validates_query_types(client, access_headers, field):
    response = await client.get(
        "/notifications", headers=access_headers(), params={field: "invalid"}
    )
    assert_validation_error(response, "query", field)


async def test_read_notification_forwards_authenticated_profile(client, downstream, access_headers):
    downstream.expect("POST", "notification", READ_PATH, 204)

    assert_no_content(await client.post(READ_PATH, headers=access_headers()))

    assert dict(downstream.requests[0].url.params) == {"profile_id": PROFILE_ID}


async def test_read_notification_preserves_not_found(client, downstream, access_headers):
    error = {"error": "Notification not found for this profile"}
    downstream.expect("POST", "notification", READ_PATH, 404, json=error)

    response = await client.post(READ_PATH, headers=access_headers())

    assert response.status_code == 404
    assert response.json() == error


async def test_read_notification_validates_uuid(client, access_headers):
    response = await client.post("/notifications/invalid/read", headers=access_headers())
    assert_validation_error(response, "path", "notification_id")
