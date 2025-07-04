# ABOUTME: Base SQLAlchemy model with common fields and functionality
# ABOUTME: Provides foundation for all database models with timestamps and utilities

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class Base:
    """Base class for all database models with common fields."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert model instance to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns  # type: ignore[attr-defined]
        }


# Create the declarative base
BaseModel = declarative_base(cls=Base)
