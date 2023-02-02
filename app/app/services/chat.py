from pathlib import Path

from telethon import TelegramClient
from telethon.types import ChatPhotoEmpty

from app.repository.chat import RepositoryChat
from app.repository.messenger import RepositoryMessenger

from app.schemas.chat import GroupIn

from fastapi.responses import JSONResponse


class ChatService:

    def __init__(
            self,
            repository_chat: RepositoryChat,
            repository_messenger: RepositoryMessenger) -> None:
        self._repository_chat = repository_chat
        self._repository_messenger = repository_messenger

    @staticmethod
    def session_name(phone: str, api_id: str):
        return f"{phone}_{api_id}"

    @staticmethod
    def create_group_image_dir(channel):
        image_dir = Path().resolve() / "image" / channel.title
        if not (image_dir / channel.title).exists():
            image_dir.mkdir(parents=True, exist_ok=True)
        return f"image/{channel.title}"

    async def all_chats(self):
        return self._repository_chat.list()

    async def create_chat(self, group_in: GroupIn):
        messenger = self._repository_messenger.get(id=group_in.messenger_id)
        phone, phone_hash, api_id, api_hash = messenger.phone, messenger.phone_hash, messenger.api_id, messenger.api_token 
        session_name = self.session_name(phone=phone, api_id=api_id)

        client = TelegramClient(session_name, api_id, api_hash)
        await client.connect()

        channel = await client.get_entity(group_in.group_url)

        if self._repository_chat.get(chat_id=str(channel.id)):
            return JSONResponse(content={"error_msg": "Данная группа уже существует"}, status_code=403)

        obj_in = {
            "chat_id": channel.id,
            "chat_name": channel.title,
            "messenger": messenger
        }

        channel_image_dir = self.create_group_image_dir(channel=channel)
        if type(channel.photo) is not ChatPhotoEmpty:
            await client.download_profile_photo(channel, file=f"{channel_image_dir}/{channel.title}_{channel.id}")
            channel_photo_path = f"{channel_image_dir}/{channel.title}_{channel.id}.jpg"
            obj_in["chat_avatars_img_paths"] = [channel_photo_path]

        await client.disconnect()
        return self._repository_chat.create(
            obj_in=obj_in, commit=True
        )
