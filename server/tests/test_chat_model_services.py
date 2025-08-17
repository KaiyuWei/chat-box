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
from services.chat_model_services import get_conversation_from_request, _generate_conversation_history, generate_prompt


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

    def test_messages_ordered_by_created_at_ascending(self, db_session: Session):
        """Test that messages are returned in ascending order by created_at timestamp."""
        import time
        
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
            title="Message Order Test",
            prompt="Test prompt"
        )

        # Add messages with explicit time delays to ensure different created_at timestamps
        message1 = Message(
            conversation_id=existing_conversation.id,
            sent_by=SenderType.USER,
            content="First message (oldest)"
        )
        db_session.add(message1)
        db_session.commit()
        
        # Small delay to ensure different timestamps
        time.sleep(0.01)
        
        message2 = Message(
            conversation_id=existing_conversation.id,
            sent_by=SenderType.ASSISTANT,
            content="Second message"
        )
        db_session.add(message2)
        db_session.commit()
        
        time.sleep(0.01)
        
        message3 = Message(
            conversation_id=existing_conversation.id,
            sent_by=SenderType.USER,
            content="Third message (newest)"
        )
        db_session.add(message3)
        db_session.commit()

        # Create chat request to retrieve the conversation
        chat_request = ChatRequest(
            conversation_id=existing_conversation.id,
            prompt="Ignored",
            messages=[
                ChatMessage(role=ChatRole.USER, content="New message")
            ]
        )

        # Call the function
        conversation = get_conversation_from_request(chat_request, db_session)

        # Verify messages are ordered by created_at in ascending order
        messages = conversation.messages
        assert len(messages) == 3
        
        # Check that messages are in chronological order (oldest first)
        assert messages[0].content == "First message (oldest)"
        assert messages[1].content == "Second message"  
        assert messages[2].content == "Third message (newest)"
        
        # Verify timestamps are actually in ascending order
        assert messages[0].created_at <= messages[1].created_at
        assert messages[1].created_at <= messages[2].created_at
        
        # Verify the order matches the insertion order
        expected_order = [message1.id, message2.id, message3.id]
        actual_order = [msg.id for msg in messages]
        assert actual_order == expected_order

    def test_messages_ordered_in_direct_conversation_access(self, db_session: Session):
        """Test that messages are ordered correctly when accessing conversation.messages directly."""
        import time
        
        # Create a test user
        test_user = User(
            username="testuser",
            email="test@example.com", 
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()

        # Create a conversation
        conversation = Conversation.create_conversation(
            db=db_session,
            user_id=1,
            title="Direct Access Test",
            prompt="Test prompt"
        )

        # Add messages in a specific order
        messages_data = [
            ("Message A - First", SenderType.USER),
            ("Message B - Second", SenderType.ASSISTANT),
            ("Message C - Third", SenderType.USER),
            ("Message D - Fourth", SenderType.ASSISTANT),
            ("Message E - Fifth", SenderType.USER)
        ]
        
        created_message_ids = []
        for content, sender_type in messages_data:
            message = Message(
                conversation_id=conversation.id,
                sent_by=sender_type,
                content=content
            )
            db_session.add(message)
            db_session.commit()
            created_message_ids.append(message.id)
            time.sleep(0.01)  # Ensure different timestamps

        # Refresh the conversation to get updated relationship
        db_session.refresh(conversation)
        
        # Access messages directly through the relationship
        messages = conversation.messages
        
        # Verify correct order (oldest first)
        assert len(messages) == 5
        assert messages[0].content == "Message A - First"
        assert messages[1].content == "Message B - Second"
        assert messages[2].content == "Message C - Third"
        assert messages[3].content == "Message D - Fourth"
        assert messages[4].content == "Message E - Fifth"
        
        # Verify timestamps are in ascending order
        for i in range(len(messages) - 1):
            assert messages[i].created_at <= messages[i + 1].created_at
            
        # Verify IDs match the creation order
        actual_ids = [msg.id for msg in messages]
        assert actual_ids == created_message_ids

    def test_messages_ordered_with_bulk_insert(self, db_session: Session):
        """Test message ordering when messages are inserted in bulk (out of chronological order)."""
        import time
        from datetime import datetime, timedelta, timezone
        
        # Create a test user
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()

        # Create a conversation
        conversation = Conversation.create_conversation(
            db=db_session,
            user_id=1,
            title="Bulk Insert Test",
            prompt="Test prompt"
        )

        # Create messages with specific timestamps (simulating out-of-order insertion)
        base_time = datetime.now(timezone.utc)
        
        # Create message objects with manually set created_at times
        message3 = Message(
            conversation_id=conversation.id,
            sent_by=SenderType.USER,
            content="Third message chronologically"
        )
        
        message1 = Message(
            conversation_id=conversation.id,
            sent_by=SenderType.USER,
            content="First message chronologically"
        )
        
        message2 = Message(
            conversation_id=conversation.id,
            sent_by=SenderType.ASSISTANT,
            content="Second message chronologically"
        )
        
        # Add them to session in non-chronological order
        db_session.add_all([message3, message1, message2])
        db_session.commit()
        
        # Now manually update their created_at timestamps to simulate different creation times
        # Note: We need to do this after commit to ensure the timestamps are set
        message1.created_at = base_time
        message2.created_at = base_time + timedelta(seconds=1)
        message3.created_at = base_time + timedelta(seconds=2)
        
        db_session.commit()
        
        # Refresh the conversation
        db_session.refresh(conversation)
        
        # Verify messages are ordered by created_at, not insertion order
        messages = conversation.messages
        assert len(messages) == 3
        
        # Should be ordered by created_at (ascending)
        assert messages[0].content == "First message chronologically"
        assert messages[1].content == "Second message chronologically"
        assert messages[2].content == "Third message chronologically"
        
        # Verify timestamps are in correct order
        assert messages[0].created_at < messages[1].created_at < messages[2].created_at


class TestGenerateConversationHistory:
    """Test the _generate_conversation_history function."""

    def _create_test_conversation_with_messages(self, db_session: Session, messages_data: list, prompt: str = "Test system prompt") -> Conversation:
        """Helper method to create a conversation with specified messages."""
        # Create a test user
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()

        # Create a conversation
        conversation = Conversation.create_conversation(
            db=db_session,
            user_id=test_user.id,
            title="Test Conversation",
            prompt=prompt
        )

        # Add messages to the conversation
        for content, sender_type in messages_data:
            message = Message(
                conversation_id=conversation.id,
                sent_by=sender_type,
                content=content
            )
            db_session.add(message)
        
        db_session.commit()
        db_session.refresh(conversation)
        return conversation

    def test_generate_conversation_history_with_mixed_messages(self, db_session: Session):
        """Test conversation history generation with mixed user and assistant messages."""
        messages_data = [
            ("Hello, how are you today?", SenderType.USER),
            ("I'm doing well, thank you! How can I help you?", SenderType.ASSISTANT),
            ("Can you explain quantum computing?", SenderType.USER),
            ("Quantum computing uses quantum mechanics principles...", SenderType.ASSISTANT),
        ]
        
        conversation = self._create_test_conversation_with_messages(db_session, messages_data, "You are a helpful assistant.")
        
        # Call the function
        result = _generate_conversation_history(conversation)
        
        # Expected output - list of dictionaries
        expected = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you today?"},
            {"role": "assistant", "content": "I'm doing well, thank you! How can I help you?"},
            {"role": "user", "content": "Can you explain quantum computing?"},
            {"role": "assistant", "content": "Quantum computing uses quantum mechanics principles..."}
        ]
        
        assert result == expected

    def test_generate_conversation_history_with_only_user_messages(self, db_session: Session):
        """Test conversation history generation with only user messages."""
        messages_data = [
            ("First user message", SenderType.USER),
            ("Second user message", SenderType.USER),
        ]
        
        conversation = self._create_test_conversation_with_messages(db_session, messages_data, "Custom prompt")
        
        # Call the function
        result = _generate_conversation_history(conversation)
        
        # Expected output
        expected = [
            {"role": "system", "content": "Custom prompt"},
            {"role": "user", "content": "First user message"},
            {"role": "user", "content": "Second user message"}
        ]
        
        assert result == expected

    def test_generate_conversation_history_with_only_assistant_messages(self, db_session: Session):
        """Test conversation history generation with only assistant messages."""
        messages_data = [
            ("First assistant response", SenderType.ASSISTANT),
            ("Second assistant response", SenderType.ASSISTANT),
        ]
        
        conversation = self._create_test_conversation_with_messages(db_session, messages_data, "Assistant only prompt")
        
        # Call the function
        result = _generate_conversation_history(conversation)
        
        # Expected output
        expected = [
            {"role": "system", "content": "Assistant only prompt"},
            {"role": "assistant", "content": "First assistant response"},
            {"role": "assistant", "content": "Second assistant response"}
        ]
        
        assert result == expected

    def test_generate_conversation_history_with_empty_messages(self, db_session: Session):
        """Test conversation history generation with no messages."""
        messages_data = []  # No messages
        
        conversation = self._create_test_conversation_with_messages(db_session, messages_data, "System only prompt")
        
        # Call the function
        result = _generate_conversation_history(conversation)
        
        # Should only include system message when no conversation messages
        expected = [
            {"role": "system", "content": "System only prompt"}
        ]
        
        assert result == expected

    def test_generate_conversation_history_preserves_message_order(self, db_session: Session):
        """Test that conversation history preserves chronological message order."""
        messages_data = [
            ("Message 1 - First", SenderType.USER),
            ("Message 2 - Response to first", SenderType.ASSISTANT),
            ("Message 3 - Follow up", SenderType.USER),
            ("Message 4 - Final response", SenderType.ASSISTANT),
        ]
        
        conversation = self._create_test_conversation_with_messages(db_session, messages_data, "Order test prompt")
        
        # Call the function
        result = _generate_conversation_history(conversation)
        
        # Verify the structure and order
        assert len(result) == 5  # 1 system + 4 messages
        assert result[0] == {"role": "system", "content": "Order test prompt"}
        assert result[1] == {"role": "user", "content": "Message 1 - First"}
        assert result[2] == {"role": "assistant", "content": "Message 2 - Response to first"}
        assert result[3] == {"role": "user", "content": "Message 3 - Follow up"}
        assert result[4] == {"role": "assistant", "content": "Message 4 - Final response"}

    def test_generate_conversation_history_with_special_characters(self, db_session: Session):
        """Test conversation history generation with special characters and formatting."""
        messages_data = [
            ("Hello! 👋 How are you? @#$%^&*()", SenderType.USER),
            ("I'm great! Here's some code: `print('Hello')` 🚀", SenderType.ASSISTANT),
            ("What about newlines?\nAnd tabs?\tDo they work?", SenderType.USER),
        ]
        
        conversation = self._create_test_conversation_with_messages(db_session, messages_data, "Special chars prompt")
        
        # Call the function
        result = _generate_conversation_history(conversation)
        
        # Expected output - special characters should be preserved
        expected = [
            {"role": "system", "content": "Special chars prompt"},
            {"role": "user", "content": "Hello! 👋 How are you? @#$%^&*()"},
            {"role": "assistant", "content": "I'm great! Here's some code: `print('Hello')` 🚀"},
            {"role": "user", "content": "What about newlines?\nAnd tabs?\tDo they work?"}
        ]
        
        assert result == expected


