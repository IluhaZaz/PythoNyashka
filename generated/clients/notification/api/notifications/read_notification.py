from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.validation_errors import ValidationErrors
from ...types import UNSET, Response


def _get_kwargs(
    notification_id: UUID,
    *,
    profile_id: UUID,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_profile_id = str(profile_id)
    params["profile_id"] = json_profile_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/notifications/{notification_id}/read".format(
            notification_id=quote(str(notification_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | Error | ValidationErrors | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if response.status_code == 422:
        response_422 = ValidationErrors.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | Error | ValidationErrors]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    notification_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    profile_id: UUID,
) -> Response[Any | Error | ValidationErrors]:
    """Mark a notification as read

     Marks the notification as read only if it belongs to profile_id.
    Repeated calls return 204. Returns 404 if absent or owned by another profile.

    Args:
        notification_id (UUID):
        profile_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error | ValidationErrors]
    """

    kwargs = _get_kwargs(
        notification_id=notification_id,
        profile_id=profile_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    notification_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    profile_id: UUID,
) -> Any | Error | ValidationErrors | None:
    """Mark a notification as read

     Marks the notification as read only if it belongs to profile_id.
    Repeated calls return 204. Returns 404 if absent or owned by another profile.

    Args:
        notification_id (UUID):
        profile_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error | ValidationErrors
    """

    return sync_detailed(
        notification_id=notification_id,
        client=client,
        profile_id=profile_id,
    ).parsed


async def asyncio_detailed(
    notification_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    profile_id: UUID,
) -> Response[Any | Error | ValidationErrors]:
    """Mark a notification as read

     Marks the notification as read only if it belongs to profile_id.
    Repeated calls return 204. Returns 404 if absent or owned by another profile.

    Args:
        notification_id (UUID):
        profile_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error | ValidationErrors]
    """

    kwargs = _get_kwargs(
        notification_id=notification_id,
        profile_id=profile_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    notification_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    profile_id: UUID,
) -> Any | Error | ValidationErrors | None:
    """Mark a notification as read

     Marks the notification as read only if it belongs to profile_id.
    Repeated calls return 204. Returns 404 if absent or owned by another profile.

    Args:
        notification_id (UUID):
        profile_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error | ValidationErrors
    """

    return (
        await asyncio_detailed(
            notification_id=notification_id,
            client=client,
            profile_id=profile_id,
        )
    ).parsed
