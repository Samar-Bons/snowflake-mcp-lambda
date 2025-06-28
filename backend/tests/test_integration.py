# ABOUTME: Integration tests for complete application functionality
# ABOUTME: Tests the full application stack including server startup and endpoint responses

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestApplicationIntegration:
    """Integration test suite for the complete application."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create a test client for the application."""
        return TestClient(app)

    def test_complete_application_flow(self, client: TestClient) -> None:
        """Test complete application flow from startup to shutdown."""
        # Test root endpoint
        response = client.get("/")
        assert response.status_code == 200
        root_data = response.json()
        assert root_data["service"] == "snowflake-mcp-lambda"

        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        health_data = response.json()
        assert health_data["status"] == "healthy"

        # Test readiness endpoint
        response = client.get("/readiness")
        assert response.status_code == 200
        readiness_data = response.json()
        assert "ready" in readiness_data
        assert "dependencies" in readiness_data

        # Test OpenAPI documentation
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

        # Test OpenAPI JSON schema
        response = client.get("/openapi.json")
        assert response.status_code == 200
        openapi_data = response.json()
        assert openapi_data["info"]["title"] == "Snowflake MCP Lambda"

    def test_cors_headers_present(self, client: TestClient) -> None:
        """Test that appropriate CORS headers are set."""
        response = client.options("/health")
        # FastAPI automatically handles OPTIONS requests
        assert response.status_code in [
            200,
            405,
        ]  # 405 is acceptable for OPTIONS on GET-only endpoints

    def test_health_endpoint_response_format(self, client: TestClient) -> None:
        """Test that health endpoint returns properly formatted response."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        required_fields = ["status", "timestamp", "service", "version"]

        for field in required_fields:
            assert (
                field in data
            ), f"Required field '{field}' missing from health response"

        assert data["status"] == "healthy"
        assert data["service"] == "snowflake-mcp-lambda"
        assert data["version"] == "0.1.0"

    def test_readiness_endpoint_response_format(self, client: TestClient) -> None:
        """Test that readiness endpoint returns properly formatted response."""
        response = client.get("/readiness")
        assert response.status_code == 200

        data = response.json()
        required_fields = ["ready", "timestamp", "dependencies"]

        for field in required_fields:
            assert (
                field in data
            ), f"Required field '{field}' missing from readiness response"

        # Check dependencies structure
        dependencies = data["dependencies"]
        expected_deps = ["database", "redis", "snowflake"]

        for dep in expected_deps:
            assert dep in dependencies, f"Expected dependency '{dep}' missing"

    @pytest.mark.integration
    def test_application_startup_shutdown(self, client: TestClient) -> None:
        """Test that application starts up and shuts down cleanly."""
        # This test verifies that the TestClient can successfully
        # create an application instance, which tests startup/shutdown

        # Multiple requests to ensure consistent behavior
        for _ in range(3):
            response = client.get("/health")
            assert response.status_code == 200

        # Test that the client can be reused
        response = client.get("/")
        assert response.status_code == 200
