from fastapi import APIRouter, Depends
from app.api.deps import create_session

from app.api.api_v1.endpoints import messengers, telegram, device


api_router = APIRouter()
api_router.include_router(messengers.router, prefix="/messengers", tags=['messengers'])
api_router.include_router(telegram.router, prefix="/telegram", tags=['telegram'])
api_router.include_router(device.router, prefix="/device", tags=['device'])
