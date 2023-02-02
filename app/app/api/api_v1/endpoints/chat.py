from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from app.core.containers import Container
from app.api.deps import commit_and_close_session

from app.schemas.chat import GroupIn


router = APIRouter()


@router.get("/all_chats")
@inject
@commit_and_close_session
async def all_chats(chat_service = Depends(Provide[Container.chat_service])):
    return await chat_service.all_chats()


@router.post("/create_chat")
@inject
@commit_and_close_session
async def create_chat(
        group_in: GroupIn,
        chat_service = Depends(Provide[Container.chat_service])):
    return await chat_service.create_chat(group_in=group_in)
