from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.chat.domain.schemas import MessageGet
from src.chat.infrastructure.storage.postgresql.models import Chat, ChatMember, Message
from src.profile.infrastructure.storage.postgresql.models import Profile


class ChatRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def profiles_exist(self, profile_ids: set[str]) -> bool:
        query = select(Profile.id).where(Profile.id.in_(profile_ids))
        result = await self.session.scalars(query)
        return set(result) == profile_ids

    async def create(self, profile_ids: set[str]) -> str:
        chat = Chat()
        self.session.add(chat)
        await self.session.flush()
        self.session.add_all([
            ChatMember(chat_id=chat.id, profile_id=profile_id)
            for profile_id in profile_ids
        ])
        await self.session.commit()
        return str(chat.id)

    async def get_by_profile(self, profile_id: str) -> list[str]:
        query = (
            select(ChatMember.chat_id)
            .where(ChatMember.profile_id == profile_id)
            .order_by(ChatMember.chat_id)
        )
        return list(await self.session.scalars(query))

    async def chat_exists(self, chat_id: str) -> bool:
        return await self.session.get(Chat, chat_id) is not None

    async def has_member(self, chat_id: str, profile_id: str) -> bool:
        return await self.session.get(ChatMember, (chat_id, profile_id)) is not None

    async def add_message(
        self, chat_id: str, sender_id: str, text: str, media: list[str],
    ) -> None:
        message = Message(chat_id=chat_id, sender_id=sender_id, text=text, media=media)
        self.session.add(message)
        await self.session.commit()

    async def get_messages(
        self, chat_id: str, limit: int | None, offset: int,
    ) -> list[MessageGet]:
        query = (
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.sent_at.desc(), Message.id.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.scalars(query)
        return [MessageGet.model_validate(message) for message in result]
