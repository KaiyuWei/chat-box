"""Configuration settings for the chat application."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # Server Configuration
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    HOST: str = os.getenv("HOST", "127.0.0.1")

settings = Settings()
