"""Configuration settings for the chat application."""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    HOST: str = os.getenv("HOST", "127.0.0.1")

settings = Settings()
