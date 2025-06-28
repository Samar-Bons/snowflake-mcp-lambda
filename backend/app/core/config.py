# ABOUTME: Comprehensive configuration management system with Pydantic settings
# ABOUTME: Handles environment switching, validation, and service-specific configurations

import os
from functools import lru_cache
from typing import Literal, Union

import structlog
from pydantic import ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings

logger = structlog.get_logger(__name__)


class Settings(BaseSettings):
    """Base configuration settings with comprehensive validation."""

    # Environment and Debug
    ENVIRONMENT: Literal["development", "production"] = Field(
        default="development", description="Application environment"
    )
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )

    # Security
    SECRET_KEY: str = Field(
        ...,
        min_length=32,
        description="Secret key for JWT and cryptographic operations (min 32 chars)",
    )
    SECURITY_HEADERS: bool = Field(default=True, description="Enable security headers")

    # Database Configuration
    DATABASE_URL: str = Field(..., description="PostgreSQL database URL")
    REDIS_URL: str = Field(..., description="Redis URL for session storage")

    # Google OAuth Configuration
    GOOGLE_CLIENT_ID: str = Field(..., description="Google OAuth Client ID")
    GOOGLE_CLIENT_SECRET: str = Field(..., description="Google OAuth Client Secret")
    GOOGLE_REDIRECT_URI: str = Field(
        default="http://localhost:8000/auth/callback", description="OAuth redirect URI"
    )

    # JWT Configuration
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    JWT_EXPIRE_HOURS: int = Field(
        default=24, ge=1, le=72, description="JWT token expiry in hours (1-72)"
    )

    # Snowflake Configuration
    SNOWFLAKE_TIMEOUT_SECONDS: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Snowflake query timeout in seconds (5-300)",
    )
    SNOWFLAKE_QUERY_ROW_LIMIT: int = Field(
        default=500,
        ge=1,
        le=10000,
        description="Maximum rows returned per query (1-10000)",
    )
    SNOWFLAKE_SCHEMA_CACHE_TTL: int = Field(
        default=3600,
        ge=60,
        le=86400,
        description="Schema cache TTL in seconds (1min-24hrs)",
    )

    # Rate Limiting Configuration
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(
        default=60, ge=1, le=1000, description="Rate limit requests per minute (1-1000)"
    )
    RATE_LIMIT_BURST_SIZE: int = Field(
        default=10, ge=1, le=100, description="Rate limit burst size (1-100)"
    )

    # CORS Configuration
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Allowed CORS origins (comma-separated string)",
    )

    # Logging Configuration
    LOG_FORMAT: Literal["json", "console"] = Field(
        default="json", description="Log output format (json or console)"
    )
    ENABLE_CORRELATION_IDS: bool = Field(
        default=True, description="Enable correlation ID tracking"
    )
    EXTERNAL_LOG_SERVICE_URL: str | None = Field(
        default=None, description="External log service URL for centralized logging"
    )

    # Monitoring Configuration
    ENABLE_PERFORMANCE_MONITORING: bool = Field(
        default=True, description="Enable performance metrics collection"
    )
    ENABLE_BUSINESS_METRICS: bool = Field(
        default=True, description="Enable business metrics tracking"
    )
    MONITORING_ALERT_WEBHOOK_URL: str | None = Field(
        default=None, description="Webhook URL for monitoring alerts"
    )
    METRICS_RETENTION_DAYS: int = Field(
        default=30, ge=1, le=90, description="Metrics retention period in days (1-90)"
    )
    PERFORMANCE_SAMPLE_INTERVAL: int = Field(
        default=60, ge=10, le=3600, description="Performance sampling interval in seconds (10-3600)"
    )

    @field_validator("DATABASE_URL")
    def validate_database_url(cls, v):
        """Validate PostgreSQL database URL format."""
        if not v.startswith("postgresql://"):
            raise ValueError("DATABASE_URL must start with postgresql://")
        return v

    @field_validator("REDIS_URL")
    def validate_redis_url(cls, v):
        """Validate Redis URL format."""
        if not v.startswith("redis://"):
            raise ValueError("REDIS_URL must start with redis://")
        return v

    @field_validator("GOOGLE_CLIENT_ID")
    def validate_google_client_id(cls, v):
        """Validate Google Client ID format."""
        if not v.endswith(".apps.googleusercontent.com"):
            raise ValueError(
                "GOOGLE_CLIENT_ID must end with .apps.googleusercontent.com"
            )
        return v

    @field_validator("SECRET_KEY")
    def validate_secret_key_strength(cls, v):
        """Validate secret key meets security requirements."""
        if len(v) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters long for security"
            )
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        validate_assignment=True
    )


