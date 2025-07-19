# ABOUTME: Test suite for Snowflake connection management API endpoints
# ABOUTME: Tests for REST API endpoints handling connection CRUD operations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestConnectionEndpoints:
    """Test connection management API endpoints."""

    def test_test_connection_endpoint_exists(self) -> None:
        """Test that the test-connection endpoint exists."""
        response = client.post(
            "/api/v1/snowflake/test-connection",
            json={
                "account": "test_account",
                "user": "test_user",
                "password": "test_password",
                "warehouse": "test_warehouse",
                "database": "test_database",
                "schema": "test_schema",
            },
        )

        # Should not be 404 (endpoint exists)
        assert response.status_code != 404

        # Should return JSON with success field
        data = response.json()
        assert "success" in data
        assert "message" in data
        assert "response_time_ms" in data
