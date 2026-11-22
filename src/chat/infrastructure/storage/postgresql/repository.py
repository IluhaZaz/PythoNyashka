from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.chat.domain.schemas import MessageGet
from src.chat.infrastructure.storage.postgresql.models import (
    Chat,
    ChatMember,
    Message,
    MessageAttachment,
)
from src.profile.infrastructure.storage.postgresql.models import Profile


class ChatRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def profiles_exist(self, profile_ids: set[str]) -> bool:
        query = select(Profile.id).where(Profile.id.in_(profile_ids))
        result = await self.session.scalars(query)
        return set(result) == profile_ids

    async def create(self, profile_ids: set[str]) -> str:
        if len(profile_ids) == 2:
            existing_id = await self._find_direct_chat(profile_ids)
            if existing_id is not None:
                return existing_id

        chat = Chat()
        self.session.add(chat)
        await self.session.flush()
        self.session.add_all([
            ChatMember(chat_id=chat.id, profile_id=profile_id)
            for profile_id in profile_ids
        ])
        await self.session.commit()
        return str(chat.id)

    async def _find_direct_chat(self, profile_ids: set[str]) -> str | None:
        first_profile_id = min(profile_ids)
        # Both participants lock the same profile before looking up or creating the chat.
        await self.session.scalar(
            select(Profile.id).where(Profile.id == first_profile_id).with_for_update()
        )
        candidate_ids = select(ChatMember.chat_id).where(ChatMember.profile_id == first_profile_id)
        query = (
            select(ChatMember.chat_id)
            .where(ChatMember.chat_id.in_(candidate_ids))
            .group_by(ChatMember.chat_id)
            .having(
                func.count() == 2,
                func.count().filter(ChatMember.profile_id.in_(profile_ids)) == 2,
            )
            .order_by(ChatMember.chat_id)
            .limit(1)
        )
        return await self.session.scalar(query)

    async def get_by_profile(self, profile_id: str) -> dict[str, list[str]]:
        owned_chat_ids = select(ChatMember.chat_id).where(ChatMember.profile_id == profile_id)
        query = (
            select(ChatMember.chat_id, ChatMember.profile_id)
            .where(ChatMember.chat_id.in_(owned_chat_ids))
            .order_by(ChatMember.chat_id, ChatMember.profile_id)
        )
        participants_by_chat: dict[str, list[str]] = {}
        for chat_id, participant_id in await self.session.execute(query):
            participants_by_chat.setdefault(chat_id, []).append(participant_id)
        return participants_by_chat

    async def chat_exists(self, chat_id: str) -> bool:
        return await self.session.get(Chat, chat_id) is not None

    async def has_member(self, chat_id: str, profile_id: str) -> bool:
        return await self.session.get(ChatMember, (chat_id, profile_id)) is not None

    async def add_message(
        self, chat_id: str, sender_id: str, text: str, media: list[str],
    ) -> None:
        message = Message(
            chat_id=chat_id,
            sender_id=sender_id,
            text=text,
            attachments=[
                MessageAttachment(media_id=media_id, position=position)
                for position, media_id in enumerate(media)
            ],
        )
        self.session.add(message)
        await self.session.commit()

    async def get_messages(
        self, chat_id: str, limit: int | None, offset: int,
    ) -> list[MessageGet]:
        query = (
            select(Message)
            .options(selectinload(Message.attachments))
            .where(Message.chat_id == chat_id)
            .order_by(Message.sent_at.desc(), Message.id.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.scalars(query)
        return [MessageGet.model_validate(message) for message in result]

    async def get_attachment_access(self, media_id: str, profile_id: str) -> bool | None:
        query = (
            select(func.bool_or(ChatMember.profile_id.is_not(None)))
            .select_from(MessageAttachment)
            .join(Message, Message.id == MessageAttachment.message_id)
            .outerjoin(
                ChatMember,
                and_(ChatMember.chat_id == Message.chat_id, ChatMember.profile_id == profile_id),
            )
            .where(MessageAttachment.media_id == media_id)
        )
        access: bool | None = await self.session.scalar(query)
        return access
