"""Configuration settings for the chat application."""

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    HOST: str = os.getenv("HOST", "127.0.0.1")

    # CORS settings
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")

    # Database settings
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_USER: str = os.getenv("DB_USER", "user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "user")
    DB_NAME: str = os.getenv("DB_NAME", "chat-box")

    # Build DATABASE_URL from components if not provided
    @property
    def DATABASE_URL(self) -> str:
        return os.getenv(
            "DATABASE_URL",
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:3306/{self.DB_NAME}",
        )

    chat_model = {"MAX_NEW_TOKENS": 100, "TRUST_REMOTE_CODE": True}

    # dev
    DUMMY_USER_ID: int = 1


settings = Settings()
