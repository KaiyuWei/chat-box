from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import Session

from .base import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    prompt = Column(String(4000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


def create_conversation(db: Session, user_id: int, title: str, prompt: str) -> Conversation:
    new_conversation = Conversation(
        user_id=user_id,
        title=title,
        prompt=prompt
    )
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    return new_conversation
