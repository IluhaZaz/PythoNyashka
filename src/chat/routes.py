from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response

from src.chat import dependencies
from src.chat.domain.schemas import (
    ChatCreate,
    ChatCreatedResponse,
    ChatMessagesResponse,
    ChatsResponse,
    Error,
    MessageCreate,
)
from src.chat.usecase import (
    ChatNotFoundError,
    CreateChat,
    GetChatMessages,
    GetChats,
    ProfileNotFoundError,
    SendMessage,
)

router = APIRouter(
    prefix="/chats",
    tags=["Chats"],
    responses={404: {"model": Error, "description": "Entity not found"}},
)


@router.post("", operation_id="createChat", response_model=ChatCreatedResponse)
async def create_chat(
    req: ChatCreate,
    usecase: Annotated[CreateChat, Depends(dependencies.create_chat_uc)],
) -> ChatCreatedResponse | Response:
    try:
        chat_id = await usecase.execute(req)
    except ProfileNotFoundError:
        return JSONResponse(status_code=404, content={"error": "Profile not found"})
    return ChatCreatedResponse(id=UUID(chat_id))


@router.get("", operation_id="getChats", response_model=ChatsResponse)
async def get_chats(
    profile_id: Annotated[UUID, Query(
        description="Acting profile ID set by the BFF from the validated JWT.",
    )],
    usecase: Annotated[GetChats, Depends(dependencies.get_chats_uc)],
) -> ChatsResponse | Response:
    try:
        return await usecase.execute(str(profile_id))
    except ProfileNotFoundError:
        return JSONResponse(status_code=404, content={"error": "Profile not found"})


@router.post(
    "/{chat_id}/message",
    operation_id="sendMessage",
    status_code=204,
    response_class=Response,
)
async def send_message(
    chat_id: UUID,
    req: MessageCreate,
    usecase: Annotated[SendMessage, Depends(dependencies.send_message_uc)],
) -> Response:
    try:
        await usecase.execute(str(chat_id), req)
    except ProfileNotFoundError:
        return JSONResponse(status_code=404, content={"error": "Profile not found"})
    except ChatNotFoundError:
        return JSONResponse(status_code=404, content={"error": "Chat not found"})
    return Response(status_code=204)


@router.get(
    "/{chat_id}/messages",
    operation_id="getChatMessages",
    response_model=ChatMessagesResponse,
)
async def get_chat_messages(
    chat_id: UUID,
    usecase: Annotated[GetChatMessages, Depends(dependencies.get_chat_messages_uc)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int | None, Query(ge=0)] = None,
) -> ChatMessagesResponse | Response:
    try:
        messages = await usecase.execute(str(chat_id), limit=limit, offset=offset)
    except ChatNotFoundError:
        return JSONResponse(status_code=404, content={"error": "Chat not found"})
    return ChatMessagesResponse(chat_id=chat_id, messages=messages)
