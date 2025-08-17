from models import Conversation, Message
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
        conversation = (
            db.query(Conversation)
            .options(joinedload(Conversation.messages))
            .filter(Conversation.id == conversation_id)
            .first()
        )
    else:
        conversation = Conversation.create_conversation(db, user_id, title, prompt)

    return conversation


def generate_prompt(conversation: Conversation) -> str:
    messages = conversation.messages
    prompt = conversation.prompt

    if messages:
        # Append the latest user message to the prompt
        latest_user_message = messages[-1].content
        prompt += f"\nUser: {latest_user_message}\nAssistant:"

    return prompt


def _generate_system_prompt(prompt: str) -> str:
    if not prompt:
        return f"[System Instruction] You are a helpful assistant."
    return f"[System Instruction]\n{prompt}"


def _generate_conversation_history(conversation: Conversation) -> str:
    history = []

    for message in conversation.messages:
        role = "User" if message.sent_by == SenderType.USER else "Assistant"
        history.append(f"{role}: {message.content}")

    joined_messages = "\n".join(history)
    return f"[Conversation History]\n{joined_messages}" if joined_messages else ""


def _generate_task_description(conversation: Conversation) -> str:
    return f"[Task]\nReply to the last user message."
