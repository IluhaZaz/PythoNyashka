import httpx

PROFILE_ID = "00000000-0000-4000-8000-000000000001"
OTHER_PROFILE_ID = "00000000-0000-4000-8000-000000000002"
MISSING_ID = "00000000-0000-4000-8000-000000000003"
MEDIA_ID = "00000000-0000-4000-8000-000000000004"
CHAT_ID = "00000000-0000-4000-8000-000000000005"
MESSAGE_ID = "00000000-0000-4000-8000-000000000006"
MATCH_ID = "00000000-0000-4000-8000-000000000007"
NOTIFICATION_ID = "00000000-0000-4000-8000-000000000008"
USER_ID = "00000000-0000-4000-8000-000000000009"
TIMESTAMP = "2025-01-02T03:04:05Z"


def profile_body(email: str = "ada@example.com") -> dict[str, str | int | list[str]]:
    return {
        "email": email,
        "name": "Ada",
        "surname": "Lovelace",
        "age": 28,
        "bio": "Writes code",
        "gender": "female",
        "tags": ["python", "sql"],
    }


def assert_validation_error(response: httpx.Response, *location: str) -> None:
    assert response.status_code == 422, response.text
    field = list(location)
    assert any(error["loc"][: len(field)] == field for error in response.json()["detail"])


def assert_no_content(response: httpx.Response) -> None:
    assert response.status_code == 204, response.text
    assert response.content == b""


def assert_unauthorized(response: httpx.Response) -> None:
    assert response.status_code == 401, response.text
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json()["error"]