class TestGeneratePrompt:
    """Test the generate_prompt function."""

    def _create_test_conversation_with_messages(self, db_session: Session, messages_data: list, prompt: str = "Test system prompt") -> Conversation:
        """Helper method to create a conversation with specified messages."""
        # Create a test user
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()

        # Create a conversation
        conversation = Conversation.create_conversation(
            db=db_session,
            user_id=test_user.id,
            title="Test Conversation",
            prompt=prompt
        )

        # Add messages to the conversation
        for content, sender_type in messages_data:
            message = Message(
                conversation_id=conversation.id,
                sent_by=sender_type,
                content=content
            )
            db_session.add(message)
        
        db_session.commit()
        db_session.refresh(conversation)
        return conversation

    def test_generate_prompt_with_conversation_history(self, db_session: Session):
        """Test generate_prompt with existing conversation history."""
        messages_data = [
            ("Hello, how are you today?", SenderType.USER),
            ("I'm doing well, thank you! How can I help you?", SenderType.ASSISTANT),
        ]
        
        conversation = self._create_test_conversation_with_messages(db_session, messages_data, "You are a helpful assistant.")
        new_message = "Tell me about elephants"
        
        # Call the function
        result = generate_prompt(conversation, new_message)
        
        # Expected output - history + new message
        expected = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you today?"},
            {"role": "assistant", "content": "I'm doing well, thank you! How can I help you?"},
            {"role": "user", "content": "Tell me about elephants"}
        ]
        
        assert result == expected

    def test_generate_prompt_with_empty_conversation(self, db_session: Session):
        """Test generate_prompt with no existing messages."""
        messages_data = []  # No messages
        
        conversation = self._create_test_conversation_with_messages(db_session, messages_data, "You are a helpful chatbot.")
        new_message = "Hello world!"
        
        # Call the function
        result = generate_prompt(conversation, new_message)
        
        # Expected output - only system prompt + new message
        expected = [
            {"role": "system", "content": "You are a helpful chatbot."},
            {"role": "user", "content": "Hello world!"}
        ]
        
        assert result == expected

    def test_generate_prompt_with_long_conversation(self, db_session: Session):
        """Test generate_prompt with a longer conversation history."""
        messages_data = [
            ("What's the capital of France?", SenderType.USER),
            ("The capital of France is Paris.", SenderType.ASSISTANT),
            ("What about Germany?", SenderType.USER),
            ("The capital of Germany is Berlin.", SenderType.ASSISTANT),
            ("And Italy?", SenderType.USER),
            ("The capital of Italy is Rome.", SenderType.ASSISTANT),
        ]
        
        conversation = self._create_test_conversation_with_messages(db_session, messages_data, "Geography expert assistant")
        new_message = "What about Spain?"
        
        # Call the function
        result = generate_prompt(conversation, new_message)
        
        # Expected output - full history + new message
        expected = [
            {"role": "system", "content": "Geography expert assistant"},
            {"role": "user", "content": "What's the capital of France?"},
            {"role": "assistant", "content": "The capital of France is Paris."},
            {"role": "user", "content": "What about Germany?"},
            {"role": "assistant", "content": "The capital of Germany is Berlin."},
            {"role": "user", "content": "And Italy?"},
            {"role": "assistant", "content": "The capital of Italy is Rome."},
            {"role": "user", "content": "What about Spain?"}
        ]
        
        assert result == expected

    def test_generate_prompt_preserves_message_order(self, db_session: Session):
        """Test that generate_prompt preserves chronological message order."""
        messages_data = [
            ("First question", SenderType.USER),
            ("First answer", SenderType.ASSISTANT),
            ("Second question", SenderType.USER),
            ("Second answer", SenderType.ASSISTANT),
        ]
        
        conversation = self._create_test_conversation_with_messages(db_session, messages_data, "Order preservation test")
        new_message = "Third question"
        
        # Call the function
        result = generate_prompt(conversation, new_message)
        
        # Verify structure and order
        assert len(result) == 6  # 1 system + 4 history + 1 new
        assert result[0]["role"] == "system"
        assert result[1]["role"] == "user" and result[1]["content"] == "First question"
        assert result[2]["role"] == "assistant" and result[2]["content"] == "First answer"
        assert result[3]["role"] == "user" and result[3]["content"] == "Second question"
        assert result[4]["role"] == "assistant" and result[4]["content"] == "Second answer"
        assert result[5]["role"] == "user" and result[5]["content"] == "Third question"

    def test_generate_prompt_with_special_characters_in_new_message(self, db_session: Session):
        """Test generate_prompt with special characters in the new message."""
        messages_data = [
            ("Hello", SenderType.USER),
            ("Hi there!", SenderType.ASSISTANT),
        ]
        
        conversation = self._create_test_conversation_with_messages(db_session, messages_data, "Test assistant")
        new_message = "Can you help with this code? `print('Hello 🌍')`\nThanks!"
        
        # Call the function
        result = generate_prompt(conversation, new_message)
        
        # Verify the new message is preserved correctly
        assert result[-1]["role"] == "user"
        assert result[-1]["content"] == "Can you help with this code? `print('Hello 🌍')`\nThanks!"
        
        # Verify full structure
        expected = [
            {"role": "system", "content": "Test assistant"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "Can you help with this code? `print('Hello 🌍')`\nThanks!"}
        ]
        
        assert result == expected
