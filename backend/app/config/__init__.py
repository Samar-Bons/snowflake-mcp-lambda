# ABOUTME: Configuration management system with Pydantic models
# ABOUTME: Handles environment variables and application settings validation

from typing import Any, Literal

from pydantic import Field, field_validator
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

    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/snowflake_mcp",
        description="PostgreSQL database URL",
    )
    DB_POOL_SIZE: int = Field(
        default=10, description="Database connection pool size", ge=1, le=100
    )
    DB_POOL_TIMEOUT: int = Field(
        default=30, description="Database connection timeout in seconds", ge=1, le=300
    )
    DB_ECHO_SQL: bool = Field(default=False, description="Echo SQL queries to logs")
    DB_SSL_MODE: str = Field(default="require", description="PostgreSQL SSL mode")

    # Redis Configuration (placeholder for future implementation)
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )

    # API Configuration
    API_V1_PREFIX: str = Field(default="/api/v1", description="API version prefix")

    # Google OAuth Configuration
    GOOGLE_CLIENT_ID: str = Field(default="", description="Google OAuth client ID")
    GOOGLE_CLIENT_SECRET: str = Field(
        default="", description="Google OAuth client secret"
    )
    GOOGLE_REDIRECT_URI: str = Field(
        default="http://localhost:8000/api/v1/auth/callback",
        description="Google OAuth redirect URI",
    )
    GOOGLE_OAUTH_SCOPES: list[str] = Field(
        default=["openid", "email", "profile"], description="Google OAuth scopes"
    )

    # JWT Configuration
    JWT_SECRET_KEY: str = Field(
        default="", description="Secret key for JWT tokens (defaults to SECRET_KEY)"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    JWT_EXPIRATION_HOURS: int = Field(
        default=24, description="JWT expiration time in hours", ge=1, le=168
    )
    JWT_COOKIE_NAME: str = Field(
        default="snowflake_token", description="JWT cookie name"
    )
    JWT_COOKIE_SECURE: bool = Field(default=True, description="Use secure cookies")
    JWT_COOKIE_SAMESITE: str = Field(
        default="lax", description="Cookie SameSite attribute"
    )

    @field_validator("DB_SSL_MODE")
    @classmethod
    def validate_ssl_mode(cls, v: str) -> str:
        """Validate PostgreSQL SSL mode."""
        valid_modes = [
            "disable",
            "allow",
            "prefer",
            "require",
            "verify-ca",
            "verify-full",
        ]
        if v not in valid_modes:
            raise ValueError(f"Invalid SSL mode: {v}. Must be one of: {valid_modes}")
        return v

    @field_validator("JWT_ALGORITHM")
    @classmethod
    def validate_jwt_algorithm(cls, v: str) -> str:
        """Validate JWT algorithm."""
        valid_algorithms = ["HS256", "HS384", "HS512"]
        if v not in valid_algorithms:
            raise ValueError(
                f"Invalid JWT algorithm: {v}. Must be one of: {valid_algorithms}"
            )
        return v

    @field_validator("JWT_COOKIE_SAMESITE")
    @classmethod
    def validate_cookie_samesite(cls, v: str) -> str:
        """Validate cookie SameSite attribute."""
        valid_values = ["strict", "lax", "none"]
        if v not in valid_values:
            raise ValueError(
                f"Invalid SameSite value: {v}. Must be one of: {valid_values}"
            )
        return v

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization to set JWT_SECRET_KEY from SECRET_KEY if not provided."""
        if not self.JWT_SECRET_KEY:
            # Use the main SECRET_KEY if JWT_SECRET_KEY is not set
            self.JWT_SECRET_KEY = self.SECRET_KEY


def get_settings() -> Settings:
    """Get application settings instance.

    This function creates a new Settings instance each time it's called,
    ensuring fresh environment variable loading for testing.
    """
    return Settings()
