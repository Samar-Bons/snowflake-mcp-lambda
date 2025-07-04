# ABOUTME: Tests for User SQLAlchemy model functionality
# ABOUTME: Tests user creation, validation, and profile methods

from collections.abc import Generator
from datetime import datetime
from typing import Any

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.models.base import BaseModel
from app.models.user import User


@pytest.fixture
def in_memory_db() -> Generator[Session, None, None]:
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    BaseModel.metadata.create_all(engine)

    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    yield session

    session.close()


class TestUserModel:
    """Test suite for User SQLAlchemy model."""

    def test_user_creation_with_required_fields(self, in_memory_db: Any) -> None:
        """Test that user can be created with required OAuth fields."""
        user = User(
            google_id="123456789",
            email="test@example.com",
            name="Test User"
        )

        in_memory_db.add(user)
        in_memory_db.commit()

        assert user.id is not None
        assert user.google_id == "123456789"
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.picture is None  # Optional field
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_creation_with_all_fields(self, in_memory_db: Any) -> None:
        """Test that user can be created with all fields including preferences."""
        user = User(
            google_id="987654321",
            email="full@example.com",
            name="Full User",
            picture="https://example.com/photo.jpg",
            auto_run_queries=True,
            default_row_limit=1000,
            default_output_format="both",
            is_active=True
        )

        in_memory_db.add(user)
        in_memory_db.commit()

        assert user.google_id == "987654321"
        assert user.email == "full@example.com"
        assert user.name == "Full User"
        assert user.picture == "https://example.com/photo.jpg"
        assert user.auto_run_queries is True
        assert user.default_row_limit == 1000
        assert user.default_output_format == "both"
        assert user.is_active is True

    def test_user_default_preferences(self, in_memory_db: Any) -> None:
        """Test that user preferences have correct default values."""
        user = User(
            google_id="default123",
            email="default@example.com",
            name="Default User"
        )

        in_memory_db.add(user)
        in_memory_db.commit()

        # Test default preference values
        assert user.auto_run_queries is False
        assert user.default_row_limit == 500
        assert user.default_output_format == "table"
        assert user.is_active is True

    def test_user_google_id_unique_constraint(self, in_memory_db: Any) -> None:
        """Test that google_id must be unique."""
        user1 = User(
            google_id="unique123",
            email="user1@example.com",
            name="User One"
        )

        user2 = User(
            google_id="unique123",  # Same google_id
            email="user2@example.com",
            name="User Two"
        )

        in_memory_db.add(user1)
        in_memory_db.commit()

        in_memory_db.add(user2)

        with pytest.raises(Exception):  # Should raise integrity error
            in_memory_db.commit()

    def test_user_email_unique_constraint(self, in_memory_db: Any) -> None:
        """Test that email must be unique."""
        user1 = User(
            google_id="email123",
            email="same@example.com",
            name="User One"
        )

        user2 = User(
            google_id="email456",
            email="same@example.com",  # Same email
            name="User Two"
        )

        in_memory_db.add(user1)
        in_memory_db.commit()

        in_memory_db.add(user2)

        with pytest.raises(Exception):  # Should raise integrity error
            in_memory_db.commit()

    def test_user_repr_method(self, in_memory_db: Any) -> None:
        """Test that user string representation is correct."""
        user = User(
            google_id="repr123",
            email="repr@example.com",
            name="Repr User"
        )

        in_memory_db.add(user)
        in_memory_db.commit()

        expected = f"<User(id={user.id}, email='repr@example.com', name='Repr User')>"
        assert repr(user) == expected

    def test_user_to_profile_dict_method(self, in_memory_db: Any) -> None:
        """Test that user profile dictionary is correctly formatted."""
        user = User(
            google_id="profile123",
            email="profile@example.com",
            name="Profile User",
            picture="https://example.com/profile.jpg",
            auto_run_queries=True,
            default_row_limit=750,
            default_output_format="natural"
        )

        in_memory_db.add(user)
        in_memory_db.commit()

        profile = user.to_profile_dict()

        assert profile["id"] == user.id
        assert profile["email"] == "profile@example.com"
        assert profile["name"] == "Profile User"
        assert profile["picture"] == "https://example.com/profile.jpg"
        assert profile["preferences"]["auto_run_queries"] is True
        assert profile["preferences"]["default_row_limit"] == 750
        assert profile["preferences"]["default_output_format"] == "natural"
        assert profile["is_active"] is True
        assert "created_at" in profile
        assert "updated_at" in profile

    def test_user_to_dict_method(self, in_memory_db: Any) -> None:
        """Test that user to_dict method includes all columns."""
        user = User(
            google_id="dict123",
            email="dict@example.com",
            name="Dict User"
        )

        in_memory_db.add(user)
        in_memory_db.commit()

        user_dict = user.to_dict()

        # Should include all table columns
        expected_keys = {
            "id", "created_at", "updated_at", "google_id", "email",
            "name", "picture", "auto_run_queries", "default_row_limit",
            "default_output_format", "is_active"
        }

        assert set(user_dict.keys()) == expected_keys
        assert user_dict["google_id"] == "dict123"
        assert user_dict["email"] == "dict@example.com"

    def test_user_timestamps_auto_populated(self, in_memory_db: Any) -> None:
        """Test that created_at and updated_at are automatically set."""
        user = User(
            google_id="timestamp123",
            email="timestamp@example.com",
            name="Timestamp User"
        )

        in_memory_db.add(user)
        in_memory_db.commit()

        # Verify timestamps are set
        assert user.created_at is not None
        assert user.updated_at is not None
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

        # For SQLite, timestamps should be equal on creation
        assert user.created_at == user.updated_at
