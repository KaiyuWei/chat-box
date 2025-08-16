from enum import Enum

from pydantic import BaseModel, Field


class ChatRole(str, Enum):
    """Enum for roles in the chat"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class MessageType(str, Enum):
    """Enum for types of messages"""

    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


class ContentItem(BaseModel):
    type: MessageType
    text: str | None = Field(
        None, description="Text content of the message", min_length=1, max_length=4000
    )
    image: str | None = Field(
        None,
        description="Local path or URL to the image",
        min_length=1,
        max_length=4000,
    )
    audio: str | None = Field(
        None,
        description="Local path or URL to the audio file",
        min_length=1,
        max_length=4000,
    )
    video: str | None = Field(
        None,
        description="Local path or URL to the video file",
        min_length=1,
        max_length=4000,
    )


class ChatMessage(BaseModel):
    role: ChatRole = Field(..., description="Role that the message is from")
    content: list[ContentItem] = Field(
        ..., description="Content of the message", min_length=1, max_length=10
    )


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(
        ..., description="List of messages in the chat", min_length=1, max_length=10
    )


class ChatResponse(BaseModel):
    messages: str = Field(..., description="Resulted text of processing", min_length=1)
