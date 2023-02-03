from fastapi import APIRouter, Depends, Query
from dependency_injector.wiring import inject, Provide

from app.core.containers import Container
from app.api.deps import commit_and_close_session

from app.schemas.messengers import MessengerIn, MessengerOut


router = APIRouter()


@router.get("/", response_model=list[MessengerOut])
@inject
@commit_and_close_session
async def all_messengers(
        messenger_service = Depends(Provide[Container.messenger_service])):
    """Возвращает все мессенджеры, активные и неактивные."""
    return await messenger_service.all_messengers()


@router.post("/create", response_model=MessengerOut)
@inject
@commit_and_close_session
async def create_messenger(
        data_in: MessengerIn,
        messenger_type = Query("telegram", enum=["telegram", "whats_app"]),
        messenger_service = Depends(Provide[Container.messenger_service])):
    return await messenger_service.create_messenger(data_in=data_in, messenger_type=messenger_type)


@router.delete("/delete_messenger")
@inject
@commit_and_close_session
async def delete_messenger(
        messenger_id: str,
        messenger_service = Depends(Provide[Container.messenger_service])):
    """Удаляет мессенджер."""
    return await messenger_service.delete_messenger(messenger_id=messenger_id)

