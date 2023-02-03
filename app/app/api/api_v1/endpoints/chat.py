import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi_pagination import Page
from dependency_injector.wiring import inject, Provide

from app.core.containers import Container
from app.api.deps import commit_and_close_session

from app.schemas.chat import ChatIn, MessageIn, MessageOut, ChatOut, WPChatsOut, WPChatIn


router = APIRouter()


@router.get("/all_saved_chats", response_model=list[ChatOut])
@inject
@commit_and_close_session
async def all_saved_chats(chat_service = Depends(Provide[Container.chat_service])):
    return await chat_service.all_chats()


@router.get("/my_whatsapp_chats", response_model=WPChatsOut)
@inject
@commit_and_close_session
async def my_whatsapp_chats(messenger_id: str, chat_service = Depends(Provide[Container.chat_service])):
    return await chat_service.my_whatsapp_chats(messenger_id)


@router.post("/create_whatsapp_chat")
@inject
@commit_and_close_session
async def create_whatsapp_chat(
        chat_in: WPChatIn,
        chat_service = Depends(Provide[Container.chat_service])):
    return await chat_service.create_whatsapp_chat(chat_in=chat_in)


@router.get("/my_telegram_chats")
@inject
@commit_and_close_session
async def my_telegram_chats(messenger_id: str, chat_service = Depends(Provide[Container.chat_service])):
    return await chat_service.my_telegram_chats(messenger_id)



@router.post("/create_tg_chat", response_model=ChatOut)
@inject
@commit_and_close_session
async def create_tg_chat(
        chat_in: ChatIn,
        chat_service = Depends(Provide[Container.chat_service])):
    return await chat_service.create_tg_chat(chat_in=chat_in)


# @router.post("/tg_messages", response_model=Page[MessageOut])
# @inject
# @commit_and_close_session
# async def tg_messages(data_in: MessageIn, chat_service = Depends(Provide[Container.chat_service])):
#     return await chat_service.tg_messages(data_in=data_in)


@router.post("/messages", response_model=Page[MessageOut])
@inject
@commit_and_close_session
async def messages(
    start_sent_at: Optional[datetime.date] = "2022-01-01",
    end_sent_at: Optional[datetime.date] = "2024-02-14",
    chat_service = Depends(Provide[Container.chat_service])):
    return await chat_service.messages(start_sent_at, end_sent_at)


@router.delete("/delete_message",)
@inject
@commit_and_close_session
async def delete_message(end_sent_at: datetime.date = "2022-01-01", chat_service = Depends(Provide[Container.chat_service])):
    return await chat_service.delete_message(end_sent_at)


@router.delete("/delete_chat",)
@inject
@commit_and_close_session
async def delete_chat(chat_id: str, chat_service = Depends(Provide[Container.chat_service])):
    return await chat_service.delete_chat(chat_id=chat_id)



@router.post("/webhook",)
@inject
@commit_and_close_session
async def webhook(request: Request, chat_service = Depends(Provide[Container.chat_service])):
    return await chat_service.webhook(request)
