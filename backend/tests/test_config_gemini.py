# ABOUTME: Tests for Gemini LLM configuration settings
# ABOUTME: Validates Google Gemini API configuration and model validation

import pytest
from pydantic import ValidationError

from app.config import Settings


class TestGeminiConfig:
    """Test suite for Gemini LLM configuration settings."""

    def test_gemini_settings_with_defaults(self) -> None:
        """Test that Gemini settings have appropriate defaults."""
        settings = Settings()

        # Should have empty API key requiring user configuration
        assert settings.GEMINI_API_KEY == ""
        assert settings.GEMINI_MODEL == "gemini-1.5-flash"
        assert settings.GEMINI_MAX_TOKENS == 1000
        assert settings.GEMINI_TEMPERATURE == 0.1
        assert settings.GEMINI_TIMEOUT_SECONDS == 30

    def test_gemini_settings_with_environment_variables(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test Gemini settings are loaded from environment variables."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_api_key_123")
        monkeypatch.setenv("GEMINI_MODEL", "gemini-1.5-pro")
        monkeypatch.setenv("GEMINI_MAX_TOKENS", "2000")
        monkeypatch.setenv("GEMINI_TEMPERATURE", "0.3")
        monkeypatch.setenv("GEMINI_TIMEOUT_SECONDS", "45")

        settings = Settings()

        assert settings.GEMINI_API_KEY == "test_api_key_123"
        assert settings.GEMINI_MODEL == "gemini-1.5-pro"
        assert settings.GEMINI_MAX_TOKENS == 2000
        assert settings.GEMINI_TEMPERATURE == 0.3
        assert settings.GEMINI_TIMEOUT_SECONDS == 45

    def test_gemini_model_validation(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Gemini model validation accepts valid models."""
        valid_models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"]

        for model in valid_models:
            monkeypatch.setenv("GEMINI_MODEL", model)
            settings = Settings()
            assert settings.GEMINI_MODEL == model

    def test_gemini_model_validation_invalid(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test Gemini model validation rejects invalid models."""
        monkeypatch.setenv("GEMINI_MODEL", "gpt-4")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        assert "Invalid Gemini model" in str(exc_info.value)

    def test_gemini_max_tokens_validation(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Gemini max tokens validation."""
        # Valid range: 100-4000 tokens
        valid_token_counts = [100, 1000, 4000]

        for tokens in valid_token_counts:
            monkeypatch.setenv("GEMINI_MAX_TOKENS", str(tokens))
            settings = Settings()
            assert settings.GEMINI_MAX_TOKENS == tokens

    def test_gemini_max_tokens_validation_out_of_range(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test Gemini max tokens validation rejects out-of-range values."""
        invalid_token_counts = [99, 4001, 10000]

        for tokens in invalid_token_counts:
            monkeypatch.setenv("GEMINI_MAX_TOKENS", str(tokens))

            with pytest.raises(ValidationError):
                Settings()

    def test_gemini_temperature_validation(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Gemini temperature validation."""
        # Valid range: 0.0-1.0
        valid_temperatures = [0.0, 0.1, 0.5, 1.0]

        for temp in valid_temperatures:
            monkeypatch.setenv("GEMINI_TEMPERATURE", str(temp))
            settings = Settings()
            assert settings.GEMINI_TEMPERATURE == temp

    def test_gemini_temperature_validation_out_of_range(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test Gemini temperature validation rejects out-of-range values."""
        invalid_temperatures = [-0.1, 1.1, 2.0]

        for temp in invalid_temperatures:
            monkeypatch.setenv("GEMINI_TEMPERATURE", str(temp))

            with pytest.raises(ValidationError):
                Settings()

    def test_gemini_timeout_validation(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Gemini timeout validation."""
        # Valid range: 5-120 seconds
        valid_timeouts = [5, 30, 120]

        for timeout in valid_timeouts:
            monkeypatch.setenv("GEMINI_TIMEOUT_SECONDS", str(timeout))
            settings = Settings()
            assert settings.GEMINI_TIMEOUT_SECONDS == timeout

    def test_gemini_timeout_validation_out_of_range(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test Gemini timeout validation rejects out-of-range values."""
        invalid_timeouts = [4, 121, 300]

        for timeout in invalid_timeouts:
            monkeypatch.setenv("GEMINI_TIMEOUT_SECONDS", str(timeout))

            with pytest.raises(ValidationError):
                Settings()

    def test_snowflake_settings_with_defaults(self) -> None:
        """Test that Snowflake settings have appropriate defaults."""
        settings = Settings()

        # Should have empty connection settings requiring user configuration
        assert settings.SNOWFLAKE_ACCOUNT == ""
        assert settings.SNOWFLAKE_USER == ""
        assert settings.SNOWFLAKE_PASSWORD == ""
        assert settings.SNOWFLAKE_WAREHOUSE == ""
        assert settings.SNOWFLAKE_DATABASE == ""
        assert settings.SNOWFLAKE_SCHEMA == ""
        assert settings.SNOWFLAKE_ROLE == ""
        assert settings.SNOWFLAKE_QUERY_TIMEOUT == 300
        assert settings.SNOWFLAKE_MAX_ROWS == 500

    def test_snowflake_settings_with_environment_variables(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test Snowflake settings are loaded from environment variables."""
        monkeypatch.setenv("SNOWFLAKE_ACCOUNT", "test_account")
        monkeypatch.setenv("SNOWFLAKE_USER", "test_user")
        monkeypatch.setenv("SNOWFLAKE_PASSWORD", "test_password")
        monkeypatch.setenv("SNOWFLAKE_WAREHOUSE", "test_warehouse")
        monkeypatch.setenv("SNOWFLAKE_DATABASE", "test_database")
        monkeypatch.setenv("SNOWFLAKE_SCHEMA", "test_schema")
        monkeypatch.setenv("SNOWFLAKE_ROLE", "test_role")
        monkeypatch.setenv("SNOWFLAKE_QUERY_TIMEOUT", "600")
        monkeypatch.setenv("SNOWFLAKE_MAX_ROWS", "1000")

        settings = Settings()

        assert settings.SNOWFLAKE_ACCOUNT == "test_account"
        assert settings.SNOWFLAKE_USER == "test_user"
        assert settings.SNOWFLAKE_PASSWORD == "test_password"
        assert settings.SNOWFLAKE_WAREHOUSE == "test_warehouse"
        assert settings.SNOWFLAKE_DATABASE == "test_database"
        assert settings.SNOWFLAKE_SCHEMA == "test_schema"
        assert settings.SNOWFLAKE_ROLE == "test_role"
        assert settings.SNOWFLAKE_QUERY_TIMEOUT == 600
        assert settings.SNOWFLAKE_MAX_ROWS == 1000

    def test_snowflake_query_timeout_validation(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test Snowflake query timeout validation."""
        # Valid range: 10-3600 seconds
        valid_timeouts = [10, 300, 3600]

        for timeout in valid_timeouts:
            monkeypatch.setenv("SNOWFLAKE_QUERY_TIMEOUT", str(timeout))
            settings = Settings()
            assert settings.SNOWFLAKE_QUERY_TIMEOUT == timeout

    def test_snowflake_query_timeout_validation_out_of_range(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test Snowflake query timeout validation rejects out-of-range values."""
        invalid_timeouts = [9, 3601, 10000]

        for timeout in invalid_timeouts:
            monkeypatch.setenv("SNOWFLAKE_QUERY_TIMEOUT", str(timeout))

            with pytest.raises(ValidationError):
                Settings()

    def test_snowflake_max_rows_validation(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Snowflake max rows validation."""
        # Valid range: 1-10000 rows
        valid_row_counts = [1, 500, 10000]

        for rows in valid_row_counts:
            monkeypatch.setenv("SNOWFLAKE_MAX_ROWS", str(rows))
            settings = Settings()
            assert settings.SNOWFLAKE_MAX_ROWS == rows

    def test_snowflake_max_rows_validation_out_of_range(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test Snowflake max rows validation rejects out-of-range values."""
        invalid_row_counts = [0, 10001, 50000]

        for rows in invalid_row_counts:
            monkeypatch.setenv("SNOWFLAKE_MAX_ROWS", str(rows))

            with pytest.raises(ValidationError):
                Settings()
