from time import sleep

from models import Conversation, Message
from models.conversation import SYSTEM_PROMPT_TYPE
from models.message import SenderType
from schemas import ChatRequest
from sqlalchemy.orm import Session, joinedload

DUMMY_USER_ID = 1


def get_conversation_from_request(
    chat_request: ChatRequest, db: Session
) -> Conversation:
    conversation_id = chat_request.conversation_id
    user_id = DUMMY_USER_ID
    messages = chat_request.messages
    title = messages[-1].content if messages else "New Conversation"
    prompt = chat_request.prompt if chat_request.prompt else ""

    if conversation_id is not None:
        conversation = Conversation.get_by_id(db, conversation_id, with_messages=True)
    else:
        conversation = Conversation.create_conversation(db, user_id, title, prompt)

    return conversation


def store_request_and_response_messages(
    db: Session, conversation_id: int, user_message: str, assistant_message: str
):
    """Store user and assistant messages in the database in one transaction."""

    Message.create_message(db, conversation_id, SenderType.USER, user_message)
    Message.create_message(db, conversation_id, SenderType.ASSISTANT, assistant_message)


def generate_prompt(conversation: Conversation, new_message: str) -> list[dict]:
    """Generate a complete prompt for the chat model based on the conversation."""

    history = _generate_conversation_history(conversation)
    history.append({"role": "user", "content": new_message})
    return history


def _generate_conversation_history(conversation: Conversation) -> list[dict]:
    """Generate a list of messages in the conversation for the chat model."""
    history = [{"role": SYSTEM_PROMPT_TYPE, "content": conversation.prompt}]

    for message in conversation.messages:
        role = "user" if message.sent_by == SenderType.USER else "assistant"
        history.append({"role": role, "content": message.content})

    return history
