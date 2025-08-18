from config import settings
from database import get_mysql_db
from fastapi import APIRouter, Depends, HTTPException
from models import Conversation
from schemas.conversation import GetConversationResponse, MessageInConversationResponse
from sqlalchemy.orm import Session

router = APIRouter(tags=["conversation"])


@router.get(
    "/conv-with-msg/{conversation_id}",
    response_model=GetConversationResponse,
)
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
                    created_at=message.created_at.isoformat(),
                )
            )

    return GetConversationResponse(
        conversation_id=conversation.id,
        title=conversation.title,
        prompt=conversation.prompt,
        created_at=conversation.created_at.isoformat(),
        messages=message_responses,
    )


@router.get("/user-conv-with-msg/{user_id}")
def get_user_conversations(user_id: int, db: Session = Depends(get_mysql_db)):
    # TODO: remove the dummy user id here after an auth system is added
    user_id = settings.DUMMY_USER_ID
    conversations = Conversation.get_by_user_id(db, user_id, with_messages=True)

    if not conversations:
        raise HTTPException(status_code=404, detail="No conversations found for user")

    return [
        GetConversationResponse(
            conversation_id=conv.id,
            title=conv.title,
            prompt=conv.prompt,
            created_at=conv.created_at.isoformat(),
            messages=[
                MessageInConversationResponse(
                    id=msg.id,
                    sender=msg.sent_by.value,
                    content=msg.content,
                    created_at=msg.created_at.isoformat(),
                )
                for msg in conv.messages
            ],
        )
        for conv in conversations
    ]
