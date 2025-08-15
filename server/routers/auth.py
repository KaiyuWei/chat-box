import re

import bcrypt
from fastapi import APIRouter, HTTPException
from models import User
from pydantic import BaseModel, Field, field_validator

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


@router.post("/users")
async def create_user(user: UserCreate):
    return {"message": "User created successfully", "username": user.username}


@router.get("/users")
async def get_users():
    return {"message": "List of users"}
