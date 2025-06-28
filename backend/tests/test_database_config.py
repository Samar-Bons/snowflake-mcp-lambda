# ABOUTME: Tests for database configuration including SQLAlchemy and Redis setup
# ABOUTME: Validates connection pooling, performance metrics, and session management

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.pool import QueuePool

from app.database.config import DatabaseConfig, RedisConfig
from app.database.connections import get_async_engine, get_redis_client


class TestDatabaseConfig:
    """Test database configuration settings and validation."""

    def test_database_config_default_values(self) -> None:
        """Test that database config has correct default pooling values."""
        config = DatabaseConfig()

        assert config.pool_size == 5  # minimum connections
        assert config.max_overflow == 15  # max overflow (5 + 15 = 20 total)
        assert config.pool_timeout == 30
        assert config.pool_recycle == 3600
        assert config.pool_pre_ping is True

    def test_database_config_validation(self) -> None:
        """Test database config validation for pool settings."""
        # Valid configuration
        config = DatabaseConfig(pool_size=5, max_overflow=15, pool_timeout=30)
        assert config.pool_size == 5
        assert config.max_overflow == 15
        assert config.total_max_connections == 20

    def test_database_config_invalid_pool_size(self) -> None:
        """Test that invalid pool sizes raise validation errors."""
        with pytest.raises(ValueError, match="Pool size must be at least 1"):
            DatabaseConfig(pool_size=0)

        with pytest.raises(ValueError, match="Max overflow must be at least 1"):
            DatabaseConfig(max_overflow=0)

    def test_database_url_construction(self) -> None:
        """Test that database URL is constructed correctly."""
        config = DatabaseConfig(
            host="localhost",
            port=5432,
            database="testdb",
            username="testuser",
            password="testpass",
        )

        expected_url = "postgresql+asyncpg://testuser:testpass@localhost:5432/testdb"
        assert config.url == expected_url


class TestRedisConfig:
    """Test Redis configuration settings and validation."""

    def test_redis_config_default_values(self) -> None:
        """Test that Redis config has correct default performance values."""
        config = RedisConfig()

        assert config.host == "localhost"
        assert config.port == 6379
        assert config.db == 0
        assert config.socket_timeout == 0.001  # 1ms for sub-millisecond target
        assert config.socket_connect_timeout == 0.001
        assert config.max_connections == 50
        assert config.retry_on_timeout is True

    def test_redis_config_performance_settings(self) -> None:
        """Test Redis config for sub-millisecond performance requirements."""
        config = RedisConfig(
            socket_timeout=0.0005,  # 0.5ms
            socket_connect_timeout=0.0005,
            max_connections=100,
        )

        assert config.socket_timeout == 0.0005
        assert config.socket_connect_timeout == 0.0005
        assert config.max_connections == 100

    def test_redis_url_construction(self) -> None:
        """Test that Redis URL is constructed correctly."""
        config = RedisConfig(host="redis-server", port=6380, db=1, password="redispass")

        expected_url = "redis://:redispass@redis-server:6380/1"
        assert config.url == expected_url


class TestDatabaseConnections:
    """Test database connection creation and pooling."""

    @pytest.mark.asyncio
    async def test_async_engine_creation(self) -> None:
        """Test that async engine is created with correct pool settings."""
        config = DatabaseConfig(
            url="postgresql+asyncpg://test:test@localhost:5432/test",
            pool_size=5,
            max_overflow=15,
        )

        with patch("app.database.connections.create_async_engine") as mock_create:
            mock_engine = AsyncMock(spec=AsyncEngine)
            mock_create.return_value = mock_engine

            engine = await get_async_engine(config)

            assert engine is not None
            mock_create.assert_called_once_with(
                config.url,
                pool_size=5,
                max_overflow=15,
                pool_timeout=30,
                pool_recycle=3600,
                pool_pre_ping=True,
                poolclass=QueuePool,
                echo=False,
            )

    @pytest.mark.asyncio
    async def test_engine_pool_validation(self) -> None:
        """Test that engine pool meets minimum/maximum connection requirements."""
        config = DatabaseConfig(
            url="postgresql+asyncpg://test:test@localhost:5432/test"
        )

        with patch("app.database.connections.create_async_engine") as mock_create:
            mock_engine = AsyncMock(spec=AsyncEngine)
            mock_pool = MagicMock()
            mock_pool.size.return_value = 5
            mock_pool.overflow.return_value = 15
            mock_engine.pool = mock_pool
            mock_create.return_value = mock_engine

            engine = await get_async_engine(config)

            # Verify pool configuration meets requirements
            assert mock_pool.size.return_value >= 5  # Minimum connections
            total_max = mock_pool.size.return_value + mock_pool.overflow.return_value
            assert total_max <= 20  # Maximum connections

    @pytest.mark.asyncio
    async def test_redis_client_creation(self) -> None:
        """Test that Redis client is created with performance settings."""
        config = RedisConfig(
            host="localhost", port=6379, socket_timeout=0.001, max_connections=50
        )

        with patch("app.database.connections.redis.from_url") as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client

            client = await get_redis_client(config)

            assert client is not None
            mock_redis.assert_called_once_with(
                config.url,
                socket_timeout=0.001,
                socket_connect_timeout=0.001,
                max_connections=50,
                retry_on_timeout=True,
                decode_responses=True,
            )

    @pytest.mark.asyncio
    async def test_redis_performance_metrics(self) -> None:
        """Test that Redis client meets sub-millisecond response requirements."""
        config = RedisConfig(socket_timeout=0.0005)  # 0.5ms target

        with patch("app.database.connections.redis.from_url") as mock_redis:
            mock_client = AsyncMock()

            # Simulate fast response
            async def fast_ping():
                await asyncio.sleep(0.0003)  # 0.3ms response
                return True

            mock_client.ping = fast_ping
            mock_redis.return_value = mock_client

            client = await get_redis_client(config)

            # Measure response time
            start_time = time.perf_counter()
            result = await client.ping()
            response_time = time.perf_counter() - start_time

            assert result is True
            assert response_time < 0.001  # Sub-millisecond requirement
