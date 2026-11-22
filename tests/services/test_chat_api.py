from datetime import datetime, timedelta
from uuid import UUID, uuid4

import pytest

from src.chat import dependencies
from src.chat.infrastructure.storage.postgresql.models import Chat, ChatMember, Message
from src.chat.main import app
from tests.helpers import (
    CHAT_ID,
    MEDIA_ID,
    MISSING_ID,
    TIMESTAMP,
    assert_no_content,
    assert_validation_error,
)

pytestmark = pytest.mark.anyio


@pytest.fixture
async def client(service_client):
    async with service_client(app, dependencies) as http:
        yield http


@pytest.fixture
async def member_id(db_sessions, seed_profile):
    actor = await seed_profile()
    async with db_sessions() as session:
        session.add(Chat(id=CHAT_ID))
        await session.flush()
        session.add(ChatMember(chat_id=CHAT_ID, profile_id=actor))
        await session.commit()
    return actor


async def test_create_direct_chat_deduplicates_members_and_reuses_chat_for_both_profiles(
    client, seed_profile
):
    first, second = await seed_profile(), await seed_profile()
    created = await client.post("/chats", json={"contactIds": [first, second, first]})

    assert created.status_code == 200, created.text
    chat_id = created.json()["id"]
    UUID(chat_id)
    repeated = await client.post("/chats", json={"contactIds": [second, first]})
    assert repeated.status_code == 200, repeated.text
    assert repeated.json() == {"id": chat_id}

    expected = {
        "chatIds": [chat_id],
        "chats": [{"id": chat_id, "participantIds": sorted([first, second])}],
    }
    for profile_id in (first, second):
        response = await client.get("/chats", params={"profile_id": profile_id})
        assert response.status_code == 200
        assert response.json() == expected


async def test_create_chat_rejects_unknown_profile(client, seed_profile):
    actor = await seed_profile()
    response = await client.post("/chats", json={"contactIds": [actor, MISSING_ID]})
    assert response.status_code == 404
    assert response.json() == {"error": "Profile not found"}
    assert (await client.get("/chats", params={"profile_id": actor})).json() == {
        "chatIds": [], "chats": [],
    }


async def test_create_chat_rejects_malformed_contact_id(client):
    response = await client.post("/chats", json={"contactIds": ["invalid"]})
    assert_validation_error(response, "body", "contactIds")


async def test_list_chats_returns_empty_for_profile_without_memberships(
    client,
    member_id,
    seed_profile,
):
    outsider = await seed_profile()
    response = await client.get("/chats", params={"profile_id": outsider})
    assert response.status_code == 200
    assert response.json() == {"chatIds": [], "chats": []}


async def test_list_chats_rejects_unknown_profile(client):
    response = await client.get("/chats", params={"profile_id": MISSING_ID})
    assert response.status_code == 404
    assert response.json() == {"error": "Profile not found"}


@pytest.mark.parametrize("params", [{}, {"profile_id": "invalid"}])
async def test_list_chats_validates_profile_id(client, params):
    assert_validation_error(await client.get("/chats", params=params), "query", "profile_id")


@pytest.mark.parametrize("media", [[], [MEDIA_ID]], ids=["text-only", "with-attachment"])
async def test_send_message_persists_and_history_serializes_message(client, member_id, media):
    body = {"senderId": member_id, "text": "Привет!", "media": media}
    assert_no_content(await client.post(f"/chats/{CHAT_ID}/message", json=body))

    response = await client.get(f"/chats/{CHAT_ID}/messages")

    assert response.status_code == 200
    payload = response.json()
    assert payload["chatId"] == CHAT_ID
    (message,) = payload["messages"]
    UUID(message["id"])
    assert datetime.fromisoformat(message["sentAt"]).tzinfo is not None
    assert {key: message[key] for key in body} == body


async def test_send_message_rejects_sender_who_is_not_a_member(client, member_id, seed_profile):
    outsider = await seed_profile()
    created = await client.post("/chats", json={"contactIds": [outsider]})
    assert created.status_code == 200, created.text
    other_chat_id = created.json()["id"]
    listed = await client.get("/chats", params={"profile_id": outsider})
    assert listed.status_code == 200, listed.text
    assert listed.json() == {
        "chatIds": [other_chat_id],
        "chats": [{"id": other_chat_id, "participantIds": [outsider]}],
    }
    response = await client.post(
        f"/chats/{CHAT_ID}/message",
        json={"senderId": outsider, "text": "Hello", "media": []},
    )

    assert response.status_code == 404
    assert response.json() == {"error": "Chat not found"}
    assert (await client.get(f"/chats/{CHAT_ID}/messages")).json()["messages"] == []


async def test_send_message_requires_sender(client, member_id):
    response = await client.post(f"/chats/{CHAT_ID}/message", json={"text": "Hello", "media": []})
    assert response.status_code == 404
    assert response.json() == {"error": "Profile not found"}


@pytest.mark.parametrize(
    ("body", "field"),
    [
        ({"media": []}, "text"),
        ({"text": "Hello", "media": ["invalid"]}, "media"),
    ],
)
async def test_send_message_validates_body(client, body, field):
    response = await client.post(f"/chats/{CHAT_ID}/message", json=body)
    assert_validation_error(response, "body", field)


async def test_get_chat_history_orders_messages_and_pages_results(client, member_id, db_sessions):
    timestamp = datetime.fromisoformat(TIMESTAMP)
    older_id, newer_id = str(uuid4()), str(uuid4())
    async with db_sessions() as session:
        session.add_all(
            [
                Message(
                    id=older_id,
                    chat_id=CHAT_ID,
                    sender_id=member_id,
                    text="First",
                    media=[],
                    sent_at=timestamp,
                ),
                Message(
                    id=newer_id,
                    chat_id=CHAT_ID,
                    sender_id=member_id,
                    text="Second",
                    media=[],
                    sent_at=timestamp + timedelta(seconds=1),
                ),
            ]
        )
        await session.commit()

    path = f"/chats/{CHAT_ID}/messages"
    for params, expected in [
        ({}, [newer_id, older_id]),
        ({"limit": 1}, [newer_id]),
        ({"limit": 1, "offset": 1}, [older_id]),
        ({"limit": 0}, []),
        ({"offset": 2}, []),
    ]:
        response = await client.get(path, params=params)
        assert response.status_code == 200, response.text
        assert [message["id"] for message in response.json()["messages"]] == expected


async def test_get_chat_history_for_missing_chat_returns_not_found(client):
    response = await client.get(f"/chats/{MISSING_ID}/messages")
    assert response.status_code == 404
    assert response.json() == {"error": "Chat not found"}


@pytest.mark.parametrize("field", ["limit", "offset"])
async def test_get_chat_history_rejects_negative_pagination(client, field):
    response = await client.get(f"/chats/{CHAT_ID}/messages", params={field: -1})
    assert_validation_error(response, "query", field)


@pytest.mark.parametrize("suffix", ["message", "messages"])
async def test_message_routes_validate_chat_id(client, suffix):
    if suffix == "message":
        response = await client.post("/chats/invalid/message", json={"text": "Hello", "media": []})
    else:
        response = await client.get("/chats/invalid/messages")
    assert_validation_error(response, "path", "chat_id")
