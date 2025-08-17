from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql import func

from .base import Base


class SenderType(PyEnum):
    USER = "user"
    ASSISTANT = "assistant"


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(
        Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    sent_by = Column(Enum(SenderType), nullable=False)
    content = Column(String(4000), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    conversation = relationship("Conversation", back_populates="messages")

    @classmethod
    def create_message(
        cls, db: Session, conversation_id: int, sent_by: SenderType, content: str
    ) -> "Message":
        message = cls(conversation_id=conversation_id, sent_by=sent_by, content=content)
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
