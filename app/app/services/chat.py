from pathlib import Path

from telethon import TelegramClient
from telethon.types import ChatPhotoEmpty, User, MessageMediaPhoto
from telethon.tl.functions.messages import GetHistoryRequest

from app.repository.chat import RepositoryChat
from app.repository.messenger import RepositoryMessenger
from app.repository.message import RepositoryMessage

from app.schemas.chat import ChatIn, MessageIn

from fastapi.responses import JSONResponse


class ChatService:

    def __init__(
            self,
            repository_chat: RepositoryChat,
            repository_messenger: RepositoryMessenger,
            repository_message: RepositoryMessage) -> None:
        self._repository_chat = repository_chat
        self._repository_messenger = repository_messenger
        self._repository_message = repository_message

    @staticmethod
    def session_name(phone: str, api_id: str):
        return f"{phone}_{api_id}"

    @staticmethod
    def create__image_dir(image_dir_name: str):
        image_dir = Path().resolve() / "image" / image_dir_name
        if not (image_dir / image_dir_name).exists():
            image_dir.mkdir(parents=True, exist_ok=True)
        return f"/image/{image_dir_name}"

    async def all_chats(self):
        return self._repository_chat.list()

    async def my_telegram_chats(self, messenger_id: str):
        messenger = self._repository_messenger.get(id=messenger_id)
        phone, phone_hash, api_id, api_hash = messenger.phone, messenger.phone_hash, messenger.api_id, messenger.api_token 
        session_name = self.session_name(phone=phone, api_id=api_id)

        client = TelegramClient(session_name, api_id, api_hash)
        await client.connect()
        all_dialogs = await client.get_dialogs()
        representation = []
        for dialog in all_dialogs:
            if dialog.is_user:
                dialog_type = "user"
            elif dialog.is_group:
                dialog_type = "group"
            elif dialog.is_chat:
                dialog_type = "chat"
            else:
                dialog_type = "Unknow"

            representation.append({
                "dialog_title": dialog.title,
                "dialog_id": dialog.id,
                "dialog_type": dialog_type
            })
        await client.disconnect()
        return representation

    async def create_chat(self, chat_in: ChatIn):
        messenger = self._repository_messenger.get(id=chat_in.messenger_id)
        phone, phone_hash, api_id, api_hash = messenger.phone, messenger.phone_hash, messenger.api_id, messenger.api_token 
        session_name = self.session_name(phone=phone, api_id=api_id)

        client = TelegramClient(session_name, api_id, api_hash)
        await client.connect()
        try:
            chat = await client.get_entity(chat_in.chat_id)

            if self._repository_chat.get(chat_id=str(chat.id)):
                return JSONResponse(content={"error_msg": "Данная группа уже существует"}, status_code=403)

            if type(chat) is User:
                chat_name = chat.username
            else:
                chat_name = chat.title

            obj_in = {
                "chat_id": chat.id,
                "chat_name": chat_name,
                "messenger": messenger
            }

            chat_image_dir = self.create__image_dir(image_dir_name=chat_name)
            if type(chat.photo) is not ChatPhotoEmpty:
                await client.download_profile_photo(chat, file=f"{chat_image_dir}/{chat_name}_{chat.id}")
                chat_photo_path = f"{chat_image_dir}/{chat_name}_{chat.id}.jpg"
                obj_in["chat_avatars_img_paths"] = [chat_photo_path]

            await client.disconnect()
            return self._repository_chat.create(
                obj_in=obj_in, commit=True
            )
        except Exception as e:
            print(str(e))
            await client.disconnect()

    async def _save_tg_message_media(self, client, message, chat_name) -> list[str]:
        """Загружает все фото из сообщения и возвращает список с относительными путями."""
        chat_image_dir = Path().resolve() / "image" / chat_name / f"{chat_name}_{message.id}"
        chat_image_dir.mkdir()
        if type(message.media) == MessageMediaPhoto:
            await client.download_media(message.media, file=f"{chat_image_dir}/{chat_name}_{message.id}")
        photos = chat_image_dir.iterdir()
        return [f"/image/{chat_name}/{chat_name}_{message.id}/{photo.name}" for photo in photos]

    async def tg_messages(self, data_in: MessageIn):
        messenger = self._repository_messenger.get(id=data_in.messenger_id)
        chat = self._repository_chat.get(id=data_in.chat_id)
        phone, phone_hash, api_id, api_hash = messenger.phone, messenger.phone_hash, messenger.api_id, messenger.api_token 
        session_name = self.session_name(phone=phone, api_id=api_id)

        client = TelegramClient(session_name, api_id, api_hash)
        await client.connect()
        try:
            tg_chat = await client.get_entity(chat.chat_id)
            all_messages = await client(GetHistoryRequest(
                peer=tg_chat,
                limit=data_in.limit,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=int(chat.last_message_id),
                add_offset=0,
                hash=0))
            for message in reversed(all_messages.messages):
                if not message.message and not message.media:
                    continue
                author = await client.get_entity(message.peer_id.user_id)
                obj_in = {
                    "message_id": message.id,
                    "text": message.message,
                    "author_id": message.id,
                    "author_name": author.username,
                    "sent_at": message.date,
                    "chat_id": chat.id,
                }
                if message.media:
                    chat_name = author.username
                    message_media_paths = await self._save_tg_message_media(client=client, message=message, chat_name=chat_name)
                    obj_in["message_media_paths"] = message_media_paths

                self._repository_message.create(obj_in=obj_in, commit=True)
                self._repository_chat.update(db_obj=chat, obj_in={"last_message_id": str(message.id)})
            await client.disconnect()
            return self._repository_message.filter_message(start_sent_at=data_in.start_sent_at, end_sent_at=data_in.end_sent_at)
        except Exception as e:
            print(str(e))
            await client.disconnect()
