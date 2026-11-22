import json

import httpx
import pytest

from tests.bff.helpers import assert_media_upload
from tests.helpers import (
    MEDIA_ID,
    OTHER_PROFILE_ID,
    PROFILE_ID,
    TIMESTAMP,
    USER_ID,
    assert_no_content,
    assert_validation_error,
    profile_body,
)

pytestmark = pytest.mark.anyio

PASSWORD = "example-test-password"
AVATAR = ("avatar.png", b"example-avatar-bytes", "image/png")
MISSING_PROFILE = {"error": "Profile not found"}


def profile_details(avatar_id=None):
    return {
        **profile_body(),
        "id": PROFILE_ID,
        "created_at": TIMESTAMP,
        "updated_at": TIMESTAMP,
        "avatar_id": avatar_id,
    }


@pytest.mark.parametrize("with_avatar", [False, True], ids=["without-avatar", "with-avatar"])
async def test_create_profile_coordinates_profile_auth_and_optional_media(
    client,
    downstream,
    with_avatar,
):
    if with_avatar:
        downstream.expect("POST", "media", "/media", 201, json={"id": MEDIA_ID})
    downstream.expect("POST", "profile", "/profiles", 201, json={"id": PROFILE_ID})
    downstream.expect("POST", "auth", "/auth/register", 201, json={"user_id": USER_ID})

    body = profile_body()
    response = await client.post(
        "/profiles",
        data={**body, "password": PASSWORD},
        files={"avatar": AVATAR} if with_avatar else None,
    )

    assert response.status_code == 201, response.text
    assert response.json() == {"id": PROFILE_ID}
    *uploads, profile_request, auth_request = downstream.requests
    expected_fields = {**body, "avatar_id": MEDIA_ID} if with_avatar else body
    assert json.loads(profile_request.content) == expected_fields
    assert json.loads(auth_request.content) == {
        "email": body["email"],
        "password": PASSWORD,
        "profile_id": PROFILE_ID,
    }
    if with_avatar:
        assert_media_upload(uploads[0], *AVATAR)


async def test_create_profile_preserves_conflict_without_registering_auth_user(client, downstream):
    error = {"error": "email already used"}
    downstream.expect("POST", "profile", "/profiles", 409, json=error)

    response = await client.post("/profiles", data={**profile_body(), "password": PASSWORD})

    assert response.status_code == 409, response.text
    assert response.json() == error


async def test_create_profile_removes_profile_if_auth_registration_is_rejected(client, downstream):
    error = {"error": "email already used"}
    downstream.expect("POST", "profile", "/profiles", 201, json={"id": PROFILE_ID})
    downstream.expect("POST", "auth", "/auth/register", 400, json=error)
    downstream.expect("DELETE", "profile", f"/profiles/{PROFILE_ID}", 204)

    response = await client.post("/profiles", data={**profile_body(), "password": PASSWORD})

    assert response.status_code == 409, response.text
    assert response.json() == error


async def test_create_profile_removes_profile_if_auth_connection_fails(client, downstream):
    downstream.expect("POST", "profile", "/profiles", 201, json={"id": PROFILE_ID})
    downstream.expect("POST", "auth", "/auth/register", httpx.ConnectError)
    downstream.expect("DELETE", "profile", f"/profiles/{PROFILE_ID}", 204)

    with pytest.raises(httpx.ConnectError):
        await client.post("/profiles", data={**profile_body(), "password": PASSWORD})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("email", "invalid-email"),
        ("name", "x" * 101),
        ("surname", "x" * 101),
        ("age", 0),
        ("age", 150),
        ("gender", "unknown"),
        ("bio", "x" * 1001),
        ("tags", ["unknown-tag"]),
    ],
)
async def test_create_profile_validates_form_fields(client, field, value):
    body = {**profile_body(), "password": PASSWORD}
    body[field] = value
    assert_validation_error(await client.post("/profiles", data=body), "body", field)


async def test_create_profile_requires_password(client):
    assert_validation_error(
        await client.post("/profiles", data=profile_body()),
        "body",
        "password",
    )


@pytest.mark.parametrize("avatar_id", [None, MEDIA_ID], ids=["no-avatar", "with-avatar"])
@pytest.mark.security
async def test_get_profile_uses_token_identity_and_maps_avatar(
    client, downstream, access_headers, avatar_id
):
    details = profile_details(avatar_id)
    downstream.expect("GET", "profile", f"/profiles/{PROFILE_ID}", 200, json={"profile": details})

    response = await client.get("/profiles", headers=access_headers())

    assert response.status_code == 200, response.text
    del details["avatar_id"]
    if avatar_id is not None:
        details["avatar"] = avatar_id
    assert response.json() == {"profile": details}


