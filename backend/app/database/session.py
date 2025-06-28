# ABOUTME: Database session management with proper cleanup and connection handling
# ABOUTME: Provides session factory, dependency injection, and resource management

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from .config import DatabaseConfig
from .connections import get_async_engine


class DatabaseSessionManager:
    """
    Manages database sessions with proper resource cleanup and connection pooling.

    Provides async context managers for database sessions and handles
    connection lifecycle, health checks, and performance metrics.
    """

    def __init__(self) -> None:
        """Initialize session manager."""
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None
        self._config: DatabaseConfig | None = None
        self._initialized = False

    async def initialize(self, config: DatabaseConfig | None = None) -> None:
        """
        Initialize the session manager with database configuration.

        Args:
            config: Database configuration, uses default if not provided
        """
        if self._initialized:
            return

        if config is None:
            config = DatabaseConfig()

        self._config = config
        self._engine = await get_async_engine(config)
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=True,
            autocommit=False,
        )
        self._initialized = True

    async def cleanup(self) -> None:
        """Clean up database connections and resources."""
        if self._engine:
            await self._engine.dispose()

        self._engine = None
        self._session_factory = None
        self._config = None
        self._initialized = False

    @property
    def is_initialized(self) -> bool:
        """Check if session manager is initialized."""
        return self._initialized

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get database session with automatic cleanup.

        Yields:
            AsyncSession: Database session

        Raises:
            RuntimeError: If session manager is not initialized
        """
        if not self._initialized or self._session_factory is None:
            raise RuntimeError("Session manager not initialized")

        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def health_check(self) -> bool:
        """
        Perform database health check.

        Returns:
            bool: True if database is healthy, False otherwise
        """
        if not self._initialized or self._engine is None:
            return False

        try:
            async with self._engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                return result.scalar() == 1
        except SQLAlchemyError:
            return False

    async def get_connection_metrics(self) -> dict[str, Any]:
        """
        Get connection pool metrics.

        Returns:
            Dict containing connection pool statistics
        """
        if not self._initialized or self._engine is None:
            return {}

        pool = self._engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total_connections": pool.size() + pool.overflow(),
        }


# Global session manager instance
_session_manager: DatabaseSessionManager | None = None


def get_session_manager() -> DatabaseSessionManager:
    """
    Get the global session manager instance (singleton).

    Returns:
        DatabaseSessionManager: Global session manager
    """
    global _session_manager
    if _session_manager is None:
        _session_manager = DatabaseSessionManager()
    return _session_manager


async def initialize_database(config: DatabaseConfig | None = None) -> None:
    """
    Initialize the global database session manager.

    Args:
        config: Database configuration
    """
    manager = get_session_manager()
    await manager.initialize(config)


async def cleanup_database() -> None:
    """Clean up the global database session manager."""
    global _session_manager
    if _session_manager:
        await _session_manager.cleanup()
        _session_manager = None


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for getting database sessions.

    Yields:
        AsyncSession: Database session for request
    """
    manager = get_session_manager()
    async with manager.get_session() as session:
        yield session
