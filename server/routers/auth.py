from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["auth"])


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


@router.post("/users")
async def create_user(user: UserCreate):
    return {"message": "User created successfully", "username": user.username}


@router.get("/users")
async def get_users():
    return {"message": "List of users"}
