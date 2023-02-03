import datetime
from uuid import UUID
from pydantic import BaseModel


class MessengerIn(BaseModel):
    phone: str
    api_token: str
    api_id: str

    class Config:
        orm_mode=True


class MessengerOut(BaseModel):
    id: UUID
    phone: str
    is_active: bool
    type: str
    created_at: datetime.date
    class Config:
        orm_mode=True
