# ABOUTME: Tests for database session management including cleanup and connection handling
# ABOUTME: Validates session lifecycle, transaction management, and resource cleanup

import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import (
    DatabaseSessionManager,
    get_async_session,
    get_session_manager,
)


class TestDatabaseSessionManager:
    """Test database session manager functionality."""

    @pytest.mark.asyncio
    async def test_session_manager_initialization(self) -> None:
        """Test that session manager initializes correctly."""
        with patch("app.database.session.get_async_engine") as mock_get_engine:
            mock_engine = AsyncMock()
            mock_get_engine.return_value = mock_engine

            manager = DatabaseSessionManager()
            await manager.initialize()

            assert manager._engine is not None
            assert manager._session_factory is not None
            assert manager.is_initialized is True

    @pytest.mark.asyncio
    async def test_session_manager_cleanup(self) -> None:
        """Test that session manager cleans up resources properly."""
        with patch("app.database.session.get_async_engine") as mock_get_engine:
            mock_engine = AsyncMock()
            mock_get_engine.return_value = mock_engine

            manager = DatabaseSessionManager()
            await manager.initialize()

            # Cleanup should dispose of engine
            await manager.cleanup()

            mock_engine.dispose.assert_called_once()
            assert manager.is_initialized is False

    @pytest.mark.asyncio
    async def test_session_creation(self) -> None:
        """Test creating database sessions."""
        with patch("app.database.session.get_async_engine") as mock_get_engine:
            mock_engine = AsyncMock()
            mock_session = AsyncMock(spec=AsyncSession)

            with patch("app.database.session.async_sessionmaker") as mock_sessionmaker:
                mock_factory = AsyncMock()
                mock_factory.return_value.__aenter__.return_value = mock_session
                mock_sessionmaker.return_value = mock_factory
                mock_get_engine.return_value = mock_engine

                manager = DatabaseSessionManager()
                await manager.initialize()

                async with manager.get_session() as session:
                    assert session is not None

    @pytest.mark.asyncio
    async def test_session_transaction_rollback(self) -> None:
        """Test that sessions rollback on exceptions."""
        with patch("app.database.session.get_async_engine") as mock_get_engine:
            mock_engine = AsyncMock()
            mock_session = AsyncMock(spec=AsyncSession)

            with patch("app.database.session.async_sessionmaker") as mock_sessionmaker:
                mock_factory = AsyncMock()
                mock_factory.return_value.__aenter__.return_value = mock_session
                mock_sessionmaker.return_value = mock_factory
                mock_get_engine.return_value = mock_engine

                manager = DatabaseSessionManager()
                await manager.initialize()

                # Simulate exception in session context
                with pytest.raises(SQLAlchemyError):
                    async with manager.get_session() as session:
                        session.execute.side_effect = SQLAlchemyError("Test error")
                        await session.execute("SELECT 1")

                # Session should have been rolled back
                mock_session.rollback.assert_called()

    @pytest.mark.asyncio
    async def test_concurrent_session_access(self) -> None:
        """Test that multiple concurrent sessions work correctly."""
        with patch("app.database.session.get_async_engine") as mock_get_engine:
            mock_engine = AsyncMock()

            sessions_created = []

            def create_mock_session():
                mock_session = AsyncMock(spec=AsyncSession)
                sessions_created.append(mock_session)
                return mock_session

            with patch("app.database.session.async_sessionmaker") as mock_sessionmaker:
                mock_factory = AsyncMock()
                mock_factory.return_value.__aenter__.side_effect = create_mock_session
                mock_sessionmaker.return_value = mock_factory
                mock_get_engine.return_value = mock_engine

                manager = DatabaseSessionManager()
                await manager.initialize()

                # Create multiple concurrent sessions
                async def use_session(session_id: int) -> int:
                    async with manager.get_session() as session:
                        # Simulate some database work
                        await asyncio.sleep(0.01)
                        return session_id

                # Run 5 concurrent sessions
                tasks = [use_session(i) for i in range(5)]
                results = await asyncio.gather(*tasks)

                assert len(results) == 5
                assert len(sessions_created) == 5
                assert results == [0, 1, 2, 3, 4]


