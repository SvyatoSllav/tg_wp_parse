from pydantic import BaseModel


class MessengerIn(BaseModel):
    phone: str
    api_token: str
    api_id: str

    class Config:
        orm_mode=True
