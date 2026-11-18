from http import HTTPStatus
from typing import Any
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.match_get import MatchGet
from ...types import UNSET, Response


def _get_kwargs(
    *,
    profile_id: UUID,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_profile_id = str(profile_id)
    params["profile_id"] = json_profile_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/matches",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> MatchGet | None:
    if response.status_code == 200:
        response_200 = MatchGet.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[MatchGet]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    profile_id: UUID,
) -> Response[MatchGet]:
    """Get match

     Get the next match for profile_id.

    Args:
        profile_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[MatchGet]
    """

    kwargs = _get_kwargs(
        profile_id=profile_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    profile_id: UUID,
) -> MatchGet | None:
    """Get match

     Get the next match for profile_id.

    Args:
        profile_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        MatchGet
    """

    return sync_detailed(
        client=client,
        profile_id=profile_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    profile_id: UUID,
) -> Response[MatchGet]:
    """Get match

     Get the next match for profile_id.

    Args:
        profile_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[MatchGet]
    """

    kwargs = _get_kwargs(
        profile_id=profile_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    profile_id: UUID,
) -> MatchGet | None:
    """Get match

     Get the next match for profile_id.

    Args:
        profile_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        MatchGet
    """

    return (
        await asyncio_detailed(
            client=client,
            profile_id=profile_id,
        )
    ).parsed
