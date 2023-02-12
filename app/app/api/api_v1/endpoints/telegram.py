from fastapi import APIRouter, Depends, Query
from dependency_injector.wiring import inject, Provide

from app.core.containers import Container
from app.api.deps import commit_and_close_session

from app.schemas.messengers import MessengerIn


router = APIRouter()


@router.get("/receive_confirm_code")
@inject
@commit_and_close_session
async def get_confirmation_code(
        tg_messenger_id: str,
        telegram_service = Depends(Provide[Container.telegram_service])):
    """Отправляет в личку мессенджера код подтверждения."""
    return await telegram_service.receive_code(tg_messenger_id=tg_messenger_id)


@router.post("/authorize_messenger")
@inject
@commit_and_close_session
async def authorize_messenger(
        tg_messenger_id: str,
        code: str,
        telegram_service = Depends(Provide[Container.telegram_service])):
    """Отправляет в личку мессенджера код подтверждения."""
    return await telegram_service.authorize_messenger(tg_messenger_id=tg_messenger_id, code=code)


# @router.post("/me")
# @inject
# @commit_and_close_session
# async def me(
#         tg_messenger_id: str,
#         telegram_service = Depends(Provide[Container.telegram_service])):
#     """Отправляет в личку мессенджера код подтверждения."""
#     return await telegram_service.me(tg_messenger_id=tg_messenger_id)
