from app.repository.base import RepositoryBase
from app.models.chat import Message


class RepositoryMessage(RepositoryBase[Message]):
    def filter_message(self, start_sent_at, end_sent_at):
        return self._session.query(self._model).filter(self._model.sent_at >= start_sent_at).filter(self._model.sent_at <= end_sent_at).all()