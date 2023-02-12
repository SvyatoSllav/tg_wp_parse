from app.db.base_class import Base
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
from uuid import uuid4
import enum
import datetime


class Messenger(Base):
    __tablename__ = "messenger"

    class MessengerType(str, enum.Enum):
        telegram = "telegram"
        whats_app = "whats_app"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)

    api_token = Column(String)
    api_id = Column(String)
    phone = Column(String)
    phone_hash = Column(String, nullable=True)
    code = Column(String, nullable=True)

    is_active = Column(Boolean, default=False)

    type = Column(Enum(MessengerType))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
