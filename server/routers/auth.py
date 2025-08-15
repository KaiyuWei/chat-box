from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

@router.post("/users")
async def create_user(user: UserCreate):
    return {"message": "User created successfully", "username": user.username}
