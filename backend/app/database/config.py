# ABOUTME: Database configuration classes for PostgreSQL and Redis connections
# ABOUTME: Provides connection pooling settings and performance optimization parameters

from typing import Any, Dict

from pydantic import BaseModel, Field, validator


class DatabaseConfig(BaseModel):
    """Configuration for PostgreSQL database connection with advanced pooling."""

    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port")
    database: str = Field(default="snowflake_mcp", description="Database name")
    username: str = Field(default="postgres", description="Database username")
    password: str = Field(default="", description="Database password")

    # Connection pooling settings
    pool_size: int = Field(
        default=5, description="Minimum number of connections in pool"
    )
    max_overflow: int = Field(default=15, description="Maximum overflow connections")
    pool_timeout: int = Field(
        default=30, description="Timeout for getting connection from pool"
    )
    pool_recycle: int = Field(
        default=3600, description="Connection recycle time in seconds"
    )
    pool_pre_ping: bool = Field(default=True, description="Enable connection pre-ping")

    # Performance settings
    echo: bool = Field(default=False, description="Enable SQL query logging")
    echo_pool: bool = Field(default=False, description="Enable pool logging")

    @validator("pool_size")
    def validate_pool_size(cls, v: int) -> int:
        """Validate minimum pool size."""
        if v < 1:
            raise ValueError("Pool size must be at least 1")
        return v

    @validator("max_overflow")
    def validate_max_overflow(cls, v: int) -> int:
        """Validate maximum overflow connections."""
        if v < 1:
            raise ValueError("Max overflow must be at least 1")
        return v

    @property
    def total_max_connections(self) -> int:
        """Calculate total maximum connections (pool + overflow)."""
        return self.pool_size + self.max_overflow

    @property
    def url(self) -> str:
        """Construct database URL for SQLAlchemy."""
        if self.password:
            return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        else:
            return f"postgresql+asyncpg://{self.username}@{self.host}:{self.port}/{self.database}"


class RedisConfig(BaseModel):
    """Configuration for Redis connection with sub-millisecond performance."""

    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, description="Redis port")
    db: int = Field(default=0, description="Redis database number")
    password: str | None = Field(default=None, description="Redis password")

    # Performance settings for sub-millisecond response times
    socket_timeout: float = Field(
        default=0.001, description="Socket timeout in seconds (1ms)"
    )
    socket_connect_timeout: float = Field(
        default=0.001, description="Connection timeout in seconds (1ms)"
    )
    socket_keepalive: bool = Field(default=True, description="Enable socket keepalive")
    socket_keepalive_options: Dict[str, Any] = Field(
        default_factory=dict, description="Keepalive options"
    )

    # Connection pooling
    max_connections: int = Field(default=50, description="Maximum connections in pool")
    retry_on_timeout: bool = Field(default=True, description="Retry on timeout")

    # Encoding settings
    decode_responses: bool = Field(
        default=True, description="Decode responses to strings"
    )
    encoding: str = Field(default="utf-8", description="Response encoding")

    @property
    def url(self) -> str:
        """Construct Redis URL."""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        else:
            return f"redis://{self.host}:{self.port}/{self.db}"
