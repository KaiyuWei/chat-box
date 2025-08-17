import logging

from database import get_mysql_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import User
from schemas import UserCreate, UserResponse
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter(tags=["user"])


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

        # TODO: move the database interaction to a funciton in User model class
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
