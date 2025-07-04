# ABOUTME: JWT token utilities for authentication
# ABOUTME: Handles JWT creation, verification, and cookie management

from datetime import datetime, timedelta
from typing import Any

import jwt
from fastapi import Request

from app.config import get_settings


class JWTError(Exception):
    """Exception raised for JWT-related errors."""

    pass


def create_jwt_token(user_id: int) -> str:
    """Create JWT token for user.

    Args:
        user_id: User ID to encode in token

    Returns:
        JWT token string

    Raises:
        JWTError: If token creation fails
    """
    try:
        settings = get_settings()

        # Token payload
        payload = {
            "user_id": user_id,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS),
        }

        # Create and return token
        return jwt.encode(
            payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

    except Exception as e:
        raise JWTError(f"Failed to create JWT token: {e!s}") from e


def verify_jwt_token(token: str) -> dict[str, Any]:
    """Verify and decode JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        JWTError: If token verification fails
    """
    try:
        settings = get_settings()

        # Decode and verify token
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        return dict(payload)

    except jwt.ExpiredSignatureError as e:
        raise JWTError("Token has expired") from e
    except jwt.InvalidTokenError as e:
        raise JWTError("Invalid token") from e
    except Exception as e:
        raise JWTError(f"Token verification failed: {e!s}") from e


def get_jwt_token_from_request(request: Request) -> str | None:
    """Extract JWT token from request cookies.

    Args:
        request: FastAPI request object

    Returns:
        JWT token string if found, None otherwise
    """
    settings = get_settings()
    return request.cookies.get(settings.JWT_COOKIE_NAME)


def create_jwt_cookie_response_headers(token: str) -> dict[str, str]:
    """Create response headers for setting JWT cookie.

    Args:
        token: JWT token to set in cookie

    Returns:
        Dictionary of response headers
    """
    settings = get_settings()

    # Calculate expiration time
    expires = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    expires_str = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")

    # Build cookie attributes
    cookie_attributes = [
        f"{settings.JWT_COOKIE_NAME}={token}",
        f"Expires={expires_str}",
        "Path=/",
        "HttpOnly",
        f"SameSite={settings.JWT_COOKIE_SAMESITE}",
    ]

    # Add Secure flag if configured
    if settings.JWT_COOKIE_SECURE:
        cookie_attributes.append("Secure")

    return {"Set-Cookie": "; ".join(cookie_attributes)}


def create_jwt_cookie_clear_headers() -> dict[str, str]:
    """Create response headers for clearing JWT cookie.

    Returns:
        Dictionary of response headers to clear cookie
    """
    settings = get_settings()

    # Set cookie with empty value and past expiration
    cookie_attributes = [
        f"{settings.JWT_COOKIE_NAME}=",
        "Expires=Thu, 01 Jan 1970 00:00:00 GMT",
        "Path=/",
        "HttpOnly",
        f"SameSite={settings.JWT_COOKIE_SAMESITE}",
    ]

    # Add Secure flag if configured
    if settings.JWT_COOKIE_SECURE:
        cookie_attributes.append("Secure")

    return {"Set-Cookie": "; ".join(cookie_attributes)}
