from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.profile_update import ProfileUpdate
from ...models.update_profile_response_404 import UpdateProfileResponse404
from ...models.update_profile_response_422 import UpdateProfileResponse422
from ...types import UNSET, Response


def _get_kwargs(
    *,
    body: ProfileUpdate,
    profile_id: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["profile_id"] = profile_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/profiles",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | UpdateProfileResponse404 | UpdateProfileResponse422 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204

    if response.status_code == 404:
        response_404 = UpdateProfileResponse404.from_dict(response.json())

        return response_404

    if response.status_code == 422:
        response_422 = UpdateProfileResponse422.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | UpdateProfileResponse404 | UpdateProfileResponse422]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ProfileUpdate,
    profile_id: str,
) -> Response[Any | UpdateProfileResponse404 | UpdateProfileResponse422]:
    """Update profile data

     Update the current user profile identified by profile_id. The BFF supplies profile_id; the request
    body contains only profile fields to change.

    Args:
        profile_id (str):
        body (ProfileUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | UpdateProfileResponse404 | UpdateProfileResponse422]
    """

    kwargs = _get_kwargs(
        body=body,
        profile_id=profile_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: ProfileUpdate,
    profile_id: str,
) -> Any | UpdateProfileResponse404 | UpdateProfileResponse422 | None:
    """Update profile data

     Update the current user profile identified by profile_id. The BFF supplies profile_id; the request
    body contains only profile fields to change.

    Args:
        profile_id (str):
        body (ProfileUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | UpdateProfileResponse404 | UpdateProfileResponse422
    """

    return sync_detailed(
        client=client,
        body=body,
        profile_id=profile_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ProfileUpdate,
    profile_id: str,
) -> Response[Any | UpdateProfileResponse404 | UpdateProfileResponse422]:
    """Update profile data

     Update the current user profile identified by profile_id. The BFF supplies profile_id; the request
    body contains only profile fields to change.

    Args:
        profile_id (str):
        body (ProfileUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | UpdateProfileResponse404 | UpdateProfileResponse422]
    """

    kwargs = _get_kwargs(
        body=body,
        profile_id=profile_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: ProfileUpdate,
    profile_id: str,
) -> Any | UpdateProfileResponse404 | UpdateProfileResponse422 | None:
    """Update profile data

     Update the current user profile identified by profile_id. The BFF supplies profile_id; the request
    body contains only profile fields to change.

    Args:
        profile_id (str):
        body (ProfileUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | UpdateProfileResponse404 | UpdateProfileResponse422
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            profile_id=profile_id,
        )
    ).parsed
