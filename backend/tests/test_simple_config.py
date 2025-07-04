# ABOUTME: Tests for simple configuration system
# ABOUTME: Ensures settings are loaded correctly from environment

import os
from unittest.mock import patch

import pytest
from pydantic_settings import SettingsConfigDict

from app.config import Settings


class TestSimpleConfiguration:
    """Test simple configuration functionality."""

    def test_default_settings(self) -> None:
        """Test that settings load with default values."""
        # Clear all env vars to test defaults
        with patch.dict(os.environ, {}, clear=True):
            # Use a non-existent env file
            class TestSettings(Settings):
                model_config = SettingsConfigDict(
                    env_file="non-existent-test-file.env",
                    env_file_encoding="utf-8",
                    case_sensitive=True,
                    extra="ignore",
                )

            settings = TestSettings()
            assert settings.DEBUG is True
            assert settings.LOG_LEVEL == "INFO"
            assert settings.API_V1_PREFIX == "/api/v1"
            assert "dev-secret-key" in settings.SECRET_KEY

    def test_environment_override(self) -> None:
        """Test that environment variables override defaults."""
        with patch.dict(
            os.environ,
            {
                "DEBUG": "false",
                "LOG_LEVEL": "WARNING",
                "SECRET_KEY": "test-secret-key",
            },
        ):
            settings = Settings()
            assert settings.DEBUG is False
            assert settings.LOG_LEVEL == "WARNING"
            assert settings.SECRET_KEY == "test-secret-key"

    def test_case_sensitive_settings(self) -> None:
        """Test that settings are case sensitive."""
        with patch.dict(os.environ, {"debug": "false", "DEBUG": "true"}):
            settings = Settings()
            # Should use DEBUG (uppercase) due to case_sensitive=True
            assert settings.DEBUG is True

    def test_extra_env_vars_ignored(self) -> None:
        """Test that extra environment variables are ignored."""
        with patch.dict(
            os.environ,
            {
                "EXTRA_VAR": "should_be_ignored",
                "DEBUG": "false",
            },
        ):
            # Should not raise an error
            settings = Settings()
            assert settings.DEBUG is False
            assert not hasattr(settings, "EXTRA_VAR")

    def test_invalid_log_level_raises_error(self) -> None:
        """Test that invalid log level raises validation error."""
        with (
            patch.dict(os.environ, {"LOG_LEVEL": "INVALID"}),
            pytest.raises(ValueError),
        ):
            Settings()
