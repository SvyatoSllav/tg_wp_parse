import requests
import base64
import datetime
import re
from pathlib import Path

from telethon import TelegramClient, functions
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
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return JSONResponse(content={"error_msg": "Не удалось установить соединение с Wappi"}, status_code=400)

    async def create_whatsapp_chat(self, chat_in: WPChatIn):
        messenger = self._repository_messenger.get(id=chat_in.messenger_id)
        api_id, api_token = messenger.api_id, messenger.api_token
        url = "https://wappi.pro/api/sync/contact/info"
        headers = {"Authorization": api_token}
        params = {"profile_id": api_id, "user_id": chat_in.chat_id}
        chat = requests.get(url, headers=headers, params=params).json()
        if not chat.get("profile").get("is_group"):
            url = "https://wappi.pro/api/sync/contact/get"

            headers = {"Authorization": api_token}
            params = {"profile_id": api_id, "recipient": chat_in.chat_id}
            chat = requests.get(url, headers=headers, params=params).json()
            contact = chat.get("contact")
            if chat.get("status") == "error":
                return JSONResponse(content={"error_msg": chat.get("detail")}, status_code=400)
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
        else:
            image = chat.get("profile").get("picture")
            name = chat.get("profile").get("group").get("Name")
            obj_in = {
                "chat_id": chat.get("profile").get("id"),
                "chat_name": name,
                "messenger_id": chat_in.messenger_id,
            }
            if image:
                self.create__image_dir(name)
                image_file_path = Path().resolve() / "image" / name / "group_img.jpg"
                img_path_to_repr = [f"/image/{name}/group_img.jpg"]
                self.decode_and_save_wp_img(image_file_path=image_file_path, image=image)
                obj_in["chat_avatars_img_paths"] = img_path_to_repr
            
        return self._repository_chat.create(obj_in=obj_in, commit=True)

    async def my_telegram_chats(self, messenger_id: str):
        messenger = self._repository_messenger.get(id=messenger_id)
        phone, phone_hash, api_id, api_hash = messenger.phone, messenger.phone_hash, messenger.api_id, messenger.api_token 
        session_name = self.session_name(phone=phone, api_id=api_id)

        client = TelegramClient(session_name, api_id, api_hash)
        try:
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
        except Exception as e:
            print(str(e))
            return JSONResponse(content={"error_msg": "Не получилось авторизоваться в телеграм. Переавторизуйтесь"}, status_code=403)

    async def create_tg_chat(self, chat_in: ChatIn):
        messenger = self._repository_messenger.get(id=chat_in.messenger_id)
        phone, phone_hash, api_id, api_hash = messenger.phone, messenger.phone_hash, messenger.api_id, messenger.api_token 
        session_name = self.session_name(phone=phone, api_id=api_id)

        try:
            client = TelegramClient(session_name, api_id, api_hash)
            await client.connect()
            chat = await client.get_entity(int(chat_in.chat_id))

            # if self._repository_chat.get(chat_id=str(chat.id)):
            #     return JSONResponse(content={"error_msg": "Данная группа уже существует"}, status_code=403)

            if type(chat) is User:
                chat_name = chat.username
            else:
                chat_name = chat.title

            all_messages = await client(GetHistoryRequest(
                peer=chat,
                limit=1,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0))

            all_messages = reversed(all_messages.messages)
            for message in all_messages:
                last_message_id = message.id

            obj_in = {
                "chat_id": str(chat.id),
                "chat_name": chat_name,
                "messenger": messenger,
                "last_message_id": last_message_id
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
            return JSONResponse(content={"error_msg": "Не получилось авторизоваться в телеграм. Переавторизуйтесь"}, status_code=403)

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
                limit=50,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=int(chat.last_message_id),
                add_offset=0,
                hash=0))
            for message in reversed(all_messages.messages):
                print(message)
                if not message.message and not message.media:
                    continue
                if type(tg_chat) == User:
                    user = await client.get_entity(message.peer_id.user_id)
                else:
                    user = await client.get_entity(message.from_id.user_id)
                message_text = message.message.replace(',', ' ').replace(";", " ").replace("\n", " ")
                message_text_list = [word.lower() for word in message_text.split()]
                username = user.username if user.username else "Unknow"
                phone = user.phone if user.phone else "Unknow"
                obj_in = {
                    "message_id": message.id,
                    "text": message.message,
                    "text_list": message_text_list,
                    "author_id": user.id,
                    "author_name": user.username,
                    "author_link": f"https://t.me/{username}",
                    "author_phone": phone,
                    "sent_at": message.date,
                    "chat_id": chat.id,
                }
                if message.media:
                    message_media_paths = await self._save_tg_message_media(client=client, message=message, chat_name=user.username)
                    obj_in["message_media_paths"] = message_media_paths
                    if not message.message:
                        last_message = self._repository_message.get(message_id=chat.last_message_id)
                        new_message_media = last_message.message_media_paths + message_media_paths
                        self._repository_message.update(db_obj=last_message, obj_in={"message_media_paths": new_message_media})
                        continue
                    self._repository_message.create(obj_in=obj_in, commit=True)
                    self._repository_chat.update(db_obj=chat, obj_in={"last_message_id": str(message.id)})
                    continue

                self._repository_message.create(obj_in=obj_in, commit=True)
                self._repository_chat.update(db_obj=chat, obj_in={"last_message_id": str(message.id)})
            await client.disconnect()
            messages = self._repository_message.filter_message(start_sent_at=data_in.start_sent_at, end_sent_at=data_in.end_sent_at)
            return paginate(messages)
        except Exception as e:
            print(str(e))
            await client.disconnect()
            return str(e)

    async def messages(
            self,
            start_sent_at: datetime.date,
            end_sent_at: datetime.date,
            searchText: str,
            category: list[str]):
        category = [cat.lower() for cat in category.split(", ")]
        searchText = searchText.lower()
        chats = self._repository_chat.tg_chats()
        for chat in chats:
            chat = chat[0]
            data_in = {
                "messenger_id": str(chat.messenger_id),
                "chat_id": str(chat.id)
            }
            await self.tg_messages(data_in=MessageIn.parse_obj(data_in))
        messages = self._repository_message.filter_message(
            start_sent_at=start_sent_at,
            end_sent_at=end_sent_at,
            searchText=searchText,
            category=category)
        return paginate(messages)
    
    async def all_messages(
            self,
            start_sent_at: datetime.date,
            end_sent_at: datetime.date,
            searchText: str,
            category: list[str]):
        category = [cat.lower() for cat in category.split(", ")]
        searchText = searchText.lower()
        chats = self._repository_chat.tg_chats()
        for chat in chats:
            chat = chat[0]
            data_in = {
                "messenger_id": str(chat.messenger_id),
                "chat_id": str(chat.id)
            }
            await self.tg_messages(data_in=MessageIn.parse_obj(data_in))
        messages = self._repository_message.filter_message(
            start_sent_at=start_sent_at,
            end_sent_at=end_sent_at,
            searchText=searchText,
            category=category)
        return messages.all()

    async def delete_message(self, end_sent_at: datetime.date):
        old_messages = self._repository_message.list(Message.sent_at <= end_sent_at)
        for message in old_messages:
            self._repository_message.delete(db_obj=message, commit=True)

    async def delete_chat(self, chat_id: str):
        chat = self._repository_chat.get(id=chat_id)
        self._repository_chat.delete(db_obj=chat)

    async def webhook(self, request):
        try:
            res = await request.json()
            print(res)
        except Exception as e:
            print(str(e))
            return str(e)
        # Логика для проверки сохраненности группы
        if type(res.get("messages")) != list and res.get("messages").get("chat_id"):
            chat = self._repository_chat.get(chat_id=res.get("messages").get("chat_id"))
            if not chat:
                return JSONResponse(content={"error_msg": "Чат не отслеживается"}, status_code=400)

        message = res.get("messages")
        if type(message) == list:
            message = message[0]
            chat_id =  message.get("chatId")
            chat = self._repository_chat.get(chat_id=str(chat_id))
            # Логика для проверки сохраненности юзера
            if not chat:
                return JSONResponse(content={"error_msg": "Чат не отслеживается"}, status_code=400)
            message_id = message.get("id")
            author_name = message.get("senderName")
            sent_at = message.get("timestamp")
            if message.get("type") == "chat":
                message_text = message.get("body").replace(',', ' ').replace(";", " ").replace("\n", " ")
                text_list = message_text.split()
                for word in text_list:
                    word.lower()
                obj_in = {
                    "message_id": message_id,
                    "text": message.get("body"),
                    "text_list":  text_list,
                    "author_id": message.get("from"),
                    "author_name": author_name,
                    "sent_at": sent_at,
                    "chat_id": chat.id
                }
                message = self._repository_message.create(obj_in=obj_in, commit=True)
                return message
            elif message.get("type") == "image":
                caption = message.get("caption")
                obj_in = {
                    "message_id": message_id,
                    "text": caption,
                    "author_id": message.get("from"),
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
                message = self._repository_message.create(obj_in=obj_in, commit=True)
        else:
            pass
