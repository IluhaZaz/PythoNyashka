from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ChatCreate(BaseModel):
    contact_ids: list[UUID] = Field(alias="contactIds")


class MessageCreate(BaseModel):
    sender_id: UUID | None = Field(default=None, alias="senderId")
    text: str
    media: list[UUID]


class MessageGet(BaseModel):
    id: UUID
    sender_id: UUID = Field(serialization_alias="senderId")
    text: str
    media: list[UUID]
    sent_at: datetime = Field(serialization_alias="sentAt")

    model_config = {"from_attributes": True}


class ChatCreatedResponse(BaseModel):
    id: UUID


class ChatsResponse(BaseModel):
    chat_ids: list[UUID] = Field(serialization_alias="chatIds")


class ChatMessagesResponse(BaseModel):
    chat_id: UUID = Field(serialization_alias="chatId")
    messages: list[MessageGet]


class Error(BaseModel):
    error: str
