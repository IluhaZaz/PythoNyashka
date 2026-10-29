from typing import Annotated

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
    RefreshTokenRequest,
)
from src.bff.usecase import (
    ChangePassword,
    CreateProfile,
    InvalidCredentialsError,
    InvalidOldPasswordError,
    Login,
    Logout,
    ProfileAlreadyExistsError,
    Refresh,
)

router = APIRouter()
profiles_router = APIRouter()


@router.post(
    "/login",
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
    "/auth",
    status_code=201,
    operation_id="createProfile",
    response_model=ProfileCreatedResponse,
    responses={409: {"model": ErrorResponse}},
    tags=["Profile"]
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
