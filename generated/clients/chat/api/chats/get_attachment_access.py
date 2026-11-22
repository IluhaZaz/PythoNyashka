from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.attachment_access_response import AttachmentAccessResponse
from ...types import UNSET, Response


def _get_kwargs(
    media_id: UUID,
    *,
    profile_id: UUID,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_profile_id = str(profile_id)
    params["profile_id"] = json_profile_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/chats/media/{media_id}/access".format(
            media_id=quote(str(media_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AttachmentAccessResponse | None:
    if response.status_code == 200:
        response_200 = AttachmentAccessResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[AttachmentAccessResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    media_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    profile_id: UUID,
) -> Response[AttachmentAccessResponse]:
    """Check access to a chat attachment

    Args:
        media_id (UUID):
        profile_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AttachmentAccessResponse]
    """

    kwargs = _get_kwargs(
        media_id=media_id,
        profile_id=profile_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    media_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    profile_id: UUID,
) -> AttachmentAccessResponse | None:
    """Check access to a chat attachment

    Args:
        media_id (UUID):
        profile_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AttachmentAccessResponse
    """

    return sync_detailed(
        media_id=media_id,
        client=client,
        profile_id=profile_id,
    ).parsed


async def asyncio_detailed(
    media_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    profile_id: UUID,
) -> Response[AttachmentAccessResponse]:
    """Check access to a chat attachment

    Args:
        media_id (UUID):
        profile_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AttachmentAccessResponse]
    """

    kwargs = _get_kwargs(
        media_id=media_id,
        profile_id=profile_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    media_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    profile_id: UUID,
) -> AttachmentAccessResponse | None:
    """Check access to a chat attachment

    Args:
        media_id (UUID):
        profile_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AttachmentAccessResponse
    """

    return (
        await asyncio_detailed(
            media_id=media_id,
            client=client,
            profile_id=profile_id,
        )
    ).parsed
