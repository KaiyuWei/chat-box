"""
Integration tests for User model methods and API endpoints.

These tests verify the database interaction behavior of User model methods
and the create_user API endpoint using a real SQLite database in memory.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from main import app
from models.user import User
from schemas.user import UserCreate
from sqlalchemy.orm import Session


class TestUserValidationMethods:
    """Test the validation class methods of the User model."""

    def test_is_username_exists_with_existing_user(self, db_session: Session):
        """Test that is_username_exists returns True when username exists."""
        existing_user = User(
            username="john_doe",
            email="john@example.com",
            password_hash="hashed_password",
        )
        db_session.add(existing_user)
        db_session.commit()

        result = User.is_username_exists("john_doe", db_session)

        assert result is True

    def test_is_username_exists_with_non_existing_user(self, db_session: Session):
        """Test that is_username_exists returns False when username doesn't exist."""
        result = User.is_username_exists("nonexistent_user", db_session)

        assert result is False

    def test_is_email_exists_with_existing_email(self, db_session: Session):
        """Test that is_email_exists returns True when email exists."""
        existing_user = User(
            username="john_doe",
            email="john@example.com",
            password_hash="hashed_password",
        )
        db_session.add(existing_user)
        db_session.commit()

        result = User.is_email_exists("john@example.com", db_session)

        assert result is True

    def test_is_email_exists_with_non_existing_email(self, db_session: Session):
        """Test that is_email_exists returns False when email doesn't exist."""
        result = User.is_email_exists("nonexistent@example.com", db_session)

        assert result is False

    def test_is_email_exists_with_empty_string(self, db_session):
        """Test email checking with empty string."""
        result = User.is_email_exists("", db_session)

        assert result is False


class TestCreateUserAPI:
    """Test the create_user API endpoint."""

    def test_create_user_success(self, client):
        """Test successful user creation."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
        }

        response = client.post("/api/users", json=user_data)

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["username"] == "testuser"
        assert response_data["email"] == "test@example.com"
        assert "id" in response_data
        assert "created_at" in response_data
        assert "password" not in response_data  # Password should not be returned

    def test_create_user_duplicate_username(self, client, db_session):
        """Test creating user with duplicate username."""
        # Create first user
        existing_user = User(
            username="existinguser",
            email="existing@example.com",
            password_hash="hashed_password",
        )
        db_session.add(existing_user)
        db_session.commit()

        # Try to create user with same username
        user_data = {
            "username": "existinguser",
            "email": "different@example.com",
            "password": "testpassword123",
        }

        response = client.post("/api/users", json=user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Username or email already exists" in response.json()["detail"]

    def test_create_user_duplicate_email(self, client, db_session):
        """Test creating user with duplicate email."""
        # Create first user
        existing_user = User(
            username="existinguser",
            email="existing@example.com",
            password_hash="hashed_password",
        )
        db_session.add(existing_user)
        db_session.commit()

        # Try to create user with same email
        user_data = {
            "username": "differentuser",
            "email": "existing@example.com",
            "password": "testpassword123",
        }

        response = client.post("/api/users", json=user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Username or email already exists" in response.json()["detail"]

    def test_create_user_case_insensitive_username(self, client, db_session):
        """Test that username checking is case insensitive."""
        # Create first user
        existing_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
        )
        db_session.add(existing_user)
        db_session.commit()

        # Try to create user with different case username
        user_data = {
            "username": "TestUser",  # Different case
            "email": "different@example.com",
            "password": "testpassword123",
        }

        response = client.post("/api/users", json=user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Username or email already exists" in response.json()["detail"]

    def test_create_user_case_insensitive_email(self, client, db_session):
        """Test that email checking is case insensitive."""
        # Create first user
        existing_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
        )
        db_session.add(existing_user)
        db_session.commit()

        # Try to create user with different case email
        user_data = {
            "username": "differentuser",
            "email": "Test@Example.Com",  # Different case
            "password": "testpassword123",
        }

        response = client.post("/api/users", json=user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Username or email already exists" in response.json()["detail"]

    def test_create_user_invalid_email_format(self, client):
        """Test creating user with invalid email format."""
        user_data = {
            "username": "testuser",
            "email": "invalid-email",  # Invalid email format
            "password": "testpassword123",
        }

        response = client.post("/api/users", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_user_short_username(self, client):
        """Test creating user with username too short."""
        user_data = {
            "username": "ab",  # Too short (min 3 chars)
            "email": "test@example.com",
            "password": "testpassword123",
        }

        response = client.post("/api/users", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_user_short_password(self, client):
        """Test creating user with password too short."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "short",  # Too short (min 8 chars)
        }

        response = client.post("/api/users", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_user_missing_fields(self, client):
        """Test creating user with missing required fields."""
        user_data = {
            "username": "testuser"
            # Missing email and password
        }

        response = client.post("/api/users", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_user_password_hashing(self, client, db_session):
        """Test that password is properly hashed and not stored in plain text."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
        }

        response = client.post("/api/users", json=user_data)

        assert response.status_code == status.HTTP_201_CREATED

        # Verify password is hashed in database
        user = db_session.query(User).filter(User.username == "testuser").first()
        assert user is not None
        assert user.password_hash != "testpassword123"  # Should be hashed
        assert len(user.password_hash) > 20  # Hashed password should be much longer

        # Verify password can be verified
        from schemas.user import UserCreate

        assert UserCreate.verify_password("testpassword123", user.password_hash) is True
        assert UserCreate.verify_password("wrongpassword", user.password_hash) is False

    def test_create_user_username_lowercase_conversion(self, client, db_session):
        """Test that username is converted to lowercase."""
        user_data = {
            "username": "TestUser",
            "email": "test@example.com",
            "password": "testpassword123",
        }

        response = client.post("/api/users", json=user_data)

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["username"] == "testuser"  # Should be lowercase

        # Verify in database
        user = db_session.query(User).filter(User.username == "testuser").first()
        assert user is not None
        assert user.username == "testuser"

    def test_create_user_email_lowercase_conversion(self, client, db_session):
        """Test that email is converted to lowercase."""
        user_data = {
            "username": "testuser",
            "email": "Test@Example.Com",
            "password": "testpassword123",
        }

        response = client.post("/api/users", json=user_data)

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["email"] == "test@example.com"  # Should be lowercase

        # Verify in database
        user = db_session.query(User).filter(User.email == "test@example.com").first()
        assert user is not None
        assert user.email == "test@example.com"

    def test_create_user_long_username(self, client):
        """Test creating user with username at maximum length."""
        long_username = "a" * 50  # Max length is 50
        user_data = {
            "username": long_username,
            "email": "test@example.com",
            "password": "testpassword123",
        }

        response = client.post("/api/users", json=user_data)

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["username"] == long_username

    def test_create_user_too_long_username(self, client):
        """Test creating user with username exceeding maximum length."""
        too_long_username = "a" * 51  # Exceeds max length of 50
        user_data = {
            "username": too_long_username,
            "email": "test@example.com",
            "password": "testpassword123",
        }

        response = client.post("/api/users", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
