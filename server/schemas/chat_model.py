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
    conversation_id: int = Field(None, description="ID of the conversation")
    prompt: str = Field(
        None, description="Initial prompt for the conversation", max_length=4000
    )
    messages: list[ChatMessage] = Field(
        ..., description="List of messages in the chat", min_length=1, max_length=10
    )


class ChatResponse(BaseModel):
    conversation_id: int = Field(..., description="ID of the conversation")
    messages: str = Field(..., description="Resulted text of processing", min_length=1)
