from datetime import datetime, timedelta, timezone

import jwt
import pytest

from tests.helpers import (
    CHAT_ID,
    MATCH_ID,
    MEDIA_ID,
    NOTIFICATION_ID,
    OTHER_PROFILE_ID,
    assert_unauthorized,
)

pytestmark = [pytest.mark.anyio, pytest.mark.security]


@pytest.mark.parametrize(
    ("method", "path", "input_data"),
    [
        ("POST", "/auth/logout", {"json": {"refresh_token": "local-test-token"}}),
        ("POST", "/auth/password/change", {"json": {"old_password": "old", "new_password": "new"}}),
        ("GET", "/profiles", {}),
        ("GET", f"/profiles/{OTHER_PROFILE_ID}/public", {}),
        ("PATCH", "/profiles", {"data": {"bio": "hello"}}),
        ("GET", f"/media/{MEDIA_ID}", {}),
        ("POST", "/chats", {"json": {"contactIds": []}}),
        ("GET", "/chats", {}),
        ("POST", f"/chats/{CHAT_ID}/message", {"data": {"text": "hello"}}),
        ("GET", f"/chats/{CHAT_ID}/messages", {}),
        ("GET", "/matches", {}),
        ("GET", "/matches/history", {}),
        ("POST", f"/matches/{MATCH_ID}/swipe", {"json": "like"}),
        ("GET", "/notifications", {}),
        ("POST", f"/notifications/{NOTIFICATION_ID}/read", {}),
    ],
)
async def test_protected_routes_require_bearer_before_contacting_services(
    client,
    method,
    path,
    input_data,
):
    assert_unauthorized(await client.request(method, path, **input_data))


@pytest.mark.parametrize(
    "claim_overrides",
    [
        {"iss": "wrong-issuer"},
        {"aud": "wrong-audience"},
        {"token_use": "refresh"},
        {"profile_id": "not-a-uuid"},
        {"sub": ""},
    ],
    ids=["issuer", "audience", "token-use", "profile-id", "subject"],
)
async def test_bff_rejects_access_tokens_with_invalid_claims(
    client, access_headers, claim_overrides
):
    response = await client.get("/profiles", headers=access_headers(**claim_overrides))
    assert_unauthorized(response)


async def test_bff_rejects_expired_access_token(client, access_headers):
    now = datetime.now(timezone.utc)
    headers = access_headers(iat=now - timedelta(minutes=2), exp=now - timedelta(minutes=1))
    assert_unauthorized(await client.get("/profiles", headers=headers))


async def test_bff_rejects_token_signed_with_an_untrusted_key(client, access_headers, jwt_secret):
    token = access_headers()["Authorization"].removeprefix("Bearer ")
    claims = jwt.decode(token, jwt_secret, algorithms=["HS256"], audience="bff")
    untrusted = jwt.encode(claims, "untrusted-key-for-isolated-test-only", algorithm="HS256")

    response = await client.get("/profiles", headers={"Authorization": f"Bearer {untrusted}"})

    assert_unauthorized(response)
