import logging

import chat_model_loader
from database import get_mysql_db
from fastapi import APIRouter, Depends, HTTPException, status
from schemas import ChatRequest, ChatResponse
from sqlalchemy.orm import Session

MODEL_NAME = "Qwen/Qwen2.5-Omni-3B"
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
        # TODO: append history messages to the conversation list.
        conversation = chat_request.messages

        text = tokenizer.apply_chat_template(
            conversation,
            add_generation_prompt=True,
            tokenize=False,
            enable_thinking=True,
        )
        inputs = tokenizer([text], return_tensors="pt").to(model.device)
        text_ids = model.generate(**inputs, max_new_tokens=32768)

        output_ids = text_ids[0][len(inputs.input_ids[0]) :].tolist()
        try:
            index = len(output_ids) - output_ids[::-1].index(151668)
        except ValueError:
            index = 0

        content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip(
            "\n"
        )

        return ChatResponse(messages=content)

    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise HTTPException(
            status_code=500, detail="Something went wrong, try again later"
        )
