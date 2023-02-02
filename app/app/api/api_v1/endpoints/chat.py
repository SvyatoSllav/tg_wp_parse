from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from app.core.containers import Container
from app.api.deps import commit_and_close_session

from app.schemas.chat import ChatIn, MessageIn


router = APIRouter()


@router.get("/all_saved_chats")
@inject
@commit_and_close_session
async def all_saved_chats(chat_service = Depends(Provide[Container.chat_service])):
    return await chat_service.all_chats()


@router.get("/my_telegram_chats")
@inject
@commit_and_close_session
async def my_telegram_chats(messenger_id: str, chat_service = Depends(Provide[Container.chat_service])):
    return await chat_service.my_telegram_chats(messenger_id)


@router.post("/create_chat")
@inject
@commit_and_close_session
async def create_chat(
        chat_in: ChatIn,
        chat_service = Depends(Provide[Container.chat_service])):
    return await chat_service.create_chat(chat_in=chat_in)


@router.post("/tg_messages")
@inject
@commit_and_close_session
async def tg_messages(data_in: MessageIn, chat_service = Depends(Provide[Container.chat_service])):
    return await chat_service.tg_messages(data_in=data_in)
