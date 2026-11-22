import httpx
import pytest

from tests.helpers import MEDIA_ID, MISSING_ID, OTHER_PROFILE_ID, PROFILE_ID, assert_validation_error

pytestmark = pytest.mark.anyio


async def test_get_media_preserves_bytes_and_content_headers(client, downstream, access_headers):
    data = b"\x00\x01\xff"
    headers = {
        "Content-Type": "image/png",
        "Content-Disposition": "inline; filename*=UTF-8''file.png",
    }
    downstream.expect(
        "GET", "chat", f"/chats/media/{MEDIA_ID}/access", 200, json={"access": "allowed"},
    )
    downstream.expect("GET", "media", f"/media/{MEDIA_ID}", 200, content=data, headers=headers)

    response = await client.get(f"/media/{MEDIA_ID}", headers=access_headers())

    assert response.status_code == 200
    assert response.content == data
    assert dict(downstream.requests[0].url.params) == {"profile_id": PROFILE_ID}
    for header, value in headers.items():
        assert response.headers[header] == value


async def test_get_avatar_defaults_to_binary_without_upstream_content_type(
    client,
    downstream,
    access_headers,
):
    data = b"\x00\xff"
    downstream.expect(
        "GET", "chat", f"/chats/media/{MEDIA_ID}/access", 200, json={"access": "unlinked"},
    )
    downstream.expect("GET", "profile", f"/profiles/avatars/{MEDIA_ID}", 204)
    downstream.expect("GET", "media", f"/media/{MEDIA_ID}", 200, content=data)

    response = await client.get(f"/media/{MEDIA_ID}", headers=access_headers(OTHER_PROFILE_ID))

    assert response.status_code == 200
    assert response.content == data
    assert response.headers["content-type"] == "application/octet-stream"
    assert "content-disposition" not in response.headers


async def test_get_media_returns_empty_not_found_response(client, downstream, access_headers):
    downstream.expect(
        "GET", "chat", f"/chats/media/{MISSING_ID}/access", 200, json={"access": "allowed"},
    )
    downstream.expect(
        "GET", "media", f"/media/{MISSING_ID}", 404, json={"error": "Media file not found"}
    )

    response = await client.get(f"/media/{MISSING_ID}", headers=access_headers())

    assert response.status_code == 404
    assert response.content == b""


async def test_get_media_denies_outsider_without_checking_avatar(client, downstream, access_headers):
    downstream.expect(
        "GET", "chat", f"/chats/media/{MEDIA_ID}/access", 200, json={"access": "denied"},
    )

    response = await client.get(f"/media/{MEDIA_ID}", headers=access_headers(OTHER_PROFILE_ID))

    assert response.status_code == 404
    assert response.content == b""


async def test_get_media_hides_unlinked_file(client, downstream, access_headers):
    downstream.expect(
        "GET", "chat", f"/chats/media/{MEDIA_ID}/access", 200, json={"access": "unlinked"},
    )
    downstream.expect("GET", "profile", f"/profiles/avatars/{MEDIA_ID}", 404)

    response = await client.get(f"/media/{MEDIA_ID}", headers=access_headers())

    assert response.status_code == 404
    assert response.content == b""


@pytest.mark.parametrize("upstream", [404, 500, httpx.ConnectError])
async def test_get_media_fails_closed_if_chat_check_fails(
    client, downstream, access_headers, upstream,
):
    downstream.expect("GET", "chat", f"/chats/media/{MEDIA_ID}/access", upstream)

    response = await client.get(f"/media/{MEDIA_ID}", headers=access_headers())

    assert response.status_code == 502


async def test_get_media_fails_closed_if_profile_check_fails(client, downstream, access_headers):
    downstream.expect(
        "GET", "chat", f"/chats/media/{MEDIA_ID}/access", 200, json={"access": "unlinked"},
    )
    downstream.expect("GET", "profile", f"/profiles/avatars/{MEDIA_ID}", 500)

    response = await client.get(f"/media/{MEDIA_ID}", headers=access_headers())

    assert response.status_code == 502


async def test_get_media_validates_uuid(client, access_headers):
    response = await client.get("/media/invalid", headers=access_headers())
    assert_validation_error(response, "path", "media_id")
