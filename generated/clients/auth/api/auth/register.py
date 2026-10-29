from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.register_request import RegisterRequest
from ...models.register_response_201 import RegisterResponse201
from ...models.register_response_400 import RegisterResponse400
from ...models.register_response_422 import RegisterResponse422
from ...types import Response


def _get_kwargs(
    *,
    body: RegisterRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/auth/register",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> RegisterResponse201 | RegisterResponse400 | RegisterResponse422 | None:
    if response.status_code == 201:
        response_201 = RegisterResponse201.from_dict(response.json())

        return response_201

    if response.status_code == 400:
        response_400 = RegisterResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 422:
        response_422 = RegisterResponse422.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[RegisterResponse201 | RegisterResponse400 | RegisterResponse422]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: RegisterRequest,
) -> Response[RegisterResponse201 | RegisterResponse400 | RegisterResponse422]:
    """Register a new user

    Args:
        body (RegisterRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RegisterResponse201 | RegisterResponse400 | RegisterResponse422]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: RegisterRequest,
) -> RegisterResponse201 | RegisterResponse400 | RegisterResponse422 | None:
    """Register a new user

    Args:
        body (RegisterRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RegisterResponse201 | RegisterResponse400 | RegisterResponse422
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: RegisterRequest,
) -> Response[RegisterResponse201 | RegisterResponse400 | RegisterResponse422]:
    """Register a new user

    Args:
        body (RegisterRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RegisterResponse201 | RegisterResponse400 | RegisterResponse422]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: RegisterRequest,
) -> RegisterResponse201 | RegisterResponse400 | RegisterResponse422 | None:
    """Register a new user

    Args:
        body (RegisterRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RegisterResponse201 | RegisterResponse400 | RegisterResponse422
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
