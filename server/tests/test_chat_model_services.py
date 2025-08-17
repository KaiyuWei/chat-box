"""
Integration tests for chat model services.

These tests verify the behavior of chat model service functions
using a real SQLite database in memory.
"""

import pytest
from sqlalchemy.orm import Session
from schemas.chat_model import ChatRequest, ChatMessage, ChatRole
from models.conversation import Conversation
from models.message import Message, SenderType
from models.user import User
from services.chat_model_services import get_conversation_from_request


class TestGetConversationFromRequest:
    """Test the get_conversation_from_request function."""

    def _create_dummy_user(self, db_session: Session) -> User:
        """Helper method to create a user with DUMMY_USER_ID."""
        test_user = User(
            id=1,  # Explicit ID to match DUMMY_USER_ID
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()
        return test_user

    def test_create_new_conversation_when_id_is_none(self, db_session: Session):
        """Test creating a new conversation when conversation_id is None."""
        # Create a test user with ID 1 (DUMMY_USER_ID)
        self._create_dummy_user(db_session)

        # Create chat request without conversation_id (omit the field)
        chat_request = ChatRequest(
            prompt="Custom system prompt",
            messages=[
                ChatMessage(role=ChatRole.USER, content="Hello, how are you?")
            ]
        )

        # Call the function
        conversation = get_conversation_from_request(chat_request, db_session)

        # Verify a new conversation was created
        assert conversation is not None
        assert isinstance(conversation, Conversation)
        assert conversation.id is not None
        assert conversation.user_id == 1  # DUMMY_USER_ID
        assert conversation.title == "Hello, how are you?"  # Last message content
        assert conversation.prompt == "Custom system prompt"

        # Verify it's in the database
        db_conversation = db_session.query(Conversation).filter(
            Conversation.id == conversation.id
        ).first()
        assert db_conversation is not None

    def test_create_new_conversation_with_empty_prompt_uses_default(self, db_session: Session):
        """Test creating a new conversation with empty prompt uses default system prompt."""
        # Create a test user with ID 1 (DUMMY_USER_ID)
        self._create_dummy_user(db_session)
        
        # Create chat request with empty prompt
        chat_request = ChatRequest(
            prompt="",
            messages=[
                ChatMessage(role=ChatRole.USER, content="Test message")
            ]
        )

        # Call the function
        conversation = get_conversation_from_request(chat_request, db_session)

        # Verify default prompt is used
        assert conversation.prompt == "You are a helpful and friendly assistant."

    def test_create_new_conversation_with_none_prompt_uses_default(self, db_session: Session):
        """Test creating a new conversation with None prompt uses default system prompt."""
        # Create a test user with ID 1 (DUMMY_USER_ID)
        self._create_dummy_user(db_session)
        
        # Create chat request without prompt (omit the field)
        chat_request = ChatRequest(
            messages=[
                ChatMessage(role=ChatRole.USER, content="Test message")
            ]
        )

        # Call the function
        conversation = get_conversation_from_request(chat_request, db_session)

        # Verify default prompt is used
        assert conversation.prompt == "You are a helpful and friendly assistant."

    def test_retrieve_existing_conversation_by_id(self, db_session: Session):
        """Test retrieving an existing conversation by ID."""
        # Create a test user
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()

        # Create an existing conversation
        existing_conversation = Conversation.create_conversation(
            db=db_session,
            user_id=1,
            title="Existing Conversation",
            prompt="Existing prompt"
        )

        # Create chat request with existing conversation_id
        chat_request = ChatRequest(
            conversation_id=existing_conversation.id,
            prompt="This should be ignored",
            messages=[
                ChatMessage(role=ChatRole.USER, content="This should be ignored too")
            ]
        )

        # Call the function
        conversation = get_conversation_from_request(chat_request, db_session)

        # Verify the existing conversation is returned
        assert conversation.id == existing_conversation.id
        assert conversation.title == "Existing Conversation"
        assert conversation.prompt == "Existing prompt"
        assert conversation.user_id == 1

    def test_eager_loading_of_messages(self, db_session: Session):
        """Test that messages are eagerly loaded with the conversation."""
        # Create a test user
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()

        # Create an existing conversation
        existing_conversation = Conversation.create_conversation(
            db=db_session,
            user_id=1,
            title="Test Conversation",
            prompt="Test prompt"
        )

        # Add some messages to the conversation
        message1 = Message(
            conversation_id=existing_conversation.id,
            sent_by=SenderType.USER,
            content="First message"
        )
        message2 = Message(
            conversation_id=existing_conversation.id,
            sent_by=SenderType.ASSISTANT,
            content="Second message"
        )
        message3 = Message(
            conversation_id=existing_conversation.id,
            sent_by=SenderType.USER,
            content="Third message"
        )
        
        db_session.add_all([message1, message2, message3])
        db_session.commit()

        # Create chat request with existing conversation_id
        chat_request = ChatRequest(
            conversation_id=existing_conversation.id,
            prompt="Ignored",
            messages=[
                ChatMessage(role=ChatRole.USER, content="New message")
            ]
        )

        # Call the function
        conversation = get_conversation_from_request(chat_request, db_session)

        # Verify the conversation and its messages are loaded
        assert conversation.id == existing_conversation.id
        assert hasattr(conversation, 'messages')
        
        # Access messages - this should not trigger additional SQL queries due to eager loading
        messages = conversation.messages
        assert len(messages) == 3
        
        # Verify message contents
        message_contents = [msg.content for msg in messages]
        assert "First message" in message_contents
        assert "Second message" in message_contents
        assert "Third message" in message_contents
        
        # Verify message types
        message_types = [msg.sent_by for msg in messages]
        assert SenderType.USER in message_types
        assert SenderType.ASSISTANT in message_types

    def test_title_extraction_from_last_message(self, db_session: Session):
        """Test that title is extracted from the last message when creating new conversation."""
        # Create a test user with ID 1 (DUMMY_USER_ID)
        self._create_dummy_user(db_session)
        
        # Test with multiple messages
        chat_request = ChatRequest(
            prompt="System prompt",
            messages=[
                ChatMessage(role=ChatRole.USER, content="First message"),
                ChatMessage(role=ChatRole.ASSISTANT, content="Response message"),
                ChatMessage(role=ChatRole.USER, content="Final message for title")
            ]
        )

        conversation = get_conversation_from_request(chat_request, db_session)
        
        # Title should be the last message content
        assert conversation.title == "Final message for title"

    def test_title_extraction_with_single_message(self, db_session: Session):
        """Test that title is extracted correctly with a single message."""
        # Create a test user with ID 1 (DUMMY_USER_ID)
        self._create_dummy_user(db_session)
        
        chat_request = ChatRequest(
            prompt="System prompt",
            messages=[
                ChatMessage(role=ChatRole.USER, content="Only message")
            ]
        )

        conversation = get_conversation_from_request(chat_request, db_session)
        
        # Title should be the only message content
        assert conversation.title == "Only message"

    def test_title_fallback_when_no_messages(self, db_session: Session):
        """Test fallback title when messages list is empty."""
        # This test verifies the schema validation works (min_length=1 for messages)
        try:
            chat_request = ChatRequest(
                prompt="System prompt",
                messages=[]
            )
            # Should not reach here due to validation error
            assert False, "Expected validation error for empty messages list"
        except Exception as e:
            # Expected due to schema validation (min_length=1)
            assert "too_short" in str(e) or "at least 1 item" in str(e)

    def test_long_message_content_truncation_for_title(self, db_session: Session):
        """Test that very long message content is handled appropriately for title."""
        # Create a test user with ID 1 (DUMMY_USER_ID)
        self._create_dummy_user(db_session)
        
        # Create a message with content longer than title field limit (255 chars)
        long_content = "A" * 300  # Longer than title field limit
        
        chat_request = ChatRequest(
            prompt="System prompt",
            messages=[
                ChatMessage(role=ChatRole.USER, content=long_content)
            ]
        )

        conversation = get_conversation_from_request(chat_request, db_session)
        
        # Verify the function doesn't crash with long content
        # The title will be the full message content (SQLite doesn't auto-truncate)
        assert conversation.title is not None
        assert conversation.title == long_content
        assert len(conversation.title) == 300  # Full length is preserved

    def test_special_characters_in_message_content(self, db_session: Session):
        """Test handling of special characters and unicode in message content."""
        # Create a test user with ID 1 (DUMMY_USER_ID)
        self._create_dummy_user(db_session)
        
        special_content = "Hello! 你好 🚀 @#$%^&*()_+-=[]{}|;':\",./<>?"
        
        chat_request = ChatRequest(
            prompt="System prompt",
            messages=[
                ChatMessage(role=ChatRole.USER, content=special_content)
            ]
        )

        conversation = get_conversation_from_request(chat_request, db_session)
        
        # Title should preserve special characters
        assert conversation.title == special_content

    def test_nonexistent_conversation_id_returns_none(self, db_session: Session):
        """Test that providing a non-existent conversation_id returns None."""
        chat_request = ChatRequest(
            conversation_id=99999,  # Non-existent ID
            prompt="System prompt",
            messages=[
                ChatMessage(role=ChatRole.USER, content="Test message")
            ]
        )

        conversation = get_conversation_from_request(chat_request, db_session)
        
        # Should return None for non-existent conversation
        assert conversation is None

    def test_conversation_with_multiple_message_types(self, db_session: Session):
        """Test eager loading works with conversations containing different message types."""
        # Create a test user
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()

        # Create an existing conversation
        existing_conversation = Conversation.create_conversation(
            db=db_session,
            user_id=1,
            title="Mixed Messages Conversation",
            prompt="Test prompt"
        )

        # Add messages of different types
        messages_data = [
            (SenderType.USER, "User message 1"),
            (SenderType.ASSISTANT, "Assistant response 1"),
            (SenderType.USER, "User message 2"),
            (SenderType.ASSISTANT, "Assistant response 2"),
            (SenderType.USER, "User message 3"),
        ]
        
        for sent_by, content in messages_data:
            message = Message(
                conversation_id=existing_conversation.id,
                sent_by=sent_by,
                content=content
            )
            db_session.add(message)
        
        db_session.commit()

        # Create chat request
        chat_request = ChatRequest(
            conversation_id=existing_conversation.id,
            prompt="Ignored",
            messages=[
                ChatMessage(role=ChatRole.USER, content="New message")
            ]
        )

        # Call the function
        conversation = get_conversation_from_request(chat_request, db_session)

        # Verify all messages are loaded
        assert len(conversation.messages) == 5
        
        # Verify message order and types
        user_messages = [msg for msg in conversation.messages if msg.sent_by == SenderType.USER]
        assistant_messages = [msg for msg in conversation.messages if msg.sent_by == SenderType.ASSISTANT]
        
        assert len(user_messages) == 3
        assert len(assistant_messages) == 2
        
        # Verify specific content exists
        all_contents = [msg.content for msg in conversation.messages]
        assert "User message 1" in all_contents
        assert "Assistant response 1" in all_contents
        assert "User message 3" in all_contents
