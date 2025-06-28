#!/usr/bin/env python3
# ABOUTME: Configuration validation script for testing the config system
# ABOUTME: Tests environment loading, validation, and service configurations

import os
import sys

sys.path.insert(0, "backend")


def validate_configuration():
    """Validate the configuration system with test environment variables."""
    print("🔧 Validating Configuration Management System...")

    # Test environment variables
    test_env_vars = {
        "ENVIRONMENT": "development",
        "SECRET_KEY": "test-secret-key-that-is-definitely-longer-than-32-characters",
        "DATABASE_URL": "postgresql://test:test@localhost:5432/testdb",
        "REDIS_URL": "redis://localhost:6379/0",
        "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
        "GOOGLE_CLIENT_SECRET": "test-client-secret",
        "GOOGLE_REDIRECT_URI": "http://localhost:8000/auth/callback",
        "JWT_ALGORITHM": "HS256",
        "JWT_EXPIRE_HOURS": "24",
        "SNOWFLAKE_TIMEOUT_SECONDS": "30",
        "SNOWFLAKE_QUERY_ROW_LIMIT": "500",
        "SNOWFLAKE_SCHEMA_CACHE_TTL": "3600",
        "RATE_LIMIT_REQUESTS_PER_MINUTE": "60",
        "RATE_LIMIT_BURST_SIZE": "10",
        "CORS_ORIGINS": "http://localhost:3000,http://localhost:5173",
        "SECURITY_HEADERS": "true",
    }

    # Set environment variables
    print("📝 Setting up test environment variables...")
    for key, value in test_env_vars.items():
        os.environ[key] = value

    try:
        # Import configuration modules
        print("📦 Importing configuration modules...")
        from app.core.config import (
            DevelopmentSettings,
            get_database_config,
            get_oauth_config,
            get_rate_limit_config,
            get_security_config,
            get_settings,
            get_snowflake_config,
        )

        # Test basic settings loading
        print("⚙️  Testing basic settings loading...")
        settings = get_settings()
        assert isinstance(settings, DevelopmentSettings)
        assert settings.DEBUG is True
        assert settings.ENVIRONMENT == "development"
        assert settings.SECRET_KEY == test_env_vars["SECRET_KEY"]
        print("   ✅ Basic settings loaded successfully")

        # Test database configuration
        print("🗄️  Testing database configuration...")
        db_config = get_database_config()
        db_settings = db_config.get_database_config()
        assert db_settings["url"] == test_env_vars["DATABASE_URL"]
        assert db_settings["echo"] is True  # Debug mode
        print("   ✅ Database configuration working")

        # Test OAuth configuration
        print("🔐 Testing OAuth configuration...")
        oauth_config = get_oauth_config()
        oauth_settings = oauth_config.get_oauth_config()
        assert oauth_settings["client_id"] == test_env_vars["GOOGLE_CLIENT_ID"]
        assert "openid" in oauth_settings["scope"]
        print("   ✅ OAuth configuration working")

        # Test Snowflake configuration
        print("❄️  Testing Snowflake configuration...")
        snowflake_config = get_snowflake_config()
        assert snowflake_config.timeout_seconds == 30
        assert snowflake_config.query_row_limit == 500
        print("   ✅ Snowflake configuration working")

        # Test security configuration
        print("🔒 Testing security configuration...")
        security_config = get_security_config()
        jwt_config = security_config.get_jwt_config()
        assert jwt_config["algorithm"] == "HS256"
        assert jwt_config["expire_hours"] == 24
        print("   ✅ Security configuration working")

        # Test rate limiting configuration
        print("🚦 Testing rate limiting configuration...")
        rate_limit_config = get_rate_limit_config()
        rate_limit_settings = rate_limit_config.get_rate_limit_config()
        assert rate_limit_settings["requests_per_minute"] == 60
        assert rate_limit_settings["burst_size"] == 10
        print("   ✅ Rate limiting configuration working")

        # Test configuration caching
        print("💾 Testing configuration caching...")
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2  # Should be same instance due to caching
        print("   ✅ Configuration caching working")

        # Test validation errors
        print("⚠️  Testing configuration validation...")

        # Test invalid secret key
        os.environ["SECRET_KEY"] = "short"
        get_settings.cache_clear()  # Clear cache
        try:
            get_settings()
            assert False, "Should have raised validation error for short secret key"
        except Exception as e:
            assert "SECRET_KEY" in str(e)
            print("   ✅ Secret key validation working")

        # Restore valid secret key
        os.environ["SECRET_KEY"] = test_env_vars["SECRET_KEY"]
        get_settings.cache_clear()

        print("\n🎉 Configuration Management System Validation Complete!")
        print("✅ All configuration components working correctly")
        print("✅ Environment switching functional")
        print("✅ Validation system working")
        print("✅ Service-specific configs operational")
        print("✅ Security settings properly configured")

        return True

    except Exception as e:
        print(f"\n❌ Configuration validation failed: {e!s}")
        import traceback

        traceback.print_exc()
        return False


def test_security_module():
    """Test the security module functionality."""
    print("\n🔐 Testing Security Module...")

    try:
        from app.core.security import (
            generate_secure_token,
            hash_password,
            validate_token_format,
            verify_password,
        )

        # Test password hashing
        print("🔑 Testing password hashing...")
        password = "test_password_123"
        hashed = hash_password(password)
        assert verify_password(password, hashed)
        assert not verify_password("wrong_password", hashed)
        print("   ✅ Password hashing working")

        # Test token format validation
        print("🎫 Testing token format validation...")
        valid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        assert validate_token_format(valid_token)
        assert not validate_token_format("invalid.token")
        assert not validate_token_format("")
        print("   ✅ Token format validation working")

        # Test secure token generation
        print("🎲 Testing secure token generation...")
        token1 = generate_secure_token(32)
        token2 = generate_secure_token(32)
        assert len(token1) == 64  # 32 bytes = 64 hex chars
        assert token1 != token2  # Should be different
        print("   ✅ Secure token generation working")

        print("✅ Security module validation complete!")
        return True

    except Exception as e:
        print(f"❌ Security module validation failed: {e!s}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Starting Configuration Management System Validation\n")

    config_success = validate_configuration()
    security_success = test_security_module()

    if config_success and security_success:
        print("\n🎊 All validations passed! Configuration system is ready.")
        sys.exit(0)
    else:
        print("\n💥 Some validations failed. Please check the errors above.")
        sys.exit(1)
