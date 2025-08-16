from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from .base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @classmethod
    def is_username_exists(cls, username: str, db: Session) -> bool:
        """Check if a username already exists in the database."""
        user = db.query(cls).filter(cls.username == username).first()
        return user is not None

    @classmethod
    def is_email_exists(cls, email: str, db: Session) -> bool:
        """Check if an email already exists in the database."""
        user = db.query(cls).filter(cls.email == email).first()
        return user is not None
