from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Form
from fastapi.responses import JSONResponse, Response

from src.bff import dependencies
from src.bff.domain.schemas import (
    AuthTokens,
    ChangePasswordRequest,
    ErrorResponse,
    LoginRequest,
    ProfileCreate,
    ProfileCreatedResponse,
    ProfileGetResponse,
    ProfileUpdate,
    RefreshTokenRequest,
)
from src.bff.usecase import (
    ChangePassword,
    CreateProfile,
    GetMedia,
    GetProfile,
    InvalidCredentialsError,
    InvalidOldPasswordError,
    Login,
    Logout,
    MediaNotFoundError,
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
    Refresh,
    UpdateProfile,
)

router = APIRouter()
profiles_router = APIRouter()
media_router = APIRouter()


@router.post(
    "/auth/login",
    operation_id="login",
    response_model=AuthTokens,
    response_model_exclude_unset=True,
    responses={
        401: {"model": ErrorResponse},
    },
    tags=["Auth"]
)
async def login(
    req: LoginRequest,
    usecase: Annotated[Login, Depends(dependencies.login_uc)],
) -> AuthTokens | JSONResponse:
    try:
        return await usecase.execute(req)
    except InvalidCredentialsError as exc:
        return JSONResponse(
            status_code=401,
            content=ErrorResponse(error=exc.error).model_dump(),
        )


@router.post(
    "/auth/refresh",
    operation_id="refreshToken",
    response_model=AuthTokens,
    response_model_exclude_unset=True,
    responses={401: {"model": ErrorResponse}},
    tags=["Auth"],
)
async def refresh_token(
    req: RefreshTokenRequest,
    usecase: Annotated[Refresh, Depends(dependencies.refresh_uc)],
) -> AuthTokens | JSONResponse:
    try:
        return await usecase.execute(req)
    except InvalidCredentialsError as exc:
        return JSONResponse(
            status_code=401,
            content=ErrorResponse(error=exc.error).model_dump(),
        )


@router.post(
    "/auth/logout",
    status_code=204,
    operation_id="logout",
    response_class=Response,
    responses={401: {"model": ErrorResponse}},
    tags=["Auth"],
)
async def logout(
    req: RefreshTokenRequest,
    usecase: Annotated[Logout, Depends(dependencies.logout_uc)],
) -> Response:
    try:
        await usecase.execute(req)
    except InvalidCredentialsError as exc:
        return JSONResponse(
            status_code=401,
            content=ErrorResponse(error=exc.error).model_dump(),
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Response(status_code=204)


@router.post(
    "/auth/password/change",
    status_code=204,
    operation_id="changePassword",
    response_class=Response,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
    },
    tags=["Auth"],
)
async def change_password(
    req: ChangePasswordRequest,
    usecase: Annotated[ChangePassword, Depends(dependencies.change_password_uc)],
) -> Response:
    try:
        await usecase.execute(req)
    except InvalidCredentialsError as exc:
        return JSONResponse(
            status_code=401,
            content=ErrorResponse(error=exc.error).model_dump(),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidOldPasswordError as exc:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(error=exc.error).model_dump(),
        )

    return Response(status_code=204)


@profiles_router.post(
    "/profiles",
    status_code=201,
    operation_id="createProfile",
    response_model=ProfileCreatedResponse,
    responses={409: {"model": ErrorResponse}},
    tags=["Profiles"]
)
async def create_profile(
    req: Annotated[ProfileCreate, Form(media_type="multipart/form-data")],
    usecase: Annotated[CreateProfile, Depends(dependencies.create_profile_uc)],
) -> ProfileCreatedResponse | JSONResponse:
    try:
        return await usecase.execute(req)
    except ProfileAlreadyExistsError as exc:
        return JSONResponse(
            status_code=409,
            content=ErrorResponse(error=exc.error).model_dump(),
        )


@profiles_router.get(
    "/profiles",
    operation_id="getProfile",
    response_model=ProfileGetResponse,
    response_model_exclude_none=True,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    tags=["Profiles"],
)
async def get_profile(
    usecase: Annotated[GetProfile, Depends(dependencies.get_profile_uc)],
) -> ProfileGetResponse | JSONResponse:
    try:
        return await usecase.execute()
    except InvalidCredentialsError as exc:
        return JSONResponse(
            status_code=401,
            content=ErrorResponse(error=exc.error).model_dump(),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ProfileNotFoundError as exc:
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(error=exc.error).model_dump(),
        )


@profiles_router.patch(
    "/profiles",
    status_code=204,
    operation_id="updateProfile",
    response_class=Response,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    tags=["Profiles"],
)
async def update_profile(
    req: Annotated[ProfileUpdate, Form(media_type="multipart/form-data")],
    usecase: Annotated[UpdateProfile, Depends(dependencies.update_profile_uc)],
) -> Response:
    try:
        await usecase.execute(req)
    except InvalidCredentialsError as exc:
        return JSONResponse(
            status_code=401,
            content=ErrorResponse(error=exc.error).model_dump(),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ProfileNotFoundError as exc:
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(error=exc.error).model_dump(),
        )

    return Response(status_code=204)


@media_router.get(
    "/media/{media_id}",
    operation_id="getMediaById",
    response_class=Response,
    responses={
        200: {
            "description": "File content with its actual Content-Type.",
            "content": {"*/*": {"schema": {"type": "string", "format": "binary"}}},
            "headers": {"Content-Disposition": {"schema": {"type": "string"}}},
        },
        401: {"model": ErrorResponse},
        404: {"description": "Media not found"},
    },
    tags=["Media"],
)
async def get_media_by_id(
    media_id: UUID,
    usecase: Annotated[GetMedia, Depends(dependencies.get_media_uc)],
) -> Response:
    try:
        content, content_type, content_disposition = await usecase.execute(media_id)
    except InvalidCredentialsError as exc:
        return JSONResponse(
            status_code=401,
            content=ErrorResponse(error=exc.error).model_dump(),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except MediaNotFoundError:
        return Response(status_code=404)

    headers = {"Content-Type": content_type}
    if content_disposition is not None:
        headers["Content-Disposition"] = content_disposition
    return Response(content=content, headers=headers)
