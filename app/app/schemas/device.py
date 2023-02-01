from pydantic import BaseModel


class DeviceIn(BaseModel):
    name: str

    class Config:
        orm_mode=True