class TestSessionDependency:
    """Test session dependency injection for FastAPI."""

    @pytest.mark.asyncio
    async def test_get_async_session_dependency(self) -> None:
        """Test that session dependency provides working session."""
        with patch("app.database.session.get_session_manager") as mock_get_manager:
            mock_manager = AsyncMock()
            mock_session = AsyncMock(spec=AsyncSession)
            mock_manager.get_session.return_value.__aenter__.return_value = mock_session
            mock_get_manager.return_value = mock_manager

            # Test the dependency
            async_gen = get_async_session()
            session = await async_gen.__anext__()

            assert session is not None

            # Complete the generator
            try:
                await async_gen.__anext__()
            except StopAsyncIteration:
                pass

    @pytest.mark.asyncio
    async def test_session_dependency_cleanup(self) -> None:
        """Test that session dependency cleans up properly."""
        with patch("app.database.session.get_session_manager") as mock_get_manager:
            mock_manager = AsyncMock()
            mock_session = AsyncMock(spec=AsyncSession)

            # Setup context manager behavior
            context_manager = AsyncMock()
            context_manager.__aenter__.return_value = mock_session
            context_manager.__aexit__.return_value = None
            mock_manager.get_session.return_value = context_manager
            mock_get_manager.return_value = mock_manager

            # Use the dependency
            async_gen = get_async_session()
            session = await async_gen.__anext__()

            assert session is mock_session

            # Generator should cleanup on completion
            try:
                await async_gen.__anext__()
            except StopAsyncIteration:
                pass

            # Context manager exit should have been called
            context_manager.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    async def test_session_manager_singleton(self) -> None:
        """Test that session manager is a singleton."""
        manager1 = get_session_manager()
        manager2 = get_session_manager()

        assert manager1 is manager2
        assert id(manager1) == id(manager2)

    @pytest.mark.asyncio
    async def test_session_health_check(self) -> None:
        """Test session health check functionality."""
        with patch("app.database.session.get_async_engine") as mock_get_engine:
            mock_engine = AsyncMock()
            mock_connection = AsyncMock()
            mock_result = AsyncMock()
            mock_result.scalar.return_value = 1
            mock_connection.execute.return_value = mock_result
            mock_engine.begin.return_value.__aenter__.return_value = mock_connection
            mock_get_engine.return_value = mock_engine

            manager = DatabaseSessionManager()
            await manager.initialize()

            # Test health check
            is_healthy = await manager.health_check()

            assert is_healthy is True
            mock_connection.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_session_health_check_failure(self) -> None:
        """Test session health check handles failures properly."""
        with patch("app.database.session.get_async_engine") as mock_get_engine:
            mock_engine = AsyncMock()
            mock_engine.begin.side_effect = SQLAlchemyError("Connection failed")
            mock_get_engine.return_value = mock_engine

            manager = DatabaseSessionManager()
            await manager.initialize()

            # Test health check failure
            is_healthy = await manager.health_check()

            assert is_healthy is False

    @pytest.mark.asyncio
    async def test_session_metrics_tracking(self) -> None:
        """Test that session manager tracks connection metrics."""
        with patch("app.database.session.get_async_engine") as mock_get_engine:
            mock_engine = AsyncMock()
            mock_pool = AsyncMock()
            mock_pool.size.return_value = 5
            mock_pool.checked_in.return_value = 3
            mock_pool.checked_out.return_value = 2
            mock_pool.overflow.return_value = 0
            mock_engine.pool = mock_pool
            mock_get_engine.return_value = mock_engine

            manager = DatabaseSessionManager()
            await manager.initialize()

            metrics = await manager.get_connection_metrics()

            assert metrics["pool_size"] == 5
            assert metrics["checked_in"] == 3
            assert metrics["checked_out"] == 2
            assert metrics["overflow"] == 0
            assert metrics["total_connections"] == 5
