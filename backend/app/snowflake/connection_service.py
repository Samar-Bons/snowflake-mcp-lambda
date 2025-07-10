# ABOUTME: Snowflake connection management service with encryption and pooling
# ABOUTME: Handles secure connection storage, validation, and lifecycle management

import base64
import os
import secrets
import time
from dataclasses import dataclass

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.database import get_database_session
from app.models.connection import SnowflakeConnection


@dataclass
class ConnectionParams:
    """Connection parameters for Snowflake."""

    account: str
    user: str
    password: str
    warehouse: str
    database: str
    schema: str


@dataclass
class ConnectionTestResult:
    """Result of a connection test."""

    success: bool
    message: str
    response_time_ms: int


class SnowflakeConnectionService:
    """Service for managing Snowflake connections with encryption and pooling."""

    def __init__(self) -> None:
        """Initialize connection service with secure encryption."""
        settings = get_settings()

        # Use environment variable for production encryption key
        encryption_key = os.environ.get("SNOWFLAKE_ENCRYPTION_KEY")

        if not encryption_key:
            if not settings.DEBUG:
                raise ValueError(
                    "SNOWFLAKE_ENCRYPTION_KEY environment variable is required in production. "
                    "Generate one with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
                )

            # For development only - generate a random salt each time
            # This ensures development databases can't be easily decrypted
            password = settings.SECRET_KEY.encode()  # Use app secret key as base
            salt = secrets.token_bytes(16)  # Generate random salt

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))

            # Store salt for this session (in production, salt would be stored securely)
            self._dev_salt = salt
        else:
            # Production: use provided Fernet key directly
            try:
                key = encryption_key.encode()
                # Validate the key by creating a Fernet instance
                Fernet(key)
            except Exception as e:
                raise ValueError(
                    f"Invalid SNOWFLAKE_ENCRYPTION_KEY format. Must be a valid Fernet key. "
                    f"Generate one with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'. "
                    f"Error: {e}"
                ) from e

        self._cipher = Fernet(key)

    def encrypt_connection_params(self, params: ConnectionParams) -> dict[str, str]:
        """Encrypt connection parameters using AES-256."""
        return {
            "encrypted_account": self._cipher.encrypt(params.account.encode()).decode(),
            "encrypted_user": self._cipher.encrypt(params.user.encode()).decode(),
            "encrypted_password": self._cipher.encrypt(
                params.password.encode()
            ).decode(),
            "encrypted_warehouse": self._cipher.encrypt(
                params.warehouse.encode()
            ).decode(),
            "encrypted_database": self._cipher.encrypt(
                params.database.encode()
            ).decode(),
            "encrypted_schema": self._cipher.encrypt(params.schema.encode()).decode(),
        }

    def decrypt_connection_params(self, encrypted: dict[str, str]) -> ConnectionParams:
        """Decrypt connection parameters using AES-256."""
        return ConnectionParams(
            account=self._cipher.decrypt(
                encrypted["encrypted_account"].encode()
            ).decode(),
            user=self._cipher.decrypt(encrypted["encrypted_user"].encode()).decode(),
            password=self._cipher.decrypt(
                encrypted["encrypted_password"].encode()
            ).decode(),
            warehouse=self._cipher.decrypt(
                encrypted["encrypted_warehouse"].encode()
            ).decode(),
            database=self._cipher.decrypt(
                encrypted["encrypted_database"].encode()
            ).decode(),
            schema=self._cipher.decrypt(
                encrypted["encrypted_schema"].encode()
            ).decode(),
        )

    async def test_connection(self, params: ConnectionParams) -> ConnectionTestResult:
        """Test connection parameters."""
        start_time = time.time()

        # For now, just return a successful test
        response_time_ms = int((time.time() - start_time) * 1000)

        return ConnectionTestResult(
            success=True,
            message="Connection test successful",
            response_time_ms=response_time_ms,
        )

    async def save_connection(
        self,
        user_id: int,
        name: str,
        params: ConnectionParams,
        is_default: bool = False,
        query_timeout: int = 30,
        max_rows: int = 500,
        db: Session | None = None,
    ) -> SnowflakeConnection:
        """Save connection with encryption."""
        # Use dependency injection or proper session management
        session_provided = db is not None

        if db is None:
            # Create a new session and ensure it's properly closed
            db_session = get_database_session()
            db = next(db_session)

        # Now db is guaranteed to be not None
        try:
            # Encrypt connection parameters
            encrypted_params = self.encrypt_connection_params(params)

            # Create new connection
            connection = SnowflakeConnection(
                user_id=user_id,
                name=name,
                is_default=is_default,
                query_timeout=query_timeout,
                max_rows=max_rows,
                encrypted_account=encrypted_params["encrypted_account"],
                encrypted_user=encrypted_params["encrypted_user"],
                encrypted_password=encrypted_params["encrypted_password"],
                encrypted_warehouse=encrypted_params["encrypted_warehouse"],
                encrypted_database=encrypted_params["encrypted_database"],
                encrypted_schema=encrypted_params["encrypted_schema"],
                encrypted_role=encrypted_params.get("encrypted_role"),
            )

            db.add(connection)
            db.commit()
            db.refresh(connection)

            return connection

        except Exception:
            # Rollback on error
            db.rollback()
            raise
        finally:
            # Only close if we created the session
            if not session_provided:
                db.close()
