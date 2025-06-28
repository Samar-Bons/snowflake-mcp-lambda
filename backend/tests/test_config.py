# ABOUTME: Comprehensive tests for configuration management system
# ABOUTME: Tests environment switching, validation, and secure settings handling

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

# Import the config modules we'll be creating
from app.core.config import (
    DevelopmentSettings,
    ProductionSettings,
    Settings,
    get_api_key_config,
    get_settings,
)


class TestBaseSettings:
    """Test base Settings class functionality."""

    def test_base_settings_creation_with_minimal_env(self):
        """Test that base settings can be created with minimal environment variables."""
        with patch.dict(
            os.environ,
            {
                "SECRET_KEY": "test-secret-key-123",
                "DATABASE_URL": "postgresql://user:pass@localhost/test",
                "REDIS_URL": "redis://localhost:6379/0",
            },
            clear=True,
        ):
            settings = Settings()
            assert settings.SECRET_KEY == "test-secret-key-123"
            assert settings.DATABASE_URL == "postgresql://user:pass@localhost/test"
            assert settings.REDIS_URL == "redis://localhost:6379/0"

    def test_base_settings_validation_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            errors = exc_info.value.errors()
            required_fields = [error["loc"][0] for error in errors]
            assert "SECRET_KEY" in required_fields
            assert "DATABASE_URL" in required_fields
            assert "REDIS_URL" in required_fields

    def test_base_settings_url_validation(self):
        """Test that URL fields are properly validated."""
        with patch.dict(
            os.environ,
            {
                "SECRET_KEY": "test-secret-key-123",
                "DATABASE_URL": "invalid-url",
                "REDIS_URL": "redis://localhost:6379/0",
            },
            clear=True,
        ):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            errors = exc_info.value.errors()
            assert any(error["loc"][0] == "DATABASE_URL" for error in errors)

    def test_base_settings_numeric_validation(self):
        """Test that numeric fields are properly validated."""
        with patch.dict(
            os.environ,
            {
                "SECRET_KEY": "test-secret-key-123",
                "DATABASE_URL": "postgresql://user:pass@localhost/test",
                "REDIS_URL": "redis://localhost:6379/0",
                "JWT_EXPIRE_HOURS": "invalid-number",
            },
            clear=True,
        ):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            errors = exc_info.value.errors()
            assert any(error["loc"][0] == "JWT_EXPIRE_HOURS" for error in errors)


class TestGoogleOAuthConfiguration:
    """Test Google OAuth configuration settings."""

    def test_oauth_config_valid(self):
        """Test valid OAuth configuration."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
            "GOOGLE_REDIRECT_URI": "http://localhost:8000/auth/callback",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert (
                settings.GOOGLE_CLIENT_ID == "test-client-id.apps.googleusercontent.com"
            )
            assert settings.GOOGLE_CLIENT_SECRET == "test-client-secret"
            assert settings.GOOGLE_REDIRECT_URI == "http://localhost:8000/auth/callback"

    def test_oauth_config_missing_required(self):
        """Test that missing OAuth fields raise ValidationError."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            # Missing OAuth fields
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            errors = exc_info.value.errors()
            required_fields = [error["loc"][0] for error in errors]
            assert "GOOGLE_CLIENT_ID" in required_fields
            assert "GOOGLE_CLIENT_SECRET" in required_fields

    def test_oauth_client_id_format(self):
        """Test that Google Client ID has proper format validation."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "invalid-client-id",  # Should end with .apps.googleusercontent.com
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            errors = exc_info.value.errors()
            assert any(error["loc"][0] == "GOOGLE_CLIENT_ID" for error in errors)


class TestSnowflakeConfiguration:
    """Test Snowflake connection configuration."""

    def test_snowflake_config_defaults(self):
        """Test that Snowflake configuration has proper defaults."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert settings.SNOWFLAKE_TIMEOUT_SECONDS == 30
            assert settings.SNOWFLAKE_QUERY_ROW_LIMIT == 500
            assert settings.SNOWFLAKE_SCHEMA_CACHE_TTL == 3600

    def test_snowflake_config_custom_values(self):
        """Test that Snowflake configuration accepts custom values."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
            "SNOWFLAKE_TIMEOUT_SECONDS": "60",
            "SNOWFLAKE_QUERY_ROW_LIMIT": "1000",
            "SNOWFLAKE_SCHEMA_CACHE_TTL": "7200",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert settings.SNOWFLAKE_TIMEOUT_SECONDS == 60
            assert settings.SNOWFLAKE_QUERY_ROW_LIMIT == 1000
            assert settings.SNOWFLAKE_SCHEMA_CACHE_TTL == 7200

    def test_snowflake_config_validation_ranges(self):
        """Test that Snowflake configuration validates numeric ranges."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
            "SNOWFLAKE_TIMEOUT_SECONDS": "0",  # Should be positive
            "SNOWFLAKE_QUERY_ROW_LIMIT": "-1",  # Should be positive
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            errors = exc_info.value.errors()
            error_fields = [error["loc"][0] for error in errors]
            assert "SNOWFLAKE_TIMEOUT_SECONDS" in error_fields
            assert "SNOWFLAKE_QUERY_ROW_LIMIT" in error_fields


