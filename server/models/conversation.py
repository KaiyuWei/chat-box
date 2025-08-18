from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Session, joinedload, relationship
from sqlalchemy.sql import func

from .base import Base

DEFAULT_SYSTEM_PROMPT = "You are a helpful and friendly assistant."
SYSTEM_PROMPT_TYPE = "system"


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(String(255), nullable=False)
    prompt = Column(String(4000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )

    @classmethod
    def create_conversation(
        cls, db: Session, user_id: int, title: str, prompt: str
    ) -> "Conversation":
        new_conversation = cls(
            user_id=user_id,
            title=title,
            prompt=prompt if prompt else DEFAULT_SYSTEM_PROMPT,
        )
        db.add(new_conversation)
        db.commit()
        db.refresh(new_conversation)
        return new_conversation

    @classmethod
    def get_by_id(
        cls, db: Session, conversation_id: int, with_messages: bool = False
    ) -> "Conversation":
        query = db.query(Conversation)
        if with_messages:
            query = query.options(joinedload(Conversation.messages))

        conversation = query.filter(Conversation.id == conversation_id).first()
        return conversation
