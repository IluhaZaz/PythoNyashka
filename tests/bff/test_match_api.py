import httpx
import pytest

from tests.helpers import (
    MATCH_ID,
    OTHER_PROFILE_ID,
    PROFILE_ID,
    TIMESTAMP,
    assert_no_content,
    assert_validation_error,
)

pytestmark = pytest.mark.anyio

MATCH = {
    "id": MATCH_ID,
    "initiatorProfileId": PROFILE_ID,
    "targetProfileId": OTHER_PROFILE_ID,
    "status": "noResponse",
    "createdAt": TIMESTAMP,
}
SWIPE_PATH = f"/matches/{MATCH_ID}/swipe"


async def test_get_match_uses_authenticated_profile_and_preserves_response(
    client,
    downstream,
    access_headers,
):
    downstream.expect("GET", "match", "/matches", 200, json=MATCH)

    response = await client.get("/matches", headers=access_headers())

    assert response.status_code == 200
    assert response.json() == MATCH
    assert dict(downstream.requests[0].url.params) == {"profile_id": PROFILE_ID}


async def test_get_match_preserves_no_candidate_response(client, downstream, access_headers):
    error = {"error": "No matches available"}
    downstream.expect("GET", "match", "/matches", 404, json=error)

    response = await client.get("/matches", headers=access_headers())

    assert response.status_code == 404
    assert response.json() == error


@pytest.mark.parametrize(
    ("upstream_status", "error"),
    [
        (503, "Unexpected Match Service response"),
        (httpx.ConnectError, "Match Service unavailable"),
    ],
)
async def test_get_match_maps_downstream_failures_to_bad_gateway(
    client,
    downstream,
    access_headers,
    upstream_status,
    error,
):
    downstream.expect("GET", "match", "/matches", upstream_status)

    response = await client.get("/matches", headers=access_headers())

    assert response.status_code == 502
    assert response.json() == {"error": error}


@pytest.mark.parametrize(
    ("params", "forwarded"),
    [
        ({}, {"limit": "10", "offset": "0"}),
        ({"limit": 100, "offset": 2}, {"limit": "100", "offset": "2"}),
    ],
)
async def test_get_match_history_forwards_pagination_and_keeps_my_swipe(
    client,
    downstream,
    access_headers,
    params,
    forwarded,
):
    body = {"matches": [{**MATCH, "mySwipe": "like"}, {**MATCH, "mySwipe": None}]}
    downstream.expect("GET", "match", "/matches/history", 200, json=body)

    response = await client.get("/matches/history", headers=access_headers(), params=params)

    assert response.status_code == 200, response.text
    assert response.json() == body
    assert dict(downstream.requests[0].url.params) == {"profile_id": PROFILE_ID, **forwarded}


async def test_get_match_history_returns_empty_list(client, downstream, access_headers):
    downstream.expect("GET", "match", "/matches/history", 200, json={"matches": []})

    response = await client.get("/matches/history", headers=access_headers())

    assert response.status_code == 200
    assert response.json() == {"matches": []}


@pytest.mark.parametrize(("field", "value"), [("offset", -1), ("limit", 0), ("limit", 101)])
async def test_get_match_history_validates_limits(client, access_headers, field, value):
    response = await client.get("/matches/history", headers=access_headers(), params={field: value})
    assert_validation_error(response, "query", field)


@pytest.mark.parametrize("swipe", ["like", "dislike"])
async def test_swipe_dispatches_to_matching_service_route(
    client, downstream, access_headers, swipe
):
    downstream.expect("POST", "match", f"/matches/{MATCH_ID}/{swipe}", 204)

    assert_no_content(await client.post(SWIPE_PATH, json=swipe, headers=access_headers()))
    assert dict(downstream.requests[0].url.params) == {"profile_id": PROFILE_ID}


async def test_swipe_returns_not_found_for_missing_match(client, downstream, access_headers):
    error = {"error": "Match not found"}
    downstream.expect("POST", "match", f"/matches/{MATCH_ID}/like", 404, json=error)

    response = await client.post(SWIPE_PATH, json="like", headers=access_headers())

    assert response.status_code == 404
    assert response.json() == error


@pytest.mark.parametrize("value", ["maybe", {"answer": "like"}, None])
async def test_swipe_rejects_invalid_json_body(client, access_headers, value):
    response = await client.post(SWIPE_PATH, json=value, headers=access_headers())
    assert_validation_error(response, "body")


async def test_swipe_validates_match_uuid(client, access_headers):
    response = await client.post("/matches/invalid/swipe", json="like", headers=access_headers())
    assert_validation_error(response, "path", "match_id")
