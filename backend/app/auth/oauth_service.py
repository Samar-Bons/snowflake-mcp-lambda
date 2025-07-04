# ABOUTME: Google OAuth 2.0 service for user authentication
# ABOUTME: Handles OAuth flow, token exchange, and user info retrieval

from dataclasses import dataclass
from typing import Any

from google.auth.exceptions import GoogleAuthError
from google_auth_oauthlib.flow import Flow  # type: ignore[import-untyped]
from googleapiclient.discovery import build  # type: ignore[import-untyped]

from app.config import Settings


class OAuthError(Exception):
    """Exception raised for OAuth-related errors."""

    pass


@dataclass
class OAuthUserInfo:
    """User information retrieved from Google OAuth."""

    google_id: str
    email: str
    name: str
    picture: str | None
    verified_email: bool


class GoogleOAuthService:
    """Service for handling Google OAuth 2.0 authentication flow."""

    def __init__(self, settings: Settings) -> None:
        """Initialize OAuth service with configuration settings."""
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
        self.scopes = settings.GOOGLE_OAUTH_SCOPES

        # Google OAuth client configuration
        self._client_config = {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [self.redirect_uri],
            }
        }

    def get_authorization_url(self, state: str | None = None) -> tuple[str, str]:
        """Generate OAuth authorization URL.

        Args:
            state: Optional state parameter for CSRF protection

        Returns:
            Tuple of (authorization_url, state)

        Raises:
            OAuthError: If URL generation fails
        """
        try:
            flow = Flow.from_client_config(
                self._client_config, scopes=self.scopes, redirect_uri=self.redirect_uri
            )

            auth_url, flow_state = flow.authorization_url(
                access_type="offline", include_granted_scopes="true", state=state
            )

            return auth_url, flow_state

        except Exception as e:
            raise OAuthError(f"Failed to generate authorization URL: {e!s}") from e

    def exchange_code_for_tokens(self, code: str, state: str) -> Any:
        """Exchange authorization code for access tokens.

        Args:
            code: Authorization code from OAuth callback
            state: State parameter for CSRF verification

        Returns:
            Google OAuth credentials object

        Raises:
            OAuthError: If token exchange fails
        """
        try:
            flow = Flow.from_client_config(
                self._client_config,
                scopes=self.scopes,
                redirect_uri=self.redirect_uri,
                state=state,
            )

            flow.fetch_token(code=code)
            return flow.credentials

        except GoogleAuthError as e:
            raise OAuthError(f"Failed to exchange code for tokens: {e!s}") from e
        except Exception as e:
            raise OAuthError(f"Unexpected error during token exchange: {e!s}") from e

    def get_user_info(self, credentials: Any) -> OAuthUserInfo:
        """Retrieve user information from Google API.

        Args:
            credentials: Google OAuth credentials

        Returns:
            OAuthUserInfo with user details

        Raises:
            OAuthError: If user info retrieval fails
        """
        try:
            # Build Google API service client
            service = build("oauth2", "v2", credentials=credentials)

            # Get user info from Google API
            user_data = service.userinfo().get().execute()

            # Verify email is verified
            if not user_data.get("verified_email", False):
                raise OAuthError("Email not verified by Google")

            # Extract user information
            return OAuthUserInfo(
                google_id=user_data["id"],
                email=user_data["email"],
                name=user_data["name"],
                picture=user_data.get("picture"),
                verified_email=user_data["verified_email"],
            )

        except OAuthError:
            # Re-raise OAuthError as-is
            raise
        except Exception as e:
            raise OAuthError(f"Failed to retrieve user info: {e!s}") from e


def create_google_oauth_service(settings: Settings) -> GoogleOAuthService:
    """Factory function to create Google OAuth service.

    Args:
        settings: Application settings

    Returns:
        Configured GoogleOAuthService instance
    """
    return GoogleOAuthService(settings)
