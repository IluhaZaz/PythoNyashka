from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_chat_messages_response_200 import GetChatMessagesResponse200
from ...models.get_chat_messages_response_404 import GetChatMessagesResponse404
from ...types import UNSET, Response, Unset


def _get_kwargs(
    chat_id: UUID,
    *,
    offset: int | Unset = UNSET,
    limit: int | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["offset"] = offset

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/chats/{chat_id}/messages".format(
            chat_id=quote(str(chat_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetChatMessagesResponse200 | GetChatMessagesResponse404 | None:
    if response.status_code == 200:
        response_200 = GetChatMessagesResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 404:
        response_404 = GetChatMessagesResponse404.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetChatMessagesResponse200 | GetChatMessagesResponse404]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    chat_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    offset: int | Unset = UNSET,
    limit: int | Unset = UNSET,
) -> Response[GetChatMessagesResponse200 | GetChatMessagesResponse404]:
    """Get chat messages

    Args:
        chat_id (UUID):
        offset (int | Unset):
        limit (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetChatMessagesResponse200 | GetChatMessagesResponse404]
    """

    kwargs = _get_kwargs(
        chat_id=chat_id,
        offset=offset,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    chat_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    offset: int | Unset = UNSET,
    limit: int | Unset = UNSET,
) -> GetChatMessagesResponse200 | GetChatMessagesResponse404 | None:
    """Get chat messages

    Args:
        chat_id (UUID):
        offset (int | Unset):
        limit (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetChatMessagesResponse200 | GetChatMessagesResponse404
    """

    return sync_detailed(
        chat_id=chat_id,
        client=client,
        offset=offset,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    chat_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    offset: int | Unset = UNSET,
    limit: int | Unset = UNSET,
) -> Response[GetChatMessagesResponse200 | GetChatMessagesResponse404]:
    """Get chat messages

    Args:
        chat_id (UUID):
        offset (int | Unset):
        limit (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetChatMessagesResponse200 | GetChatMessagesResponse404]
    """

    kwargs = _get_kwargs(
        chat_id=chat_id,
        offset=offset,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    chat_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    offset: int | Unset = UNSET,
    limit: int | Unset = UNSET,
) -> GetChatMessagesResponse200 | GetChatMessagesResponse404 | None:
    """Get chat messages

    Args:
        chat_id (UUID):
        offset (int | Unset):
        limit (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetChatMessagesResponse200 | GetChatMessagesResponse404
    """

    return (
        await asyncio_detailed(
            chat_id=chat_id,
            client=client,
            offset=offset,
            limit=limit,
        )
    ).parsed
