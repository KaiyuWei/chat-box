import logging
from cmd import PROMPT

import chat_model_loader
import services
from database import get_mysql_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import Conversation
from schemas import ChatRequest, ChatResponse
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat_model"])


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_with_model(
    chat_request: ChatRequest, db: Session = Depends(get_mysql_db)
):
    """Get a user input message and reply"""

    model = chat_model_loader.model
    tokenizer = chat_model_loader.tokenizer

    if model is None or tokenizer is None:
        logger.error("Model or tokenizer not loaded.")
        raise HTTPException(
            status_code=500, detail="Model not loaded. Please try again later"
        )

    try:
        # TODO: enable thinking process and streaming it to the frontend.
        conversation = services.get_conversation_from_request(chat_request, db)
        complete_prompt = services.generate_prompt(
            conversation, chat_request.messages[0].content
        )
        # TODO: store user message

        text = tokenizer.apply_chat_template(
            complete_prompt,
            add_generation_prompt=True,
            tokenize=False,
            enable_thinking=False,
        )
        inputs = tokenizer([text], return_tensors="pt").to(model.device)
        text_ids = model.generate(**inputs, max_new_tokens=100)

        output_ids = text_ids[0][len(inputs.input_ids[0]) :].tolist()
        content = tokenizer.decode(output_ids, skip_special_tokens=True).strip("\n")

        # TODO: store assistant's message
        return ChatResponse(messages=content)

    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise HTTPException(
            status_code=500, detail="Something went wrong, try again later"
        )
