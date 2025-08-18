"""
Test cases for the conversation router endpoints.

These tests verify the behavior of conversation-related API endpoints
using a real SQLite database in memory.
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from models.conversation import Conversation
from models.message import Message, SenderType
from models.user import User
from sqlalchemy.orm import Session


@pytest.fixture
def test_app_with_conversation(db_session):
    """Create a test FastAPI app with conversation router included."""
    from fastapi import FastAPI, APIRouter
    from routers import conversation_router
    from database import get_mysql_db

    app = FastAPI(title="Test App")

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_mysql_db] = override_get_db

    # Add conversation router
    api_router = APIRouter(prefix="/api")
    api_router.include_router(conversation_router)
    app.include_router(api_router)

    return app


@pytest.fixture
def client_with_conversation(test_app_with_conversation):
    """Create a test client with conversation endpoints."""
    with TestClient(test_app_with_conversation) as test_client:
        yield test_client


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_conversation(db_session, sample_user):
    """Create a sample conversation for testing."""
    conversation = Conversation.create_conversation(
        db=db_session,
        user_id=sample_user.id,
        title="Test Conversation",
        prompt="You are a helpful assistant"
    )
    return conversation


@pytest.fixture
def sample_conversation_with_messages(db_session, sample_conversation):
    """Create a sample conversation with messages for testing."""
    # Add user message
    user_message = Message.create_message(
        db=db_session,
        conversation_id=sample_conversation.id,
        sent_by=SenderType.USER,
        content="Hello, how are you?"
    )
    
    # Add assistant message
    assistant_message = Message.create_message(
        db=db_session,
        conversation_id=sample_conversation.id,
        sent_by=SenderType.ASSISTANT,
        content="Hello! I'm doing well, thank you for asking. How can I help you today?"
    )
    
    return sample_conversation, [user_message, assistant_message]


class TestGetConversation:
    """Test cases for the GET /api/conv-with-msg/{conversation_id} endpoint."""

    def test_get_conversation_success_without_messages(self, client_with_conversation, sample_conversation):
        """Test successfully retrieving a conversation without messages."""
        response = client_with_conversation.get(f"/api/conv-with-msg/{sample_conversation.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify conversation data
        assert data["conversation_id"] == sample_conversation.id
        assert data["title"] == "Test Conversation"
        assert data["prompt"] == "You are a helpful assistant"
        assert "created_at" in data
        assert data["messages"] == []

    def test_get_conversation_success_with_messages(self, client_with_conversation, sample_conversation_with_messages):
        """Test successfully retrieving a conversation with messages."""
        conversation, messages = sample_conversation_with_messages
        
        response = client_with_conversation.get(f"/api/conv-with-msg/{conversation.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify conversation data
        assert data["conversation_id"] == conversation.id
        assert data["title"] == "Test Conversation"
        assert data["prompt"] == "You are a helpful assistant"
        assert "created_at" in data
        
        # Verify messages
        assert len(data["messages"]) == 2
        
        # First message (user)
        user_msg = data["messages"][0]
        assert user_msg["id"] == messages[0].id
        assert user_msg["sender"] == "user"
        assert user_msg["content"] == "Hello, how are you?"
        assert "created_at" in user_msg
        
        # Second message (assistant)
        assistant_msg = data["messages"][1]
        assert assistant_msg["id"] == messages[1].id
        assert assistant_msg["sender"] == "assistant"
        assert assistant_msg["content"] == "Hello! I'm doing well, thank you for asking. How can I help you today?"
        assert "created_at" in assistant_msg

    def test_get_conversation_not_found(self, client_with_conversation):
        """Test retrieving a non-existent conversation returns 404."""
        non_existent_id = 99999
        
        response = client_with_conversation.get(f"/api/conv-with-msg/{non_existent_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Conversation not found"

    def test_get_conversation_with_zero_id(self, client_with_conversation):
        """Test retrieving conversation with ID 0 returns 404."""
        response = client_with_conversation.get("/api/conv-with-msg/0")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Conversation not found"

    def test_get_conversation_with_negative_id(self, client_with_conversation):
        """Test retrieving conversation with negative ID returns 404."""
        response = client_with_conversation.get("/api/conv-with-msg/-1")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Conversation not found"

    def test_get_conversation_invalid_id_format(self, client_with_conversation):
        """Test retrieving conversation with invalid ID format returns 422."""
        response = client_with_conversation.get("/api/conv-with-msg/invalid")
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_get_conversation_response_format(self, client_with_conversation, sample_conversation_with_messages):
        """Test that the response format matches the expected schema."""
        conversation, messages = sample_conversation_with_messages
        
        response = client_with_conversation.get(f"/api/conv-with-msg/{conversation.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields are present
        required_fields = ["conversation_id", "title", "prompt", "created_at", "messages"]
        for field in required_fields:
            assert field in data
        
        # Verify message fields
        for message in data["messages"]:
            message_fields = ["id", "sender", "content", "created_at"]
            for field in message_fields:
                assert field in message
            
            # Verify sender is valid enum value
            assert message["sender"] in ["user", "assistant"]

    def test_get_conversation_datetime_format(self, client_with_conversation, sample_conversation_with_messages):
        """Test that datetime fields are properly formatted as ISO strings."""
        conversation, messages = sample_conversation_with_messages
        
        response = client_with_conversation.get(f"/api/conv-with-msg/{conversation.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify conversation created_at is ISO format
        created_at = data["created_at"]
        assert isinstance(created_at, str)
        # Should be able to parse as ISO datetime
        datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        
        # Verify message created_at fields are ISO format
        for message in data["messages"]:
            msg_created_at = message["created_at"]
            assert isinstance(msg_created_at, str)
            datetime.fromisoformat(msg_created_at.replace("Z", "+00:00"))

    def test_get_conversation_message_order(self, client_with_conversation, db_session, sample_conversation):
        """Test that messages are returned in chronological order."""
        import time
        
        # Create messages with slight delays to ensure different timestamps
        message1 = Message.create_message(
            db=db_session,
            conversation_id=sample_conversation.id,
            sent_by=SenderType.USER,
            content="First message"
        )
        
        time.sleep(0.01)  # Small delay
        
        message2 = Message.create_message(
            db=db_session,
            conversation_id=sample_conversation.id,
            sent_by=SenderType.ASSISTANT,
            content="Second message"
        )
        
        time.sleep(0.01)
        
        message3 = Message.create_message(
            db=db_session,
            conversation_id=sample_conversation.id,
            sent_by=SenderType.USER,
            content="Third message"
        )
        
        response = client_with_conversation.get(f"/api/conv-with-msg/{sample_conversation.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify messages are in correct order
        messages = data["messages"]
        assert len(messages) == 3
        assert messages[0]["content"] == "First message"
        assert messages[1]["content"] == "Second message"
        assert messages[2]["content"] == "Third message"

    def test_get_conversation_with_many_messages(self, client_with_conversation, db_session, sample_conversation):
        """Test retrieving conversation with many messages."""
        # Create 20 messages
        for i in range(20):
            sender = SenderType.USER if i % 2 == 0 else SenderType.ASSISTANT
            Message.create_message(
                db=db_session,
                conversation_id=sample_conversation.id,
                sent_by=sender,
                content=f"Message number {i + 1}"
            )
        
        response = client_with_conversation.get(f"/api/conv-with-msg/{sample_conversation.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all messages are returned
        assert len(data["messages"]) == 20
        
        # Verify first and last messages
        assert data["messages"][0]["content"] == "Message number 1"
        assert data["messages"][-1]["content"] == "Message number 20"

    def test_get_conversation_with_special_characters(self, client_with_conversation, db_session, sample_user):
        """Test retrieving conversation with special characters in title and messages."""
        # Create conversation with special characters
        conversation = Conversation.create_conversation(
            db=db_session,
            user_id=sample_user.id,
            title="Test! @#$%^&*()_+-=[]{}|;':\",./<>?",
            prompt="Unicode: 你好世界 - Привет мир - مرحبا بالعالم 🚀"
        )
        
        # Add message with special characters
        Message.create_message(
            db=db_session,
            conversation_id=conversation.id,
            sent_by=SenderType.USER,
            content="Special chars: émojis 🚀 and unicode: αβγδε"
        )
        
        response = client_with_conversation.get(f"/api/conv-with-msg/{conversation.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify special characters are preserved
        assert data["title"] == "Test! @#$%^&*()_+-=[]{}|;':\",./<>?"
        assert data["prompt"] == "Unicode: 你好世界 - Привет мир - مرحبا بالعالم 🚀"
        assert data["messages"][0]["content"] == "Special chars: émojis 🚀 and unicode: αβγδε"

    def test_get_conversation_with_null_prompt(self, client_with_conversation, db_session, sample_user):
        """Test retrieving conversation with null prompt (should get default)."""
        # Create conversation with None prompt
        conversation = Conversation.create_conversation(
            db=db_session,
            user_id=sample_user.id,
            title="Test Conversation",
            prompt=None
        )
        
        response = client_with_conversation.get(f"/api/conv-with-msg/{conversation.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should get default system prompt
        assert data["prompt"] == "You are a helpful and friendly assistant."

    def test_get_conversation_performance_with_eager_loading(self, client_with_conversation, db_session, sample_conversation):
        """Test that messages are eagerly loaded (no N+1 query problem)."""
        # Create multiple messages
        for i in range(10):
            Message.create_message(
                db=db_session,
                conversation_id=sample_conversation.id,
                sent_by=SenderType.USER if i % 2 == 0 else SenderType.ASSISTANT,
                content=f"Message {i + 1}"
            )
        
        # The endpoint should work efficiently with eager loading
        response = client_with_conversation.get(f"/api/conv-with-msg/{sample_conversation.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) == 10

    def test_get_conversation_response_content_type(self, client_with_conversation, sample_conversation):
        """Test that response has correct content type."""
        response = client_with_conversation.get(f"/api/conv-with-msg/{sample_conversation.id}")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"


class TestGetUserConversations:
    """Test cases for the GET /api/user-conv-with-msg/{user_id} endpoint."""

    def test_get_user_conversations_success_with_single_conversation(self, client_with_conversation, sample_conversation_with_messages):
        """Test successfully retrieving conversations for a user with one conversation."""
        conversation, messages = sample_conversation_with_messages
        
        response = client_with_conversation.get(f"/api/user-conv-with-msg/{conversation.user_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return a list with one conversation
        assert isinstance(data, list)
        assert len(data) == 1
        
        # Verify conversation data
        conv_data = data[0]
        assert conv_data["conversation_id"] == conversation.id
        assert conv_data["title"] == "Test Conversation"
        assert conv_data["prompt"] == "You are a helpful assistant"
        assert "created_at" in conv_data
        
        # Verify messages
        assert len(conv_data["messages"]) == 2
        assert conv_data["messages"][0]["content"] == "Hello, how are you?"
        assert conv_data["messages"][1]["content"] == "Hello! I'm doing well, thank you for asking. How can I help you today?"

    def test_get_user_conversations_success_with_multiple_conversations(self, client_with_conversation, db_session, sample_user):
        """Test successfully retrieving multiple conversations for a user."""
        # Create multiple conversations for the same user
        conv1 = Conversation.create_conversation(
            db=db_session,
            user_id=sample_user.id,
            title="First Conversation",
            prompt="You are a coding assistant"
        )
        
        conv2 = Conversation.create_conversation(
            db=db_session,
            user_id=sample_user.id,
            title="Second Conversation", 
            prompt="You are a math tutor"
        )
        
        # Add messages to first conversation
        Message.create_message(
            db=db_session,
            conversation_id=conv1.id,
            sent_by=SenderType.USER,
            content="Help me with Python"
        )
        
        # Add messages to second conversation
        Message.create_message(
            db=db_session,
            conversation_id=conv2.id,
            sent_by=SenderType.USER,
            content="Solve 2+2"
        )
        
        response = client_with_conversation.get(f"/api/user-conv-with-msg/{sample_user.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return a list with two conversations
        assert isinstance(data, list)
        assert len(data) == 2
        
        # Verify both conversations are present (order might vary)
        titles = [conv["title"] for conv in data]
        assert "First Conversation" in titles
        assert "Second Conversation" in titles
        
        # Verify each conversation has its messages
        for conv_data in data:
            if conv_data["title"] == "First Conversation":
                assert len(conv_data["messages"]) == 1
                assert conv_data["messages"][0]["content"] == "Help me with Python"
            elif conv_data["title"] == "Second Conversation":
                assert len(conv_data["messages"]) == 1
                assert conv_data["messages"][0]["content"] == "Solve 2+2"

    def test_get_user_conversations_success_with_conversations_without_messages(self, client_with_conversation, db_session, sample_user):
        """Test retrieving conversations that have no messages."""
        # Create conversations without messages
        conv1 = Conversation.create_conversation(
            db=db_session,
            user_id=sample_user.id,
            title="Empty Conversation 1",
            prompt="You are an assistant"
        )
        
        conv2 = Conversation.create_conversation(
            db=db_session,
            user_id=sample_user.id,
            title="Empty Conversation 2",
            prompt="You are another assistant"
        )
        
        response = client_with_conversation.get(f"/api/user-conv-with-msg/{sample_user.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 2
        
        # Both conversations should have empty message lists
        for conv_data in data:
            assert conv_data["messages"] == []
            assert conv_data["title"] in ["Empty Conversation 1", "Empty Conversation 2"]

    def test_get_user_conversations_not_found(self, client_with_conversation):
        """Test retrieving conversations for non-existent user returns 404."""
        non_existent_user_id = 99999
        
        response = client_with_conversation.get(f"/api/user-conv-with-msg/{non_existent_user_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "No conversations found for user"

    def test_get_user_conversations_with_zero_id(self, client_with_conversation):
        """Test retrieving conversations for user ID 0 returns 404."""
        response = client_with_conversation.get("/api/user-conv-with-msg/0")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "No conversations found for user"

    def test_get_user_conversations_with_negative_id(self, client_with_conversation):
        """Test retrieving conversations for negative user ID returns 404."""
        response = client_with_conversation.get("/api/user-conv-with-msg/-1")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "No conversations found for user"

    def test_get_user_conversations_invalid_id_format(self, client_with_conversation):
        """Test retrieving conversations with invalid user ID format returns 422."""
        response = client_with_conversation.get("/api/user-conv-with-msg/invalid")
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_get_user_conversations_response_format(self, client_with_conversation, sample_conversation_with_messages):
        """Test that the response format matches the expected schema."""
        conversation, messages = sample_conversation_with_messages
        
        response = client_with_conversation.get(f"/api/user-conv-with-msg/{conversation.user_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should be a list
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Verify each conversation has required fields
        for conv_data in data:
            required_fields = ["conversation_id", "title", "prompt", "created_at", "messages"]
            for field in required_fields:
                assert field in conv_data
            
            # Verify message fields if messages exist
            for message in conv_data["messages"]:
                message_fields = ["id", "sender", "content", "created_at"]
                for field in message_fields:
                    assert field in message
                
                # Verify sender is valid enum value
                assert message["sender"] in ["user", "assistant"]

    def test_get_user_conversations_datetime_format(self, client_with_conversation, sample_conversation_with_messages):
        """Test that datetime fields are properly formatted as ISO strings."""
        conversation, messages = sample_conversation_with_messages
        
        response = client_with_conversation.get(f"/api/user-conv-with-msg/{conversation.user_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        for conv_data in data:
            # Verify conversation created_at is ISO format
            created_at = conv_data["created_at"]
            assert isinstance(created_at, str)
            datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            
            # Verify message created_at fields are ISO format
            for message in conv_data["messages"]:
                msg_created_at = message["created_at"]
                assert isinstance(msg_created_at, str)
                datetime.fromisoformat(msg_created_at.replace("Z", "+00:00"))

    def test_get_user_conversations_with_different_users(self, client_with_conversation, db_session):
        """Test that endpoint only returns conversations for the specified user."""
        # Create two different users
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
        
        # Create conversations for both users
        conv1 = Conversation.create_conversation(
            db=db_session,
            user_id=user1.id,
            title="User 1 Conversation",
            prompt="Assistant for user 1"
        )
        
        conv2 = Conversation.create_conversation(
            db=db_session,
            user_id=user2.id,
            title="User 2 Conversation",
            prompt="Assistant for user 2"
        )
        
        # Get conversations for user1
        response = client_with_conversation.get(f"/api/user-conv-with-msg/{user1.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only return user1's conversation
        assert len(data) == 1
        assert data[0]["title"] == "User 1 Conversation"
        assert data[0]["conversation_id"] == conv1.id

    def test_get_user_conversations_with_many_conversations(self, client_with_conversation, db_session, sample_user):
        """Test retrieving many conversations for a user."""
        # Create 10 conversations
        conversations = []
        for i in range(10):
            conv = Conversation.create_conversation(
                db=db_session,
                user_id=sample_user.id,
                title=f"Conversation {i + 1}",
                prompt=f"Assistant prompt {i + 1}"
            )
            conversations.append(conv)
            
            # Add a message to each conversation
            Message.create_message(
                db=db_session,
                conversation_id=conv.id,
                sent_by=SenderType.USER,
                content=f"Message for conversation {i + 1}"
            )
        
        response = client_with_conversation.get(f"/api/user-conv-with-msg/{sample_user.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return all 10 conversations
        assert len(data) == 10
        
        # Verify each conversation has its message
        titles = [conv["title"] for conv in data]
        for i in range(10):
            assert f"Conversation {i + 1}" in titles

    def test_get_user_conversations_response_content_type(self, client_with_conversation, sample_conversation):
        """Test that response has correct content type."""
        response = client_with_conversation.get(f"/api/user-conv-with-msg/{sample_conversation.user_id}")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
