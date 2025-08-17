import logging

import chat_model_loader
import services
from config import settings
from database import get_mysql_db
from fastapi import APIRouter, Depends, HTTPException, status
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
        conversation = services.get_conversation_from_request(chat_request, db)
        complete_prompt = services.generate_prompt(
            conversation, chat_request.messages[0].content
        )

        logger.info(f">>>>>>>> Complete prompt: {complete_prompt}")

        text = tokenizer.apply_chat_template(
            complete_prompt,
            add_generation_prompt=True,
            tokenize=False,
            enable_thinking=False,
        )
        inputs = tokenizer([text], return_tensors="pt").to(model.device)
        text_ids = model.generate(
            **inputs, max_new_tokens=settings.chat_model["MAX_NEW_TOKENS"]
        )

        output_ids = text_ids[0][len(inputs.input_ids[0]) :].tolist()
        response_message = tokenizer.decode(output_ids, skip_special_tokens=True).strip(
            "\n"
        )

        services.store_request_and_response_messages(
            db, conversation.id, chat_request.messages[0].content, response_message
        )

        return ChatResponse(messages=response_message)

    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise HTTPException(
            status_code=500, detail="Something went wrong, try again later"
        )
