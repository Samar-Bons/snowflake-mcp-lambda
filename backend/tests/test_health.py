# ABOUTME: Unit tests for health check functionality
# ABOUTME: Demonstrates TDD approach with comprehensive coverage

from datetime import datetime
from typing import Any
from unittest.mock import Mock, patch

from app.health import get_health_status, get_readiness_status


class TestHealthChecks:
    """Test suite for health check endpoints."""

    def test_get_health_status_returns_healthy(self) -> None:
        """Test that health status returns healthy response."""
        fixed_time = datetime(2024, 1, 1, 12, 0, 0)
        with patch("app.health.datetime") as mock_datetime:
            mock_datetime.utcnow.return_value = fixed_time

            result = get_health_status()

            assert result["status"] == "healthy"
            assert result["service"] == "snowflake-mcp-lambda"
            assert result["version"] == "0.1.0"
            assert result["timestamp"] == fixed_time.isoformat()

    def test_get_health_status_logs_request(self, caplog: Any) -> None:
        """Test that health check logs the request."""
        with caplog.at_level("INFO"):
            get_health_status()

        assert "Health check requested" in caplog.text

    def test_get_readiness_status_returns_ready_state(self) -> None:
        """Test that readiness status includes dependency information."""
        fixed_time = datetime(2024, 1, 1, 12, 0, 0)
        with patch("app.health.datetime") as mock_datetime:
            mock_datetime.utcnow.return_value = fixed_time

            result = get_readiness_status()

            assert "ready" in result
            assert "dependencies" in result
            assert "database" in result["dependencies"]
            assert "redis" in result["dependencies"]
            assert "snowflake" in result["dependencies"]
            assert result["timestamp"] == fixed_time.isoformat()

    def test_get_readiness_status_logs_request(self, caplog: Any) -> None:
        """Test that readiness check logs the request."""
        with caplog.at_level("INFO"):
            get_readiness_status()

        assert "Readiness check requested" in caplog.text

    def test_readiness_dependencies_structure(self) -> None:
        """Test that dependencies have expected structure."""
        with patch("app.core.database.get_database_manager") as mock_get_db_manager:
            # Mock the database manager to prevent initialization issues
            mock_db_manager = Mock()
            mock_db_manager.health_check.return_value = {"status": "pending"}
            mock_get_db_manager.return_value = mock_db_manager

            result = get_readiness_status()

            dependencies = result["dependencies"]
            expected_deps = ["database", "redis", "snowflake"]

            for dep in expected_deps:
                assert dep in dependencies
            # Redis and snowflake should still be "pending"
            assert dependencies["redis"] == "pending"
            assert dependencies["snowflake"] == "pending"
            # Database should be "pending" with our mock
            assert dependencies["database"] == "pending"

    def test_get_readiness_status_includes_database_health(self) -> None:
        """Test that readiness status includes actual database health check."""
        fixed_time = datetime(2024, 1, 1, 12, 0, 0)

        with patch("app.health.datetime") as mock_datetime:
            mock_datetime.utcnow.return_value = fixed_time

            with patch("app.core.database.get_database_manager") as mock_get_db_manager:
                mock_db_manager = Mock()
                mock_db_manager.health_check.return_value = {
                    "status": "healthy",
                    "connected": True,
                    "response_time_ms": 15.5,
                }
                mock_get_db_manager.return_value = mock_db_manager

                result = get_readiness_status()

                assert result["dependencies"]["database"] == "healthy"
                assert result["database_health"]["status"] == "healthy"
                assert result["database_health"]["connected"] is True
                assert result["database_health"]["response_time_ms"] == 15.5

    def test_get_readiness_status_handles_database_failure(self) -> None:
        """Test that readiness status handles database connection failures."""
        with patch("app.core.database.get_database_manager") as mock_get_db_manager:
            mock_db_manager = Mock()
            mock_db_manager.health_check.return_value = {
                "status": "unhealthy",
                "connected": False,
                "error": "Connection timeout",
            }
            mock_get_db_manager.return_value = mock_db_manager

            result = get_readiness_status()

            assert result["dependencies"]["database"] == "unhealthy"
            assert result["database_health"]["status"] == "unhealthy"
            assert result["database_health"]["connected"] is False
            assert "Connection timeout" in result["database_health"]["error"]

    def test_get_readiness_status_handles_database_manager_exception(self) -> None:
        """Test that readiness status handles database manager exceptions."""
        with patch("app.core.database.get_database_manager") as mock_get_db_manager:
            mock_get_db_manager.side_effect = Exception(
                "Database manager initialization failed"
            )

            result = get_readiness_status()

            assert result["dependencies"]["database"] == "error"
            assert result["database_health"]["status"] == "error"
            assert (
                "Database manager initialization failed"
                in result["database_health"]["error"]
            )
