from typing import Annotated

from fastapi import APIRouter, Depends, Form
from fastapi.responses import JSONResponse

from src.bff import dependencies
from src.bff.domain.schemas import (
    AuthTokens,
    ErrorResponse,
    LoginRequest,
    ProfileCreate,
    ProfileCreatedResponse,
)
from src.bff.usecase import CreateProfile, InvalidCredentialsError, Login, ProfileAlreadyExistsError

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