@pytest.mark.security
async def test_get_public_profile_returns_only_public_fields(client, downstream, access_headers):
    details = {**profile_details(MEDIA_ID), "id": OTHER_PROFILE_ID}
    downstream.expect(
        "GET", "profile", f"/profiles/{OTHER_PROFILE_ID}", 200, json={"profile": details}
    )

    response = await client.get(
        f"/profiles/{OTHER_PROFILE_ID}/public", headers=access_headers()
    )

    assert response.status_code == 200, response.text
    public_fields = ("id", "name", "surname", "age", "bio", "gender", "tags")
    expected = {
        **{field: details[field] for field in public_fields},
        "avatar": MEDIA_ID,
    }
    assert response.json() == {"profile": expected}


async def test_get_public_profile_preserves_not_found(client, downstream, access_headers):
    downstream.expect("GET", "profile", f"/profiles/{OTHER_PROFILE_ID}", 404, json=MISSING_PROFILE)

    response = await client.get(
        f"/profiles/{OTHER_PROFILE_ID}/public", headers=access_headers()
    )

    assert response.status_code == 404, response.text
    assert response.json() == MISSING_PROFILE


@pytest.mark.parametrize("method", ["GET", "PATCH"])
async def test_get_and_patch_return_not_found_for_missing_profile(
    client,
    downstream,
    access_headers,
    method,
):
    downstream.expect("GET", "profile", f"/profiles/{PROFILE_ID}", 404, json=MISSING_PROFILE)

    response = await client.request(method, "/profiles", headers=access_headers())

    assert response.status_code == 404, response.text
    assert response.json() == MISSING_PROFILE


@pytest.mark.parametrize("with_avatar", [False, True], ids=["fields-only", "new-avatar"])
async def test_patch_profile_forwards_only_changes_to_authenticated_profile(
    client,
    downstream,
    access_headers,
    with_avatar,
):
    downstream.expect(
        "GET",
        "profile",
        f"/profiles/{PROFILE_ID}",
        200,
        json={"profile": profile_details()},
    )
    if with_avatar:
        downstream.expect("POST", "media", "/media", 201, json={"id": MEDIA_ID})
    downstream.expect("PATCH", "profile", "/profiles", 204)

    patch = {"bio": "Updated bio", "tags": ["devops"], "age": 149}
    response = await client.patch(
        "/profiles",
        data=patch,
        headers=access_headers(),
        files={"avatar": AVATAR} if with_avatar else None,
    )

    assert_no_content(response)
    _, *uploads, update = downstream.requests
    assert dict(update.url.params) == {"profile_id": PROFILE_ID}
    assert json.loads(update.content) == (
        {**patch, "avatar_id": MEDIA_ID} if with_avatar else patch
    )
    if with_avatar:
        assert_media_upload(uploads[0], *AVATAR)


async def test_patch_profile_with_empty_form_skips_update(client, downstream, access_headers):
    downstream.expect(
        "GET",
        "profile",
        f"/profiles/{PROFILE_ID}",
        200,
        json={"profile": profile_details()},
    )
    assert_no_content(await client.patch("/profiles", headers=access_headers()))


async def test_patch_profile_handles_removal_between_read_and_update(
    client,
    downstream,
    access_headers,
):
    downstream.expect(
        "GET",
        "profile",
        f"/profiles/{PROFILE_ID}",
        200,
        json={"profile": profile_details()},
    )
    downstream.expect("PATCH", "profile", "/profiles", 404, json=MISSING_PROFILE)

    response = await client.patch("/profiles", data={"age": 30}, headers=access_headers())

    assert response.status_code == 404, response.text
    assert response.json() == MISSING_PROFILE


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("name", "x" * 101),
        ("age", 0),
        ("age", 150),
        ("bio", "x" * 1001),
        ("gender", "unknown"),
        ("tags", ["unknown-tag"]),
    ],
)
async def test_patch_profile_validates_form_before_forwarding(client, access_headers, field, value):
    response = await client.patch("/profiles", data={field: value}, headers=access_headers())
    assert_validation_error(response, "body", field)
