import os
import subprocess
import sys
import time
from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from pathlib import Path
from types import ModuleType
from uuid import uuid4

import httpx
import psycopg2
import pytest
from fastapi import FastAPI
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.profile.infrastructure.storage.postgresql.models import Profile
from tests.helpers import profile_body

REPO_ROOT = Path(__file__).resolve().parents[2]
POSTGRES_USER = "api_test"
POSTGRES_PASSWORD = "local_fixture_only"
POSTGRES_DB = "pythonyashka_test"


def docker(*args: str, timeout: int = 30) -> str:
    try:
        result = subprocess.run(
            ["docker", *args],
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        pytest.fail("Docker is required for tests/services. Start Docker and run pytest again.")
    except subprocess.CalledProcessError as exc:
        pytest.fail(f"Docker {args[0]} failed: {exc.stderr.strip()}")
    return result.stdout.strip()


def wait_for_postgres(port: int) -> None:
    deadline = time.monotonic() + 60
    while True:
        try:
            connection = psycopg2.connect(
                host="127.0.0.1",
                port=port,
                dbname=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                connect_timeout=2,
            )
        except psycopg2.OperationalError as exc:
            if time.monotonic() >= deadline:
                pytest.fail(f"Test PostgreSQL did not accept connections: {exc}")
            time.sleep(0.25)
        else:
            connection.close()
            return


@pytest.fixture(scope="session")
def postgres() -> Iterator[URL]:
    container = docker(
        "run",
        "--rm",
        "--detach",
        "--label",
        "pythonyashka.api-tests=true",
        "--publish",
        "127.0.0.1::5432",
        "--env",
        f"POSTGRES_USER={POSTGRES_USER}",
        "--env",
        f"POSTGRES_PASSWORD={POSTGRES_PASSWORD}",
        "--env",
        f"POSTGRES_DB={POSTGRES_DB}",
        "postgres:16",
        timeout=300,
    )
    try:
        port = int(docker("port", container, "5432/tcp").rsplit(":", 1)[1])
        wait_for_postgres(port)
        migration = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=REPO_ROOT,
            env={
                **os.environ,
                "DB_HOST": "127.0.0.1",
                "DB_PORT": str(port),
                "DB_USER": POSTGRES_USER,
                "DB_PASSWORD": POSTGRES_PASSWORD,
                "DB_NAME": POSTGRES_DB,
            },
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        assert migration.returncode == 0, migration.stdout + migration.stderr
        yield URL.create(
            "postgresql+asyncpg",
            username=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host="127.0.0.1",
            port=port,
            database=POSTGRES_DB,
        )
    finally:
        docker("stop", "--time", "5", container)


@pytest.fixture
async def db_sessions(postgres: URL) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_async_engine(postgres)
    try:
        async with engine.connect() as connection:
            transaction = await connection.begin()
            try:
                # A repository can commit while the outer transaction still isolates the test.
                yield async_sessionmaker(
                    connection,
                    autoflush=False,
                    expire_on_commit=False,
                    join_transaction_mode="create_savepoint",
                )
            finally:
                await transaction.rollback()
    finally:
        await engine.dispose()


@pytest.fixture
def service_client(
    db_sessions: async_sessionmaker[AsyncSession],
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[[FastAPI, ModuleType], httpx.AsyncClient]:
    def make_client(app: FastAPI, dependencies: ModuleType) -> httpx.AsyncClient:
        monkeypatch.setattr(dependencies, "DBSession", db_sessions)
        return httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://service.test",
        )

    return make_client


@pytest.fixture
def seed_profile(db_sessions: async_sessionmaker[AsyncSession]) -> Callable[[], Awaitable[str]]:
    async def create() -> str:
        profile_id = str(uuid4())
        async with db_sessions() as session:
            session.add(Profile(id=profile_id, **profile_body(f"{profile_id}@example.com")))
            await session.commit()
        return profile_id

    return create
