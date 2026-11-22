from base64 import b64decode
from time import monotonic, sleep
from urllib.parse import urlsplit

import pytest

from tests.helpers import profile_body

pytestmark = pytest.mark.e2e

PASSWORD = "test-original-password"
NEW_PASSWORD = "test-replacement-password"
PNG = b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jGdsAAAAASUVORK5CYII="
)
ATTACHMENT = b"Message attachment for the isolated end-to-end check\n"


def request(client, method, path, status, **kwargs):
    response = client.request(method, path, **kwargs)
    assert response.status_code == status, f"{method} {path} expected HTTP {status}"
    return response


def credentials(email, password=PASSWORD):
    return {"email": email, "password": password}


def bearer(tokens):
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def signup(client, email, *, avatar=False, expected=201):
    files = {"avatar": ("avatar.png", PNG, "image/png")} if avatar else None
    return request(
        client,
        "POST",
        "/profiles",
        expected,
        data={**profile_body(email), "password": PASSWORD},
        files=files,
    )


def await_notification(stand, headers, profile_id, email, text, subject):
    deadline = monotonic() + 45
    while monotonic() < deadline:
        notifications = request(
            stand.client,
            "GET",
            "/notifications",
            200,
            headers=headers,
        ).json()["notifications"]
        for item in notifications:
            if text in item["text"] and item["is_sent"]:
                assert item["profile_id"] == profile_id
                if any(
                    subject in message["Subject"]
                    and any(address["Address"] == email for address in message["To"])
                    for message in stand.inbox()
                ):
                    return item
        sleep(0.5)
    pytest.fail(f"Notification and captured SMTP message did not arrive for {email}: {subject}")


