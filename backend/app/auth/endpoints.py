# ABOUTME: Authentication API endpoints for OAuth and user management
# ABOUTME: Handles login, callback, logout, profile, and preferences endpoints

import base64
import json
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from app.auth.jwt_utils import (
    JWTError,
    create_jwt_cookie_clear_headers,
    create_jwt_cookie_response_headers,
    create_jwt_token,
    get_jwt_token_from_request,
    verify_jwt_token,
)
from app.auth.oauth_service import (
    GoogleOAuthService,
    OAuthError,
    create_google_oauth_service,
)
from app.auth.user_service import UserService, get_user_service
from app.config import get_settings
from app.models.user import User

# Router for auth endpoints
router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


# Request/Response models
class UserPreferencesUpdate(BaseModel):
    """Model for user preferences update request."""

    auto_run_queries: bool | None = Field(
        None, description="Auto-run queries without confirmation"
    )
    default_row_limit: int | None = Field(
        None, ge=1, le=10000, description="Default row limit"
    )
    default_output_format: str | None = Field(None, description="Default output format")


class AuthHealthResponse(BaseModel):
    """Model for auth health check response."""

    status: str = Field(description="Health status")
    oauth_configured: bool = Field(description="Whether OAuth is properly configured")
    timestamp: str = Field(description="Current timestamp")


# Helper functions
def get_oauth_service() -> GoogleOAuthService:
    """Get OAuth service instance."""
    settings = get_settings()
    return create_google_oauth_service(settings)


def encode_state(redirect_url: str | None = None) -> str:
    """Encode state parameter for OAuth flow.

    Args:
        redirect_url: Optional URL to redirect to after auth

    Returns:
        Base64-encoded state string
    """
    state_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "redirect_url": redirect_url,
    }

    state_json = json.dumps(state_data)
    return base64.urlsafe_b64encode(state_json.encode()).decode()


def decode_state(state: str) -> str | None:
    """Decode state parameter from OAuth flow.

    Args:
        state: Base64-encoded state string

    Returns:
        Redirect URL if present, None otherwise
    """
    try:
        state_json = base64.urlsafe_b64decode(state.encode()).decode()
        state_data = json.loads(state_json)
        return state_data.get("redirect_url")
    except Exception:
        return None


def get_current_user(request: Request) -> User:
    """Get current authenticated user from JWT token.

    Args:
        request: FastAPI request object

    Returns:
        Current user object

    Raises:
        HTTPException: If authentication fails
    """
    # Get JWT token from cookie
    token = get_jwt_token_from_request(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    try:
        # Verify token and extract user ID
        payload = verify_jwt_token(token)
        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
            )

        # Get user from database
        user_service = get_user_service()
        user = user_service.get_user_by_id(user_id)

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        return user

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        ) from e


# Auth endpoints
@router.get("/login")
async def login(
    request: Request,
    redirect: str | None = Query(None, description="URL to redirect to after login"),
) -> RedirectResponse:
    """Initiate Google OAuth login flow.

    Args:
        request: FastAPI request object
        redirect: Optional redirect URL after successful login

    Returns:
        Redirect response to Google OAuth authorization URL
    """
    try:
        oauth_service = get_oauth_service()

        # Encode redirect URL in state parameter
        state = encode_state(redirect)

        # Get authorization URL
        auth_url, _ = oauth_service.get_authorization_url(state=state)

        return RedirectResponse(url=auth_url, status_code=302)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate login: {e!s}",
        ) from e


@router.get("/callback")
async def oauth_callback(
    code: str | None = Query(None, description="OAuth authorization code"),
    state: str | None = Query(None, description="OAuth state parameter"),
    error: str | None = Query(None, description="OAuth error parameter"),
) -> RedirectResponse:
    """Handle OAuth callback from Google.

    Args:
        code: Authorization code from Google
        state: State parameter for CSRF protection
        error: Error parameter if OAuth failed

    Returns:
        Redirect response to app or error page
    """
    # Check for OAuth errors
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {error}",
        )

    # Validate required parameters
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing authorization code"
        )

    if not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing state parameter"
        )

    try:
        # Exchange code for tokens
        oauth_service = get_oauth_service()
        credentials = oauth_service.exchange_code_for_tokens(code, state)

        # Get user info from Google
        oauth_user_info = oauth_service.get_user_info(credentials)

        # Get or create user in database
        user_service = get_user_service()
        user = user_service.get_or_create_user(oauth_user_info)

        # Create JWT token
        jwt_token = create_jwt_token(user.id)

        # Determine redirect URL
        redirect_url = decode_state(state) or "/"

        # Create response with JWT cookie
        response = RedirectResponse(url=redirect_url, status_code=302)

        # Set JWT cookie
        cookie_headers = create_jwt_cookie_response_headers(jwt_token)
        for key, value in cookie_headers.items():
            response.headers[key] = value

        return response

    except OAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {e!s}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {e!s}",
        ) from e


@router.post("/logout")
async def logout() -> Response:
    """Logout user by clearing JWT cookie.

    Returns:
        Response with cleared JWT cookie
    """
    response = Response(
        content=json.dumps({"message": "Logged out successfully"}),
        media_type="application/json",
    )

    # Clear JWT cookie
    cookie_headers = create_jwt_cookie_clear_headers()
    for key, value in cookie_headers.items():
        response.headers[key] = value

    return response


@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)) -> dict[str, Any]:  # noqa: B008
    """Get current user profile.

    Args:
        current_user: Current authenticated user

    Returns:
        User profile data
    """
    return current_user.to_profile_dict()


@router.put("/preferences")
async def update_preferences(
    preferences: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    user_service: UserService = Depends(get_user_service),  # noqa: B008
) -> dict[str, Any]:
    """Update user preferences.

    Args:
        preferences: Preferences to update
        current_user: Current authenticated user

    Returns:
        Updated user profile data
    """
    try:
        # Convert preferences to dict, excluding None values
        preferences_dict = preferences.model_dump(exclude_none=True)

        # Update user preferences
        updated_user = user_service.update_user_preferences(
            current_user.id, preferences_dict
        )

        return updated_user.to_profile_dict()

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {e!s}",
        ) from e


@router.get("/health", response_model=AuthHealthResponse)
async def auth_health_check() -> AuthHealthResponse:
    """Health check for authentication system.

    Returns:
        Auth health status
    """
    settings = get_settings()

    # Check if OAuth is configured
    oauth_configured = bool(
        settings.GOOGLE_CLIENT_ID
        and settings.GOOGLE_CLIENT_SECRET
        and settings.GOOGLE_CLIENT_ID != ""
        and settings.GOOGLE_CLIENT_SECRET != ""
    )

    return AuthHealthResponse(
        status="healthy",
        oauth_configured=oauth_configured,
        timestamp=datetime.utcnow().isoformat(),
    )
