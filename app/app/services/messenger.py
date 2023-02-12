import requests
from fastapi.responses import JSONResponse

from sqlalchemy.exc import DataError, IntegrityError, PendingRollbackError

from app.core.config import settings

from app.models.messenger import Messenger

from app.repository.messenger import RepositoryMessenger
from app.repository.chat import RepositoryChat
from app.repository.message import RepositoryMessage

from app.schemas.messengers import MessengerIn


class MessengerService:

    def __init__(
            self,
            repository_messenger: RepositoryMessenger,
            repository_chat: RepositoryChat,
            repository_message: RepositoryMessage) -> None:
        self._repository_messenger = repository_messenger
        self._repository_chat = repository_chat
        self._repository_message = repository_message

    async def all_messengers(self):
        """Получает все активные и неактивные сессии"""
        return self._repository_messenger.list()

    async def create_messenger(
            self,
            data_in: MessengerIn,
            messenger_type:Messenger.MessengerType):
        """Создаёт сессию месенджера в зависимости от его типа."""

        obj_in = {
            "phone": data_in.phone,
            "api_token": data_in.api_token,
            "api_id": data_in.api_id,
        }
        if messenger_type == Messenger.MessengerType.telegram:
            obj_in["type"] = Messenger.MessengerType.telegram
            return self._repository_messenger.create(
                obj_in=obj_in, commit=True
            )
        elif messenger_type == Messenger.MessengerType.whats_app:
            obj_in["type"] = Messenger.MessengerType.whats_app
            url = "https://wappi.pro/api/webhook/url/set"
            headers = {"Authorization": data_in.api_token}
            params = {"profile_id": data_in.api_id, "url": f"{settings.SERVER_IP}/api/v1/chat/webhook"}
            requests.post(url, headers=headers, params=params)
            obj_in["is_active"] = True
            return self._repository_messenger.create(
                obj_in=obj_in, commit=True
            )
        else:
            return JSONResponse(content={"error_msg": "Неизвестный вид мессенджера."}, status_code=403)

    async def delete_messenger(self, messenger_id: str):
        try:
            messenger = self._repository_messenger.get(id=messenger_id)
            chats = self._repository_chat.list(messenger_id=messenger.id)
            for chat in chats:
                messages = self._repository_message.list(chat_id=chat.id)
                for message in messages:
                    self._repository_message.delete(db_obj=message, commit=True)
                self._repository_chat.delete(db_obj=chat, commit=True)
            self._repository_messenger.delete(db_obj=messenger, commit=True)
            return JSONResponse(content={"isDeleted": True, "message": "Мессенджер удалён"}, status_code=200)
        except DataError as e:
            print(str(e))
            return JSONResponse(content={"isDeleted": False, "message": "Мессенджер не существует"}, status_code=400)
        except IntegrityError as e:
            print(str(e))
            return JSONResponse(content={"isDeleted": False, "message": "Мессенджер имеет связанные чаты, удалите сначала их"}, status_code=400)
