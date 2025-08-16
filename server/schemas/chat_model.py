from enum import Enum

from pydantic import BaseModel, Field


class ChatRole(str, Enum):
    """Enum for roles in the chat"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class ChatMessage(BaseModel):
    role: ChatRole = Field(..., description="Role that the message is from")
    content: str = Field(
        ..., description="Content of the message", min_length=1, max_length=4000
    )


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(
        ..., description="List of messages in the chat", min_length=1, max_length=10
    )


class ChatResponse(BaseModel):
    messages: str = Field(..., description="Resulted text of processing", min_length=1)
