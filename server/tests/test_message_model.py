"""
Integration tests for Message model methods.

These tests verify the database interaction behavior of Message model methods
using a real SQLite database in memory.
"""

import pytest
from datetime import datetime
from models.message import Message, SenderType
from models.conversation import Conversation
from models.user import User
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


class TestCreateMessageFunction:
    """Test the create_message function."""

    def _create_test_user_and_conversation(self, db_session: Session) -> tuple[User, Conversation]:
        """Helper method to create a test user and conversation for message tests."""
        # Create a test user
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # Create a test conversation
        conversation = Conversation.create_conversation(
            db=db_session,
            user_id=test_user.id,
            title="Test Conversation",
            prompt="Test prompt"
        )
        
        return test_user, conversation

    def test_create_message_user_success(self, db_session: Session):
        """Test successful creation of a user message."""
        user, conversation = self._create_test_user_and_conversation(db_session)
        
        content = "Hello, how are you today?"
        
        message = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.USER,
            content=content
        )

        # Verify message was created correctly
        assert message is not None
        assert isinstance(message, Message)
        assert message.id is not None
        assert message.conversation_id == conversation.id
        assert message.sent_by == SenderType.USER
        assert message.content == content
        assert message.created_at is not None
        assert isinstance(message.created_at, datetime)
        
        # Verify it's in the database
        db_message = db_session.query(Message).filter(
            Message.id == message.id
        ).first()
        assert db_message is not None
        assert db_message.content == content
        assert db_message.sent_by == SenderType.USER

    def test_create_message_assistant_success(self, db_session: Session):
        """Test successful creation of an assistant message."""
        user, conversation = self._create_test_user_and_conversation(db_session)
        
        content = "I'm doing well, thank you! How can I help you today?"
        
        message = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.ASSISTANT,
            content=content
        )

        # Verify message was created correctly
        assert message is not None
        assert isinstance(message, Message)
        assert message.id is not None
        assert message.conversation_id == conversation.id
        assert message.sent_by == SenderType.ASSISTANT
        assert message.content == content
        assert message.created_at is not None
        assert isinstance(message.created_at, datetime)

    def test_create_message_with_long_content(self, db_session: Session):
        """Test creating message with maximum length content (4000 chars)."""
        user, conversation = self._create_test_user_and_conversation(db_session)
        
        # Create content at the maximum length (4000 chars)
        long_content = "A" * 4000
        
        message = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.USER,
            content=long_content
        )

        assert message is not None
        assert message.content == long_content
        assert len(message.content) == 4000

    def test_create_message_with_special_characters(self, db_session: Session):
        """Test creating message with special characters and formatting."""
        user, conversation = self._create_test_user_and_conversation(db_session)
        
        content = "Hello! 👋 How are you? @#$%^&*()_+-=[]{}|;':\",./<>?"
        
        message = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.USER,
            content=content
        )

        assert message is not None
        assert message.content == content

    def test_create_message_with_unicode_characters(self, db_session: Session):
        """Test creating message with unicode characters."""
        user, conversation = self._create_test_user_and_conversation(db_session)
        
        content = "Unicode test: 你好世界 - Привет мир - مرحبا بالعالم 🚀"
        
        message = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.ASSISTANT,
            content=content
        )

        assert message is not None
        assert message.content == content

    def test_create_message_with_newlines_and_tabs(self, db_session: Session):
        """Test creating message with newlines and tab characters."""
        user, conversation = self._create_test_user_and_conversation(db_session)
        
        content = "Line 1\nLine 2\n\tIndented line\n\nEmpty line above"
        
        message = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.USER,
            content=content
        )

        assert message is not None
        assert message.content == content
        assert "\n" in message.content
        assert "\t" in message.content

    def test_create_message_with_empty_content(self, db_session: Session):
        """Test creating message with empty content."""
        user, conversation = self._create_test_user_and_conversation(db_session)
        
        content = ""
        
        message = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.USER,
            content=content
        )

        assert message is not None
        assert message.content == ""

    def test_create_message_with_invalid_conversation_id(self, db_session: Session):
        """Test creating message with non-existent conversation_id."""
        non_existent_conversation_id = 99999
        content = "This should fail"
        
        # This should raise an IntegrityError due to foreign key constraint
        with pytest.raises(IntegrityError):
            Message.create_message(
                db=db_session,
                conversation_id=non_existent_conversation_id,
                sent_by=SenderType.USER,
                content=content
            )

    def test_create_multiple_messages_same_conversation(self, db_session: Session):
        """Test creating multiple messages in the same conversation."""
        user, conversation = self._create_test_user_and_conversation(db_session)
        
        # Create first message (user)
        message1 = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.USER,
            content="Hello, how are you?"
        )

        # Create second message (assistant)
        message2 = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.ASSISTANT,
            content="I'm doing well, thank you!"
        )

        # Create third message (user)
        message3 = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.USER,
            content="That's great to hear!"
        )

        # Verify all messages exist and are different
        assert message1.id != message2.id != message3.id
        assert message1.content != message2.content != message3.content
        assert message1.sent_by != message2.sent_by
        assert message2.sent_by != message3.sent_by
        assert message1.conversation_id == message2.conversation_id == message3.conversation_id

        # Verify all are in database
        messages = db_session.query(Message).filter(
            Message.conversation_id == conversation.id
        ).all()
        assert len(messages) == 3

    def test_create_message_timestamps(self, db_session: Session):
        """Test that timestamps are set correctly."""
        user, conversation = self._create_test_user_and_conversation(db_session)
        
        message = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.USER,
            content="Test timestamp message"
        )

        # Verify timestamps
        assert message.created_at is not None
        assert isinstance(message.created_at, datetime)
        
        # updated_at should be None initially (only set on updates)
        assert message.updated_at is None

    def test_create_message_cascade_delete_with_conversation(self, db_session: Session):
        """Test that messages are deleted when conversation is deleted (CASCADE)."""
        user, conversation = self._create_test_user_and_conversation(db_session)
        
        # Create messages
        message1 = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.USER,
            content="First message"
        )
        
        message2 = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.ASSISTANT,
            content="Second message"
        )
        
        message1_id = message1.id
        message2_id = message2.id
        conversation_id = conversation.id

        # Verify messages exist
        assert db_session.query(Message).filter(Message.id == message1_id).first() is not None
        assert db_session.query(Message).filter(Message.id == message2_id).first() is not None

        # Delete the conversation
        db_session.delete(conversation)
        db_session.commit()

        # Verify messages are also deleted due to CASCADE
        assert db_session.query(Message).filter(Message.id == message1_id).first() is None
        assert db_session.query(Message).filter(Message.id == message2_id).first() is None

    def test_create_message_cascade_delete_with_user(self, db_session: Session):
        """Test that messages are deleted when user is deleted (CASCADE through conversation)."""
        user, conversation = self._create_test_user_and_conversation(db_session)
        
        # Create messages
        message1 = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.USER,
            content="First message"
        )
        
        message2 = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.ASSISTANT,
            content="Second message"
        )
        
        message1_id = message1.id
        message2_id = message2.id

        # Verify messages exist
        assert db_session.query(Message).filter(Message.id == message1_id).first() is not None
        assert db_session.query(Message).filter(Message.id == message2_id).first() is not None

        # Delete the user (which should cascade delete conversation and messages)
        db_session.delete(user)
        db_session.commit()

        # Verify messages are also deleted due to CASCADE
        assert db_session.query(Message).filter(Message.id == message1_id).first() is None
        assert db_session.query(Message).filter(Message.id == message2_id).first() is None

    def test_create_message_return_type(self, db_session: Session):
        """Test that create_message returns the correct type."""
        user, conversation = self._create_test_user_and_conversation(db_session)
        
        message = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.USER,
            content="Type test message"
        )

        # Verify return type
        assert isinstance(message, Message)
        assert hasattr(message, 'id')
        assert hasattr(message, 'conversation_id')
        assert hasattr(message, 'sent_by')
        assert hasattr(message, 'content')
        assert hasattr(message, 'created_at')
        assert hasattr(message, 'updated_at')

    def test_create_message_relationship_access(self, db_session: Session):
        """Test that message can access its conversation through relationship."""
        user, conversation = self._create_test_user_and_conversation(db_session)
        
        message = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.USER,
            content="Relationship test message"
        )

        # Access conversation through relationship
        related_conversation = message.conversation
        
        assert related_conversation is not None
        assert isinstance(related_conversation, Conversation)
        assert related_conversation.id == conversation.id
        assert related_conversation.title == conversation.title
        assert related_conversation.prompt == conversation.prompt

    def test_create_message_with_different_conversations(self, db_session: Session):
        """Test creating messages in different conversations."""
        user, conversation1 = self._create_test_user_and_conversation(db_session)
        
        # Create second conversation for the same user
        conversation2 = Conversation.create_conversation(
            db=db_session,
            user_id=user.id,
            title="Second Test Conversation",
            prompt="Second test prompt"
        )

        # Create messages in different conversations
        message1 = Message.create_message(
            db=db_session,
            conversation_id=conversation1.id,
            sent_by=SenderType.USER,
            content="Message in first conversation"
        )
        
        message2 = Message.create_message(
            db=db_session,
            conversation_id=conversation2.id,
            sent_by=SenderType.ASSISTANT,
            content="Message in second conversation"
        )

        # Verify messages are in correct conversations
        assert message1.conversation_id == conversation1.id
        assert message2.conversation_id == conversation2.id
        assert message1.conversation_id != message2.conversation_id

        # Verify each conversation has the correct message
        conv1_messages = db_session.query(Message).filter(
            Message.conversation_id == conversation1.id
        ).all()
        conv2_messages = db_session.query(Message).filter(
            Message.conversation_id == conversation2.id
        ).all()
        
        assert len(conv1_messages) == 1
        assert len(conv2_messages) == 1
        assert conv1_messages[0].content == "Message in first conversation"
        assert conv2_messages[0].content == "Message in second conversation"

    def test_create_message_chronological_order(self, db_session: Session):
        """Test that messages are created with proper chronological timestamps."""
        import time
        
        user, conversation = self._create_test_user_and_conversation(db_session)
        
        # Create messages with small delays to ensure different timestamps
        message1 = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.USER,
            content="First message"
        )
        
        time.sleep(0.01)  # Small delay
        
        message2 = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.ASSISTANT,
            content="Second message"
        )
        
        time.sleep(0.01)  # Small delay
        
        message3 = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.USER,
            content="Third message"
        )

        # Verify chronological order
        assert message1.created_at <= message2.created_at
        assert message2.created_at <= message3.created_at
        
        # Verify database ordering (should match creation order due to ordering in conversation model)
        messages = db_session.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at).all()
        
        assert len(messages) == 3
        assert messages[0].id == message1.id
        assert messages[1].id == message2.id
        assert messages[2].id == message3.id

    def test_create_message_with_code_content(self, db_session: Session):
        """Test creating message with code content."""
        user, conversation = self._create_test_user_and_conversation(db_session)
        
        code_content = '''Here's a Python function:

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Example usage
print(fibonacci(10))
```

This function calculates Fibonacci numbers recursively.'''
        
        message = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.ASSISTANT,
            content=code_content
        )

        assert message is not None
        assert message.content == code_content
        assert "```python" in message.content
        assert "def fibonacci" in message.content

    def test_create_message_with_markdown_content(self, db_session: Session):
        """Test creating message with markdown formatted content."""
        user, conversation = self._create_test_user_and_conversation(db_session)
        
        markdown_content = '''# Heading 1

## Heading 2

Here's some **bold text** and *italic text*.

- Bullet point 1
- Bullet point 2
  - Nested bullet
  
1. Numbered item 1
2. Numbered item 2

[Link example](https://example.com)

> This is a blockquote

`inline code` example'''
        
        message = Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.ASSISTANT,
            content=markdown_content
        )

        assert message is not None
        assert message.content == markdown_content
        assert "# Heading 1" in message.content
        assert "**bold text**" in message.content
        assert "`inline code`" in message.content
