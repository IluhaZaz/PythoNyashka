import json

import pytest

from tests.bff.helpers import assert_media_upload
from tests.helpers import (
    CHAT_ID,
    MEDIA_ID,
    MESSAGE_ID,
    MISSING_ID,
    OTHER_PROFILE_ID,
    PROFILE_ID,
    TIMESTAMP,
    assert_no_content,
    assert_validation_error,
)

pytestmark = pytest.mark.anyio

SECOND_MEDIA_ID = "00000000-0000-4000-8000-000000000010"
GROUP_CHAT_ID = "00000000-0000-4000-8000-000000000011"
THIRD_PROFILE_ID = "00000000-0000-4000-8000-000000000012"
MESSAGE_PATH = f"/chats/{CHAT_ID}/message"
HISTORY_PATH = f"/chats/{CHAT_ID}/messages"
ATTACHMENT = ("note.txt", b"note text", "text/plain")


def expect_membership(downstream, *, member=True):
    chat_id = CHAT_ID if member else MISSING_ID
    downstream.expect(
        "GET",
        "chat",
        "/chats",
        200,
        json={
            "chatIds": [chat_id],
            "chats": [{"id": chat_id, "participantIds": [PROFILE_ID, OTHER_PROFILE_ID]}],
        },
    )


async def test_create_chat_includes_caller_and_deduplicates_contact_ids(
    client,
    downstream,
    access_headers,
):
    downstream.expect("POST", "chat", "/chats", 200, json={"id": CHAT_ID})
    body = {"contactIds": [OTHER_PROFILE_ID, OTHER_PROFILE_ID]}

    response = await client.post("/chats", json=body, headers=access_headers())

    assert response.status_code == 200
    assert response.json() == {"id": CHAT_ID}
    contacts = json.loads(downstream.requests[0].content)["contactIds"]
    assert sorted(contacts) == sorted([PROFILE_ID, OTHER_PROFILE_ID])


async def test_create_chat_returns_not_found_for_unknown_contact(
    client, downstream, access_headers
):
    error = {"error": "Profile not found"}
    downstream.expect("POST", "chat", "/chats", 404, json=error)

    response = await client.post(
        "/chats",
        json={"contactIds": [MISSING_ID]},
        headers=access_headers(),
    )

    assert response.status_code == 404
    assert response.json() == error


async def test_create_chat_validates_contact_ids(client, access_headers):
    response = await client.post(
        "/chats",
        json={"contactIds": ["invalid"]},
        headers=access_headers(),
    )
    assert_validation_error(response, "body", "contactIds")


@pytest.mark.parametrize(
    ("upstream_body", "expected"),
    [
        (
            {
                "chatIds": [CHAT_ID, GROUP_CHAT_ID],
                "chats": [
                    {"id": CHAT_ID, "participantIds": [OTHER_PROFILE_ID, PROFILE_ID]},
                    {
                        "id": GROUP_CHAT_ID,
                        "participantIds": [PROFILE_ID, OTHER_PROFILE_ID, THIRD_PROFILE_ID],
                    },
                ],
            },
            {
                "chatIds": [CHAT_ID, GROUP_CHAT_ID],
                "chats": [
                    {"id": CHAT_ID, "contactId": OTHER_PROFILE_ID},
                    {"id": GROUP_CHAT_ID, "contactId": None},
                ],
            },
        ),
        ({"chatIds": [CHAT_ID]}, {"chatIds": [CHAT_ID], "chats": []}),
        ({"chatIds": [], "chats": []}, {"chatIds": [], "chats": []}),
        ({}, {"chatIds": [], "chats": []}),
    ],
    ids=["direct-and-group", "ids-only", "empty", "omitted"],
)
async def test_list_chats_queries_for_authenticated_profile(
    client,
    downstream,
    access_headers,
    upstream_body,
    expected,
):
    downstream.expect("GET", "chat", "/chats", 200, json=upstream_body)

    response = await client.get("/chats", headers=access_headers())

    assert response.status_code == 200
    assert response.json() == expected
    assert dict(downstream.requests[0].url.params) == {"profile_id": PROFILE_ID}


async def test_list_chats_preserves_profile_not_found(client, downstream, access_headers):
    downstream.expect("GET", "chat", "/chats", 404, json={"error": "Profile not found"})

    response = await client.get("/chats", headers=access_headers())

    assert response.status_code == 404
    assert response.json() == {"error": "Profile not found"}


