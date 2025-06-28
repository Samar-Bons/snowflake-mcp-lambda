# ABOUTME: Pytest configuration and fixtures for database testing
# ABOUTME: Provides test database setup, session management, and cleanup utilities

import asyncio
import os
from collections.abc import AsyncGenerator, Generator
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from app.database.config import DatabaseConfig, RedisConfig
from app.database.models import Base
from app.database.session import DatabaseSessionManager


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create test database engine with in-memory SQLite."""
    # Use in-memory SQLite for fast testing
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Create async database session for testing."""
    async with AsyncSession(test_engine) as session:
        yield session
        await session.rollback()


@pytest.fixture
def db_config() -> DatabaseConfig:
    """Create test database configuration."""
    return DatabaseConfig(
        host="localhost",
        port=5432,
        database="test_snowflake_mcp",
        username="test_user",
        password="test_pass",
        pool_size=5,
        max_overflow=15,
    )


@pytest.fixture
def redis_config() -> RedisConfig:
    """Create test Redis configuration."""
    return RedisConfig(
        host="localhost",
        port=6379,
        db=1,  # Use different DB for tests
        socket_timeout=0.001,
        max_connections=50,
    )


@pytest_asyncio.fixture
async def session_manager(
    db_config: DatabaseConfig,
) -> AsyncGenerator[DatabaseSessionManager, None]:
    """Create test session manager."""
    manager = DatabaseSessionManager()

    # Mock the engine creation for testing
    mock_engine = AsyncMock()
    manager._engine = mock_engine
    manager._initialized = True

    yield manager

    await manager.cleanup()


# Mock fixtures for external dependencies
@pytest.fixture
def mock_redis_client():
    """Mock Redis client for testing."""
    mock_client = AsyncMock()
    mock_client.ping.return_value = True
    mock_client.get.return_value = None
    mock_client.set.return_value = True
    mock_client.delete.return_value = 1
    return mock_client


@pytest.fixture
def mock_postgres_engine():
    """Mock PostgreSQL engine for testing."""
    mock_engine = AsyncMock()
    mock_pool = AsyncMock()
    mock_pool.size.return_value = 5
    mock_pool.checkedin.return_value = 3
    mock_pool.checkedout.return_value = 2
    mock_pool.overflow.return_value = 0
    mock_engine.pool = mock_pool
    return mock_engine


# Environment setup
@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
    yield
    # Cleanup
    os.environ.pop("TESTING", None)
    os.environ.pop("DATABASE_URL", None)
