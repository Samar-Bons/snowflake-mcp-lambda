# ABOUTME: Tests for FastAPI application endpoints and basic functionality
# ABOUTME: Validates API responses, health checks, and basic routing

from fastapi.testclient import TestClient

from app.main import app


class TestFastAPIApp:
    """Test FastAPI application endpoints."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = TestClient(app)

    def test_root_endpoint_returns_service_info(self) -> None:
        """Test that root endpoint returns basic service information."""
        response = self.client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert data["service"] == "snowflake-mcp-lambda"
        assert data["version"] == "0.1.0"
        assert data["status"] == "running"
        assert "endpoints" in data
        assert "/health" in data["endpoints"]["health"]
        assert "/readiness" in data["endpoints"]["readiness"]
        assert "/docs" in data["endpoints"]["docs"]

    def test_health_endpoint_returns_healthy_status(self) -> None:
        """Test that health endpoint returns healthy status."""
        response = self.client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert data["service"] == "snowflake-mcp-lambda"
        assert data["version"] == "0.1.0"
        assert "timestamp" in data

    def test_readiness_endpoint_returns_status(self) -> None:
        """Test that readiness endpoint returns appropriate status based on dependencies."""
        response = self.client.get("/readiness")

        # Should return 503 when database is not available (expected in test environment)
        assert response.status_code == 503
        data = response.json()

        assert data["ready"] is False
        assert "dependencies" in data
        assert "timestamp" in data
        assert "database_health" in data
        # Database should be in error state due to missing connection
        assert data["dependencies"]["database"] == "error"

    def test_app_has_correct_metadata(self) -> None:
        """Test that FastAPI app has correct title and description."""
        assert app.title == "Snowflake MCP Lambda"
        assert app.version == "0.1.0"
        assert "Snowflake" in app.description

    def test_docs_endpoint_is_available(self) -> None:
        """Test that OpenAPI docs endpoint is available."""
        response = self.client.get("/docs")
        # Docs endpoint should be available and return HTML
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
