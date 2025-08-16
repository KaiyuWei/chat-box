import logging

# debug
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import logging as transformers_logging

transformers_logging.set_verbosity_debug()

MODEL_NAME = "Qwen/Qwen3-0.6B"

model = None
tokenizer = None


def load_model_and_processor():
    global model, tokenizer

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype="auto", device_map="auto"
    )

    if model is None or tokenizer is None:
        logger.error(">>>>>> Model or tokenizer not loaded.")
        return
