import logging

from database import get_mysql_db
from fastapi import APIRouter, Depends, status
from schemas import ChatRequest, ChatResponse
from sqlalchemy.orm import Session
from transformers import Qwen2_5OmniForConditionalGeneration, Qwen2_5OmniProcessor

MODEL_NAME = "Qwen/Qwen2.5-Omni-3B"

logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat_model"])


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_with_model(
    chat_request: ChatRequest, db: Session = Depends(get_mysql_db)
):
    """Get a user input message and reply"""

    try:
        model = Qwen2_5OmniForConditionalGeneration.from_pretrained(
            MODEL_NAME, torch_dtype="auto", device_map="auto"
        )

        processor = Qwen2_5OmniProcessor.from_pretrained(MODEL_NAME)

        # Dummy value for now
        conversation = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are Qwen, a virtual human developed by the Qwen Team, Alibaba Group, capable of perceiving auditory and visual inputs, as well as generating text and speech.",
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "tell a joke",
                    },
                ],
            },
        ]

        text = processor.apply_chat_template(
            conversation, add_generation_prompt=True, tokenize=False
        )
        inputs = processor(text=text, return_tensors="pt", padding=True)
        inputs = inputs.to(model.device).to(model.dtype)
        text_ids, audio = model.generate(**inputs)

    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return ChatResponse(messages="Something went wrong, try again later")
