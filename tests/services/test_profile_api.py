from uuid import UUID

import pytest

from src.profile import dependencies
from src.profile.main import app
from tests.helpers import MISSING_ID, assert_no_content, assert_validation_error, profile_body

pytestmark = pytest.mark.anyio


@pytest.fixture
async def client(service_client):
    async with service_client(app, dependencies) as http:
        yield http


@pytest.mark.parametrize(
    "fields",
    [
        {},
        {"name": "A", "surname": "L", "age": 1, "bio": ""},
        {"name": "A" * 100, "surname": "L" * 100, "age": 149, "bio": "x" * 1000},
    ],
    ids=["regular", "lower-limits", "upper-limits"],
)
async def test_create_profile_and_get_persisted_fields(client, fields):
    body = {**profile_body(), **fields}
    response = await client.post("/profiles", json=body)

    assert response.status_code == 201, response.text
    profile_id = response.json()["id"]
    UUID(profile_id)
    fetched = await client.get(f"/profiles/{profile_id}")
    assert fetched.status_code == 200
    profile = fetched.json()["profile"]
    assert profile["id"] == profile_id
    assert {key: profile[key] for key in body} == body
    assert profile["avatar_id"] is None
    assert profile["created_at"] and profile["updated_at"]


async def test_create_profile_defaults_optional_tags_and_avatar(client):
    body = profile_body()
    del body["tags"]
    created = await client.post("/profiles", json=body)
    assert created.status_code == 201

    response = await client.get(f"/profiles/{created.json()['id']}")
    assert response.status_code == 200
    assert response.json()["profile"]["tags"] == []
    assert response.json()["profile"]["avatar_id"] is None


async def test_create_profile_rejects_duplicate_email(client, seed_profile):
    profile_id = await seed_profile()
    response = await client.post("/profiles", json=profile_body(f"{profile_id}@example.com"))

    assert response.status_code == 409
    assert response.json() == {"error": "email already used"}


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("name", ""),
        ("name", "x" * 101),
        ("surname", ""),
        ("surname", "x" * 101),
        ("age", 0),
        ("age", 150),
        ("bio", "x" * 1001),
        ("gender", "unknown"),
        ("tags", "python"),
    ],
)
async def test_create_profile_validates_fields(client, field, value):
    response = await client.post("/profiles", json={**profile_body(), field: value})
    assert_validation_error(response, "body", field)


async def test_get_missing_profile_returns_not_found(client):
    response = await client.get(f"/profiles/{MISSING_ID}")
    assert response.status_code == 404
    assert response.json() == {"error": "Profile not found"}


@pytest.mark.parametrize("patch", [{"name": "Augusta", "tags": []}, {}], ids=["partial", "empty"])
async def test_patch_changes_only_supplied_fields(client, seed_profile, patch):
    profile_id = await seed_profile()
    before = (await client.get(f"/profiles/{profile_id}")).json()["profile"]

    response = await client.patch("/profiles", params={"profile_id": profile_id}, json=patch)

    assert_no_content(response)
    after = (await client.get(f"/profiles/{profile_id}")).json()["profile"]
    assert {key: value for key, value in after.items() if key != "updated_at"} == {
        key: value for key, value in (before | patch).items() if key != "updated_at"
    }


async def test_patch_of_missing_profile_returns_not_found(client):
    response = await client.patch("/profiles", params={"profile_id": MISSING_ID}, json={"age": 31})
    assert response.status_code == 404
    assert response.json() == {"error": "Profile not found"}


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("name", ""),
        ("surname", "x" * 101),
        ("age", 150),
        ("bio", "x" * 1001),
        ("gender", "unknown"),
        ("tags", False),
    ],
)
async def test_patch_validates_fields(client, field, value):
    response = await client.patch(
        "/profiles", params={"profile_id": MISSING_ID}, json={field: value}
    )
    assert_validation_error(response, "body", field)


async def test_patch_requires_profile_id(client):
    assert_validation_error(await client.patch("/profiles", json={}), "query", "profile_id")


async def test_delete_profile_is_idempotent_and_leaves_other_profiles(client, seed_profile):
    profile_id = await seed_profile()
    other_id = await seed_profile()

    assert_no_content(await client.delete(f"/profiles/{profile_id}"))
    assert (await client.get(f"/profiles/{profile_id}")).status_code == 404
    assert_no_content(await client.delete(f"/profiles/{profile_id}"))
    assert (await client.get(f"/profiles/{other_id}")).status_code == 200
