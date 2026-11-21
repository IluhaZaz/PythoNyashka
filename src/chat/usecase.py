from uuid import UUID

from src.chat.domain.schemas import (
    ChatCreate,
    ChatMembership,
    ChatsResponse,
    MessageCreate,
    MessageGet,
)
from src.chat.infrastructure.storage.postgresql.repository import ChatRepository


class ChatNotFoundError(Exception):
    pass


class ProfileNotFoundError(Exception):
    pass


class CreateChat:
    def __init__(self, repository: ChatRepository) -> None:
        self.repository = repository

    async def execute(self, req: ChatCreate) -> str:
        profile_ids = {str(profile_id) for profile_id in req.contact_ids}
        if not await self.repository.profiles_exist(profile_ids):
            raise ProfileNotFoundError()
        return await self.repository.create(profile_ids)


class GetChats:
    def __init__(self, repository: ChatRepository) -> None:
        self.repository = repository

    async def execute(self, profile_id: str) -> ChatsResponse:
        if not await self.repository.profiles_exist({profile_id}):
            raise ProfileNotFoundError()

        participants_by_chat = await self.repository.get_by_profile(profile_id)
        chats = [
            ChatMembership(id=UUID(chat_id), participant_ids=[UUID(member) for member in members])
            for chat_id, members in participants_by_chat.items()
        ]
        return ChatsResponse(chat_ids=[chat.id for chat in chats], chats=chats)


class SendMessage:
    def __init__(self, repository: ChatRepository) -> None:
        self.repository = repository

    async def execute(self, chat_id: str, req: MessageCreate) -> None:
        if req.sender_id is None:
            raise ProfileNotFoundError()
        sender_id = str(req.sender_id)
        if not await self.repository.has_member(chat_id, sender_id):
            raise ChatNotFoundError()
        await self.repository.add_message(
            chat_id, sender_id, req.text, [str(media_id) for media_id in req.media],
        )


class GetChatMessages:
    def __init__(self, repository: ChatRepository) -> None:
        self.repository = repository

    async def execute(
        self, chat_id: str, limit: int | None, offset: int,
    ) -> list[MessageGet]:
        if not await self.repository.chat_exists(chat_id):
            raise ChatNotFoundError()
        return await self.repository.get_messages(chat_id, limit=limit, offset=offset)
