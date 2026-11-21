from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Form, Query, Request
from fastapi.responses import JSONResponse, Response

from src.bff import dependencies
from src.bff.domain.schemas import (
    AuthTokens,
    ChangePasswordRequest,
    ChatCreate,
    ChatCreatedResponse,
    ChatMessagesResponse,
    ChatsResponse,
    ErrorResponse,
    LoginRequest,
    MatchGet,
    MatchesGetResponse,
    MatchSwipe,
    MessageCreate,
    NotificationsGetResponse,
    ProfileCreate,
    ProfileCreatedResponse,
    ProfileGetResponse,
    PublicProfileGetResponse,
    ProfileUpdate,
    RefreshTokenRequest,
)
from src.bff.usecase import (
    ChangePassword,
    Chats,
    CreateProfile,
    GetMedia,
    GetNotifications,
    GetProfile,
    InvalidCredentialsError,
    InvalidOldPasswordError,
    Login,
    Logout,
    Matches,
    MediaNotFoundError,
    NotificationNotFoundError,
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
    ReadNotification,
    Refresh,
    UpdateProfile,
)

router = APIRouter()
profiles_router = APIRouter()
media_router = APIRouter()
notifications_router = APIRouter()
chats_router = APIRouter(
    prefix="/chats",
    tags=["Chats"],
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
matches_router = APIRouter(
    prefix="/matches",
    tags=["Matches"],
    responses={401: {"model": ErrorResponse}, 502: {"model": ErrorResponse}},
)


@matches_router.get("", operation_id="getMatch", responses={404: {"model": ErrorResponse}})
async def get_match(usecase: Annotated[Matches, Depends(dependencies.matches_uc)]) -> MatchGet:
    return await usecase.get_next()


@matches_router.get("/history", operation_id="getMatchHistory")
async def get_match_history(
    usecase: Annotated[Matches, Depends(dependencies.matches_uc)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> MatchesGetResponse:
    return await usecase.history(offset, limit)


@matches_router.post(
    "/{match_id}/swipe",
    operation_id="answerMatch",
    status_code=204,
    response_class=Response,
    responses={404: {"model": ErrorResponse}},
)
async def answer_match(
    match_id: UUID,
    answer: Annotated[MatchSwipe, Body()],
    usecase: Annotated[Matches, Depends(dependencies.matches_uc)],
) -> Response:
    await usecase.swipe(match_id, answer)
    return Response(status_code=204)


@notifications_router.get(
    "/notifications",
    operation_id="getNotifications",
    response_model=NotificationsGetResponse,
    responses={401: {"model": ErrorResponse}},
    tags=["Notifications"],
)
async def get_notifications(
    usecase: Annotated[GetNotifications, Depends(dependencies.get_notifications_uc)],
    limit: Annotated[int, Query(description="Maximum number of notifications to return.")] = 10,
    offset: Annotated[int, Query(description="Number of notifications to skip.")] = 0,
) -> NotificationsGetResponse | JSONResponse:
    try:
        return await usecase.execute(limit=limit, offset=offset)
    except InvalidCredentialsError as exc:
        return JSONResponse(
            status_code=401,
            content=ErrorResponse(error=exc.error).model_dump(),
            headers={"WWW-Authenticate": "Bearer"},
        )


@notifications_router.post(
    "/notifications/{notification_id}/read",
    status_code=204,
    operation_id="readNotification",
    response_class=Response,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    tags=["Notifications"],
)
async def read_notification(
    notification_id: UUID,
    usecase: Annotated[ReadNotification, Depends(dependencies.read_notification_uc)],
) -> Response:
    try:
        await usecase.execute(notification_id)
    except InvalidCredentialsError as exc:
        return JSONResponse(
            status_code=401,
            content=ErrorResponse(error=exc.error).model_dump(),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except NotificationNotFoundError as exc:
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(error=exc.error).model_dump(),
        )

    return Response(status_code=204)


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
    openapi_extra={
        "requestBody": {
            "content": {
                "multipart/form-data": {
                    "encoding": {"tags": {"style": "form", "explode": True}},
                },
            },
        },
    },
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


@profiles_router.get(
    "/profiles/{profile_id}/public",
    operation_id="getPublicProfile",
    response_model=PublicProfileGetResponse,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    tags=["Profiles"],
)
async def get_public_profile(
    profile_id: UUID,
    usecase: Annotated[GetProfile, Depends(dependencies.get_profile_uc)],
) -> PublicProfileGetResponse:
    return await usecase.get_public(profile_id)


@profiles_router.patch(
    "/profiles",
    status_code=204,
    operation_id="updateProfile",
    openapi_extra={
        "requestBody": {
            "content": {
                "multipart/form-data": {
                    "encoding": {"tags": {"style": "form", "explode": True}},
                },
            },
        },
    },
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


@chats_router.post("", operation_id="createChat", response_model=ChatCreatedResponse)
async def create_chat(
    req: ChatCreate,
    usecase: Annotated[Chats, Depends(dependencies.chats_uc)],
) -> ChatCreatedResponse:
    return await usecase.create(req)


@chats_router.get("", operation_id="getChats", response_model=ChatsResponse)
async def get_chats(
    usecase: Annotated[Chats, Depends(dependencies.chats_uc)],
) -> ChatsResponse:
    return await usecase.list()


@chats_router.post(
    "/{chat_id}/message",
    operation_id="sendMessage",
    status_code=204,
    response_class=Response,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        415: {"model": ErrorResponse},
    },
)
async def send_message(
    chat_id: UUID,
    req: Annotated[MessageCreate, Form(media_type="multipart/form-data")],
    usecase: Annotated[Chats, Depends(dependencies.chats_uc)],
) -> Response:
    await usecase.send(chat_id, req)
    return Response(status_code=204)


@chats_router.get(
    "/{chat_id}/messages",
    operation_id="getChatMessages",
    response_model=ChatMessagesResponse,
    response_model_exclude_none=True,
)
async def get_chat_messages(
    chat_id: UUID,
    request: Request,
    usecase: Annotated[Chats, Depends(dependencies.chats_uc)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int | None, Query(ge=0)] = None,
) -> ChatMessagesResponse:
    return await usecase.messages(
        chat_id,
        offset=offset,
        limit=limit,
        media_url=lambda media_id: str(request.url_for("get_media_by_id", media_id=str(media_id))),
    )
