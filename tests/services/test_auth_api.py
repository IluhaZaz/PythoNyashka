import hashlib
import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, create_autospec
from uuid import UUID

import jwt
import pytest
from aiokafka import AIOKafkaProducer
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from src.auth import dependencies
from src.auth.infrastructure.messaging.kafka.publisher import NotificationPublisher
from src.auth.infrastructure.storage.postgresql.models import Session, User
from src.auth.infrastructure.storage.postgresql.repository import AuthRepository
from src.auth.main import app
from src.auth.security import password_hasher
from tests.helpers import (
    OTHER_PROFILE_ID,
    PROFILE_ID,
    USER_ID,
    assert_no_content,
    assert_unauthorized,
    assert_validation_error,
)

pytestmark = pytest.mark.anyio

CREDENTIALS = {"email": "ada@example.com", "password": "first-test-password"}
PASSWORD_CHANGE = {"old_password": CREDENTIALS["password"], "new_password": "new-test-password"}


@pytest.fixture
def producer():
    return create_autospec(AIOKafkaProducer, instance=True)


@pytest.fixture
async def client(service_client, monkeypatch, producer, jwt_secret):
    monkeypatch.setattr(
        app.state, "notification_publisher", NotificationPublisher(producer), raising=False
    )
    async with service_client(app, dependencies) as http:
        yield http


@pytest.fixture(scope="module")
def password_hash():
    return password_hasher.hash(CREDENTIALS["password"])


@pytest.fixture
async def registered_user(db_sessions, password_hash):
    async with db_sessions() as session:
        session.add(
            User(
                id=USER_ID,
                profile_id=PROFILE_ID,
                email=CREDENTIALS["email"],
                password_hash=password_hash,
            )
        )
        await session.commit()


@pytest.fixture
async def tokens(client, registered_user):
    response = await client.post("/auth/login", json=CREDENTIALS)
    assert response.status_code == 200, response.text
    return response.json()


def authorization(tokens):
    return {"Authorization": f"Bearer {tokens['access_token']}"}


async def test_register_hashes_password_and_publishes_notification(client, db_sessions, producer):
    response = await client.post("/auth/register", json={**CREDENTIALS, "profile_id": PROFILE_ID})

    assert response.status_code == 201, response.text
    user_id = response.json()["user_id"]
    UUID(user_id)
    async with db_sessions() as session:
        user = await session.get(User, user_id)
        assert user.profile_id == PROFILE_ID
        assert user.email == CREDENTIALS["email"]
        assert user.password_hash != CREDENTIALS["password"]
        assert password_hasher.verify(CREDENTIALS["password"], user.password_hash)

    producer.send_and_wait.assert_awaited_once()
    args = producer.send_and_wait.await_args
    assert args.args == ("notification.events",)
    assert args.kwargs["key"] == PROFILE_ID.encode()
    event = json.loads(args.kwargs["value"])
    assert (event["source"], event["profile_id"], event["email"]) == (
        "auth",
        PROFILE_ID,
        CREDENTIALS["email"],
    )
    assert event["text"]
    assert "password" not in event


@pytest.mark.xfail(
    strict=True,
    raises=IntegrityError,
    reason="Auth OpenAPI documents 400, but duplicate email raises an uncaught IntegrityError",
)
async def test_register_rejects_duplicate_email(client, registered_user):
    response = await client.post(
        "/auth/register",
        json={**CREDENTIALS, "profile_id": OTHER_PROFILE_ID},
    )
    assert response.status_code == 400, response.text


async def test_login_issues_access_and_persists_hash_of_refresh_token(
    tokens, jwt_secret, db_sessions
):
    assert tokens["token_type"] == "Bearer"
    assert tokens["expires_in"] == 900
    claims = jwt.decode(
        tokens["access_token"],
        jwt_secret,
        algorithms=["HS256"],
        issuer="auth",
        audience="bff",
    )
    assert (claims["sub"], claims["profile_id"], claims["token_use"]) == (
        USER_ID,
        PROFILE_ID,
        "access",
    )
    assert claims["exp"] - claims["iat"] == tokens["expires_in"]
    async with db_sessions() as session:
        stored = (await session.scalars(select(Session))).one()
        assert stored.user_id == USER_ID
        assert (
            stored.refresh_token_hash
            == hashlib.sha256(tokens["refresh_token"].encode()).hexdigest()
        )
        assert stored.expires_at > datetime.now(timezone.utc)
        assert stored.is_revoked is False


@pytest.mark.parametrize("changes", [{"email": "unknown@example.com"}, {"password": "wrong"}])
async def test_login_rejects_wrong_credentials(client, registered_user, db_sessions, changes):
    response = await client.post("/auth/login", json={**CREDENTIALS, **changes})

    assert response.status_code == 401
    assert response.json()["error"]
    async with db_sessions() as session:
        assert (await session.scalars(select(Session))).all() == []


async def test_refresh_rotates_token_and_rejects_previous_one(client, tokens, jwt_secret):
    old = {"refresh_token": tokens["refresh_token"]}
    response = await client.post("/auth/refresh", json=old)

    assert response.status_code == 200, response.text
    refreshed = response.json()
    assert refreshed["refresh_token"] != old["refresh_token"]
    claims = jwt.decode(
        refreshed["access_token"],
        jwt_secret,
        algorithms=["HS256"],
        audience="bff",
    )
    assert claims["profile_id"] == PROFILE_ID
    assert (await client.post("/auth/refresh", json=old)).status_code == 401
    assert (
        await client.post(
            "/auth/refresh",
            json={"refresh_token": refreshed["refresh_token"]},
        )
    ).status_code == 200


