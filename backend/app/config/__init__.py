# ABOUTME: Configuration management system with Pydantic models
# ABOUTME: Handles environment variables and application settings validation

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Base application settings with common configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra environment variables
    )

    # Application Configuration
    DEBUG: bool = Field(default=True, description="Enable debug mode")
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )

    # Security Configuration
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for cryptographic operations",
    )

    # Database Configuration (placeholder for future implementation)
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/snowflake_mcp",
        description="PostgreSQL database URL",
    )

    # Redis Configuration (placeholder for future implementation)
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )

    # API Configuration
    API_V1_PREFIX: str = Field(default="/api/v1", description="API version prefix")


def get_settings() -> Settings:
    """Get application settings instance.

    This function creates a new Settings instance each time it's called,
    ensuring fresh environment variable loading for testing.
    """
    return Settings()
