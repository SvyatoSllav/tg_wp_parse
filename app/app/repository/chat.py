from sqlalchemy.orm import joinedload
from app.repository.base import RepositoryBase
from app.models.chat import Chat

from app.models.messenger import Messenger


class RepositoryChat(RepositoryBase[Chat]):
    def tg_chats(self,):
        return self._session.query(
            self._model,
            Messenger.type,
            Messenger.id
            ).filter(
                self._model.messenger_id == Messenger.id,
                Messenger.type==Messenger.MessengerType.telegram
            ).all()