async def test_refresh_rejects_unknown_token(client):
    response = await client.post("/auth/refresh", json={"refresh_token": "unknown-test-token"})
    assert response.status_code == 401
    assert response.json()["error"]


async def test_refresh_rejects_expired_session(client, tokens, db_sessions):
    async with db_sessions() as session:
        await session.execute(update(Session).values(expires_at=datetime.now(timezone.utc)))
        await session.commit()
    response = await client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert response.status_code == 401


async def test_refresh_returns_unauthorized_if_repository_declines_rotation(
    client,
    tokens,
    monkeypatch,
):
    rotate = AsyncMock(return_value=False)
    monkeypatch.setattr(AuthRepository, "rotate_refresh_token", rotate)

    response = await client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})

    assert response.status_code == 401
    rotate.assert_awaited_once()


async def test_logout_revokes_session(client, tokens):
    data = {"refresh_token": tokens["refresh_token"]}

    assert_no_content(await client.post("/auth/logout", json=data, headers=authorization(tokens)))
    assert (await client.post("/auth/refresh", json=data)).status_code == 401


async def test_logout_rejects_unknown_session(client, tokens):
    response = await client.post(
        "/auth/logout",
        json={"refresh_token": "unknown-test-token"},
        headers=authorization(tokens),
    )
    assert_unauthorized(response)


@pytest.mark.security
async def test_logout_cannot_revoke_another_users_session(
    client,
    tokens,
    db_sessions,
    password_hash,
):
    other_email = "other@example.com"
    async with db_sessions() as session:
        session.add(
            User(
                email=other_email,
                profile_id=OTHER_PROFILE_ID,
                password_hash=password_hash,
            )
        )
        await session.commit()
    other_login = await client.post("/auth/login", json={**CREDENTIALS, "email": other_email})
    assert other_login.status_code == 200
    data = {"refresh_token": tokens["refresh_token"]}

    response = await client.post(
        "/auth/logout", json=data, headers=authorization(other_login.json())
    )

    assert_unauthorized(response)
    assert (await client.post("/auth/refresh", json=data)).status_code == 200


async def test_change_password_revokes_all_sessions_and_notifies(client, tokens, producer):
    second_login = await client.post("/auth/login", json=CREDENTIALS)
    assert second_login.status_code == 200

    response = await client.post(
        "/auth/password/reset",
        json=PASSWORD_CHANGE,
        headers=authorization(tokens),
    )

    assert_no_content(response)
    for login in (tokens, second_login.json()):
        assert (
            await client.post(
                "/auth/refresh",
                json={"refresh_token": login["refresh_token"]},
            )
        ).status_code == 401
    assert (await client.post("/auth/login", json=CREDENTIALS)).status_code == 401
    assert (
        await client.post(
            "/auth/login",
            json={**CREDENTIALS, "password": PASSWORD_CHANGE["new_password"]},
        )
    ).status_code == 200
    producer.send_and_wait.assert_awaited_once()
    assert json.loads(producer.send_and_wait.await_args.kwargs["value"])["profile_id"] == PROFILE_ID


async def test_change_password_rejects_wrong_old_password(client, tokens, producer):
    response = await client.post(
        "/auth/password/reset",
        json={**PASSWORD_CHANGE, "old_password": "wrong"},
        headers=authorization(tokens),
    )

    assert response.status_code == 400
    assert response.json()["error"]
    assert (await client.post("/auth/login", json=CREDENTIALS)).status_code == 200
    producer.send_and_wait.assert_not_awaited()


async def test_change_password_rejects_valid_token_for_missing_user(client, access_headers):
    response = await client.post(
        "/auth/password/reset",
        json=PASSWORD_CHANGE,
        headers=access_headers(sub=USER_ID),
    )
    assert_unauthorized(response)


@pytest.mark.parametrize(
    ("path", "body"),
    [
        ("/auth/logout", {"refresh_token": "example-test-token"}),
        ("/auth/password/reset", PASSWORD_CHANGE),
    ],
)
@pytest.mark.parametrize("headers", [{}, {"Authorization": "Bearer invalid"}])
async def test_protected_auth_routes_reject_missing_or_invalid_bearer(client, path, body, headers):
    assert_unauthorized(await client.post(path, json=body, headers=headers))


@pytest.mark.parametrize(
    ("path", "body", "field"),
    [
        ("/auth/register", CREDENTIALS, "profile_id"),
        ("/auth/register", {**CREDENTIALS, "profile_id": 123}, "profile_id"),
        ("/auth/login", {"email": CREDENTIALS["email"]}, "password"),
        ("/auth/refresh", {"refresh_token": []}, "refresh_token"),
        ("/auth/logout", {}, "refresh_token"),
        ("/auth/password/reset", {"old_password": "test"}, "new_password"),
    ],
)
async def test_auth_validates_request_bodies(client, path, body, field):
    assert_validation_error(await client.post(path, json=body), "body", field)
