# ABOUTME: Tests for UserService database operations and user management
# ABOUTME: Tests user creation, retrieval, preference updates, and service functions

from collections.abc import Generator
from unittest.mock import Mock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth.oauth_service import OAuthUserInfo
from app.auth.user_service import UserService, get_user_service
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


@pytest.fixture
def user_service(in_memory_db: Session) -> UserService:
    """Create UserService instance with test database."""
    return UserService(in_memory_db)


@pytest.fixture
def sample_oauth_info() -> OAuthUserInfo:
    """Create sample OAuth user info for testing."""
    return OAuthUserInfo(
        google_id="123456789",
        email="test@example.com",
        name="Test User",
        picture="https://example.com/avatar.jpg",
        verified_email=True,
    )


@pytest.fixture
def sample_user(in_memory_db: Session) -> User:
    """Create a sample user in the database."""
    user = User(
        google_id="existing_user_123",
        email="existing@example.com",
        name="Existing User",
        picture="https://example.com/existing.jpg",
        auto_run_queries=True,
        default_row_limit=1000,
        default_output_format="natural",
        is_active=True,
    )
    in_memory_db.add(user)
    in_memory_db.commit()
    in_memory_db.refresh(user)
    return user


class TestUserService:
    """Test UserService database operations."""

    def test_get_user_by_google_id_existing(
        self, user_service: UserService, sample_user: User
    ) -> None:
        """Test getting existing user by Google ID."""
        result = user_service.get_user_by_google_id(sample_user.google_id)

        assert result is not None
        assert result.id == sample_user.id
        assert result.google_id == sample_user.google_id
        assert result.email == sample_user.email

    def test_get_user_by_google_id_not_found(self, user_service: UserService) -> None:
        """Test getting non-existent user by Google ID."""
        result = user_service.get_user_by_google_id("nonexistent_id")

        assert result is None

    def test_get_user_by_id_existing(
        self, user_service: UserService, sample_user: User
    ) -> None:
        """Test getting existing user by internal ID."""
        result = user_service.get_user_by_id(sample_user.id)

        assert result is not None
        assert result.id == sample_user.id
        assert result.google_id == sample_user.google_id
        assert result.email == sample_user.email

    def test_get_user_by_id_not_found(self, user_service: UserService) -> None:
        """Test getting non-existent user by internal ID."""
        result = user_service.get_user_by_id(99999)

        assert result is None

    def test_create_user(
        self, user_service: UserService, sample_oauth_info: OAuthUserInfo
    ) -> None:
        """Test creating new user from OAuth info."""
        result = user_service.create_user(sample_oauth_info)

        assert result.google_id == sample_oauth_info.google_id
        assert result.email == sample_oauth_info.email
        assert result.name == sample_oauth_info.name
        assert result.picture == sample_oauth_info.picture
        assert result.auto_run_queries is False  # Default value
        assert result.default_row_limit == 500  # Default value
        assert result.default_output_format == "table"  # Default value
        assert result.is_active is True  # Default value
        assert result.id is not None  # Should have been assigned by DB

    def test_update_user_from_oauth(
        self, user_service: UserService, sample_user: User
    ) -> None:
        """Test updating existing user with fresh OAuth info."""
        new_oauth_info = OAuthUserInfo(
            google_id=sample_user.google_id,
            email="updated@example.com",
            name="Updated Name",
            picture="https://example.com/updated.jpg",
            verified_email=True,
        )

        result = user_service.update_user_from_oauth(sample_user, new_oauth_info)

        assert result.id == sample_user.id
        assert result.google_id == sample_user.google_id  # Unchanged
        assert result.email == "updated@example.com"  # Updated
        assert result.name == "Updated Name"  # Updated
        assert result.picture == "https://example.com/updated.jpg"  # Updated
        # Preferences should remain unchanged
        assert result.auto_run_queries == sample_user.auto_run_queries
        assert result.default_row_limit == sample_user.default_row_limit

    def test_get_or_create_user_existing(
        self, user_service: UserService, sample_user: User
    ) -> None:
        """Test get_or_create with existing user."""
        oauth_info = OAuthUserInfo(
            google_id=sample_user.google_id,
            email="new_email@example.com",
            name="New Name",
            picture="https://example.com/new.jpg",
            verified_email=True,
        )

        result = user_service.get_or_create_user(oauth_info)

        # Should return existing user with updated info
        assert result.id == sample_user.id
        assert result.google_id == sample_user.google_id
        assert result.email == "new_email@example.com"  # Updated
        assert result.name == "New Name"  # Updated

    def test_get_or_create_user_new(
        self, user_service: UserService, sample_oauth_info: OAuthUserInfo
    ) -> None:
        """Test get_or_create with new user."""
        result = user_service.get_or_create_user(sample_oauth_info)

        # Should create new user
        assert result.google_id == sample_oauth_info.google_id
        assert result.email == sample_oauth_info.email
        assert result.name == sample_oauth_info.name
        assert result.id is not None

    def test_update_user_preferences_valid(
        self, user_service: UserService, sample_user: User
    ) -> None:
        """Test updating user preferences with valid data."""
        preferences = {
            "auto_run_queries": True,
            "default_row_limit": 2000,
            "default_output_format": "both",
        }

        result = user_service.update_user_preferences(sample_user.id, preferences)

        assert result.id == sample_user.id
        assert result.auto_run_queries is True
        assert result.default_row_limit == 2000
        assert result.default_output_format == "both"

    def test_update_user_preferences_partial(
        self, user_service: UserService, sample_user: User
    ) -> None:
        """Test updating only some user preferences."""
        original_format = sample_user.default_output_format
        preferences = {"auto_run_queries": False}

        result = user_service.update_user_preferences(sample_user.id, preferences)

        assert result.auto_run_queries is False
        assert result.default_output_format == original_format  # Unchanged

    def test_update_user_preferences_user_not_found(
        self, user_service: UserService
    ) -> None:
        """Test updating preferences for non-existent user."""
        with pytest.raises(ValueError, match="User with ID 99999 not found"):
            user_service.update_user_preferences(99999, {"auto_run_queries": True})

    def test_update_user_preferences_invalid_row_limit_type(
        self, user_service: UserService, sample_user: User
    ) -> None:
        """Test updating row limit with invalid type."""
        preferences = {"default_row_limit": "invalid"}

        with pytest.raises(
            ValueError, match="default_row_limit must be between 1 and 10000"
        ):
            user_service.update_user_preferences(sample_user.id, preferences)

    def test_update_user_preferences_invalid_row_limit_range(
        self, user_service: UserService, sample_user: User
    ) -> None:
        """Test updating row limit with invalid range."""
        preferences = {"default_row_limit": 0}

        with pytest.raises(
            ValueError, match="default_row_limit must be between 1 and 10000"
        ):
            user_service.update_user_preferences(sample_user.id, preferences)

        preferences = {"default_row_limit": 20000}

        with pytest.raises(
            ValueError, match="default_row_limit must be between 1 and 10000"
        ):
            user_service.update_user_preferences(sample_user.id, preferences)

    def test_update_user_preferences_invalid_output_format(
        self, user_service: UserService, sample_user: User
    ) -> None:
        """Test updating output format with invalid value."""
        preferences = {"default_output_format": "invalid"}

        with pytest.raises(
            ValueError,
            match="default_output_format must be one of: \\['table', 'natural', 'both'\\]",
        ):
            user_service.update_user_preferences(sample_user.id, preferences)

    def test_deactivate_user_existing(
        self, user_service: UserService, sample_user: User
    ) -> None:
        """Test deactivating existing user."""
        assert sample_user.is_active is True

        result = user_service.deactivate_user(sample_user.id)

        assert result.id == sample_user.id
        assert result.is_active is False

    def test_deactivate_user_not_found(self, user_service: UserService) -> None:
        """Test deactivating non-existent user."""
        with pytest.raises(ValueError, match="User with ID 99999 not found"):
            user_service.deactivate_user(99999)


class TestGetUserService:
    """Test get_user_service factory function."""

    @patch("app.auth.user_service.get_database_session")
    def test_get_user_service_factory(self, mock_get_db_session: Mock) -> None:
        """Test that get_user_service creates UserService with database session."""
        mock_session = Mock()
        mock_get_db_session.return_value = iter([mock_session])

        result = get_user_service()

        assert isinstance(result, UserService)
        assert result.db_session is mock_session
        mock_get_db_session.assert_called_once()
