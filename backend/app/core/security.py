# ABOUTME: Security utilities for JWT token handling and OAuth validation
# ABOUTME: Provides secure authentication and authorization functionality

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any

import jwt
import structlog
from google.auth.exceptions import GoogleAuthError
from google.auth.transport import requests
from google.oauth2 import id_token

from .config import SecurityConfig, get_security_config

logger = structlog.get_logger(__name__)


class JWTError(Exception):
    """Custom JWT error exception."""

    pass


class OAuthError(Exception):
    """Custom OAuth error exception."""

    pass


class SecurityManager:
    """Centralized security management for JWT and OAuth operations."""

    def __init__(self, security_config: SecurityConfig | None = None):
        """Initialize security manager with configuration."""
        self.config = security_config or get_security_config()
        self.jwt_config = self.config.get_jwt_config()

    def create_access_token(
        self, data: dict[str, Any], expires_delta: timedelta | None = None
    ) -> str:
        """
        Create a JWT access token.

        Args:
            data: Payload data to encode in token
            expires_delta: Optional custom expiration time

        Returns:
            str: Encoded JWT token

        Raises:
            JWTError: If token creation fails
        """
        try:
            to_encode = data.copy()

            # Set expiration time
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(
                    hours=self.jwt_config["expire_hours"]
                )

            to_encode.update(
                {"exp": expire, "iat": datetime.utcnow(), "type": "access_token"}
            )

            # Create token
            encoded_jwt = jwt.encode(
                to_encode,
                self.jwt_config["secret_key"],
                algorithm=self.jwt_config["algorithm"],
            )

            logger.info(
                "JWT token created successfully",
                user_id=data.get("sub"),
                expires_at=expire.isoformat(),
                token_type="access_token",
            )

            return encoded_jwt

        except Exception as e:
            logger.error(
                "Failed to create JWT token",
                error=str(e),
                error_type=type(e).__name__,
                user_id=data.get("sub"),
            )
            raise JWTError(f"Failed to create access token: {e!s}")

    def verify_token(self, token: str) -> dict[str, Any]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token to verify

        Returns:
            Dict[str, Any]: Decoded token payload

        Raises:
            JWTError: If token verification fails
        """
        try:
            payload = jwt.decode(
                token,
                self.jwt_config["secret_key"],
                algorithms=[self.jwt_config["algorithm"]],
            )

            # Validate token type
            if payload.get("type") != "access_token":
                raise JWTError("Invalid token type")

            logger.debug(
                "JWT token verified successfully",
                user_id=payload.get("sub"),
                expires_at=datetime.fromtimestamp(payload.get("exp", 0)).isoformat(),
            )

            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired", token_preview=token[:20] + "...")
            raise JWTError("Token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning(
                "Invalid JWT token", error=str(e), token_preview=token[:20] + "..."
            )
            raise JWTError(f"Invalid token: {e!s}")
        except Exception as e:
            logger.error(
                "JWT token verification failed",
                error=str(e),
                error_type=type(e).__name__,
            )
            raise JWTError(f"Token verification failed: {e!s}")

    def create_refresh_token(self, data: dict[str, Any]) -> str:
        """
        Create a JWT refresh token.

        Args:
            data: Payload data to encode in token

        Returns:
            str: Encoded JWT refresh token

        Raises:
            JWTError: If token creation fails
        """
        try:
            to_encode = data.copy()

            # Refresh tokens have longer expiration (7 days)
            expire = datetime.utcnow() + timedelta(days=7)

            to_encode.update(
                {"exp": expire, "iat": datetime.utcnow(), "type": "refresh_token"}
            )

            encoded_jwt = jwt.encode(
                to_encode,
                self.jwt_config["secret_key"],
                algorithm=self.jwt_config["algorithm"],
            )

            logger.info(
                "JWT refresh token created successfully",
                user_id=data.get("sub"),
                expires_at=expire.isoformat(),
            )

            return encoded_jwt

        except Exception as e:
            logger.error(
                "Failed to create JWT refresh token",
                error=str(e),
                error_type=type(e).__name__,
            )
            raise JWTError(f"Failed to create refresh token: {e!s}")

    def verify_refresh_token(self, token: str) -> dict[str, Any]:
        """
        Verify and decode a JWT refresh token.

        Args:
            token: JWT refresh token to verify

        Returns:
            Dict[str, Any]: Decoded token payload

        Raises:
            JWTError: If token verification fails
        """
        try:
            payload = jwt.decode(
                token,
                self.jwt_config["secret_key"],
                algorithms=[self.jwt_config["algorithm"]],
            )

            # Validate token type
            if payload.get("type") != "refresh_token":
                raise JWTError("Invalid refresh token type")

            logger.debug(
                "JWT refresh token verified successfully", user_id=payload.get("sub")
            )

            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("JWT refresh token has expired")
            raise JWTError("Refresh token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning("Invalid JWT refresh token", error=str(e))
            raise JWTError(f"Invalid refresh token: {e!s}")
        except Exception as e:
            logger.error(
                "JWT refresh token verification failed",
                error=str(e),
                error_type=type(e).__name__,
            )
            raise JWTError(f"Refresh token verification failed: {e!s}")


class OAuthManager:
    """OAuth validation and token management."""

    def __init__(self, client_id: str):
        """Initialize OAuth manager with Google client ID."""
        self.client_id = client_id

    def verify_google_token(self, token: str) -> dict[str, Any]:
        """
        Verify a Google OAuth ID token.

        Args:
            token: Google ID token to verify

        Returns:
            Dict[str, Any]: Decoded token payload with user info

        Raises:
            OAuthError: If token verification fails
        """
        try:
            # Verify the token using Google's library
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), self.client_id
            )

            # Verify the issuer
            if idinfo["iss"] not in [
                "accounts.google.com",
                "https://accounts.google.com",
            ]:
                raise OAuthError("Invalid token issuer")

            logger.info(
                "Google OAuth token verified successfully",
                user_id=idinfo.get("sub"),
                email=idinfo.get("email"),
                domain=idinfo.get("hd"),  # G Suite domain if applicable
            )

            return idinfo

        except GoogleAuthError as e:
            logger.warning(
                "Google OAuth token verification failed",
                error=str(e),
                error_type=type(e).__name__,
            )
            raise OAuthError(f"Google token verification failed: {e!s}")
        except Exception as e:
            logger.error(
                "OAuth token verification error",
                error=str(e),
                error_type=type(e).__name__,
            )
            raise OAuthError(f"Token verification error: {e!s}")

    def extract_user_info(self, token_payload: dict[str, Any]) -> dict[str, Any]:
        """
        Extract user information from verified Google token payload.

        Args:
            token_payload: Verified Google token payload

        Returns:
            Dict[str, Any]: Extracted user information
        """
        return {
            "google_id": token_payload.get("sub"),
            "email": token_payload.get("email"),
            "email_verified": token_payload.get("email_verified", False),
            "name": token_payload.get("name"),
            "given_name": token_payload.get("given_name"),
            "family_name": token_payload.get("family_name"),
            "picture": token_payload.get("picture"),
            "locale": token_payload.get("locale"),
            "domain": token_payload.get("hd"),  # G Suite domain
        }


# Password hashing utilities (for future use)
def hash_password(password: str) -> str:
    """
    Hash a password using PBKDF2 with SHA-256.

    Args:
        password: Plain text password

    Returns:
        str: Hashed password with salt
    """
    salt = secrets.token_hex(32)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    )
    return f"{salt}:{password_hash.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password with salt

    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        salt, password_hash = hashed_password.split(":")
        computed_hash = hashlib.pbkdf2_hmac(
            "sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100000
        )
        return password_hash == computed_hash.hex()
    except ValueError:
        return False


# Token validation utilities
def validate_token_format(token: str) -> bool:
    """
    Validate JWT token format without decoding.

    Args:
        token: JWT token string

    Returns:
        bool: True if format is valid, False otherwise
    """
    if not token:
        return False

    parts = token.split(".")
    if len(parts) != 3:
        return False

    # Basic validation - each part should be base64url encoded
    try:
        for part in parts:
            # Check if it's valid base64url
            if not part.replace("-", "+").replace("_", "/").isalnum():
                return False
        return True
    except Exception:
        return False


def extract_token_from_header(authorization_header: str) -> str | None:
    """
    Extract JWT token from Authorization header.

    Args:
        authorization_header: Authorization header value

    Returns:
        Optional[str]: Extracted token or None if invalid format
    """
    if not authorization_header:
        return None

    try:
        scheme, token = authorization_header.split(" ", 1)
        if scheme.lower() != "bearer":
            return None

        return token.strip()
    except ValueError:
        return None


# Security helper functions
def generate_secure_token(length: int = 32) -> str:
    """
    Generate a secure random token.

    Args:
        length: Token length in bytes

    Returns:
        str: Secure random token as hex string
    """
    import secrets

    return secrets.token_hex(length)


def is_token_expired(token_payload: dict[str, Any]) -> bool:
    """
    Check if a token payload indicates expiration.

    Args:
        token_payload: Decoded token payload

    Returns:
        bool: True if token is expired, False otherwise
    """
    exp = token_payload.get("exp")
    if not exp:
        return True

    return datetime.fromtimestamp(exp) < datetime.utcnow()


# Global security manager instance
security_manager = SecurityManager()


# Convenience functions for easy access
def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Create access token using global security manager."""
    return security_manager.create_access_token(data, expires_delta)


def verify_token(token: str) -> dict[str, Any]:
    """Verify token using global security manager."""
    return security_manager.verify_token(token)


def create_refresh_token(data: dict[str, Any]) -> str:
    """Create refresh token using global security manager."""
    return security_manager.create_refresh_token(data)


def verify_refresh_token(token: str) -> dict[str, Any]:
    """Verify refresh token using global security manager."""
    return security_manager.verify_refresh_token(token)