class DevelopmentSettings(Settings):
    """Development environment specific settings."""

    DEBUG: bool = True
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"

    # Development-specific CORS origins
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ]

    # More permissive rate limits for development
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 120
    RATE_LIMIT_BURST_SIZE: int = 20

    # Shorter cache TTL for development (easier testing)
    SNOWFLAKE_SCHEMA_CACHE_TTL: int = 300  # 5 minutes

    model_config = ConfigDict(env_file=".env.development")


class ProductionSettings(Settings):
    """Production environment specific settings."""

    DEBUG: bool = False
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # Stricter security settings for production
    JWT_EXPIRE_HOURS: int = 8  # Shorter expiry for production
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 30  # Stricter rate limits
    RATE_LIMIT_BURST_SIZE: int = 5

    # Production CORS origins (must be HTTPS)
    CORS_ORIGINS: list[str] = []  # Must be explicitly set in production

    @field_validator("CORS_ORIGINS")
    def validate_production_cors_origins(cls, v):
        """Ensure all CORS origins use HTTPS in production."""
        for origin in v:
            if not origin.startswith("https://") and origin != "http://localhost:3000":
                raise ValueError(f"Production CORS origins must use HTTPS: {origin}")
        return v

    @field_validator("SECRET_KEY")
    def validate_production_secret_key(cls, v):
        """Extra validation for production secret key."""
        if len(v) < 50:
            raise ValueError(
                "Production SECRET_KEY should be at least 50 characters long"
            )
        if v.lower() in ["secret", "password", "key", "changeme"]:
            raise ValueError("SECRET_KEY cannot be a common/weak value in production")
        return v

    model_config = ConfigDict(env_file=".env.production")


