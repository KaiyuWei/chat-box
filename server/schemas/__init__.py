"""
This package contains all Pydantic models (schemas) used in the API.
"""

from .user import UserCreate, UserResponse

__all__ = ["UserCreate", "UserResponse"]
