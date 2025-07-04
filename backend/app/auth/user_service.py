# ABOUTME: User service for database operations and user management
# ABOUTME: Handles user creation, retrieval, and preference updates

from typing import Any

from sqlalchemy.orm import Session

from app.auth.oauth_service import OAuthUserInfo
from app.core.database import get_database_session
from app.models.user import User


class UserService:
    """Service for user database operations."""

    def __init__(self, db_session: Session) -> None:
        """Initialize user service with database session."""
        self.db_session = db_session

    def get_user_by_google_id(self, google_id: str) -> User | None:
        """Get user by Google OAuth ID.

        Args:
            google_id: Google OAuth user ID

        Returns:
            User object if found, None otherwise
        """
        return self.db_session.query(User).filter(User.google_id == google_id).first()

    def get_user_by_id(self, user_id: int) -> User | None:
        """Get user by internal user ID.

        Args:
            user_id: Internal user ID

        Returns:
            User object if found, None otherwise
        """
        return self.db_session.query(User).filter(User.id == user_id).first()

    def create_user(self, oauth_info: OAuthUserInfo) -> User:
        """Create new user from OAuth information.

        Args:
            oauth_info: OAuth user information

        Returns:
            Created user object
        """
        user = User(
            google_id=oauth_info.google_id,
            email=oauth_info.email,
            name=oauth_info.name,
            picture=oauth_info.picture,
            # Use default preferences
            auto_run_queries=False,
            default_row_limit=500,
            default_output_format="table",
            is_active=True,
        )

        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        return user

    def update_user_from_oauth(self, user: User, oauth_info: OAuthUserInfo) -> User:
        """Update existing user with fresh OAuth information.

        Args:
            user: Existing user object
            oauth_info: Fresh OAuth user information

        Returns:
            Updated user object
        """
        # Update profile information that might have changed
        user.email = oauth_info.email
        user.name = oauth_info.name
        user.picture = oauth_info.picture

        self.db_session.commit()
        self.db_session.refresh(user)

        return user

    def get_or_create_user(self, oauth_info: OAuthUserInfo) -> User:
        """Get existing user or create new one from OAuth information.

        Args:
            oauth_info: OAuth user information

        Returns:
            User object (existing or newly created)
        """
        # Try to find existing user
        existing_user = self.get_user_by_google_id(oauth_info.google_id)

        if existing_user:
            # Update with fresh OAuth info and return
            return self.update_user_from_oauth(existing_user, oauth_info)
        else:
            # Create new user
            return self.create_user(oauth_info)

    def update_user_preferences(
        self, user_id: int, preferences: dict[str, Any]
    ) -> User:
        """Update user preferences.

        Args:
            user_id: User ID
            preferences: Dictionary of preference updates

        Returns:
            Updated user object

        Raises:
            ValueError: If user not found or invalid preferences
        """
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")

        # Update allowed preference fields
        if "auto_run_queries" in preferences:
            user.auto_run_queries = preferences["auto_run_queries"]

        if "default_row_limit" in preferences:
            row_limit = preferences["default_row_limit"]
            max_row_limit = 10000
            if (
                not isinstance(row_limit, int)
                or row_limit < 1
                or row_limit > max_row_limit
            ):
                raise ValueError(
                    f"default_row_limit must be between 1 and {max_row_limit}"
                )
            user.default_row_limit = row_limit

        if "default_output_format" in preferences:
            output_format = preferences["default_output_format"]
            valid_formats = ["table", "natural", "both"]
            if output_format not in valid_formats:
                raise ValueError(
                    f"default_output_format must be one of: {valid_formats}"
                )
            user.default_output_format = output_format

        self.db_session.commit()
        self.db_session.refresh(user)

        return user

    def deactivate_user(self, user_id: int) -> User:
        """Deactivate user account.

        Args:
            user_id: User ID

        Returns:
            Updated user object

        Raises:
            ValueError: If user not found
        """
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")

        user.is_active = False
        self.db_session.commit()
        self.db_session.refresh(user)

        return user


def get_user_service() -> UserService:
    """Factory function to create user service.

    Returns:
        UserService instance
    """
    db_session = next(get_database_session())
    return UserService(db_session)
