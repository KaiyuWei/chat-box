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
    """Test the get_by_id classmethod with lazy loading and eager loading."""

    def test_get_by_id_lazy_loading_success(self, db_session: Session):
        """Test successfully retrieving a conversation by ID with lazy loading (default behavior)."""
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

        # Retrieve the conversation by ID with lazy loading (default)
        retrieved_conversation = Conversation.get_by_id(
            db=db_session,
            conversation_id=original_conversation.id,
            with_messages=False
        )

        # Verify the retrieved conversation matches the original
        assert retrieved_conversation is not None
        assert isinstance(retrieved_conversation, Conversation)
        assert retrieved_conversation.id == original_conversation.id
        assert retrieved_conversation.user_id == original_conversation.user_id
        assert retrieved_conversation.title == original_conversation.title
        assert retrieved_conversation.prompt == original_conversation.prompt
        assert retrieved_conversation.created_at == original_conversation.created_at

    def test_get_by_id_lazy_loading_default(self, db_session: Session):
        """Test that with_messages defaults to False (lazy loading)."""
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
        conversation = Conversation.create_conversation(
            db=db_session,
            user_id=test_user.id,
            title="Test Conversation",
            prompt="Test prompt"
        )

        # Retrieve without specifying with_messages (should default to False)
        retrieved = Conversation.get_by_id(
            db=db_session,
            conversation_id=conversation.id
        )

        assert retrieved is not None
        assert retrieved.id == conversation.id

    def test_get_by_id_eager_loading_without_messages(self, db_session: Session):
        """Test eager loading when conversation has no messages."""
        from models.message import Message, SenderType
        
        # Create a test user
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # Create a conversation without messages
        conversation = Conversation.create_conversation(
            db=db_session,
            user_id=test_user.id,
            title="Empty Conversation",
            prompt="Test prompt"
        )

        # Retrieve with eager loading
        retrieved = Conversation.get_by_id(
            db=db_session,
            conversation_id=conversation.id,
            with_messages=True
        )

        # Verify conversation is retrieved correctly
        assert retrieved is not None
        assert retrieved.id == conversation.id
        assert retrieved.title == "Empty Conversation"
        
        # Verify messages relationship is loaded and empty
        assert hasattr(retrieved, 'messages')
        assert retrieved.messages == []

    def test_get_by_id_eager_loading_with_messages(self, db_session: Session):
        """Test eager loading when conversation has messages."""
        from models.message import Message, SenderType
        
        # Create a test user
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # Create a conversation
        conversation = Conversation.create_conversation(
            db=db_session,
            user_id=test_user.id,
            title="Test Conversation",
            prompt="Test prompt"
        )

        # Add some messages to the conversation
        message1 = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.USER,
            content="Hello, this is a user message"
        )
        message2 = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.ASSISTANT,
            content="Hello! This is an assistant response"
        )
        message3 = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.USER,
            content="Another user message"
        )

        # Retrieve with eager loading
        retrieved = Conversation.get_by_id(
            db=db_session,
            conversation_id=conversation.id,
            with_messages=True
        )

        # Verify conversation is retrieved correctly
        assert retrieved is not None
        assert retrieved.id == conversation.id
        assert retrieved.title == "Test Conversation"
        
        # Verify messages are eagerly loaded
        assert hasattr(retrieved, 'messages')
        assert len(retrieved.messages) == 3
        
        # Verify message order (should be ordered by created_at as per relationship definition)
        messages = retrieved.messages
        assert messages[0].id == message1.id
        assert messages[0].content == "Hello, this is a user message"
        assert messages[0].sent_by == SenderType.USER
        
        assert messages[1].id == message2.id
        assert messages[1].content == "Hello! This is an assistant response"
        assert messages[1].sent_by == SenderType.ASSISTANT
        
        assert messages[2].id == message3.id
        assert messages[2].content == "Another user message"
        assert messages[2].sent_by == SenderType.USER

    def test_get_by_id_lazy_vs_eager_loading_comparison(self, db_session: Session):
        """Test that lazy and eager loading return the same conversation but with different message loading behavior."""
        from models.message import Message, SenderType
        
        # Create a test user
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # Create a conversation with messages
        conversation = Conversation.create_conversation(
            db=db_session,
            user_id=test_user.id,
            title="Test Conversation",
            prompt="Test prompt"
        )
        
        Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.USER,
            content="Test message"
        )

        # Retrieve with lazy loading
        lazy_retrieved = Conversation.get_by_id(
            db=db_session,
            conversation_id=conversation.id,
            with_messages=False
        )

        # Retrieve with eager loading
        eager_retrieved = Conversation.get_by_id(
            db=db_session,
            conversation_id=conversation.id,
            with_messages=True
        )

        # Both should return the same conversation data
        assert lazy_retrieved.id == eager_retrieved.id
        assert lazy_retrieved.title == eager_retrieved.title
        assert lazy_retrieved.prompt == eager_retrieved.prompt
        assert lazy_retrieved.user_id == eager_retrieved.user_id
        
        # Both should have messages attribute, but eager loading should have them preloaded
        assert hasattr(lazy_retrieved, 'messages')
        assert hasattr(eager_retrieved, 'messages')

    def test_get_by_id_not_found_lazy_loading(self, db_session: Session):
        """Test retrieving a conversation with non-existent ID returns None with lazy loading."""
        non_existent_id = 99999
        
        result = Conversation.get_by_id(
            db=db_session,
            conversation_id=non_existent_id,
            with_messages=False
        )
        
        assert result is None

    def test_get_by_id_not_found_eager_loading(self, db_session: Session):
        """Test retrieving a conversation with non-existent ID returns None with eager loading."""
        non_existent_id = 99999
        
        result = Conversation.get_by_id(
            db=db_session,
            conversation_id=non_existent_id,
            with_messages=True
        )
        
        assert result is None

    def test_get_by_id_with_zero_id(self, db_session: Session):
        """Test retrieving a conversation with ID 0 returns None."""
        result = Conversation.get_by_id(
            db=db_session,
            conversation_id=0,
            with_messages=True
        )
        
        assert result is None

    def test_get_by_id_with_negative_id(self, db_session: Session):
        """Test retrieving a conversation with negative ID returns None."""
        result = Conversation.get_by_id(
            db=db_session,
            conversation_id=-1,
            with_messages=False
        )
        
        assert result is None

    def test_get_by_id_eager_loading_message_order(self, db_session: Session):
        """Test that eager loading preserves message order (by created_at)."""
        from models.message import Message, SenderType
        import time
        
        # Create a test user
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # Create a conversation
        conversation = Conversation.create_conversation(
            db=db_session,
            user_id=test_user.id,
            title="Test Conversation",
            prompt="Test prompt"
        )

        # Add messages with slight delays to ensure different timestamps
        message1 = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.USER,
            content="First message"
        )
        
        time.sleep(0.01)  # Small delay to ensure different timestamps
        
        message2 = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.ASSISTANT,
            content="Second message"
        )
        
        time.sleep(0.01)
        
        message3 = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.USER,
            content="Third message"
        )

        # Retrieve with eager loading
        retrieved = Conversation.get_by_id(
            db=db_session,
            conversation_id=conversation.id,
            with_messages=True
        )

        # Verify messages are in correct chronological order
        messages = retrieved.messages
        assert len(messages) == 3
        assert messages[0].content == "First message"
        assert messages[1].content == "Second message"
        assert messages[2].content == "Third message"
        
        # Verify timestamps are in ascending order
        assert messages[0].created_at <= messages[1].created_at <= messages[2].created_at

    def test_get_by_id_eager_loading_large_number_of_messages(self, db_session: Session):
        """Test eager loading performance with many messages."""
        from models.message import Message, SenderType
        
        # Create a test user
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # Create a conversation
        conversation = Conversation.create_conversation(
            db=db_session,
            user_id=test_user.id,
            title="Conversation with Many Messages",
            prompt="Test prompt"
        )

        # Add many messages
        num_messages = 50
        for i in range(num_messages):
            sender = SenderType.USER if i % 2 == 0 else SenderType.ASSISTANT
            Message.create_message(
                db=db_session,
                conversation_id=conversation.id,
                sent_by=sender,
                content=f"Message number {i + 1}"
            )

        # Retrieve with eager loading
        retrieved = Conversation.get_by_id(
            db=db_session,
            conversation_id=conversation.id,
            with_messages=True
        )

        # Verify all messages are loaded
        assert retrieved is not None
        assert len(retrieved.messages) == num_messages
        
        # Verify first and last messages
        assert retrieved.messages[0].content == "Message number 1"
        assert retrieved.messages[-1].content == f"Message number {num_messages}"

    def test_get_by_id_return_type_with_eager_loading(self, db_session: Session):
        """Test that get_by_id returns the correct type with eager loading."""
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

        # Retrieve the conversation with eager loading
        retrieved = Conversation.get_by_id(
            db=db_session, 
            conversation_id=conversation.id,
            with_messages=True
        )

        # Verify return type and attributes
        assert isinstance(retrieved, Conversation)
        assert hasattr(retrieved, 'id')
        assert hasattr(retrieved, 'user_id')
        assert hasattr(retrieved, 'title')
        assert hasattr(retrieved, 'prompt')
        assert hasattr(retrieved, 'created_at')
        assert hasattr(retrieved, 'updated_at')
        assert hasattr(retrieved, 'messages')
        assert isinstance(retrieved.messages, list)
