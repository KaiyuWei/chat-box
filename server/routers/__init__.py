"""
This package contains all API routes
"""

from .chat_model import router as chat_model_router
from .user import router as user_router

__all__ = ["user_router", "chat_model_router"]
