import requests
import base64
import datetime
from pathlib import Path

from telethon import TelegramClient
from telethon.types import ChatPhotoEmpty, User, MessageMediaPhoto, Channel, Chat
from telethon.tl.functions.messages import GetHistoryRequest

from app.repository.chat import RepositoryChat
from app.repository.messenger import RepositoryMessenger
from app.repository.message import RepositoryMessage, Message

from app.schemas.chat import ChatIn, MessageIn, WPChatIn

from fastapi.responses import JSONResponse
from fastapi_pagination.ext.sqlalchemy import paginate


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

    @staticmethod
    def decode_and_save_wp_img(image_file_path: Path, image: bytes):
        bytes_img_base64 = bytes(image, "utf-8")
        with open(image_file_path, "wb") as fh:
            fh.write(base64.decodebytes(bytes_img_base64))

    async def all_chats(self):
        return self._repository_chat.list()

    async def my_whatsapp_chats(self, messenger_id: str):
        messenger = self._repository_messenger.get(id=messenger_id)
        api_id, api_token = messenger.api_id, messenger.api_token

        headers = {"Authorization": api_token}
        url = f"https://wappi.pro/api/sync/chats/get?profile_id={api_id}"
        chats = requests.get(url=url, headers=headers).json()
        return chats

    async def create_whatsapp_chat(self, chat_in: WPChatIn):
        messenger = self._repository_messenger.get(id=chat_in.messenger_id)
        api_id, api_token = messenger.api_id, messenger.api_token
        url = "https://wappi.pro/api/sync/contact/get"

        headers = {"Authorization": api_token}
        params = {"profile_id": api_id, "recipient": chat_in.chat_id}
        chat = requests.get(url, headers=headers, params=params).json()
        contact = chat.get("contact")
        names = [contact.get("pushname"), contact.get("name"), contact.get("shortName"), contact.get("businessName")]
        name = next((name for name in names if name not in (None, "")), "Unknow")

        chat = self._repository_chat.get(chat_id=contact.get("id"))
        if chat:
            return "Чат уже создан"

        obj_in = {
            "chat_id": contact.get("id"),
            "chat_name": name,
            "messenger_id": chat_in.messenger_id
        }
        image = contact.get("picture")
        if image:
            self.create__image_dir(name)
            image_file_path = Path().resolve() / "image" / name / "profile_img.jpg"
            img_path_to_repr = [f"/image/{name}/profile_img.jpg"]
            self.decode_and_save_wp_img(image_file_path=image_file_path, image=image)

            obj_in["chat_avatars_img_paths"] = img_path_to_repr

        return self._repository_chat.create(obj_in=obj_in, commit=True)

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
                dialog_type = "user/bot"
            elif dialog.is_group:
                dialog_type = "group"
            else:
                dialog_type = "channel"

            representation.append({
                "dialog_title": dialog.title,
                "dialog_id": dialog.id,
                "dialog_type": dialog_type
            })
        await client.disconnect()
        return representation

    async def create_tg_chat(self, chat_in: ChatIn):
        messenger = self._repository_messenger.get(id=chat_in.messenger_id)
        phone, phone_hash, api_id, api_hash = messenger.phone, messenger.phone_hash, messenger.api_id, messenger.api_token 
        session_name = self.session_name(phone=phone, api_id=api_id)

        client = TelegramClient(session_name, api_id, api_hash)
        await client.connect()
        try:
            chat = await client.get_entity(int(chat_in.chat_id))

            if self._repository_chat.get(chat_id=str(chat.id)):
                return JSONResponse(content={"error_msg": "Данная группа уже существует"}, status_code=403)

            if type(chat) is User:
                chat_name = chat.username
            else:
                chat_name = chat.title

            obj_in = {
                "chat_id": str(chat.id),
                "chat_name": chat_name,
                "messenger": messenger
            }

            self.create__image_dir(image_dir_name=chat_name)
            if type(chat.photo) is not ChatPhotoEmpty:
                image_file_path = Path().resolve() / "image" / chat_name
                await client.download_profile_photo(chat, file=f"{image_file_path}/{chat_name}_{chat.id}")
                chat_photo_path = [f"/image/{chat_name}/{chat_name}_{chat.id}.jpg"]
                obj_in["chat_avatars_img_paths"] = chat_photo_path

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
        if type(message.media) == MessageMediaPhoto:
            chat_image_dir.mkdir()
            await client.download_media(message.media, file=f"{chat_image_dir}/{chat_name}_{message.id}")
            photos = chat_image_dir.iterdir()
            return [f"/image/{chat_name}/{chat_name}_{message.id}/{photo.name}" for photo in photos]
        return []

    async def tg_messages(self, data_in: MessageIn):
        messenger = self._repository_messenger.get(id=data_in.messenger_id)
        chat = self._repository_chat.get(id=data_in.chat_id)
        phone, phone_hash, api_id, api_hash = messenger.phone, messenger.phone_hash, messenger.api_id, messenger.api_token 
        session_name = self.session_name(phone=phone, api_id=api_id)

        client = TelegramClient(session_name, api_id, api_hash)
        await client.connect()
        try:
            tg_chat = await client.get_entity(int(chat.chat_id))
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
                if type(tg_chat) not in (Chat, Channel):
                    author_name = tg_chat.username
                else:
                    author_name = tg_chat.title
                obj_in = {
                    "message_id": message.id,
                    "text": message.message,
                    "author_id": message.id,
                    "author_name": author_name,
                    "sent_at": message.date,
                    "chat_id": chat.id,
                }
                if message.media:
                    message_media_paths = await self._save_tg_message_media(client=client, message=message, chat_name=author_name)
                    obj_in["message_media_paths"] = message_media_paths

                self._repository_message.create(obj_in=obj_in, commit=True)
                self._repository_chat.update(db_obj=chat, obj_in={"last_message_id": str(message.id)})
            await client.disconnect()
            messages = self._repository_message.filter_message(start_sent_at=data_in.start_sent_at, end_sent_at=data_in.end_sent_at)
            return paginate(messages)
        except Exception as e:
            print(str(e))
            await client.disconnect()

    async def messages(self, start_sent_at: datetime.date, end_sent_at: datetime.date):
        chats = self._repository_chat.tg_chats()
        for chat in chats:
            chat = chat[0]
            data_in = {
                "messenger_id": str(chat.messenger_id),
                "chat_id": str(chat.id)
            }
            await self.tg_messages(data_in=MessageIn.parse_obj(data_in))
        messages = self._repository_message.filter_message(start_sent_at=start_sent_at, end_sent_at=end_sent_at)
        return paginate(messages)

    async def delete_message(self, end_sent_at: datetime.date):
        old_messages = self._repository_message.list(Message.sent_at <= end_sent_at)
        for message in old_messages:
            self._repository_message.delete(db_obj=message, commit=True)

    async def delete_chat(self, chat_id: str):
        chat = self._repository_chat.get(id=chat_id)
        self._repository_chat.delete(db_obj=chat)

    async def webhook(self, request):
        res = await request.json()
        message = res.get("messages")[0]
        message_id = message.get("id")
        author_id =  message.get("from")
        author_name = message.get("senderName")
        sent_at = message.get("timestamp")

        chat = self._repository_chat.get(chat_id=author_id)
        if not chat:
            return "Чат не отслеживается"

        if message.get("type") == "chat":
            obj_in = {
                "message_id": message_id,
                "text": message.get("body"),
                "author_id": author_id,
                "author_name": author_name,
                "sent_at": sent_at,
                "chat_id": chat.id
            }
        elif message.get("type") == "image":
            obj_in = {
                "message_id": message_id,
                "text": message.get("caption"),
                "author_id": author_id,
                "author_name": author_name,
                "sent_at": sent_at,
                "chat_id": chat.id
            }
            self.create__image_dir(author_name)
            image = res.get("messages")[0].get("body")
            image_file_path = Path().resolve() / "image" / author_name / f"{message_id[:11]}.jpg"
            image_path_to_repr = [f"/image/{author_name}/{message_id[:11]}.jpg"]
            self.decode_and_save_wp_img(image_file_path=image_file_path, image=image)

            obj_in["message_media_paths"] = image_path_to_repr

        return self._repository_message.create(obj_in=obj_in, commit=True)
