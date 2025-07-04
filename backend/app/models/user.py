# ABOUTME: User model for OAuth authentication and profile management
# ABOUTME: Stores Google OAuth user data and application preferences

from typing import Any

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class User(BaseModel):  # type: ignore[misc]
    """User model for storing Google OAuth user information and preferences."""

    __tablename__ = "users"

    # Google OAuth fields
    google_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="Google OAuth user ID",
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="User email address from Google",
    )
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="User display name from Google"
    )
    picture: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="User profile picture URL from Google"
    )

    # Application preferences (defaults for UI)
    auto_run_queries: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether to auto-run queries without confirmation",
    )
    default_row_limit: Mapped[int] = mapped_column(
        default=500, nullable=False, comment="Default row limit for query results"
    )
    default_output_format: Mapped[str] = mapped_column(
        String(50),
        default="table",
        nullable=False,
        comment="Default output format: table, natural, or both",
    )

    # Account status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether the user account is active",
    )

    def __repr__(self) -> str:
        """String representation of the user."""
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"

    def to_profile_dict(self) -> dict[str, Any]:
        """Convert user to profile dictionary for API responses."""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "picture": self.picture,
            "preferences": {
                "auto_run_queries": self.auto_run_queries,
                "default_row_limit": self.default_row_limit,
                "default_output_format": self.default_output_format,
            },
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
