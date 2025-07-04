# ABOUTME: Tests for .env file loading functionality
# ABOUTME: Ensures settings can be loaded from .env files

import os
import tempfile

from pydantic_settings import SettingsConfigDict

from app.config import Settings


class TestEnvFileLoading:
    """Test .env file loading functionality."""

    def test_env_file_loading(self) -> None:
        """Test that settings load from .env file."""
        # Create a temporary .env file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("DEBUG=false\n")
            f.write("LOG_LEVEL=ERROR\n")
            f.write("SECRET_KEY=test-from-env-file\n")
            env_file = f.name

        try:
            # Create a custom settings class that uses our temp file
            class TestSettings(Settings):
                model_config = SettingsConfigDict(
                    env_file=env_file,
                    env_file_encoding="utf-8",
                    case_sensitive=True,
                    extra="ignore",
                )

            settings = TestSettings()

            assert settings.DEBUG is False
            assert settings.LOG_LEVEL == "ERROR"
            assert settings.SECRET_KEY == "test-from-env-file"
        finally:
            # Clean up
            os.unlink(env_file)

    def test_env_var_overrides_env_file(self) -> None:
        """Test that environment variables override .env file values."""
        # Create a temporary .env file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("DEBUG=false\n")
            f.write("LOG_LEVEL=ERROR\n")
            env_file = f.name

        try:
            # Set an environment variable that should override the file
            os.environ["LOG_LEVEL"] = "DEBUG"

            # Create a custom settings class that uses our temp file
            class TestSettings(Settings):
                model_config = SettingsConfigDict(
                    env_file=env_file,
                    env_file_encoding="utf-8",
                    case_sensitive=True,
                    extra="ignore",
                )

            settings = TestSettings()

            assert settings.DEBUG is False  # From file
            assert settings.LOG_LEVEL == "DEBUG"  # From env var (override)
        finally:
            # Clean up
            os.unlink(env_file)
            del os.environ["LOG_LEVEL"]

    def test_missing_env_file_uses_defaults(self) -> None:
        """Test that missing .env file doesn't cause errors."""

        # Create a custom settings class with non-existent env file
        class TestSettings(Settings):
            model_config = SettingsConfigDict(
                env_file="non-existent-file.env",
                env_file_encoding="utf-8",
                case_sensitive=True,
                extra="ignore",
            )

        # Should use defaults
        settings = TestSettings()
        assert settings.DEBUG is True
        assert settings.LOG_LEVEL == "INFO"
        assert "dev-secret-key" in settings.SECRET_KEY
