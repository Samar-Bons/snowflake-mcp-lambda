# ABOUTME: Database connection management for PostgreSQL and Redis clients
# ABOUTME: Handles connection creation, pooling, and performance optimization

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import QueuePool

from .config import DatabaseConfig, RedisConfig


async def get_async_engine(config: DatabaseConfig) -> AsyncEngine:
    """
    Create async SQLAlchemy engine with optimized connection pooling.

    Args:
        config: Database configuration with pooling settings

    Returns:
        Configured AsyncEngine with connection pool
    """
    engine = create_async_engine(
        config.url,
        # Connection pooling settings
        pool_size=config.pool_size,
        max_overflow=config.max_overflow,
        pool_timeout=config.pool_timeout,
        pool_recycle=config.pool_recycle,
        pool_pre_ping=config.pool_pre_ping,
        poolclass=QueuePool,
        # Performance settings
        echo=config.echo,
        echo_pool=config.echo_pool,
        # Async settings
        future=True,
    )

    return engine


async def get_redis_client(config: RedisConfig) -> redis.Redis:
    """
    Create Redis client with sub-millisecond performance configuration.

    Args:
        config: Redis configuration with performance settings

    Returns:
        Configured Redis client with connection pool
    """
    client = redis.from_url(
        config.url,
        # Performance settings for sub-millisecond response
        socket_timeout=config.socket_timeout,
        socket_connect_timeout=config.socket_connect_timeout,
        socket_keepalive=config.socket_keepalive,
        socket_keepalive_options=config.socket_keepalive_options,
        # Connection pooling
        max_connections=config.max_connections,
        retry_on_timeout=config.retry_on_timeout,
        # Response handling
        decode_responses=config.decode_responses,
        encoding=config.encoding,
    )

    return client
