import datetime

from pydantic import BaseModel
from typing import Optional, Union

from uuid import UUID



class ChatIn(BaseModel):
    messenger_id: str
    chat_id: str

    class Config:
        orm_mode=True


class WPChatIn(BaseModel):
    messenger_id: str
    chat_id: str

    class Config:
        orm_mode=True


class MessageIn(BaseModel):
    messenger_id: str
    chat_id: str
    limit: int = 500
    start_sent_at: Optional[datetime.date] = "2022-01-01"
    end_sent_at: Optional[datetime.date] = "2024-02-14"

    class Config:
        orm_mode=True


class MessageOut(BaseModel):
    id: UUID
    chat_id: UUID
    author_id: str
    message_id: str
    author_name: str
    text: Optional[str]
    message_media_paths: list[str]
    messenger_type: str
    sent_at: datetime.date
    created_at: datetime.date

    class Config:
        orm_mode = True


class ChatOut(BaseModel):
    id: UUID
    chat_id: str
    chat_name: str
    last_message_id: int
    created_at: datetime.date
    chat_avatars_img_paths: list[str]
    messenger_id: UUID
    messenger_type: str

    class Config:
        orm_mode=True


class ChatName(BaseModel):
    FirstName: str
    FullName: str
    PushName: str


class Chat(BaseModel):
    id: str
    name: Optional[str]
    contact: Optional[ChatName]
    isGroup: Optional[bool] = False


class WPChatsOut(BaseModel):
    dialogs: list[Chat]
