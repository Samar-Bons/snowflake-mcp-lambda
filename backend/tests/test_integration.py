# ABOUTME: Integration tests for complete application functionality
# ABOUTME: Tests end-to-end functionality including server startup and configuration

import subprocess
import time

import pytest
import requests

from app.config import settings


class TestApplicationIntegration:
    """Test complete application integration."""

    def test_application_settings_load_correctly(self) -> None:
        """Test that application settings can be loaded without errors."""
        # This should not raise any exceptions
        assert settings.DEBUG is not None
        assert settings.LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert len(settings.SECRET_KEY) > 0
        assert "postgresql://" in settings.DATABASE_URL
        assert "redis://" in settings.REDIS_URL

    def test_fastapi_app_can_be_imported(self) -> None:
        """Test that the FastAPI app can be imported without errors."""
        from app.main import app

        assert app is not None
        assert app.title == "Snowflake MCP Lambda"
        assert app.version == "0.1.0"

    @pytest.mark.slow
    def test_development_server_starts_successfully(self) -> None:
        """Test that the development server can start and respond to requests."""
        # Start the server in a subprocess
        server_cmd = [
            "poetry",
            "run",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8002",
            "--app-dir",
            "backend",
            "--timeout-keep-alive",
            "5",
        ]

        try:
            # Start server process
            process = subprocess.Popen(
                server_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=".",
            )

            # Give the server time to start
            time.sleep(3)

            # Check if server is responsive
            try:
                response = requests.get("http://127.0.0.1:8002/health", timeout=5)
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "healthy"
                assert data["service"] == "snowflake-mcp-lambda"

                # Test another endpoint
                response = requests.get("http://127.0.0.1:8002/", timeout=5)
                assert response.status_code == 200
                root_data = response.json()
                assert root_data["service"] == "snowflake-mcp-lambda"
                assert "endpoints" in root_data

            except requests.exceptions.ConnectionError:
                pytest.fail("Could not connect to development server")

        finally:
            # Clean up: terminate the server process
            if process:
                process.terminate()
                process.wait(timeout=10)

    def test_configuration_environment_isolation(self) -> None:
        """Test that configuration properly handles environment isolation."""
        # Test that we can create different settings instances
        from app.config import Settings

        # Create a settings instance with custom values
        custom_settings = Settings(
            DEBUG=False,
            LOG_LEVEL="WARNING",
            SECRET_KEY="custom-test-key",
        )

        assert custom_settings.DEBUG is False
        assert custom_settings.LOG_LEVEL == "WARNING"
        assert custom_settings.SECRET_KEY == "custom-test-key"

        # Original settings should be unaffected
        assert settings.DEBUG is True  # default value
