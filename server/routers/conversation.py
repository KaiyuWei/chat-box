from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_mysql_db
from models import Conversation
from schemas.conversation import GetConversationResponse, MessageInConversationResponse

router = APIRouter(tags=["conversation"])


@router.get("/conversation/{conversation_id}", response_model=GetConversationResponse)
def get_conversation(conversation_id: int, db: Session = Depends(get_mysql_db)):
    conversation = Conversation.get_by_id(db, conversation_id, with_messages=True)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    message_responses = []
    if conversation.messages:
        for message in conversation.messages:
            message_responses.append(
                MessageInConversationResponse(
                    id=message.id,
                    sender=message.sent_by.value,
                    content=message.content,
                    created_at=message.created_at.isoformat()
                )
            )
    
    return GetConversationResponse(
        conversation_id=conversation.id,
        title=conversation.title,
        prompt=conversation.prompt,
        created_at=conversation.created_at.isoformat(),
        messages=message_responses
    )