def test_registration_matching_chat_notifications_and_sessions(stand):
    client = stand.client
    alice, bob, outsider = "e2e-alice@example.com", "e2e-bob@example.com", "e2e-third@example.com"

    alice_id = signup(client, alice, avatar=True).json()["id"]
    bob_id = signup(client, bob).json()["id"]
    assert alice_id != bob_id
    signup(client, alice, expected=409)
    request(client, "POST", "/auth/login", 401, json=credentials(alice, "wrong"))
    a_tokens = request(client, "POST", "/auth/login", 200, json=credentials(alice)).json()
    b_tokens = request(client, "POST", "/auth/login", 200, json=credentials(bob)).json()
    a_headers, b_headers = bearer(a_tokens), bearer(b_tokens)

    before = request(client, "GET", "/profiles", 200, headers=a_headers).json()["profile"]
    assert before["id"] == alice_id
    request(client, "PATCH", "/profiles", 204, headers=a_headers, data={"bio": "Updated bio"})
    after = request(client, "GET", "/profiles", 200, headers=a_headers).json()["profile"]
    assert after == {**before, "bio": "Updated bio", "updated_at": after["updated_at"]}
    avatar_path = f"/media/{after['avatar']}"
    avatar = request(client, "GET", avatar_path, 200, headers=a_headers)
    assert avatar.content == PNG
    assert avatar.headers["content-type"] == "image/png"
    request(client, "GET", avatar_path, 401)

    def swipe(headers, actor, target, answer):
        match = request(client, "GET", "/matches", 200, headers=headers).json()
        assert (match["initiatorProfileId"], match["targetProfileId"]) == (actor, target)
        request(client, "POST", f"/matches/{match['id']}/swipe", 204, headers=headers, json=answer)
        return match["id"]

    def check_match(headers, match_id, answer, status):
        history = request(client, "GET", "/matches/history", 200, headers=headers).json()
        (match,) = (item for item in history["matches"] if item["id"] == match_id)
        assert (match["mySwipe"], match["status"]) == (answer, status)

    a_match = swipe(a_headers, alice_id, bob_id, "like")
    check_match(a_headers, a_match, "like", "noResponse")
    check_match(b_headers, a_match, None, "noResponse")
    b_match = swipe(b_headers, bob_id, alice_id, "like")
    check_match(a_headers, a_match, "like", "accepted")
    check_match(b_headers, b_match, "like", "accepted")

    chat_id = request(
        client,
        "POST",
        "/chats",
        200,
        headers=a_headers,
        json={"contactIds": [bob_id]},
    ).json()["id"]
    for headers, contact_id in ((a_headers, bob_id), (b_headers, alice_id)):
        assert request(client, "GET", "/chats", 200, headers=headers).json() == {
            "chatIds": [chat_id],
            "chats": [{"id": chat_id, "contactId": contact_id}],
        }
    send_path, history_path = f"/chats/{chat_id}/message", f"/chats/{chat_id}/messages"
    request(
        client,
        "POST",
        send_path,
        204,
        headers=a_headers,
        data={"text": "First message"},
        files={"media": ("note.txt", ATTACHMENT, "text/plain")},
    )
    request(client, "POST", send_path, 204, headers=b_headers, data={"text": "Reply"})
    pages = [
        request(
            client,
            "GET",
            history_path,
            200,
            headers=b_headers,
            params={"limit": 1, "offset": offset},
        ).json()["messages"]
        for offset in (0, 1)
    ]
    (second,), (first,) = pages
    assert (second["senderId"], second["text"], second["media"]) == (bob_id, "Reply", [])
    assert (first["senderId"], first["text"]) == (alice_id, "First message")
    (attachment_url,) = first["media"]
    # Follow the response URL only within the local BFF carrying these test credentials.
    assert url_origin(attachment_url) == url_origin(str(client.base_url))
    attachment = request(client, "GET", attachment_url, 200, headers=b_headers)
    assert attachment.content == ATTACHMENT
    assert attachment.headers["content-type"].split(";")[0] == "text/plain"

    third_id = signup(client, outsider).json()["id"]
    third = request(client, "POST", "/auth/login", 200, json=credentials(outsider)).json()
    third_headers = bearer(third)
    other_chat_id = request(
        client, "POST", "/chats", 200, headers=third_headers, json={"contactIds": [bob_id]}
    ).json()["id"]
    assert other_chat_id != chat_id
    assert request(client, "GET", "/chats", 200, headers=third_headers).json() == {
        "chatIds": [other_chat_id],
        "chats": [{"id": other_chat_id, "contactId": bob_id}],
    }
    request(client, "GET", history_path, 404, headers=third_headers)
    request(client, "POST", send_path, 404, headers=third_headers, data={"text": "No access"})
    assert request(client, "GET", history_path, 200, headers=a_headers).json()["messages"] == [
        second,
        first,
    ]
    a_third_match = swipe(a_headers, alice_id, third_id, "dislike")
    check_match(a_headers, a_third_match, "dislike", "rejected")

    welcome = await_notification(
        stand,
        a_headers,
        alice_id,
        alice,
        "Регистрация завершена",
        "Добро пожаловать",
    )
    await_notification(stand, b_headers, bob_id, bob, "Регистрация завершена", "Добро пожаловать")
    assert welcome["is_read"] is False
    read_path = f"/notifications/{welcome['id']}/read"
    request(client, "POST", read_path, 204, headers=a_headers)
    request(client, "POST", read_path, 404, headers=b_headers)
    items = request(client, "GET", "/notifications", 200, headers=a_headers).json()["notifications"]
    assert next(item for item in items if item["id"] == welcome["id"])["is_read"] is True

    a_refresh = {"refresh_token": a_tokens["refresh_token"]}
    rotated = request(client, "POST", "/auth/refresh", 200, json=a_refresh).json()
    fresh_refresh = {"refresh_token": rotated["refresh_token"]}
    changed = a_refresh != fresh_refresh
    assert changed, "Refresh must rotate the token"
    request(client, "POST", "/auth/refresh", 401, json=a_refresh)
    request(client, "POST", "/auth/logout", 204, headers=bearer(rotated), json=fresh_refresh)
    request(client, "POST", "/auth/refresh", 401, json=fresh_refresh)

    second_b_login = request(client, "POST", "/auth/login", 200, json=credentials(bob)).json()
    request(
        client,
        "POST",
        "/auth/password/change",
        204,
        headers=b_headers,
        json={"old_password": PASSWORD, "new_password": NEW_PASSWORD},
    )
    request(client, "POST", "/auth/login", 401, json=credentials(bob))
    updated = request(
        client, "POST", "/auth/login", 200, json=credentials(bob, NEW_PASSWORD)
    ).json()
    for tokens in (b_tokens, second_b_login):
        request(
            client, "POST", "/auth/refresh", 401, json={"refresh_token": tokens["refresh_token"]}
        )
    await_notification(
        stand,
        bearer(updated),
        bob_id,
        bob,
        "пароль успешно изменён",
        "Изменение пароля",
    )


def url_origin(url):
    parts = urlsplit(url)
    return parts.scheme, parts.hostname, parts.port
