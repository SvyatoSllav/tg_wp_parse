import datetime
from pydantic import BaseModel


class DeviceIn(BaseModel):
    name: str
    device_id: str

    class Config:
        orm_mode=True


class DeviceOut(BaseModel):
    name: str
    device_id: str
    created_at: datetime.date

    class Config:
        orm_mode=True
