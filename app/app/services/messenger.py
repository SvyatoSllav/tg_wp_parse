from fastapi.responses import JSONResponse

from app.models.messenger import Messenger

from app.repository.messenger import RepositoryMessenger

from app.schemas.messengers import MessengerIn


class MessengerService:

    def __init__(
            self,
            repository_messenger: RepositoryMessenger) -> None:
        self._repository_messenger = repository_messenger

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
            return self._repository_messenger.create(
                obj_in=obj_in, commit=True
            )
        else:
            return JSONResponse(content={"error_msg": "Неизвестный вид мессенджера."}, status_code=403)