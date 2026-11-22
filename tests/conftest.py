from collections.abc import Callable
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from tests.helpers import PROFILE_ID


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def jwt_secret(monkeypatch: pytest.MonkeyPatch) -> str:
    secret = "pythonyashka-test-key-only-for-local-tests"
    monkeypatch.setenv("AUTH_JWT_SECRET", secret)
    monkeypatch.setenv("AUTH_ACCESS_TTL_SECONDS", "900")
    monkeypatch.setenv("AUTH_REFRESH_TTL_DAYS", "30")
    return secret


@pytest.fixture
def access_headers(jwt_secret: str) -> Callable[..., dict[str, str]]:
    def make_headers(profile_id: str = PROFILE_ID, **claim_overrides: object) -> dict[str, str]:
        now = datetime.now(timezone.utc)
        claims = {
            "sub": "api-test-user",
            "profile_id": profile_id,
            "iat": now - timedelta(minutes=1),
            "exp": now + timedelta(minutes=5),
            "iss": "auth",
            "aud": "bff",
            "token_use": "access",
            **claim_overrides,
        }
        token = jwt.encode(claims, jwt_secret, algorithm="HS256")
        return {"Authorization": f"Bearer {token}"}

    return make_headers
