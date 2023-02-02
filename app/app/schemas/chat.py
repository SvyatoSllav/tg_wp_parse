from pydantic import BaseModel
from typing import Optional
import datetime


class ChatIn(BaseModel):
    messenger_id: str
    chat_id: int

    class Config:
        orm_mode=True


class MessageIn(BaseModel):
    messenger_id: str
    chat_id: str
    limit: int = 1000000000
    start_sent_at: Optional[datetime.date] = "2022-01-01"
    end_sent_at: Optional[datetime.date] = "2024-02-14"

    class Config:
        orm_mode=True
