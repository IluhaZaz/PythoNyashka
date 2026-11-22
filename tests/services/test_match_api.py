from datetime import datetime, timedelta
from uuid import UUID

import pytest

from src.match import dependencies
from src.match.infrastructure.storage.postgresql.models import Match
from src.match.main import app
from tests.helpers import (
    MATCH_ID,
    MISSING_ID,
    TIMESTAMP,
    assert_no_content,
    assert_validation_error,
)

pytestmark = pytest.mark.anyio


@pytest.fixture
async def client(service_client):
    async with service_client(app, dependencies) as http:
        yield http


@pytest.fixture
async def pair(seed_profile):
    return await seed_profile(), await seed_profile()


@pytest.fixture
async def pending_match(db_sessions, pair):
    actor, target = pair
    async with db_sessions() as session:
        session.add(Match(id=MATCH_ID, initiator_profile_id=actor, target_profile_id=target))
        await session.commit()
    return actor, target


async def test_get_match_prioritizes_incoming_like_and_keeps_card_until_swipe(
    client,
    pair,
    seed_profile,
    db_sessions,
):
    actor, candidate = pair
    # Without incoming-like priority, the candidate with the lower ID would be first.
    other, liked_by = sorted((candidate, await seed_profile()))
    async with db_sessions() as session:
        session.add(
            Match(
                initiator_profile_id=liked_by,
                target_profile_id=actor,
                decision="accepted",
            )
        )
        await session.commit()

    params = {"profile_id": actor}
    first = await client.get("/matches", params=params)
    assert first.status_code == 200, first.text
    match = first.json()
    UUID(match["id"])
    assert match["initiatorProfileId"] == actor
    assert match["targetProfileId"] == liked_by
    assert match["status"] == "noResponse"
    assert match["createdAt"]

    repeated = await client.get("/matches", params=params)
    assert repeated.status_code == 200, repeated.text
    assert repeated.json() == match
    assert_no_content(await client.post(f"/matches/{match['id']}/dislike", params=params))

    second = await client.get("/matches", params=params)
    assert second.status_code == 200
    second_match = second.json()
    assert second_match["targetProfileId"] == other
    assert_no_content(await client.post(f"/matches/{second_match['id']}/dislike", params=params))

    exhausted = await client.get("/matches", params=params)
    assert exhausted.status_code == 404
    assert exhausted.json() == {"error": "No matches available"}


async def test_get_match_rejects_unknown_profile(client):
    response = await client.get("/matches", params={"profile_id": MISSING_ID})
    assert response.status_code == 404
    assert response.json()["error"]


@pytest.mark.parametrize(
    ("swipe", "stored_decision", "status"),
    [
        ("like", "accepted", "noResponse"),
        ("dislike", "rejected", "rejected"),
    ],
)
async def test_swipe_persists_decision_and_exposes_it_in_history(
    client,
    pending_match,
    db_sessions,
    swipe,
    stored_decision,
    status,
):
    actor, target = pending_match
    params = {"profile_id": actor}
    response = await client.post(f"/matches/{MATCH_ID}/{swipe}", params=params)

    assert_no_content(response)
    async with db_sessions() as session:
        assert (await session.get(Match, MATCH_ID)).decision == stored_decision
    history = await client.get("/matches/history", params=params)
    assert history.status_code == 200, history.text
    (item,) = history.json()["matches"]
    assert item["id"] == MATCH_ID
    assert item["targetProfileId"] == target
    assert (item["mySwipe"], item["status"]) == (swipe, status)


@pytest.mark.parametrize("swipe", ["like", "dislike"])
@pytest.mark.security
async def test_swipe_returns_not_found_for_unknown_or_unowned_match(client, pending_match, swipe):
    actor, target = pending_match
    for match_id, profile_id in [(MISSING_ID, actor), (MATCH_ID, target)]:
        response = await client.post(
            f"/matches/{match_id}/{swipe}",
            params={"profile_id": profile_id},
        )
        assert response.status_code == 404
        assert response.json() == {"error": "Match not found"}

    response = await client.get("/matches/history", params={"profile_id": actor})
    assert response.status_code == 200
    assert response.json() == {"matches": []}
    current = await client.get("/matches", params={"profile_id": actor})
    assert current.status_code == 200, current.text
    assert current.json()["id"] == MATCH_ID


