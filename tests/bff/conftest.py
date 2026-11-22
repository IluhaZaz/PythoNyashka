from collections import deque
from collections.abc import AsyncIterator, Iterator
from functools import partial

import httpx
import pytest

from src.bff import dependencies
from src.bff.main import app


class Downstream:
    def __init__(self) -> None:
        self.requests: list[httpx.Request] = []
        self.pending: deque[tuple[str, str, str, httpx.Response | type[httpx.RequestError]]] = (
            deque()
        )

    def expect(
        self,
        method: str,
        service: str,
        path: str,
        status: int | type[httpx.RequestError],
        **response_options: object,
    ) -> None:
        reply = httpx.Response(status, **response_options) if isinstance(status, int) else status
        self.pending.append((method, f"{service}.test", path, reply))

    def handle(self, request: httpx.Request) -> httpx.Response:
        assert self.pending, f"Unexpected upstream request: {request.method} {request.url}"
        method, host, path, reply = self.pending.popleft()
        assert (request.method, request.url.host, request.url.path) == (method, host, path)
        self.requests.append(request)
        if isinstance(reply, httpx.Response):
            return reply
        raise reply("simulated upstream failure", request=request)


@pytest.fixture
def downstream(monkeypatch: pytest.MonkeyPatch) -> Iterator[Downstream]:
    upstream = Downstream()
    for name, service in [
        ("Client", "auth"),
        ("AuthenticatedClient", "auth"),
        ("ProfileClient", "profile"),
        ("MediaClient", "media"),
        ("ChatClient", "chat"),
        ("MatchClient", "match"),
        ("NotificationClient", "notification"),
    ]:
        monkeypatch.setenv(f"BFF_{service.upper()}_BASE_URL", f"http://{service}.test")
        monkeypatch.setenv(f"BFF_{service.upper()}_TIMEOUT_SECONDS", "2")
        options = {"transport": httpx.MockTransport(upstream.handle), "trust_env": False}
        monkeypatch.setattr(
            dependencies, name, partial(getattr(dependencies, name), httpx_args=options)
        )
    yield upstream
    assert not upstream.pending, f"Expected upstream requests not sent: {list(upstream.pending)}"


@pytest.fixture
async def client(downstream: Downstream, jwt_secret: str) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://bff.test",
    ) as http:
        yield http
