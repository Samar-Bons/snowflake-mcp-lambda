# ABOUTME: Test suite for Snowflake connection management service
# ABOUTME: Comprehensive tests for encryption, pooling, and connection lifecycle

import pytest

from app.snowflake.connection_service import (
    ConnectionParams,
    SnowflakeConnectionService,
)


class TestSnowflakeConnectionService:
    """Test main connection service functionality."""

    def test_connection_service_exists(self) -> None:
        """Test that we can create a connection service."""
        service = SnowflakeConnectionService()
        assert service is not None

    @pytest.mark.asyncio
    async def test_can_encrypt_connection_params(self) -> None:
        """Test that service can encrypt connection parameters."""
        service = SnowflakeConnectionService()

        params = ConnectionParams(
            account="test_account",
            user="test_user",
            password="test_password",
            warehouse="test_warehouse",
            database="test_database",
            schema="test_schema",
        )

        encrypted = service.encrypt_connection_params(params)

        assert encrypted["encrypted_account"] != "test_account"
        assert encrypted["encrypted_password"] != "test_password"
        assert "encrypted_account" in encrypted
        assert "encrypted_user" in encrypted
        assert "encrypted_password" in encrypted
        assert "encrypted_warehouse" in encrypted
        assert "encrypted_database" in encrypted
        assert "encrypted_schema" in encrypted

    @pytest.mark.asyncio
    async def test_can_test_connection(self) -> None:
        """Test that service can test a connection."""
        service = SnowflakeConnectionService()

        params = ConnectionParams(
            account="test_account",
            user="test_user",
            password="test_password",
            warehouse="test_warehouse",
            database="test_database",
            schema="test_schema",
        )

        result = await service.test_connection(params)

        assert hasattr(result, "success")
        assert hasattr(result, "message")
        assert hasattr(result, "response_time_ms")
        assert isinstance(result.success, bool)
        assert isinstance(result.message, str)
        assert isinstance(result.response_time_ms, int)
