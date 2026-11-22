from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.chat import usecase
from src.chat.infrastructure.storage.postgresql.repository import ChatRepository
from src.infrastructure.storage.postgresql.core import DBSession


async def get_session() -> AsyncIterator[AsyncSession]:
    async with DBSession() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


def get_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ChatRepository:
    return ChatRepository(session)


def create_chat_uc(
    repo: Annotated[ChatRepository, Depends(get_repository)],
) -> usecase.CreateChat:
    return usecase.CreateChat(repository=repo)


def get_chats_uc(
    repo: Annotated[ChatRepository, Depends(get_repository)],
) -> usecase.GetChats:
    return usecase.GetChats(repository=repo)


def send_message_uc(
    repo: Annotated[ChatRepository, Depends(get_repository)],
) -> usecase.SendMessage:
    return usecase.SendMessage(repository=repo)


def get_chat_messages_uc(
    repo: Annotated[ChatRepository, Depends(get_repository)],
) -> usecase.GetChatMessages:
    return usecase.GetChatMessages(repository=repo)


def get_attachment_access_uc(
    repo: Annotated[ChatRepository, Depends(get_repository)],
) -> usecase.GetAttachmentAccess:
    return usecase.GetAttachmentAccess(repository=repo)
