import logging

import bcrypt
from database import get_mysql_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import User
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])


class UserCreate(BaseModel):
    # TODO: add more specific validations:
    # - Username, password should be in some patterns
    # - Username must be unique
    # - Email must be unique
    # - Password must meet complexity requirements

    username: str = Field(
        ..., min_length=3, max_length=50, description="Unique user name for the account"
    )
    email: str = Field(
        ...,
        pattern=r"^[^@]+@[^@]+\.[^@]+$",
        description="User email address",
    )
    password: str = Field(..., min_length=8, description="User password")

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


class UserResponse(BaseModel):
    """Response model for user data"""

    id: int
    username: str
    email: str
    created_at: str

    class Config:
        from_attributes = True


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_mysql_db)):
    """
    Create a new user account.
    """

    try:
        user.email = user.email.lower()
        user.username = user.username.lower()

        if User.is_username_exists(user.username, db) or User.is_email_exists(
            user.email, db
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists",
            )

        password_hash = UserCreate.hash_password(user.password)
        new_user = User(
            username=user.username, email=user.email, password_hash=password_hash
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(
            f"User created successfully: {new_user.username} (ID: {new_user.id})"
        )

        return UserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            created_at=new_user.created_at.isoformat() if new_user.created_at else "",
        )

    except HTTPException as e:
        raise
    except Exception as e:
        # Handle unexpected errors
        db.rollback()
        logger.error(f"Unexpected error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while creating user",
        )
