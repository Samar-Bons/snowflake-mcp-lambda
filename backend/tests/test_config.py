# ABOUTME: Tests for configuration management system
# ABOUTME: Validates settings loading, environment variable handling, and defaults

import os
from unittest.mock import patch

import pytest
from app.config import Settings, settings


class TestSettings:
    """Test configuration system functionality."""

    def test_default_settings_values(self) -> None:
        """Test that default configuration values are set correctly."""
        default_settings = Settings()

        assert default_settings.DEBUG is True
        assert default_settings.LOG_LEVEL == "INFO"
        assert default_settings.SECRET_KEY == "dev-secret-key-change-in-production"
        assert "postgresql://" in default_settings.DATABASE_URL
        assert "redis://" in default_settings.REDIS_URL
        assert default_settings.API_V1_PREFIX == "/api/v1"

    def test_settings_from_environment_variables(self) -> None:
        """Test that settings can be loaded from environment variables."""
        env_vars = {
            "DEBUG": "false",
            "LOG_LEVEL": "DEBUG",
            "SECRET_KEY": "test-secret-key",
            "DATABASE_URL": "postgresql://test:test@localhost:5432/test",
            "REDIS_URL": "redis://localhost:6380/1",
            "API_V1_PREFIX": "/api/v2",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            env_settings = Settings()

            assert env_settings.DEBUG is False
            assert env_settings.LOG_LEVEL == "DEBUG"
            assert env_settings.SECRET_KEY == "test-secret-key"
            assert (
                env_settings.DATABASE_URL
                == "postgresql://test:test@localhost:5432/test"
            )
            assert env_settings.REDIS_URL == "redis://localhost:6380/1"
            assert env_settings.API_V1_PREFIX == "/api/v2"

    def test_settings_validation(self) -> None:
        """Test that settings validation works correctly."""
        # Test valid log level
        valid_settings = Settings(LOG_LEVEL="WARNING")
        assert valid_settings.LOG_LEVEL == "WARNING"

        # Test invalid log level should be rejected
        with pytest.raises(ValueError):
            Settings(LOG_LEVEL="INVALID_LEVEL")  # type: ignore[arg-type]

    def test_settings_singleton_instance(self) -> None:
        """Test that the global settings instance is accessible."""
        assert settings is not None
        assert isinstance(settings, Settings)
        assert hasattr(settings, "DEBUG")
        assert hasattr(settings, "SECRET_KEY")

    def test_settings_types(self) -> None:
        """Test that settings have correct types."""
        test_settings = Settings()

        assert isinstance(test_settings.DEBUG, bool)
        assert isinstance(test_settings.LOG_LEVEL, str)
        assert isinstance(test_settings.SECRET_KEY, str)
        assert isinstance(test_settings.DATABASE_URL, str)
        assert isinstance(test_settings.REDIS_URL, str)
        assert isinstance(test_settings.API_V1_PREFIX, str)

    def test_environment_file_configuration(self) -> None:
        """Test that settings respect environment file configuration."""
        # This tests the Config class attributes
        test_settings = Settings()
        config = test_settings.Config

        assert config.env_file_encoding == "utf-8"
        assert config.case_sensitive is True
        assert config.extra == "ignore"
