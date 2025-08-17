"""
Integration tests for Conversation model methods.

These tests verify the database interaction behavior of Conversation model methods
using a real SQLite database in memory.
"""

import pytest
from datetime import datetime
from models.conversation import Conversation, create_conversation
from models.user import User
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


class TestCreateConversationFunction:
    """Test the create_conversation function."""

    def test_create_conversation_success(self, db_session: Session):
        """Test successful conversation creation."""
        # Create a test user first
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # Create conversation
        title = "Test Conversation"
        prompt = "This is a test prompt"
        
        conversation = create_conversation(
            db=db_session,
            user_id=test_user.id,
            title=title,
            prompt=prompt
        )

        # Verify conversation was created correctly
        assert conversation is not None
        assert isinstance(conversation, Conversation)
        assert conversation.id is not None
        assert conversation.user_id == test_user.id
        assert conversation.title == title
        assert conversation.prompt == prompt
        assert conversation.created_at is not None
        assert isinstance(conversation.created_at, datetime)
        
        # Verify it's in the database
        db_conversation = db_session.query(Conversation).filter(
            Conversation.id == conversation.id
        ).first()
        assert db_conversation is not None
        assert db_conversation.title == title
        assert db_conversation.prompt == prompt

    def test_create_conversation_with_empty_prompt(self, db_session: Session):
        """Test creating conversation with empty prompt."""
        # Create a test user first
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # Create conversation with empty prompt
        title = "Test Conversation"
        prompt = ""
        
        conversation = create_conversation(
            db=db_session,
            user_id=test_user.id,
            title=title,
            prompt=prompt
        )

        assert conversation is not None
        assert conversation.prompt == ""
        assert conversation.title == title

    def test_create_conversation_with_null_prompt(self, db_session: Session):
        """Test creating conversation with None prompt."""
        # Create a test user first
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # Create conversation with None prompt
        title = "Test Conversation"
        
        conversation = create_conversation(
            db=db_session,
            user_id=test_user.id,
            title=title,
            prompt=None
        )

        assert conversation is not None
        assert conversation.prompt is None
        assert conversation.title == title

    def test_create_conversation_with_long_title(self, db_session: Session):
        """Test creating conversation with maximum length title."""
        # Create a test user first
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # Create conversation with long title (255 chars is the limit)
        long_title = "A" * 255
        prompt = "Test prompt"
        
        conversation = create_conversation(
            db=db_session,
            user_id=test_user.id,
            title=long_title,
            prompt=prompt
        )

        assert conversation is not None
        assert conversation.title == long_title
        assert len(conversation.title) == 255

    def test_create_conversation_with_long_prompt(self, db_session: Session):
        """Test creating conversation with maximum length prompt."""
        # Create a test user first
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # Create conversation with long prompt (4000 chars is the limit)
        title = "Test Conversation"
        long_prompt = "A" * 4000
        
        conversation = create_conversation(
            db=db_session,
            user_id=test_user.id,
            title=title,
            prompt=long_prompt
        )

        assert conversation is not None
        assert conversation.prompt == long_prompt
        assert len(conversation.prompt) == 4000

    def test_create_conversation_with_invalid_user_id(self, db_session: Session):
        """Test creating conversation with non-existent user_id."""
        title = "Test Conversation"
        prompt = "Test prompt"
        non_existent_user_id = 99999
        
        # This should raise an IntegrityError due to foreign key constraint
        with pytest.raises(IntegrityError):
            create_conversation(
                db=db_session,
                user_id=non_existent_user_id,
                title=title,
                prompt=prompt
            )

    def test_create_conversation_multiple_for_same_user(self, db_session: Session):
        """Test creating multiple conversations for the same user."""
        # Create a test user first
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # Create first conversation
        conversation1 = create_conversation(
            db=db_session,
            user_id=test_user.id,
            title="First Conversation",
            prompt="First prompt"
        )

        # Create second conversation
        conversation2 = create_conversation(
            db=db_session,
            user_id=test_user.id,
            title="Second Conversation",
            prompt="Second prompt"
        )

        # Verify both conversations exist and are different
        assert conversation1.id != conversation2.id
        assert conversation1.title != conversation2.title
        assert conversation1.prompt != conversation2.prompt
        assert conversation1.user_id == conversation2.user_id == test_user.id

        # Verify both are in database
        conversations = db_session.query(Conversation).filter(
            Conversation.user_id == test_user.id
        ).all()
        assert len(conversations) == 2

    def test_create_conversation_special_characters_in_title(self, db_session: Session):
        """Test creating conversation with special characters in title."""
        # Create a test user first
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # Create conversation with special characters
        title = "Test Conversation! @#$%^&*()_+-=[]{}|;':\",./<>?"
        prompt = "Test prompt with émojis 🚀 and unicode characters: αβγδε"
        
        conversation = create_conversation(
            db=db_session,
            user_id=test_user.id,
            title=title,
            prompt=prompt
        )

        assert conversation is not None
        assert conversation.title == title
        assert conversation.prompt == prompt

    def test_create_conversation_unicode_characters(self, db_session: Session):
        """Test creating conversation with unicode characters."""
        # Create a test user first
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # Create conversation with unicode characters
        title = "测试对话 - Тест разговор - محادثة اختبار"
        prompt = "Unicode prompt: 你好世界 - Привет мир - مرحبا بالعالم"
        
        conversation = create_conversation(
            db=db_session,
            user_id=test_user.id,
            title=title,
            prompt=prompt
        )

        assert conversation is not None
        assert conversation.title == title
        assert conversation.prompt == prompt

    def test_create_conversation_timestamps(self, db_session: Session):
        """Test that timestamps are set correctly."""
        # Create a test user first
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        conversation = create_conversation(
            db=db_session,
            user_id=test_user.id,
            title="Test Conversation",
            prompt="Test prompt"
        )

        # Verify timestamps
        assert conversation.created_at is not None
        assert isinstance(conversation.created_at, datetime)
        
        # updated_at should be None initially (only set on updates)
        assert conversation.updated_at is None

    def test_create_conversation_cascade_delete(self, db_session: Session):
        """Test that conversations are deleted when user is deleted (CASCADE)."""
        # Create a test user
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # Create conversation
        conversation = create_conversation(
            db=db_session,
            user_id=test_user.id,
            title="Test Conversation",
            prompt="Test prompt"
        )
        
        conversation_id = conversation.id

        # Verify conversation exists
        assert db_session.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first() is not None

        # Delete the user
        db_session.delete(test_user)
        db_session.commit()

        # Verify conversation is also deleted due to CASCADE
        assert db_session.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first() is None

    def test_create_conversation_empty_title_behavior(self, db_session: Session):
        """Test behavior when creating conversation with empty title."""
        # Create a test user first
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # SQLite allows empty strings, so test that it's stored correctly
        conversation = create_conversation(
            db=db_session,
            user_id=test_user.id,
            title="",  # Empty title
            prompt="Test prompt"
        )
        
        assert conversation is not None
        assert conversation.title == ""
        assert conversation.prompt == "Test prompt"

    def test_create_conversation_return_type(self, db_session: Session):
        """Test that create_conversation returns the correct type."""
        # Create a test user first
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        conversation = create_conversation(
            db=db_session,
            user_id=test_user.id,
            title="Test Conversation",
            prompt="Test prompt"
        )

        # Verify return type
        assert isinstance(conversation, Conversation)
        assert hasattr(conversation, 'id')
        assert hasattr(conversation, 'user_id')
        assert hasattr(conversation, 'title')
        assert hasattr(conversation, 'prompt')
        assert hasattr(conversation, 'created_at')
        assert hasattr(conversation, 'updated_at')
