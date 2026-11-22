import json

import pytest

from tests.helpers import assert_no_content, assert_unauthorized, assert_validation_error

pytestmark = pytest.mark.anyio

LOGIN = {"email": "ada@example.com", "password": "test-password"}
REFRESH = {"refresh_token": "previous-local-test-token"}
PASSWORD_CHANGE = {"old_password": "test-password", "new_password": "updated-test-password"}
TOKEN_REPLY = {
    "access_token": "new-test-access-token",
    "refresh_token": "new-test-refresh-token",
    "token_type": "Bearer",
    "expires_in": 900,
}


@pytest.mark.parametrize(
    ("path", "body"),
    [
        ("/auth/login", LOGIN),
        ("/auth/refresh", REFRESH),
    ],
)
async def test_public_auth_routes_forward_body_and_return_tokens(client, downstream, path, body):
    downstream.expect("POST", "auth", path, 200, json=TOKEN_REPLY)

    response = await client.post(path, json=body)

    assert response.status_code == 200
    assert response.json() == TOKEN_REPLY
    (request,) = downstream.requests
    assert json.loads(request.content) == body
    assert "authorization" not in request.headers


@pytest.mark.parametrize(
    ("path", "body"),
    [
        ("/auth/login", LOGIN),
        ("/auth/refresh", REFRESH),
    ],
)
async def test_public_auth_routes_propagate_rejected_credentials(client, downstream, path, body):
    error = {"error": "Invalid credentials"}
    downstream.expect("POST", "auth", path, 401, json=error)

    response = await client.post(path, json=body)

    assert response.status_code == 401
    assert response.json() == error


@pytest.mark.parametrize(
    ("public_path", "internal_path", "body"),
    [
        ("/auth/logout", "/auth/logout", REFRESH),
        ("/auth/password/change", "/auth/password/reset", PASSWORD_CHANGE),
    ],
)
async def test_protected_auth_routes_forward_bearer_and_body(
    client,
    downstream,
    access_headers,
    public_path,
    internal_path,
    body,
):
    headers = access_headers()
    downstream.expect("POST", "auth", internal_path, 204)

    assert_no_content(await client.post(public_path, json=body, headers=headers))

    (request,) = downstream.requests
    assert json.loads(request.content) == body
    assert request.headers["authorization"] == headers["Authorization"]


@pytest.mark.parametrize(
    ("public_path", "internal_path", "body"),
    [
        ("/auth/logout", "/auth/logout", REFRESH),
        ("/auth/password/change", "/auth/password/reset", PASSWORD_CHANGE),
    ],
)
async def test_protected_auth_routes_propagate_unauthorized_from_auth(
    client,
    downstream,
    public_path,
    internal_path,
    body,
):
    error = {"error": "Invalid token"}
    downstream.expect("POST", "auth", internal_path, 401, json=error)

    response = await client.post(
        public_path, json=body, headers={"Authorization": "Bearer invalid"}
    )

    assert_unauthorized(response)
    assert response.json() == error


async def test_change_password_preserves_wrong_old_password_error(
    client, downstream, access_headers
):
    error = {"error": "Incorrect old password"}
    downstream.expect("POST", "auth", "/auth/password/reset", 400, json=error)

    response = await client.post(
        "/auth/password/change", json=PASSWORD_CHANGE, headers=access_headers()
    )

    assert response.status_code == 400
    assert response.json() == error


@pytest.mark.parametrize(
    ("path", "body", "field"),
    [
        ("/auth/login", {**LOGIN, "email": "invalid"}, "email"),
        ("/auth/login", {**LOGIN, "password": 42}, "password"),
        ("/auth/refresh", {"refresh_token": None}, "refresh_token"),
        ("/auth/logout", {}, "refresh_token"),
        ("/auth/password/change", {"old_password": "test"}, "new_password"),
    ],
)
async def test_auth_validates_input_before_forwarding(client, path, body, field):
    response = await client.post(path, json=body)
    assert_validation_error(response, "body", field)
