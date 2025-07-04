# ABOUTME: Tests for database module functionality
# ABOUTME: Tests SQLAlchemy setup, connection pooling, and health checks

import logging
from typing import Any
from unittest.mock import Mock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.config import Settings
from app.core.database import (
    DatabaseManager,
    check_database_health,
    get_database_manager,
    get_database_status,
    get_engine,
)


class TestDatabaseModule:
    """Test suite for database module functionality."""

    def test_get_engine_creates_engine_with_correct_config(self) -> None:
        """Test that get_engine creates SQLAlchemy engine with correct configuration."""
        settings = Settings()

        with patch("app.core.database.create_engine") as mock_create_engine:
            mock_engine = Mock()
            mock_create_engine.return_value = mock_engine

            result = get_engine(settings)

            # Verify create_engine was called with correct parameters
            mock_create_engine.assert_called_once()
            call_args = mock_create_engine.call_args

            # Check URL (first positional argument) - should include SSL mode
            expected_url = f"{settings.DATABASE_URL}?sslmode={settings.DB_SSL_MODE}"
            assert call_args[0][0] == expected_url

            # Check keyword arguments
            kwargs = call_args[1]
            assert kwargs["pool_size"] == settings.DB_POOL_SIZE
            assert kwargs["pool_timeout"] == settings.DB_POOL_TIMEOUT
            assert kwargs["echo"] == settings.DB_ECHO_SQL
            assert kwargs["pool_recycle"] == 3600
            assert kwargs["pool_pre_ping"] is True

            # Verify it returns the mocked engine
            assert result == mock_engine

    def test_get_engine_uses_custom_settings(self) -> None:
        """Test that get_engine uses custom settings from environment."""
        with patch.dict(
            "os.environ",
            {
                "DB_POOL_SIZE": "15",
                "DB_POOL_TIMEOUT": "45",
                "DB_ECHO_SQL": "true",
            },
        ):
            settings = Settings()

            with patch("app.core.database.create_engine") as mock_create_engine:
                mock_engine = Mock()
                mock_create_engine.return_value = mock_engine

                result = get_engine(settings)

                # Verify create_engine was called with custom settings
                call_args = mock_create_engine.call_args
                kwargs = call_args[1]

                assert kwargs["pool_size"] == 15
                assert kwargs["pool_timeout"] == 45
                assert kwargs["echo"] is True

                # Verify it returns the mocked engine
                assert result == mock_engine

    def test_check_database_health_returns_healthy_status(self) -> None:
        """Test that check_database_health returns healthy status on success."""
        mock_engine = Mock()
        mock_connection = Mock()
        mock_result = Mock()
        mock_connection.execute.return_value = mock_result

        # Set up the context manager properly
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_engine.connect.return_value.__exit__ = Mock(return_value=None)

        result = check_database_health(mock_engine)

        assert result["status"] == "healthy"
        assert result["connected"] is True
        assert "response_time_ms" in result
        mock_connection.execute.assert_called_once()
        mock_result.fetchone.assert_called_once()

    def test_check_database_health_handles_connection_error(self) -> None:
        """Test that check_database_health handles connection errors gracefully."""
        mock_engine = Mock()
        mock_engine.connect.side_effect = SQLAlchemyError("Connection failed")

        result = check_database_health(mock_engine)

        assert result["status"] == "unhealthy"
        assert result["connected"] is False
        assert "Connection failed" in result["error"]

    def test_check_database_health_logs_errors(self, caplog: Any) -> None:
        """Test that check_database_health logs database errors."""
        mock_engine = Mock()
        mock_engine.connect.side_effect = SQLAlchemyError("Connection timeout")

        with caplog.at_level(logging.ERROR):
            check_database_health(mock_engine)

        assert "Database health check failed" in caplog.text
        assert "Connection timeout" in caplog.text

    def test_get_database_status_returns_detailed_status(self) -> None:
        """Test that get_database_status returns detailed database status."""
        mock_engine = Mock()
        mock_pool = Mock()
        mock_engine.pool = mock_pool
        mock_pool.size.return_value = 10
        mock_pool.checkedin.return_value = 8
        mock_pool.checkedout.return_value = 2
        mock_pool.overflow.return_value = 0

        with patch("app.core.database.check_database_health") as mock_health:
            mock_health.return_value = {"status": "healthy", "connected": True}

            result = get_database_status(mock_engine)

            assert result["status"] == "healthy"
            assert result["pool_info"]["size"] == 10
            assert result["pool_info"]["checked_in"] == 8
            assert result["pool_info"]["checked_out"] == 2
            assert result["pool_info"]["overflow"] == 0


class TestDatabaseManager:
    """Test suite for DatabaseManager class."""

    def test_database_manager_initialization(self) -> None:
        """Test that DatabaseManager initializes correctly."""
        settings = Settings()

        with patch("app.core.database.get_engine") as mock_get_engine:
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine

            manager = DatabaseManager(settings)

            assert manager.settings == settings
            assert manager.engine == mock_engine
            mock_get_engine.assert_called_once_with(settings)

    def test_database_manager_health_check(self) -> None:
        """Test that DatabaseManager health check works correctly."""
        settings = Settings()

        with patch("app.core.database.get_engine") as mock_get_engine:
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine

            manager = DatabaseManager(settings)

            with patch("app.core.database.check_database_health") as mock_health:
                mock_health.return_value = {"status": "healthy"}

                result = manager.health_check()

                assert result["status"] == "healthy"
                mock_health.assert_called_once_with(mock_engine)

    def test_database_manager_get_status(self) -> None:
        """Test that DatabaseManager get_status works correctly."""
        settings = Settings()

        with patch("app.core.database.get_engine") as mock_get_engine:
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine

            manager = DatabaseManager(settings)

            with patch("app.core.database.get_database_status") as mock_status:
                mock_status.return_value = {"status": "healthy", "pool_info": {}}

                result = manager.get_status()

                assert result["status"] == "healthy"
                mock_status.assert_called_once_with(mock_engine)

    def test_get_database_manager_singleton(self) -> None:
        """Test that get_database_manager returns singleton instance."""
        with patch("app.core.database.DatabaseManager") as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager

            # First call
            result1 = get_database_manager()
            # Second call
            result2 = get_database_manager()

            # Should return same instance
            assert result1 == result2
            # Should only create once
            mock_manager_class.assert_called_once()

    def test_database_manager_close_connections(self) -> None:
        """Test that DatabaseManager properly closes connections."""
        settings = Settings()

        with patch("app.core.database.get_engine") as mock_get_engine:
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine

            manager = DatabaseManager(settings)
            manager.close()

            mock_engine.dispose.assert_called_once()


class TestDatabaseIntegration:
    """Integration tests for database functionality."""

    @pytest.mark.integration
    def test_database_connection_with_real_settings(self) -> None:
        """Test database connection with real settings (requires database)."""
        # This test would require a real database connection
        # For now, we'll skip it unless running integration tests
        pytest.skip("Requires real database connection")

    @pytest.mark.integration
    def test_database_health_check_integration(self) -> None:
        """Test database health check with real database connection."""
        # This test would require a real database connection
        # For now, we'll skip it unless running integration tests
        pytest.skip("Requires real database connection")
