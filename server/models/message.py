from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from sqlalchemy import Enum

from .base import Base

class SenderType(PyEnum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    sent_by = Column(Enum(SenderType), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
