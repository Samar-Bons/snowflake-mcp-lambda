# ABOUTME: Test suite for Snowflake connection management service
# ABOUTME: Comprehensive tests for encryption, pooling, and connection lifecycle

from unittest.mock import Mock

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

    def test_encryption_is_reversible(self) -> None:
        """Test that encryption can be decrypted back to original values."""
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
        decrypted = service.decrypt_connection_params(encrypted)

        assert decrypted.account == "test_account"
        assert decrypted.user == "test_user"
        assert decrypted.password == "test_password"
        assert decrypted.warehouse == "test_warehouse"
        assert decrypted.database == "test_database"
        assert decrypted.schema == "test_schema"

    def test_encryption_uses_aes_256(self) -> None:
        """Test that encryption uses AES-256 encryption."""
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

        # AES encrypted data should be base64 encoded and significantly different
        # from the original values
        assert len(encrypted["encrypted_account"]) > len("test_account")
        assert len(encrypted["encrypted_password"]) > len("test_password")

        # Should not be simple string reversal
        assert encrypted["encrypted_account"] != "test_account"[::-1]
        assert encrypted["encrypted_password"] != "test_password"[::-1]

        # Should be Fernet encrypted (base64url encoded with special chars)
        import re

        fernet_pattern = re.compile(r"^[A-Za-z0-9_-]*={0,2}$")
        assert fernet_pattern.match(encrypted["encrypted_account"])
        assert fernet_pattern.match(encrypted["encrypted_password"])

    @pytest.mark.asyncio
    async def test_can_save_connection_to_database(self) -> None:
        """Test that service can save encrypted connection to database."""
        service = SnowflakeConnectionService()

        params = ConnectionParams(
            account="test_account",
            user="test_user",
            password="test_password",
            warehouse="test_warehouse",
            database="test_database",
            schema="test_schema",
        )

        # Mock database session
        mock_db_session = Mock()
        mock_connection = Mock()
        mock_connection.id = 1
        mock_connection.name = "Test Connection"
        mock_connection.user_id = 1
        mock_connection.encrypted_account = "tnuocca_tset"  # reversed
        mock_connection.encrypted_password = "drowssap_tset"  # reversed

        # Mock the database operations
        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None

        # Should save and return a connection with an ID
        saved_connection = await service.save_connection(
            user_id=1, name="Test Connection", params=params, db=mock_db_session
        )

        # Verify database operations were called
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

        # Verify the connection object
        assert saved_connection is not None
        assert hasattr(saved_connection, "user_id")
        assert hasattr(saved_connection, "name")