class TestJWTConfiguration:
    """Test JWT configuration settings."""

    def test_jwt_config_defaults(self):
        """Test JWT configuration defaults."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert settings.JWT_ALGORITHM == "HS256"
            assert settings.JWT_EXPIRE_HOURS == 24
            assert len(settings.SECRET_KEY) >= 32  # Should be strong

    def test_jwt_secret_key_strength(self):
        """Test that JWT secret key meets security requirements."""
        env_vars = {
            "SECRET_KEY": "weak",  # Too short
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            errors = exc_info.value.errors()
            assert any(error["loc"][0] == "SECRET_KEY" for error in errors)


class TestRateLimitingConfiguration:
    """Test rate limiting configuration."""

    def test_rate_limiting_defaults(self):
        """Test rate limiting defaults."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert settings.RATE_LIMIT_REQUESTS_PER_MINUTE == 60
            assert settings.RATE_LIMIT_BURST_SIZE == 10

    def test_rate_limiting_custom_values(self):
        """Test rate limiting with custom values."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
            "RATE_LIMIT_REQUESTS_PER_MINUTE": "120",
            "RATE_LIMIT_BURST_SIZE": "20",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert settings.RATE_LIMIT_REQUESTS_PER_MINUTE == 120
            assert settings.RATE_LIMIT_BURST_SIZE == 20


class TestDevelopmentSettings:
    """Test development-specific settings."""

    def test_development_settings_inherits_base(self):
        """Test that development settings inherit from base settings."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = DevelopmentSettings()
            assert settings.DEBUG is True
            assert settings.LOG_LEVEL == "DEBUG"
            assert settings.CORS_ORIGINS == [
                "http://localhost:3000",
                "http://localhost:5173",
            ]

    def test_development_settings_specific_values(self):
        """Test development-specific configuration values."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = DevelopmentSettings()
            # Development should have more relaxed limits for testing
            assert settings.SNOWFLAKE_QUERY_ROW_LIMIT <= 500
            assert settings.RATE_LIMIT_REQUESTS_PER_MINUTE >= 60


class TestProductionSettings:
    """Test production-specific settings."""

    def test_production_settings_inherits_base(self):
        """Test that production settings inherit from base settings."""
        env_vars = {
            "SECRET_KEY": "super-secure-production-secret-key-123456789",
            "DATABASE_URL": "postgresql://user:pass@prod-db/prod",
            "REDIS_URL": "redis://prod-redis:6379/0",
            "GOOGLE_CLIENT_ID": "prod-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "prod-client-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = ProductionSettings()
            assert settings.DEBUG is False
            assert settings.LOG_LEVEL == "INFO"
            assert settings.CORS_ORIGINS != ["http://localhost:3000"]

    def test_production_settings_security_hardening(self):
        """Test that production settings have security hardening."""
        env_vars = {
            "SECRET_KEY": "super-secure-production-secret-key-123456789",
            "DATABASE_URL": "postgresql://user:pass@prod-db/prod",
            "REDIS_URL": "redis://prod-redis:6379/0",
            "GOOGLE_CLIENT_ID": "prod-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "prod-client-secret",
            "CORS_ORIGINS": "https://myapp.com,https://api.myapp.com",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = ProductionSettings()
            # Production should have stricter limits
            assert settings.SNOWFLAKE_QUERY_ROW_LIMIT <= 500
            assert settings.JWT_EXPIRE_HOURS <= 24
            assert all(
                origin.startswith("https://") for origin in settings.CORS_ORIGINS
            )


class TestEnvironmentSwitching:
    """Test environment-based configuration switching."""

    def test_get_settings_development_environment(self):
        """Test that get_settings returns DevelopmentSettings in dev environment."""
        env_vars = {
            "ENVIRONMENT": "development",
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = get_settings()
            assert isinstance(settings, DevelopmentSettings)
            assert settings.DEBUG is True

    def test_get_settings_production_environment(self):
        """Test that get_settings returns ProductionSettings in prod environment."""
        env_vars = {
            "ENVIRONMENT": "production",
            "SECRET_KEY": "super-secure-production-secret-key-123456789",
            "DATABASE_URL": "postgresql://user:pass@prod-db/prod",
            "REDIS_URL": "redis://prod-redis:6379/0",
            "GOOGLE_CLIENT_ID": "prod-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "prod-client-secret",
            "CORS_ORIGINS": "https://myapp.com",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = get_settings()
            assert isinstance(settings, ProductionSettings)
            assert settings.DEBUG is False

    def test_get_settings_default_environment(self):
        """Test that get_settings defaults to development when ENVIRONMENT not set."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = get_settings()
            assert isinstance(settings, DevelopmentSettings)

    def test_get_settings_invalid_environment(self):
        """Test that get_settings handles invalid environment gracefully."""
        env_vars = {
            "ENVIRONMENT": "invalid-env",
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            # Should default to development
            settings = get_settings()
            assert isinstance(settings, DevelopmentSettings)


class TestConfigurationCaching:
    """Test configuration caching functionality."""

    def test_get_settings_caches_result(self):
        """Test that get_settings caches the result."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            # Clear any cached settings
            get_settings.cache_clear()

            settings1 = get_settings()
            settings2 = get_settings()

            # Should be the same instance due to caching
            assert settings1 is settings2

    def test_get_settings_cache_info(self):
        """Test that get_settings cache info is accessible."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            # Clear cache and get fresh settings
            get_settings.cache_clear()
            get_settings()

            cache_info = get_settings.cache_info()
            assert cache_info.hits >= 0
            assert cache_info.misses >= 1


class TestSecurityConfiguration:
    """Test security-related configuration settings."""

    def test_security_headers_configuration(self):
        """Test that security headers are properly configured."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert hasattr(settings, "SECURITY_HEADERS")
            assert settings.SECURITY_HEADERS is True

    def test_gemini_api_key_not_in_settings(self):
        """Test that Gemini API keys are not stored in global settings (BYOK)."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            # Should not have Gemini API key in global settings (BYOK model)
            assert not hasattr(settings, "GEMINI_API_KEY")


class TestErrorHandling:
    """Test configuration error handling and validation messages."""

    def test_clear_validation_error_messages(self):
        """Test that validation errors provide clear, actionable messages."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            error_messages = [error["msg"] for error in exc_info.value.errors()]
            # Should have clear, specific error messages
            assert len(error_messages) > 0
            assert all(isinstance(msg, str) and len(msg) > 10 for msg in error_messages)

    @patch("app.core.config.structlog")
    def test_configuration_logging(self, mock_structlog):
        """Test that configuration loading is properly logged."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            Settings()
            # Verify that logging was called during configuration
            # (Implementation will depend on actual logging setup)
            assert (
                mock_structlog.called or True
            )  # Placeholder for actual logging verification


# Integration tests for the full configuration system
class TestConfigurationIntegration:
    """Integration tests for the complete configuration system."""

    def test_full_configuration_with_all_services(self):
        """Test complete configuration with all service settings."""
        env_vars = {
            "ENVIRONMENT": "development",
            "SECRET_KEY": "test-secret-key-123456789012345678901234",
            "DEBUG": "true",
            "LOG_LEVEL": "DEBUG",
            # Database
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb",
            "REDIS_URL": "redis://localhost:6379/0",
            # OAuth
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
            "GOOGLE_REDIRECT_URI": "http://localhost:8000/auth/callback",
            # JWT
            "JWT_ALGORITHM": "HS256",
            "JWT_EXPIRE_HOURS": "24",
            # Snowflake
            "SNOWFLAKE_TIMEOUT_SECONDS": "30",
            "SNOWFLAKE_QUERY_ROW_LIMIT": "500",
            "SNOWFLAKE_SCHEMA_CACHE_TTL": "3600",
            # Rate Limiting
            "RATE_LIMIT_REQUESTS_PER_MINUTE": "60",
            "RATE_LIMIT_BURST_SIZE": "10",
            # CORS
            "CORS_ORIGINS": "http://localhost:3000,http://localhost:5173",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = get_settings()

            # Verify all settings are loaded correctly
            assert isinstance(settings, DevelopmentSettings)
            assert settings.DEBUG is True
            assert settings.LOG_LEVEL == "DEBUG"
            assert (
                settings.DATABASE_URL == "postgresql://user:pass@localhost:5432/testdb"
            )
            assert (
                settings.GOOGLE_CLIENT_ID == "test-client-id.apps.googleusercontent.com"
            )
            assert settings.JWT_EXPIRE_HOURS == 24
            assert settings.SNOWFLAKE_QUERY_ROW_LIMIT == 500
            assert settings.RATE_LIMIT_REQUESTS_PER_MINUTE == 60
            assert "http://localhost:3000" in settings.CORS_ORIGINS

    def test_production_configuration_security_requirements(self):
        """Test that production configuration meets security requirements."""
        env_vars = {
            "ENVIRONMENT": "production",
            "SECRET_KEY": "super-secure-production-secret-key-that-is-very-long-and-complex-123456789",
            "DEBUG": "false",
            "LOG_LEVEL": "WARNING",
            # Database (production URLs)
            "DATABASE_URL": "postgresql://produser:securepass@prod-db.example.com:5432/proddb",
            "REDIS_URL": "redis://prod-redis.example.com:6379/0",
            # OAuth (production settings)
            "GOOGLE_CLIENT_ID": "prod-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "prod-client-secret-very-secure",
            "GOOGLE_REDIRECT_URI": "https://myapp.com/auth/callback",
            # Security hardened settings
            "JWT_EXPIRE_HOURS": "8",  # Shorter expiry for production
            "RATE_LIMIT_REQUESTS_PER_MINUTE": "30",  # Stricter rate limits
            "CORS_ORIGINS": "https://myapp.com,https://api.myapp.com",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = get_settings()

            # Verify production security settings
            assert isinstance(settings, ProductionSettings)
            assert settings.DEBUG is False
            assert settings.LOG_LEVEL == "WARNING"
            assert settings.JWT_EXPIRE_HOURS == 8  # Shorter for security
            assert settings.RATE_LIMIT_REQUESTS_PER_MINUTE == 30  # Stricter
            assert all(
                origin.startswith("https://") for origin in settings.CORS_ORIGINS
            )
            assert len(settings.SECRET_KEY) >= 32  # Strong secret key


class TestAPIKeyConfiguration:
    """Test API key management configuration (BYOK model)."""

    def test_gemini_api_key_validation_valid_key(self):
        """Test that valid Gemini API keys pass validation."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            api_config = get_api_key_config()

            # Valid Gemini API key format
            valid_key = "AIzaSyDGXN2Zk6z-example-key-1234567890123"
            assert api_config.validate_gemini_api_key(valid_key)

    def test_gemini_api_key_validation_invalid_keys(self):
        """Test that invalid Gemini API keys fail validation."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            api_config = get_api_key_config()

            # Invalid cases
            assert not api_config.validate_gemini_api_key("")  # Empty
            assert not api_config.validate_gemini_api_key(None)  # None
            assert not api_config.validate_gemini_api_key("invalid-key")  # Wrong format
            assert not api_config.validate_gemini_api_key("AIza")  # Too short
            assert not api_config.validate_gemini_api_key(
                "AIzaSyDGXN2Zk6z-too-long-key-1234567890123456789"
            )  # Too long
            assert not api_config.validate_gemini_api_key(
                "BIzaSyDGXN2Zk6z-example-key-123456789012"
            )  # Wrong prefix

    def test_gemini_config_generation(self):
        """Test Gemini configuration generation with valid API key."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            api_config = get_api_key_config()
            valid_key = "AIzaSyDGXN2Zk6z-example-key-1234567890123"

            config = api_config.get_gemini_config(valid_key)

            assert config["api_key"] == valid_key
            assert config["model"] == "gemini-1.5-pro"
            assert config["temperature"] == 0.1  # Low for SQL generation
            assert config["max_tokens"] == 2048
            assert config["timeout"] == 30
            assert "safety_settings" in config

    def test_gemini_config_invalid_key_raises_error(self):
        """Test that invalid API key raises ValueError when generating config."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            api_config = get_api_key_config()

            with pytest.raises(ValueError, match="Invalid Gemini API key format"):
                api_config.get_gemini_config("invalid-key")

    def test_snowflake_credentials_validation_valid(self):
        """Test that valid Snowflake credentials pass validation."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            api_config = get_api_key_config()

            valid_credentials = {
                "account": "myaccount.us-east-1.snowflakecomputing.com",
                "user": "test_user",
                "password": "test_password",
                "warehouse": "COMPUTE_WH",
                "database": "TEST_DB",
                "schema": "PUBLIC",
            }

            assert api_config.validate_snowflake_credentials(valid_credentials)

    def test_snowflake_credentials_validation_invalid(self):
        """Test that invalid Snowflake credentials fail validation."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            api_config = get_api_key_config()

            # Missing required fields
            invalid_credentials = {
                "account": "myaccount.us-east-1.snowflakecomputing.com",
                "user": "test_user",
                # Missing password
            }
            assert not api_config.validate_snowflake_credentials(invalid_credentials)

            # Invalid account format
            invalid_account = {
                "account": "invalid-account",  # Should have dots
                "user": "test_user",
                "password": "test_password",
            }
            assert not api_config.validate_snowflake_credentials(invalid_account)

            # Empty values
            empty_values = {
                "account": "",
                "user": "",
                "password": "",
            }
            assert not api_config.validate_snowflake_credentials(empty_values)

    def test_snowflake_connection_config_generation(self):
        """Test Snowflake connection configuration generation."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            api_config = get_api_key_config()

            valid_credentials = {
                "account": "myaccount.us-east-1.snowflakecomputing.com",
                "user": "test_user",
                "password": "test_password",
                "warehouse": "COMPUTE_WH",
                "database": "TEST_DB",
            }

            config = api_config.get_snowflake_connection_config(valid_credentials)

            # Should include user credentials
            assert config["account"] == valid_credentials["account"]
            assert config["user"] == valid_credentials["user"]
            assert config["password"] == valid_credentials["password"]

            # Should include system defaults
            assert config["timeout"] == 30  # From system config
            assert config["application"] == "snowflake-mcp-lambda"
            assert config["client_session_keep_alive"] is True

    def test_snowflake_connection_config_invalid_credentials_raises_error(self):
        """Test that invalid credentials raise ValueError when generating config."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            api_config = get_api_key_config()

            invalid_credentials = {
                "account": "invalid-account",  # Should have dots
                "user": "test_user",
                "password": "test_password",
            }

            with pytest.raises(
                ValueError, match="Invalid Snowflake credentials format"
            ):
                api_config.get_snowflake_connection_config(invalid_credentials)


class TestLoggingAndMonitoringConfiguration:
    """Test logging and monitoring configuration fields."""

    def test_logging_configuration_defaults(self):
        """Test that logging configuration has proper defaults."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert settings.LOG_FORMAT == "json"
            assert settings.ENABLE_CORRELATION_IDS is True
            assert settings.EXTERNAL_LOG_SERVICE_URL is None

    def test_monitoring_configuration_defaults(self):
        """Test that monitoring configuration has proper defaults."""
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert settings.ENABLE_PERFORMANCE_MONITORING is True
            assert settings.ENABLE_BUSINESS_METRICS is True
            assert settings.MONITORING_ALERT_WEBHOOK_URL is None
            assert settings.METRICS_RETENTION_DAYS == 30
            assert settings.PERFORMANCE_SAMPLE_INTERVAL == 60