@pytest.mark.parametrize(
    ("own", "reciprocal", "my_swipe", "status"),
    [
        ("accepted", "accepted", "like", "accepted"),
        ("accepted", "rejected", "like", "rejected"),
        ("accepted", "noResponse", "like", "noResponse"),
        ("rejected", "accepted", "dislike", "rejected"),
    ],
)
async def test_history_computes_status_from_legacy_stored_swipes(
    client,
    pair,
    db_sessions,
    own,
    reciprocal,
    my_swipe,
    status,
):
    actor, target = pair
    async with db_sessions() as session:
        session.add_all(
            [
                Match(
                    id=MATCH_ID, initiator_profile_id=actor, target_profile_id=target, decision=own
                ),
                Match(initiator_profile_id=target, target_profile_id=actor, decision=reciprocal),
            ]
        )
        await session.commit()

    response = await client.get("/matches/history", params={"profile_id": actor})

    assert response.status_code == 200, response.text
    (item,) = response.json()["matches"]
    assert (item["id"], item["mySwipe"], item["status"]) == (MATCH_ID, my_swipe, status)


@pytest.mark.parametrize(("swipe", "status"), [("like", "accepted"), ("dislike", "rejected")])
async def test_history_shows_incoming_like_until_recipient_answers(
    client, pending_match, swipe, status,
):
    sender, recipient = pending_match
    sender_params = {"profile_id": sender}
    recipient_params = {"profile_id": recipient}
    assert_no_content(await client.post(f"/matches/{MATCH_ID}/like", params=sender_params))

    response = await client.get("/matches/history", params=recipient_params)
    assert response.status_code == 200, response.text
    (incoming,) = response.json()["matches"]
    assert incoming["id"] == MATCH_ID
    assert (incoming["initiatorProfileId"], incoming["targetProfileId"]) == (sender, recipient)
    assert (incoming["mySwipe"], incoming["status"]) == (None, "noResponse")

    for _ in range(2):
        assert_no_content(
            await client.post(f"/matches/{MATCH_ID}/{swipe}", params=recipient_params)
        )

    response = await client.get("/matches/history", params=recipient_params)
    assert response.status_code == 200, response.text
    (answered,) = response.json()["matches"]
    assert answered["id"] != MATCH_ID
    assert (answered["initiatorProfileId"], answered["targetProfileId"]) == (recipient, sender)
    assert (answered["mySwipe"], answered["status"]) == (swipe, status)

    response = await client.get("/matches/history", params=sender_params)
    assert response.status_code == 200, response.text
    (original,) = response.json()["matches"]
    assert original["id"] == MATCH_ID
    assert (original["mySwipe"], original["status"]) == ("like", status)


async def test_history_orders_by_creation_and_paginates(client, pair, seed_profile, db_sessions):
    actor, first_target = pair
    second_target = await seed_profile()
    timestamp = datetime.fromisoformat(TIMESTAMP)
    async with db_sessions() as session:
        session.add_all(
            [
                Match(
                    initiator_profile_id=actor,
                    target_profile_id=first_target,
                    decision="accepted",
                    created_at=timestamp,
                ),
                Match(
                    initiator_profile_id=actor,
                    target_profile_id=second_target,
                    decision="rejected",
                    created_at=timestamp + timedelta(seconds=1),
                ),
            ]
        )
        await session.commit()

    for page, expected in [
        ({"limit": 100}, [second_target, first_target]),
        ({"limit": 1}, [second_target]),
        ({"limit": 1, "offset": 1}, [first_target]),
        ({"offset": 2}, []),
    ]:
        response = await client.get("/matches/history", params={"profile_id": actor, **page})
        assert response.status_code == 200
        assert [item["targetProfileId"] for item in response.json()["matches"]] == expected


@pytest.mark.parametrize(("key", "value"), [("offset", -1), ("limit", 0), ("limit", 101)])
async def test_history_validates_pagination(client, key, value):
    response = await client.get("/matches/history", params={"profile_id": MISSING_ID, key: value})
    assert_validation_error(response, "query", key)


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/matches"),
        ("GET", "/matches/history"),
        ("POST", f"/matches/{MATCH_ID}/like"),
        ("POST", f"/matches/{MATCH_ID}/dislike"),
    ],
)
async def test_match_routes_require_profile_id(client, method, path):
    assert_validation_error(await client.request(method, path), "query", "profile_id")
