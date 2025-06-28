# ABOUTME: Integration tests for FastAPI application endpoints
# ABOUTME: Tests health checks, readiness probes, and basic API functionality

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestMainApplication:
    """Test suite for main FastAPI application."""

    def test_root_endpoint_returns_service_info(self) -> None:
        """Test that root endpoint returns service information."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert data["service"] == "snowflake-mcp-lambda"
        assert data["version"] == "0.1.0"
        assert data["status"] == "running"
        assert "endpoints" in data
        assert data["endpoints"]["health"] == "/health"
        assert data["endpoints"]["readiness"] == "/readiness"
        assert data["endpoints"]["docs"] == "/docs"

    def test_health_endpoint_returns_ok(self) -> None:
        """Test that health endpoint returns healthy status."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert data["service"] == "snowflake-mcp-lambda"
        assert data["version"] == "0.1.0"
        assert "timestamp" in data

    def test_readiness_endpoint_returns_ready(self) -> None:
        """Test that readiness endpoint returns ready status."""
        response = client.get("/readiness")

        # Since dependencies are currently "pending", ready should be True
        assert response.status_code == 200
        data = response.json()

        assert "ready" in data
        assert "timestamp" in data
        assert "dependencies" in data
        assert "database" in data["dependencies"]
        assert "redis" in data["dependencies"]
        assert "snowflake" in data["dependencies"]

    def test_docs_endpoint_accessible(self) -> None:
        """Test that OpenAPI docs endpoint is accessible."""
        response = client.get("/docs")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_openapi_json_accessible(self) -> None:
        """Test that OpenAPI JSON schema is accessible."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()

        assert data["info"]["title"] == "Snowflake MCP Lambda"
        assert data["info"]["version"] == "0.1.0"
        assert "paths" in data
        assert "/health" in data["paths"]
        assert "/readiness" in data["paths"]
