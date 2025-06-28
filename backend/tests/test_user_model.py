# ABOUTME: Tests for User model including validation, constraints, and database operations
# ABOUTME: Validates all required fields, relationships, and data integrity rules

from datetime import datetime, timezone
from uuid import UUID

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User


class TestUserModel:
    """Test User model creation, validation, and constraints."""

    def test_user_model_required_fields(self) -> None:
        """Test that User model has all required fields."""
        user = User(
            email="test@example.com", name="Test User", google_id="google_123456"
        )

        # Check required fields exist
        assert hasattr(user, "id")
        assert hasattr(user, "email")
        assert hasattr(user, "name")
        assert hasattr(user, "google_id")
        assert hasattr(user, "is_active")
        assert hasattr(user, "created_at")
        assert hasattr(user, "updated_at")
        assert hasattr(user, "snowflake_config")

    def test_user_model_default_values(self) -> None:
        """Test that User model has correct default values."""
        user = User(
            email="test@example.com", name="Test User", google_id="google_123456"
        )

        assert user.is_active is True
        assert user.snowflake_config is None
        assert isinstance(user.id, UUID)

    def test_user_model_timestamps(self) -> None:
        """Test that timestamps are automatically set."""
        user = User(
            email="test@example.com", name="Test User", google_id="google_123456"
        )

        # Timestamps should be set on creation
        assert user.created_at is not None
        assert user.updated_at is not None
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

        # Should be timezone-aware UTC
        assert user.created_at.tzinfo == timezone.utc
        assert user.updated_at.tzinfo == timezone.utc

    def test_user_email_validation(self) -> None:
        """Test email validation constraints."""
        # Valid email should work
        user = User(
            email="valid.email+tag@example.com",
            name="Test User",
            google_id="google_123456",
        )
        assert user.email == "valid.email+tag@example.com"

    def test_user_model_string_length_constraints(self) -> None:
        """Test string length constraints on fields."""
        # Test maximum lengths
        long_name = "a" * 255
        long_google_id = "g" * 255

        user = User(email="test@example.com", name=long_name, google_id=long_google_id)

        assert len(user.name) == 255
        assert len(user.google_id) == 255

    def test_user_snowflake_config_json(self) -> None:
        """Test that snowflake_config can store JSON data."""
        config_data = {
            "account": "test_account",
            "warehouse": "test_warehouse",
            "database": "test_db",
            "schema": "test_schema",
            "role": "test_role",
        }

        user = User(
            email="test@example.com",
            name="Test User",
            google_id="google_123456",
            snowflake_config=config_data,
        )

        assert user.snowflake_config == config_data
        assert isinstance(user.snowflake_config, dict)

    @pytest.mark.asyncio
    async def test_user_creation_in_database(self, async_session: AsyncSession) -> None:
        """Test creating user in database with all constraints."""
        user = User(
            email="db.test@example.com",
            name="Database Test User",
            google_id="google_db_123456",
        )

        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)

        # Verify user was created with auto-generated fields
        assert user.id is not None
        assert isinstance(user.id, UUID)
        assert user.created_at is not None
        assert user.updated_at is not None

    @pytest.mark.asyncio
    async def test_user_email_unique_constraint(
        self, async_session: AsyncSession
    ) -> None:
        """Test that email uniqueness is enforced."""
        user1 = User(email="unique@example.com", name="User One", google_id="google_1")

        user2 = User(
            email="unique@example.com",  # Same email
            name="User Two",
            google_id="google_2",
        )

        async_session.add(user1)
        await async_session.commit()

        async_session.add(user2)

        with pytest.raises(IntegrityError):
            await async_session.commit()

    @pytest.mark.asyncio
    async def test_user_google_id_unique_constraint(
        self, async_session: AsyncSession
    ) -> None:
        """Test that google_id uniqueness is enforced."""
        user1 = User(
            email="user1@example.com", name="User One", google_id="google_unique_123"
        )

        user2 = User(
            email="user2@example.com",
            name="User Two",
            google_id="google_unique_123",  # Same google_id
        )

        async_session.add(user1)
        await async_session.commit()

        async_session.add(user2)

        with pytest.raises(IntegrityError):
            await async_session.commit()

    @pytest.mark.asyncio
    async def test_user_updated_at_changes(self, async_session: AsyncSession) -> None:
        """Test that updated_at changes when user is modified."""
        user = User(
            email="update.test@example.com",
            name="Update Test User",
            google_id="google_update_123",
        )

        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)

        original_updated_at = user.updated_at

        # Modify user
        user.name = "Updated Name"
        await async_session.commit()
        await async_session.refresh(user)

        # updated_at should have changed
        assert user.updated_at > original_updated_at

    @pytest.mark.asyncio
    async def test_user_query_by_email(self, async_session: AsyncSession) -> None:
        """Test querying user by email."""
        user = User(
            email="query.test@example.com",
            name="Query Test User",
            google_id="google_query_123",
        )

        async_session.add(user)
        await async_session.commit()

        # Query by email
        result = await async_session.execute(
            select(User).where(User.email == "query.test@example.com")
        )
        found_user = result.scalar_one_or_none()

        assert found_user is not None
        assert found_user.email == "query.test@example.com"
        assert found_user.name == "Query Test User"

    @pytest.mark.asyncio
    async def test_user_query_by_google_id(self, async_session: AsyncSession) -> None:
        """Test querying user by google_id."""
        user = User(
            email="google.query@example.com",
            name="Google Query User",
            google_id="google_unique_query_456",
        )

        async_session.add(user)
        await async_session.commit()

        # Query by google_id
        result = await async_session.execute(
            select(User).where(User.google_id == "google_unique_query_456")
        )
        found_user = result.scalar_one_or_none()

        assert found_user is not None
        assert found_user.google_id == "google_unique_query_456"
        assert found_user.email == "google.query@example.com"

    def test_user_repr(self) -> None:
        """Test User model string representation."""
        user = User(
            email="repr.test@example.com",
            name="Repr Test User",
            google_id="google_repr_123",
        )

        repr_str = repr(user)
        assert "User" in repr_str
        assert "repr.test@example.com" in repr_str
