import datetime
import enum
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


class Device(Base):
    __tablename__ = "device"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)

    name = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
