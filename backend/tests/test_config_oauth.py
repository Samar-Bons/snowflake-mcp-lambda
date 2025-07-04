# ABOUTME: Tests for OAuth configuration settings
# ABOUTME: Validates Google OAuth client configuration and JWT settings

import pytest
from pydantic import ValidationError

from app.config import Settings


class TestOAuthConfig:
    """Test suite for OAuth configuration settings."""

    def test_oauth_settings_with_defaults(self) -> None:
        """Test that OAuth settings have appropriate defaults."""
        settings = Settings()

        # Should have empty client credentials requiring configuration
        assert settings.GOOGLE_CLIENT_ID == ""
        assert settings.GOOGLE_CLIENT_SECRET == ""
        assert (
            settings.GOOGLE_REDIRECT_URI == "http://localhost:8000/api/v1/auth/callback"
        )

        # JWT settings should have secure defaults
        assert settings.JWT_SECRET_KEY == settings.SECRET_KEY
        assert settings.JWT_ALGORITHM == "HS256"
        assert settings.JWT_EXPIRATION_HOURS == 24
        assert settings.JWT_COOKIE_NAME == "snowflake_token"
        assert settings.JWT_COOKIE_SECURE is True
        assert settings.JWT_COOKIE_SAMESITE == "lax"

    def test_oauth_settings_with_environment_variables(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test OAuth settings are loaded from environment variables."""
        monkeypatch.setenv("GOOGLE_CLIENT_ID", "test_client_id")
        monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test_client_secret")
        monkeypatch.setenv("GOOGLE_REDIRECT_URI", "https://example.com/callback")
        monkeypatch.setenv("JWT_SECRET_KEY", "custom_jwt_secret")
        monkeypatch.setenv("JWT_ALGORITHM", "HS512")
        monkeypatch.setenv("JWT_EXPIRATION_HOURS", "12")
        monkeypatch.setenv("JWT_COOKIE_NAME", "custom_token")
        monkeypatch.setenv("JWT_COOKIE_SECURE", "false")
        monkeypatch.setenv("JWT_COOKIE_SAMESITE", "strict")

        settings = Settings()

        assert settings.GOOGLE_CLIENT_ID == "test_client_id"
        assert settings.GOOGLE_CLIENT_SECRET == "test_client_secret"
        assert settings.GOOGLE_REDIRECT_URI == "https://example.com/callback"
        assert settings.JWT_SECRET_KEY == "custom_jwt_secret"
        assert settings.JWT_ALGORITHM == "HS512"
        assert settings.JWT_EXPIRATION_HOURS == 12
        assert settings.JWT_COOKIE_NAME == "custom_token"
        assert settings.JWT_COOKIE_SECURE is False
        assert settings.JWT_COOKIE_SAMESITE == "strict"

    def test_jwt_algorithm_validation(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test JWT algorithm validation accepts valid algorithms."""
        valid_algorithms = ["HS256", "HS384", "HS512"]

        for algorithm in valid_algorithms:
            monkeypatch.setenv("JWT_ALGORITHM", algorithm)
            settings = Settings()
            assert algorithm == settings.JWT_ALGORITHM

    def test_jwt_algorithm_validation_invalid(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test JWT algorithm validation rejects invalid algorithms."""
        monkeypatch.setenv("JWT_ALGORITHM", "INVALID_ALG")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        assert "Invalid JWT algorithm" in str(exc_info.value)

    def test_jwt_expiration_validation(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test JWT expiration hours validation."""
        # Valid range: 1-168 hours (1 hour to 1 week)
        valid_hours = [1, 24, 168]

        for hours in valid_hours:
            monkeypatch.setenv("JWT_EXPIRATION_HOURS", str(hours))
            settings = Settings()
            assert hours == settings.JWT_EXPIRATION_HOURS

    def test_jwt_expiration_validation_out_of_range(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test JWT expiration hours validation rejects out-of-range values."""
        invalid_hours = [0, -1, 169, 1000]

        for hours in invalid_hours:
            monkeypatch.setenv("JWT_EXPIRATION_HOURS", str(hours))

            with pytest.raises(ValidationError):
                Settings()

    def test_cookie_samesite_validation(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test cookie SameSite validation accepts valid values."""
        valid_values = ["strict", "lax", "none"]

        for value in valid_values:
            monkeypatch.setenv("JWT_COOKIE_SAMESITE", value)
            settings = Settings()
            assert value == settings.JWT_COOKIE_SAMESITE

    def test_cookie_samesite_validation_invalid(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test cookie SameSite validation rejects invalid values."""
        monkeypatch.setenv("JWT_COOKIE_SAMESITE", "invalid_value")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        assert "Invalid SameSite value" in str(exc_info.value)

    def test_oauth_scopes_configuration(self) -> None:
        """Test that OAuth scopes are properly configured."""
        settings = Settings()

        # Should have basic Google OAuth scopes
        expected_scopes = ["openid", "email", "profile"]
        assert expected_scopes == settings.GOOGLE_OAUTH_SCOPES

    def test_oauth_settings_ready_for_production(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that OAuth settings work for production configuration."""
        monkeypatch.setenv("GOOGLE_CLIENT_ID", "prod_client_id")
        monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "prod_client_secret")
        monkeypatch.setenv(
            "GOOGLE_REDIRECT_URI", "https://prod.example.com/api/v1/auth/callback"
        )
        monkeypatch.setenv("JWT_SECRET_KEY", "super_secure_production_secret")
        monkeypatch.setenv("JWT_COOKIE_SECURE", "true")
        monkeypatch.setenv("DEBUG", "false")

        settings = Settings()

        # Production settings should be secure
        assert settings.GOOGLE_CLIENT_ID == "prod_client_id"
        assert settings.GOOGLE_CLIENT_SECRET == "prod_client_secret"
        assert (
            settings.GOOGLE_REDIRECT_URI
            == "https://prod.example.com/api/v1/auth/callback"
        )
        assert settings.JWT_SECRET_KEY == "super_secure_production_secret"
        assert settings.JWT_COOKIE_SECURE is True
        assert settings.DEBUG is False
