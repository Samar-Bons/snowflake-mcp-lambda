# ABOUTME: Snowflake connection model for secure per-user connection storage
# ABOUTME: Handles encrypted connection parameters and connection metadata

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User


class SnowflakeConnection(BaseModel):
    """Model for storing encrypted Snowflake connection parameters per user."""

    __tablename__ = "snowflake_connections"

    # User relationship
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who owns this connection",
    )
    user: Mapped["User"] = relationship("User", back_populates="snowflake_connections")

    # Connection identification
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="User-friendly name for this connection",
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether this is the user's default connection",
    )

    # Encrypted connection parameters
    encrypted_account: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Encrypted Snowflake account identifier"
    )
    encrypted_user: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Encrypted Snowflake username"
    )
    encrypted_password: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Encrypted Snowflake password"
    )
    encrypted_warehouse: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Encrypted Snowflake warehouse"
    )
    encrypted_database: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Encrypted Snowflake database"
    )
    encrypted_schema: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Encrypted Snowflake schema"
    )
    encrypted_role: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Encrypted Snowflake role (optional)"
    )

    # Connection settings
    query_timeout: Mapped[int] = mapped_column(
        Integer,
        default=30,
        nullable=False,
        comment="Query timeout in seconds",
    )
    max_rows: Mapped[int] = mapped_column(
        Integer,
        default=500,
        nullable=False,
        comment="Maximum rows to return per query",
    )

    # Connection status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether this connection is active",
    )
    last_tested_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="When connection was last tested"
    )
    last_test_success: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, comment="Result of last connection test"
    )

    def __repr__(self) -> str:
        """String representation of the connection."""
        return f"<SnowflakeConnection(id={self.id}, user_id={self.user_id}, name='{self.name}')>"

    def to_dict(self) -> dict[str, Any]:
        """Convert connection to dictionary (without sensitive data)."""
        return {
            "id": self.id,
            "name": self.name,
            "is_default": self.is_default,
            "query_timeout": self.query_timeout,
            "max_rows": self.max_rows,
            "is_active": self.is_active,
            "last_tested_at": self.last_tested_at.isoformat()
            if self.last_tested_at
            else None,
            "last_test_success": self.last_test_success,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
