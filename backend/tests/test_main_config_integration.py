# ABOUTME: Tests for main app integration with configuration
# ABOUTME: Ensures app uses configuration settings correctly

from fastapi.testclient import TestClient


class TestMainConfigIntegration:
    """Test main app configuration integration."""

    def test_app_configuration(self) -> None:
        """Test that app is configured with settings."""
        from app.main import app, settings

        # Just verify app exists and has debug setting from config
        assert app is not None
        assert hasattr(app, "debug")
        assert app.debug == settings.DEBUG

    def test_app_logging_configured(self) -> None:
        """Test that app configures logging properly."""
        from app.main import logger

        # Just verify logger exists and has a level set
        assert logger is not None
        assert logger.getEffectiveLevel() in [
            10,
            20,
            30,
            40,
            50,
        ]  # Valid logging levels

    def test_health_endpoint_works(self) -> None:
        """Test health endpoint returns expected response."""
        from app.main import app

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "service" in data

    def test_readiness_endpoint_works(self) -> None:
        """Test readiness endpoint returns expected response."""
        from app.main import app

        client = TestClient(app)
        response = client.get("/readiness")

        # Should return 503 when database is not available (expected in test environment)
        assert response.status_code == 503
        data = response.json()
        assert "ready" in data
        assert "timestamp" in data
        assert "dependencies" in data
        assert "database_health" in data
        # Should not be ready when database is unavailable
        assert data["ready"] is False

    def test_root_endpoint_works(self) -> None:
        """Test root endpoint returns API information."""
        from app.main import app

        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "snowflake-mcp-lambda"
        assert data["status"] == "running"
        assert "endpoints" in data
        assert data["endpoints"]["health"] == "/health"
