from schemas import ChatRequest
from sqlalchemy.orm import Session
from models import Conversation

DUMMY_USER_ID = 1

def get_conversation_from_request(chat_request: ChatRequest, db: Session) -> Conversation:
    conversation_id = chat_request.conversation_id
    user_id = DUMMY_USER_ID
    messages = chat_request.messages
    title = messages[-1].content if messages else "New Conversation"
    prompt = chat_request.prompt if chat_request.prompt else ""

    if conversation_id is not None:
        conversation = Conversation.get_by_id(conversation_id, db)
    else:
        conversation = Conversation.create_conversation(db, user_id, title, prompt)
    
    return conversation