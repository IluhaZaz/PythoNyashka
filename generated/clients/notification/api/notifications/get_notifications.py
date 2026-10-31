from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_notifications_response_200 import GetNotificationsResponse200
from ...models.validation_errors import ValidationErrors
from ...types import UNSET, Response, Unset


def _get_kwargs(
    profile_id: UUID,
    *,
    limit: int | Unset = 10,
    offset: int | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/notifications/{profile_id}".format(
            profile_id=quote(str(profile_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetNotificationsResponse200 | ValidationErrors | None:
    if response.status_code == 200:
        response_200 = GetNotificationsResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 422:
        response_422 = ValidationErrors.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetNotificationsResponse200 | ValidationErrors]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    profile_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 10,
    offset: int | Unset = UNSET,
) -> Response[GetNotificationsResponse200 | ValidationErrors]:
    """Get profile notifications

    Args:
        profile_id (UUID):
        limit (int | Unset):  Default: 10.
        offset (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetNotificationsResponse200 | ValidationErrors]
    """

    kwargs = _get_kwargs(
        profile_id=profile_id,
        limit=limit,
        offset=offset,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    profile_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 10,
    offset: int | Unset = UNSET,
) -> GetNotificationsResponse200 | ValidationErrors | None:
    """Get profile notifications

    Args:
        profile_id (UUID):
        limit (int | Unset):  Default: 10.
        offset (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetNotificationsResponse200 | ValidationErrors
    """

    return sync_detailed(
        profile_id=profile_id,
        client=client,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    profile_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 10,
    offset: int | Unset = UNSET,
) -> Response[GetNotificationsResponse200 | ValidationErrors]:
    """Get profile notifications

    Args:
        profile_id (UUID):
        limit (int | Unset):  Default: 10.
        offset (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetNotificationsResponse200 | ValidationErrors]
    """

    kwargs = _get_kwargs(
        profile_id=profile_id,
        limit=limit,
        offset=offset,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    profile_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 10,
    offset: int | Unset = UNSET,
) -> GetNotificationsResponse200 | ValidationErrors | None:
    """Get profile notifications

    Args:
        profile_id (UUID):
        limit (int | Unset):  Default: 10.
        offset (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetNotificationsResponse200 | ValidationErrors
    """

    return (
        await asyncio_detailed(
            profile_id=profile_id,
            client=client,
            limit=limit,
            offset=offset,
        )
    ).parsed
