# ABOUTME: Unit tests for health check functionality
# ABOUTME: Demonstrates TDD approach with comprehensive coverage

from datetime import datetime
from typing import Any
from unittest.mock import patch

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
        result = get_readiness_status()

        dependencies = result["dependencies"]
        expected_deps = ["database", "redis", "snowflake"]

        for dep in expected_deps:
            assert dep in dependencies
            # For now, all should be "pending" until actual implementations
            assert dependencies[dep] == "pending"
