import pytest

from tests.helpers import MEDIA_ID, MISSING_ID, assert_validation_error

pytestmark = pytest.mark.anyio


async def test_get_media_preserves_bytes_and_content_headers(client, downstream, access_headers):
    data = b"\x00\x01\xff"
    headers = {
        "Content-Type": "image/png",
        "Content-Disposition": "inline; filename*=UTF-8''file.png",
    }
    downstream.expect("GET", "media", f"/media/{MEDIA_ID}", 200, content=data, headers=headers)

    response = await client.get(f"/media/{MEDIA_ID}", headers=access_headers())

    assert response.status_code == 200
    assert response.content == data
    for header, value in headers.items():
        assert response.headers[header] == value


async def test_get_media_defaults_to_binary_without_upstream_content_type(
    client,
    downstream,
    access_headers,
):
    data = b"\x00\xff"
    downstream.expect("GET", "media", f"/media/{MEDIA_ID}", 200, content=data)

    response = await client.get(f"/media/{MEDIA_ID}", headers=access_headers())

    assert response.status_code == 200
    assert response.content == data
    assert response.headers["content-type"] == "application/octet-stream"
    assert "content-disposition" not in response.headers


async def test_get_media_returns_empty_not_found_response(client, downstream, access_headers):
    downstream.expect(
        "GET", "media", f"/media/{MISSING_ID}", 404, json={"error": "Media file not found"}
    )

    response = await client.get(f"/media/{MISSING_ID}", headers=access_headers())

    assert response.status_code == 404
    assert response.content == b""


async def test_get_media_validates_uuid(client, access_headers):
    response = await client.get("/media/invalid", headers=access_headers())
    assert_validation_error(response, "path", "media_id")
