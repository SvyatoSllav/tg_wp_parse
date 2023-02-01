import datetime
from uuid import uuid4

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Enum,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType

from app.db.base_class import Base


class Chat(Base):
    __tablename__ = "chat"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)

    chat_id = Column(String)
    chat_name = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    chat_avatars_img_paths = Column(MutableList.as_mutable(PickleType), default=[])

    messenger_id = Column(
        UUID(as_uuid=True),
        ForeignKey("messenger.id"),
    )
    messenger = relationship("Messenger")


class Message(Base):
    __tablename__ = "message"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)

    message_id = Column(String)
    text = Column(String, nullable=True)
    author_id = Column(String)
    author_name = Column(String, nullable=True)
    auhtor_phone = Column(String, nullable=True)
    sent_at = Column(DateTime)
    message_media_paths = Column(MutableList.as_mutable(PickleType), default=[])

    last_message_id = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    chat_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat.id"),
    )
    chat = relationship("Chat")
