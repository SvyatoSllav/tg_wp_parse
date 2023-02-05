import datetime
from sqlalchemy import func, and_, or_
from app.repository.base import RepositoryBase
from app.models.chat import Message


class RepositoryMessage(RepositoryBase[Message]):
    def filter_message(
            self,
            start_sent_at: datetime.date,
            end_sent_at: datetime.date,
            searchText: str,
            category: list[str]):
        filters = [func.lower(self._model.text).contains(cat.lower()) for cat in category]
        query = self._session.query(self._model
            ).filter(self._model.sent_at >= start_sent_at
            ).filter(self._model.sent_at <= end_sent_at
            ).filter(func.lower(self._model.text).contains(searchText))
        if category != [""]:
            query = query.filter(or_(*filters)
            )
        return query.order_by(self._model.sent_at.desc())
