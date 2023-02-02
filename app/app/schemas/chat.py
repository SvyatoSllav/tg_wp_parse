from pydantic import BaseModel


class GroupIn(BaseModel):
    messenger_id: str
    group_url: str

    class Config:
        orm_mode=True