@pytest.mark.parametrize("with_attachments", [False, True], ids=["text-only", "files"])
async def test_send_message_uses_authenticated_sender_and_uploads_files_in_order(
    client,
    downstream,
    access_headers,
    with_attachments,
):
    expect_membership(downstream)
    attachments = (
        [
            (MEDIA_ID, ATTACHMENT),
            (SECOND_MEDIA_ID, ("second.bin", b"\x00\xff", "application/octet-stream")),
        ]
        if with_attachments
        else []
    )
    for media_id, _ in attachments:
        downstream.expect("POST", "media", "/media", 201, json={"id": media_id})
    downstream.expect("POST", "chat", MESSAGE_PATH, 204)

    response = await client.post(
        MESSAGE_PATH,
        headers=access_headers(),
        data={"text": "Привет"},
        files=[("media", file) for _, file in attachments] or None,
    )

    assert_no_content(response)
    membership, *uploads, message = downstream.requests
    assert dict(membership.url.params) == {"profile_id": PROFILE_ID}
    for upload, (_, file) in zip(uploads, attachments, strict=True):
        assert_media_upload(upload, *file)
    assert json.loads(message.content) == {
        "senderId": PROFILE_ID,
        "text": "Привет",
        "media": [media_id for media_id, _ in attachments],
    }


@pytest.mark.parametrize("status", [400, 413, 415])
async def test_send_message_propagates_media_rejection_without_sending_message(
    client,
    downstream,
    access_headers,
    status,
):
    expect_membership(downstream)
    error = {"error": "Attachment rejected"}
    downstream.expect("POST", "media", "/media", status, json=error)

    response = await client.post(
        MESSAGE_PATH,
        headers=access_headers(),
        data={"text": "hello"},
        files={"media": ATTACHMENT},
    )

    assert response.status_code == status, response.text
    assert response.json() == error


@pytest.mark.parametrize(("method", "path"), [("POST", MESSAGE_PATH), ("GET", HISTORY_PATH)])
@pytest.mark.security
async def test_message_routes_reject_non_members(client, downstream, access_headers, method, path):
    expect_membership(downstream, member=False)

    response = await client.request(
        method,
        path,
        headers=access_headers(),
        **({"data": {"text": "hello"}, "files": {"media": ATTACHMENT}} if method == "POST" else {}),
    )

    assert response.status_code == 404
    assert response.json() == {"error": "Chat not found"}


@pytest.mark.parametrize(("method", "path"), [("POST", MESSAGE_PATH), ("GET", HISTORY_PATH)])
async def test_message_routes_preserve_not_found_after_membership_check(
    client,
    downstream,
    access_headers,
    method,
    path,
):
    expect_membership(downstream)
    error = {"error": "Chat not found"}
    downstream.expect(method, "chat", path, 404, json=error)
    options = {"data": {"text": "hello"}} if method == "POST" else {}

    response = await client.request(method, path, headers=access_headers(), **options)

    assert response.status_code == 404
    assert response.json() == error


async def test_send_message_validates_text_and_chat_id(client, access_headers):
    headers = access_headers()
    assert_validation_error(await client.post(MESSAGE_PATH, headers=headers), "body", "text")
    response = await client.post("/chats/invalid/message", headers=headers, data={"text": "hello"})
    assert_validation_error(response, "path", "chat_id")


@pytest.mark.parametrize("include_timestamp", [True, False], ids=["dated", "undated"])
async def test_get_chat_history_forwards_pagination_and_builds_media_urls(
    client,
    downstream,
    access_headers,
    include_timestamp,
):
    expect_membership(downstream)
    message = {"id": MESSAGE_ID, "senderId": PROFILE_ID, "text": "Hello", "media": [MEDIA_ID]}
    if include_timestamp:
        message["sentAt"] = TIMESTAMP
    downstream.expect(
        "GET",
        "chat",
        HISTORY_PATH,
        200,
        json={"chatId": CHAT_ID, "messages": [message]},
    )

    response = await client.get(
        HISTORY_PATH,
        headers=access_headers(),
        params={"offset": 2, "limit": 1},
    )

    assert response.status_code == 200
    assert response.json() == {
        "chatId": CHAT_ID,
        "messages": [{**message, "media": [f"http://bff.test/media/{MEDIA_ID}"]}],
    }
    assert dict(downstream.requests[1].url.params) == {"offset": "2", "limit": "1"}


@pytest.mark.parametrize(
    ("params", "forwarded"),
    [
        ({}, {"offset": "0"}),
        ({"limit": 0}, {"limit": "0", "offset": "0"}),
    ],
)
async def test_get_chat_history_handles_empty_result(
    client,
    downstream,
    access_headers,
    params,
    forwarded,
):
    expect_membership(downstream)
    downstream.expect("GET", "chat", HISTORY_PATH, 200, json={"chatId": CHAT_ID})

    response = await client.get(HISTORY_PATH, headers=access_headers(), params=params)

    assert response.status_code == 200
    assert response.json() == {"chatId": CHAT_ID, "messages": []}
    assert dict(downstream.requests[1].url.params) == forwarded


@pytest.mark.parametrize("field", ["limit", "offset"])
async def test_get_chat_history_rejects_negative_pagination(client, access_headers, field):
    response = await client.get(HISTORY_PATH, headers=access_headers(), params={field: -1})
    assert_validation_error(response, "query", field)


async def test_get_chat_history_validates_uuid(client, access_headers):
    response = await client.get("/chats/invalid/messages", headers=access_headers())
    assert_validation_error(response, "path", "chat_id")
