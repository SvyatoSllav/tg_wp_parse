from fastapi.responses import JSONResponse

from telethon import TelegramClient

from app.models.messenger import Messenger

from app.repository.messenger import RepositoryMessenger


class TelegramService:

    def __init__(
            self,
            repository_messenger: RepositoryMessenger) -> None:
        self._repository_messenger = repository_messenger

    @staticmethod
    def session_name(phone: str, api_id: str):
        return f"{phone}_{api_id}"

    async def receive_code(self, tg_messenger_id: str):
        messenger = self._repository_messenger.get(id=tg_messenger_id)
        phone, api_id, api_hash = messenger.phone, messenger.api_id, messenger.api_token 
        session_name = self.session_name(phone=phone, api_id=api_id)

        client = TelegramClient(session_name, api_id, api_hash)
        await client.connect()
        phone_hash = await client.send_code_request(phone=phone)
        self._repository_messenger.update(db_obj=messenger, obj_in={"phone_hash": phone_hash.phone_code_hash})
        await client.disconnect()
        return str(phone_hash)

    async def authorize_messenger(self, tg_messenger_id: str, code: str):
        messenger = self._repository_messenger.get(id=tg_messenger_id)
        phone, phone_hash, api_id, api_hash = messenger.phone, messenger.phone_hash, messenger.api_id, messenger.api_token 
        session_name = self.session_name(phone=phone, api_id=api_id)

        client = TelegramClient(session_name, api_id, api_hash)
        await client.connect()
        await client.sign_in(
            phone=phone,
            code=code,
            phone_code_hash=phone_hash,
        )
        self._repository_messenger.update(db_obj=messenger, obj_in={"is_active": True, "code": code})
        status = await client.is_user_authorized()
        client.disconnect()
        return JSONResponse(content={"status": status}, status_code=200)

    async def me(self, tg_messenger_id):
        messenger = self._repository_messenger.get(id=tg_messenger_id)
        phone, phone_hash, api_id, api_hash, code = messenger.phone, messenger.phone_hash, messenger.api_id, messenger.api_token, messenger.code
        session_name = self.session_name(phone=phone, api_id=api_id)
        print(session_name)

        client = TelegramClient(session_name, api_id, api_hash)
        await client.connect()
        if not await client.is_user_authorized():
            print("FOOBAR")
            await client.sign_in(
                phone=phone,
                code=code,
                phone_code_hash=phone_hash,
            )
        me = await client.get_me()
        await client.disconnect()
        return me.first_name
