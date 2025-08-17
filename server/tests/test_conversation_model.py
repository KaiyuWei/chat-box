"""
Integration tests for Conversation model methods.

These tests verify the database interaction behavior of Conversation model methods
using a real SQLite database in memory.
"""

import pytest
from datetime import datetime
from models.conversation import Conversation
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
        
        conversation = Conversation.create_conversation(
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
        """Test creating conversation with empty prompt gets default system prompt."""
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
        
        conversation = Conversation.create_conversation(
            db=db_session,
            user_id=test_user.id,
            title=title,
            prompt=prompt
        )

        assert conversation is not None
        assert conversation.prompt == "You are a helpful and friendly assistant."
        assert conversation.title == title

    def test_create_conversation_with_null_prompt(self, db_session: Session):
        """Test creating conversation with None prompt gets default system prompt."""
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
        
        conversation = Conversation.create_conversation(
            db=db_session,
            user_id=test_user.id,
            title=title,
            prompt=None
        )

        assert conversation is not None
        assert conversation.prompt == "You are a helpful and friendly assistant."
        assert conversation.title == title

    def test_create_conversation_with_custom_prompt_overrides_default(self, db_session: Session):
        """Test that providing a custom prompt overrides the default system prompt."""
        # Create a test user first
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # Create conversation with custom prompt
        title = "Test Conversation"
        custom_prompt = "You are a specialized assistant for coding tasks."
        
        conversation = Conversation.create_conversation(
            db=db_session,
            user_id=test_user.id,
            title=title,
            prompt=custom_prompt
        )

        assert conversation is not None
        assert conversation.prompt == custom_prompt
        assert conversation.prompt != "You are a helpful and friendly assistant."
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
        
        conversation = Conversation.create_conversation(
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
        
        conversation = Conversation.create_conversation(
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
            Conversation.create_conversation(
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
        conversation1 = Conversation.create_conversation(
            db=db_session,
            user_id=test_user.id,
            title="First Conversation",
            prompt="First prompt"
        )

        # Create second conversation
        conversation2 = Conversation.create_conversation(
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
        
        conversation = Conversation.create_conversation(
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
        
        conversation = Conversation.create_conversation(
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

        conversation = Conversation.create_conversation(
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
        conversation = Conversation.create_conversation(
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
        conversation = Conversation.create_conversation(
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

        conversation = Conversation.create_conversation(
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


class TestConversationGetById:
    """Test the get_by_id classmethod."""

    def test_get_by_id_success(self, db_session: Session):
        """Test successfully retrieving a conversation by ID."""
        # Create a test user first
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # Create a conversation
        original_conversation = Conversation.create_conversation(
            db=db_session,
            user_id=test_user.id,
            title="Test Conversation",
            prompt="Test prompt"
        )

        # Retrieve the conversation by ID
        retrieved_conversation = Conversation.get_by_id(
            db=db_session,
            conversation_id=original_conversation.id
        )

        # Verify the retrieved conversation matches the original
        assert retrieved_conversation is not None
        assert isinstance(retrieved_conversation, Conversation)
        assert retrieved_conversation.id == original_conversation.id
        assert retrieved_conversation.user_id == original_conversation.user_id
        assert retrieved_conversation.title == original_conversation.title
        assert retrieved_conversation.prompt == original_conversation.prompt
        assert retrieved_conversation.created_at == original_conversation.created_at

    def test_get_by_id_not_found(self, db_session: Session):
        """Test retrieving a conversation with non-existent ID returns None."""
        non_existent_id = 99999
        
        result = Conversation.get_by_id(
            db=db_session,
            conversation_id=non_existent_id
        )
        
        assert result is None

    def test_get_by_id_with_zero_id(self, db_session: Session):
        """Test retrieving a conversation with ID 0 returns None."""
        result = Conversation.get_by_id(
            db=db_session,
            conversation_id=0
        )
        
        assert result is None

    def test_get_by_id_with_negative_id(self, db_session: Session):
        """Test retrieving a conversation with negative ID returns None."""
        result = Conversation.get_by_id(
            db=db_session,
            conversation_id=-1
        )
        
        assert result is None

    def test_get_by_id_multiple_conversations(self, db_session: Session):
        """Test get_by_id works correctly when multiple conversations exist."""
        # Create a test user
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # Create multiple conversations
        conversation1 = Conversation.create_conversation(
            db=db_session,
            user_id=test_user.id,
            title="First Conversation",
            prompt="First prompt"
        )
        
        conversation2 = Conversation.create_conversation(
            db=db_session,
            user_id=test_user.id,
            title="Second Conversation",
            prompt="Second prompt"
        )
        
        conversation3 = Conversation.create_conversation(
            db=db_session,
            user_id=test_user.id,
            title="Third Conversation",
            prompt="Third prompt"
        )

        # Retrieve each conversation by ID and verify they're correct
        retrieved1 = Conversation.get_by_id(db=db_session, conversation_id=conversation1.id)
        retrieved2 = Conversation.get_by_id(db=db_session, conversation_id=conversation2.id)
        retrieved3 = Conversation.get_by_id(db=db_session, conversation_id=conversation3.id)

        # Verify each retrieved conversation matches the original
        assert retrieved1.id == conversation1.id
        assert retrieved1.title == "First Conversation"
        assert retrieved1.prompt == "First prompt"

        assert retrieved2.id == conversation2.id
        assert retrieved2.title == "Second Conversation"
        assert retrieved2.prompt == "Second prompt"

        assert retrieved3.id == conversation3.id
        assert retrieved3.title == "Third Conversation"
        assert retrieved3.prompt == "Third prompt"

        # Verify they're all different conversations
        assert retrieved1.id != retrieved2.id != retrieved3.id

    def test_get_by_id_with_different_users(self, db_session: Session):
        """Test get_by_id retrieves conversations regardless of user ownership."""
        # Create two test users
        user1 = User(
            username="user1",
            email="user1@example.com",
            password_hash="hashed_password1"
        )
        user2 = User(
            username="user2",
            email="user2@example.com",
            password_hash="hashed_password2"
        )
        db_session.add_all([user1, user2])
        db_session.commit()
        db_session.refresh(user1)
        db_session.refresh(user2)

        # Create conversations for different users
        conversation1 = Conversation.create_conversation(
            db=db_session,
            user_id=user1.id,
            title="User 1 Conversation",
            prompt="User 1 prompt"
        )
        
        conversation2 = Conversation.create_conversation(
            db=db_session,
            user_id=user2.id,
            title="User 2 Conversation",
            prompt="User 2 prompt"
        )

        # Retrieve conversations by ID
        retrieved1 = Conversation.get_by_id(db=db_session, conversation_id=conversation1.id)
        retrieved2 = Conversation.get_by_id(db=db_session, conversation_id=conversation2.id)

        # Verify we get the correct conversations
        assert retrieved1.id == conversation1.id
        assert retrieved1.user_id == user1.id
        assert retrieved1.title == "User 1 Conversation"

        assert retrieved2.id == conversation2.id
        assert retrieved2.user_id == user2.id
        assert retrieved2.title == "User 2 Conversation"

    def test_get_by_id_return_type(self, db_session: Session):
        """Test that get_by_id returns the correct type."""
        # Create a test user and conversation
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        conversation = Conversation.create_conversation(
            db=db_session,
            user_id=test_user.id,
            title="Test Conversation",
            prompt="Test prompt"
        )

        # Retrieve the conversation
        retrieved = Conversation.get_by_id(db=db_session, conversation_id=conversation.id)

        # Verify return type and attributes
        assert isinstance(retrieved, Conversation)
        assert hasattr(retrieved, 'id')
        assert hasattr(retrieved, 'user_id')
        assert hasattr(retrieved, 'title')
        assert hasattr(retrieved, 'prompt')
        assert hasattr(retrieved, 'created_at')
        assert hasattr(retrieved, 'updated_at')

    def test_get_by_id_with_none_prompt(self, db_session: Session):
        """Test get_by_id works with conversations that have None prompt (gets default)."""
        # Create a test user
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # Create conversation with None prompt (gets default system prompt)
        conversation = Conversation.create_conversation(
            db=db_session,
            user_id=test_user.id,
            title="Test Conversation",
            prompt=None
        )

        # Retrieve the conversation
        retrieved = Conversation.get_by_id(db=db_session, conversation_id=conversation.id)

        # Verify the conversation is retrieved correctly
        assert retrieved is not None
        assert retrieved.id == conversation.id
        assert retrieved.title == "Test Conversation"
        assert retrieved.prompt == "You are a helpful and friendly assistant."

    def test_get_by_id_with_special_characters(self, db_session: Session):
        """Test get_by_id works with conversations containing special characters."""
        # Create a test user
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # Create conversation with special characters
        title_with_special_chars = "Test! @#$%^&*()_+-=[]{}|;':\",./<>?"
        prompt_with_unicode = "Unicode: 你好世界 - Привет мир - مرحبا بالعالم 🚀"
        
        conversation = Conversation.create_conversation(
            db=db_session,
            user_id=test_user.id,
            title=title_with_special_chars,
            prompt=prompt_with_unicode
        )

        # Retrieve the conversation
        retrieved = Conversation.get_by_id(db=db_session, conversation_id=conversation.id)

        # Verify the conversation is retrieved correctly with all special characters
        assert retrieved is not None
        assert retrieved.id == conversation.id
        assert retrieved.title == title_with_special_chars
        assert retrieved.prompt == prompt_with_unicode
