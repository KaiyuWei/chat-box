"""
Integration tests for User model methods.

These tests verify the database interaction behavior of User model methods
using a real SQLite database in memory.
"""

from models.user import User
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
