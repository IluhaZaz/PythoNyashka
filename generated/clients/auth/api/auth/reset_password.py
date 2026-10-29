from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.password_reset_request import PasswordResetRequest
from ...models.reset_password_response_400 import ResetPasswordResponse400
from ...models.reset_password_response_422 import ResetPasswordResponse422
from ...types import Response


def _get_kwargs(
    *,
    body: PasswordResetRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/auth/password/reset",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | ResetPasswordResponse400 | ResetPasswordResponse422 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204

    if response.status_code == 400:
        response_400 = ResetPasswordResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 422:
        response_422 = ResetPasswordResponse422.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | ResetPasswordResponse400 | ResetPasswordResponse422]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PasswordResetRequest,
) -> Response[Any | ResetPasswordResponse400 | ResetPasswordResponse422]:
    """Request or confirm password reset

    Args:
        body (PasswordResetRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ResetPasswordResponse400 | ResetPasswordResponse422]
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
    body: PasswordResetRequest,
) -> Any | ResetPasswordResponse400 | ResetPasswordResponse422 | None:
    """Request or confirm password reset

    Args:
        body (PasswordResetRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ResetPasswordResponse400 | ResetPasswordResponse422
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PasswordResetRequest,
) -> Response[Any | ResetPasswordResponse400 | ResetPasswordResponse422]:
    """Request or confirm password reset

    Args:
        body (PasswordResetRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ResetPasswordResponse400 | ResetPasswordResponse422]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: PasswordResetRequest,
) -> Any | ResetPasswordResponse400 | ResetPasswordResponse422 | None:
    """Request or confirm password reset

    Args:
        body (PasswordResetRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ResetPasswordResponse400 | ResetPasswordResponse422
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