@lru_cache
def get_settings() -> DevelopmentSettings | ProductionSettings:
    """
    Get application settings based on environment.

    Returns:
        Union[DevelopmentSettings, ProductionSettings]: Environment-specific settings
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()

    try:
        if environment == "production":
            logger.info("Loading production configuration")
            settings = ProductionSettings()
        else:
            logger.info("Loading development configuration")
            settings = DevelopmentSettings()

        logger.info(
            "Configuration loaded successfully",
            environment=settings.ENVIRONMENT,
            debug=settings.DEBUG,
            log_level=settings.LOG_LEVEL,
            cors_origins_count=len(settings.CORS_ORIGINS),
            rate_limit=settings.RATE_LIMIT_REQUESTS_PER_MINUTE,
        )

        return settings

    except Exception as e:
        logger.error(
            "Failed to load configuration",
            environment=environment,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise


# Service-specific configuration classes for better organization
class DatabaseConfig:
    """Database configuration utilities."""

    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def database_url(self) -> str:
        """Get database URL."""
        return self.settings.DATABASE_URL

    @property
    def redis_url(self) -> str:
        """Get Redis URL."""
        return self.settings.REDIS_URL

    def get_database_config(self) -> dict:
        """Get database connection configuration."""
        return {
            "url": self.database_url,
            "pool_size": 10,
            "pool_timeout": 30,
            "pool_recycle": 3600,
            "echo": self.settings.DEBUG,
        }

    def get_redis_config(self) -> dict:
        """Get Redis connection configuration."""
        return {
            "url": self.redis_url,
            "decode_responses": True,
            "max_connections": 20,
            "retry_on_timeout": True,
        }


class OAuthConfig:
    """OAuth configuration utilities."""

    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def client_id(self) -> str:
        """Get Google OAuth client ID."""
        return self.settings.GOOGLE_CLIENT_ID

    @property
    def client_secret(self) -> str:
        """Get Google OAuth client secret."""
        return self.settings.GOOGLE_CLIENT_SECRET

    @property
    def redirect_uri(self) -> str:
        """Get OAuth redirect URI."""
        return self.settings.GOOGLE_REDIRECT_URI

    def get_oauth_config(self) -> dict:
        """Get complete OAuth configuration."""
        return {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "scope": ["openid", "email", "profile"],
            "prompt": "select_account",
        }


class SnowflakeConfig:
    """Snowflake configuration utilities."""

    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def timeout_seconds(self) -> int:
        """Get query timeout in seconds."""
        return self.settings.SNOWFLAKE_TIMEOUT_SECONDS

    @property
    def query_row_limit(self) -> int:
        """Get maximum rows per query."""
        return self.settings.SNOWFLAKE_QUERY_ROW_LIMIT

    @property
    def schema_cache_ttl(self) -> int:
        """Get schema cache TTL in seconds."""
        return self.settings.SNOWFLAKE_SCHEMA_CACHE_TTL

    def get_connection_config(self, user_config: dict) -> dict:
        """
        Get Snowflake connection configuration with user-specific settings.

        Args:
            user_config: User-specific Snowflake connection parameters

        Returns:
            dict: Complete connection configuration
        """
        return {
            **user_config,  # User-provided account, user, password, etc.
            "timeout": self.timeout_seconds,
            "client_session_keep_alive": True,
            "application": "snowflake-mcp-lambda",
            "numpy": False,  # Disable numpy for simpler data handling
        }


class SecurityConfig:
    """Security configuration utilities."""

    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def secret_key(self) -> str:
        """Get application secret key."""
        return self.settings.SECRET_KEY

    @property
    def jwt_algorithm(self) -> str:
        """Get JWT algorithm."""
        return self.settings.JWT_ALGORITHM

    @property
    def jwt_expire_hours(self) -> int:
        """Get JWT expiry in hours."""
        return self.settings.JWT_EXPIRE_HOURS

    def get_jwt_config(self) -> dict:
        """Get JWT configuration."""
        return {
            "secret_key": self.secret_key,
            "algorithm": self.jwt_algorithm,
            "expire_hours": self.jwt_expire_hours,
        }

    def get_security_headers(self) -> dict:
        """Get security headers configuration."""
        return (
            {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
                "Content-Security-Policy": "default-src 'self'",
                "Referrer-Policy": "strict-origin-when-cross-origin",
            }
            if self.settings.SECURITY_HEADERS
            else {}
        )


class RateLimitConfig:
    """Rate limiting configuration utilities."""

    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def requests_per_minute(self) -> int:
        """Get requests per minute limit."""
        return self.settings.RATE_LIMIT_REQUESTS_PER_MINUTE

    @property
    def burst_size(self) -> int:
        """Get burst size limit."""
        return self.settings.RATE_LIMIT_BURST_SIZE

    def get_rate_limit_config(self) -> dict:
        """Get rate limiting configuration."""
        return {
            "requests_per_minute": self.requests_per_minute,
            "burst_size": self.burst_size,
            "key_func": lambda request: request.client.host,  # Rate limit by IP
        }


class APIKeyConfig:
    """API key management for external services (BYOK model)."""

    def __init__(self, settings: Settings):
        self.settings = settings

    def validate_gemini_api_key(self, api_key: str) -> bool:
        """
        Validate Gemini API key format.

        Args:
            api_key: User-provided Gemini API key

        Returns:
            bool: True if key format is valid, False otherwise
        """
        if not api_key or not isinstance(api_key, str):
            return False

        # Gemini API keys typically start with "AIza" and are 39 characters long
        if not api_key.startswith("AIza") or len(api_key) != 39:
            return False

        # Basic character validation - should be alphanumeric with some special chars
        import re
        if not re.match(r"^[A-Za-z0-9_-]+$", api_key):
            return False

        return True

    def get_gemini_config(self, api_key: str) -> dict:
        """
        Get Gemini API configuration with user-provided key.

        Args:
            api_key: User's Gemini API key

        Returns:
            dict: Gemini service configuration

        Raises:
            ValueError: If API key is invalid
        """
        if not self.validate_gemini_api_key(api_key):
            raise ValueError("Invalid Gemini API key format")

        return {
            "api_key": api_key,
            "model": "gemini-1.5-pro",
            "temperature": 0.1,  # Lower temperature for SQL generation
            "max_tokens": 2048,
            "timeout": 30,
            "safety_settings": {
                "harassment": "BLOCK_NONE",
                "hate_speech": "BLOCK_NONE", 
                "sexually_explicit": "BLOCK_NONE",
                "dangerous_content": "BLOCK_MEDIUM_AND_ABOVE",
            },
        }

    def validate_snowflake_credentials(self, credentials: dict) -> bool:
        """
        Validate user-provided Snowflake connection credentials.

        Args:
            credentials: User-provided Snowflake connection parameters

        Returns:
            bool: True if credentials format is valid, False otherwise
        """
        required_fields = ["account", "user", "password"]
        
        # Check required fields are present and non-empty
        for field in required_fields:
            if field not in credentials or not credentials[field]:
                return False

        # Validate account format (should be like "account.region.provider")
        account = credentials["account"]
        if not account or "." not in account:
            return False

        # Validate user format (basic alphanumeric check)
        user = credentials["user"]
        if not user or not user.replace("_", "").replace("-", "").isalnum():
            return False

        # Password should be non-empty string
        password = credentials["password"]
        if not password or len(str(password)) < 1:
            return False

        return True

    def get_snowflake_connection_config(self, user_credentials: dict) -> dict:
        """
        Get Snowflake connection configuration with user credentials.

        Args:
            user_credentials: User-provided Snowflake credentials

        Returns:
            dict: Complete Snowflake connection configuration

        Raises:
            ValueError: If credentials are invalid
        """
        if not self.validate_snowflake_credentials(user_credentials):
            raise ValueError("Invalid Snowflake credentials format")

        # Get system-level Snowflake configuration
        snowflake_config = get_snowflake_config()
        
        return snowflake_config.get_connection_config(user_credentials)


# Convenience functions for getting service-specific configurations
def get_database_config() -> DatabaseConfig:
    """Get database configuration."""
    return DatabaseConfig(get_settings())


def get_oauth_config() -> OAuthConfig:
    """Get OAuth configuration."""
    return OAuthConfig(get_settings())


def get_snowflake_config() -> SnowflakeConfig:
    """Get Snowflake configuration."""
    return SnowflakeConfig(get_settings())


def get_security_config() -> SecurityConfig:
    """Get security configuration."""
    return SecurityConfig(get_settings())


def get_rate_limit_config() -> RateLimitConfig:
    """Get rate limiting configuration."""
    return RateLimitConfig(get_settings())


def get_api_key_config() -> APIKeyConfig:
    """Get API key management configuration."""
    return APIKeyConfig(get_settings())


class LoggingConfig:
    """Logging configuration utilities."""

    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def log_level(self) -> str:
        """Get logging level."""
        return self.settings.LOG_LEVEL

    @property
    def log_format(self) -> str:
        """Get log format."""
        return self.settings.LOG_FORMAT

    @property
    def enable_correlation_ids(self) -> bool:
        """Get correlation ID setting."""
        return self.settings.ENABLE_CORRELATION_IDS

    @property
    def external_service_url(self) -> str | None:
        """Get external log service URL."""
        return self.settings.EXTERNAL_LOG_SERVICE_URL

    def get_logging_config(self) -> dict:
        """Get complete logging configuration."""
        return {
            "level": self.log_level,
            "format": self.log_format,
            "enable_correlation_ids": self.enable_correlation_ids,
            "external_service_url": self.external_service_url,
        }


class MonitoringConfig:
    """Monitoring configuration utilities."""

    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def enable_performance_monitoring(self) -> bool:
        """Get performance monitoring setting."""
        return self.settings.ENABLE_PERFORMANCE_MONITORING

    @property
    def enable_business_metrics(self) -> bool:
        """Get business metrics setting."""
        return self.settings.ENABLE_BUSINESS_METRICS

    @property
    def alert_webhook_url(self) -> str | None:
        """Get alert webhook URL."""
        return self.settings.MONITORING_ALERT_WEBHOOK_URL

    @property
    def metrics_retention_days(self) -> int:
        """Get metrics retention period."""
        return self.settings.METRICS_RETENTION_DAYS

    @property
    def performance_sample_interval(self) -> int:
        """Get performance sampling interval."""
        return self.settings.PERFORMANCE_SAMPLE_INTERVAL

    def get_monitoring_config(self) -> dict:
        """Get complete monitoring configuration."""
        return {
            "enable_performance_monitoring": self.enable_performance_monitoring,
            "enable_business_metrics": self.enable_business_metrics,
            "alert_webhook_url": self.alert_webhook_url,
            "metrics_retention_days": self.metrics_retention_days,
            "performance_sample_interval": self.performance_sample_interval,
        }


def get_logging_config() -> LoggingConfig:
    """Get logging configuration."""
    return LoggingConfig(get_settings())


def get_monitoring_config() -> MonitoringConfig:
    """Get monitoring configuration."""
    return MonitoringConfig(get_settings())


# Export commonly used settings getter
settings = get_settings()
