from pydantic import BaseModel, Field


class MessageInConversationResponse(BaseModel):
    id: int = Field(..., description="The ID of the message")
    sender: str = Field(..., description="The sender of the message")
    content: str = Field(..., description="The content of the message")
    created_at: str = Field(..., description="The timestamp of the message")


class GetConversationResponse(BaseModel):
    conversation_id: int = Field(..., description="The ID of the conversation")
    title: str = Field(..., description="The title of the conversation")
    prompt: str | None = Field(None, description="The prompt of the conversation")
    created_at: str = Field(..., description="The timestamp of the conversation")
    messages: list[MessageInConversationResponse] = Field(
        None, description="The messages in the conversation"
    )
