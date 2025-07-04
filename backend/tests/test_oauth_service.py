# ABOUTME: Tests for OAuth service functionality
# ABOUTME: Tests Google OAuth flow integration and user authentication

from unittest.mock import Mock, patch

import pytest
from google.auth.exceptions import GoogleAuthError

from app.auth.oauth_service import (
    GoogleOAuthService,
    OAuthError,
    OAuthUserInfo,
    create_google_oauth_service,
)
from app.config import Settings


class TestGoogleOAuthService:
    """Test suite for Google OAuth service."""

    def test_oauth_service_initialization(self) -> None:
        """Test that OAuth service initializes with correct settings."""
        settings = Settings()
        service = GoogleOAuthService(settings)

        assert service.client_id == settings.GOOGLE_CLIENT_ID
        assert service.client_secret == settings.GOOGLE_CLIENT_SECRET
        assert service.redirect_uri == settings.GOOGLE_REDIRECT_URI
        assert service.scopes == settings.GOOGLE_OAUTH_SCOPES

    def test_create_google_oauth_service_factory(self) -> None:
        """Test that factory function creates OAuth service correctly."""
        settings = Settings()
        service = create_google_oauth_service(settings)

        assert isinstance(service, GoogleOAuthService)
        assert service.client_id == settings.GOOGLE_CLIENT_ID

    def test_get_authorization_url(self) -> None:
        """Test that authorization URL is generated correctly."""
        settings = Settings()
        service = GoogleOAuthService(settings)

        with patch("app.auth.oauth_service.Flow") as mock_flow:
            mock_flow_instance = Mock()
            mock_flow.from_client_config.return_value = mock_flow_instance
            mock_flow_instance.authorization_url.return_value = (
                "https://accounts.google.com/oauth/authorize?...",
                "random_state",
            )

            auth_url, state = service.get_authorization_url()

            assert auth_url.startswith("https://accounts.google.com/oauth/authorize")
            assert state == "random_state"
            mock_flow.from_client_config.assert_called_once()

    def test_get_authorization_url_with_state(self) -> None:
        """Test that authorization URL can be generated with custom state."""
        settings = Settings()
        service = GoogleOAuthService(settings)

        with patch("app.auth.oauth_service.Flow") as mock_flow:
            mock_flow_instance = Mock()
            mock_flow.from_client_config.return_value = mock_flow_instance
            mock_flow_instance.authorization_url.return_value = (
                "https://accounts.google.com/oauth/authorize?...",
                "custom_state",
            )

            auth_url, state = service.get_authorization_url(state="custom_state")

            assert state == "custom_state"
            mock_flow_instance.authorization_url.assert_called_with(
                access_type="offline",
                include_granted_scopes="true",
                state="custom_state",
            )

    def test_exchange_code_for_tokens_success(self) -> None:
        """Test successful code exchange for tokens."""
        settings = Settings()
        service = GoogleOAuthService(settings)

        with patch("app.auth.oauth_service.Flow") as mock_flow:
            mock_flow_instance = Mock()
            mock_flow.from_client_config.return_value = mock_flow_instance
            mock_credentials = Mock()
            mock_flow_instance.fetch_token.return_value = None
            mock_flow_instance.credentials = mock_credentials

            result = service.exchange_code_for_tokens("auth_code", "state")

            assert result == mock_credentials
            mock_flow_instance.fetch_token.assert_called_once_with(code="auth_code")

    def test_exchange_code_for_tokens_failure(self) -> None:
        """Test code exchange failure handling."""
        settings = Settings()
        service = GoogleOAuthService(settings)

        with patch("app.auth.oauth_service.Flow") as mock_flow:
            mock_flow_instance = Mock()
            mock_flow.from_client_config.return_value = mock_flow_instance
            mock_flow_instance.fetch_token.side_effect = GoogleAuthError("Invalid code")  # type: ignore[no-untyped-call]

            with pytest.raises(OAuthError) as exc_info:
                service.exchange_code_for_tokens("invalid_code", "state")

            assert "Failed to exchange code for tokens" in str(exc_info.value)

    def test_get_user_info_success(self) -> None:
        """Test successful user info retrieval."""
        settings = Settings()
        service = GoogleOAuthService(settings)

        mock_credentials = Mock()
        mock_user_data = {
            "id": "123456789",
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/photo.jpg",
            "verified_email": True,
        }

        with patch("app.auth.oauth_service.build") as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service
            mock_service.userinfo.return_value.get.return_value.execute.return_value = (
                mock_user_data
            )

            user_info = service.get_user_info(mock_credentials)

            assert isinstance(user_info, OAuthUserInfo)
            assert user_info.google_id == "123456789"
            assert user_info.email == "test@example.com"
            assert user_info.name == "Test User"
            assert user_info.picture == "https://example.com/photo.jpg"
            assert user_info.verified_email is True

    def test_get_user_info_unverified_email(self) -> None:
        """Test user info retrieval with unverified email."""
        settings = Settings()
        service = GoogleOAuthService(settings)

        mock_credentials = Mock()
        mock_user_data = {
            "id": "123456789",
            "email": "test@example.com",
            "name": "Test User",
            "verified_email": False,
        }

        with patch("app.auth.oauth_service.build") as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service
            mock_service.userinfo.return_value.get.return_value.execute.return_value = (
                mock_user_data
            )

            with pytest.raises(OAuthError) as exc_info:
                service.get_user_info(mock_credentials)

            assert "Email not verified" in str(exc_info.value)

    def test_get_user_info_api_failure(self) -> None:
        """Test user info retrieval API failure."""
        settings = Settings()
        service = GoogleOAuthService(settings)

        mock_credentials = Mock()

        with patch("app.auth.oauth_service.build") as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service
            mock_service.userinfo.return_value.get.return_value.execute.side_effect = (
                Exception("API Error")
            )

            with pytest.raises(OAuthError) as exc_info:
                service.get_user_info(mock_credentials)

            assert "Failed to retrieve user info" in str(exc_info.value)

    def test_oauth_user_info_dataclass(self) -> None:
        """Test OAuthUserInfo dataclass functionality."""
        user_info = OAuthUserInfo(
            google_id="123456789",
            email="test@example.com",
            name="Test User",
            picture="https://example.com/photo.jpg",
            verified_email=True,
        )

        assert user_info.google_id == "123456789"
        assert user_info.email == "test@example.com"
        assert user_info.name == "Test User"
        assert user_info.picture == "https://example.com/photo.jpg"
        assert user_info.verified_email is True

    def test_oauth_user_info_optional_picture(self) -> None:
        """Test OAuthUserInfo with optional picture field."""
        user_info = OAuthUserInfo(
            google_id="123456789",
            email="test@example.com",
            name="Test User",
            picture=None,
            verified_email=True,
        )

        assert user_info.picture is None

    def test_oauth_error_exception(self) -> None:
        """Test OAuthError exception class."""
        error = OAuthError("Test error message")

        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    def test_full_oauth_flow_integration(self) -> None:
        """Test complete OAuth flow integration."""
        settings = Settings()
        service = GoogleOAuthService(settings)

        with (
            patch("app.auth.oauth_service.Flow") as mock_flow,
            patch("app.auth.oauth_service.build") as mock_build,
        ):
            # Mock authorization URL generation
            mock_flow_instance = Mock()
            mock_flow.from_client_config.return_value = mock_flow_instance
            mock_flow_instance.authorization_url.return_value = (
                "https://accounts.google.com/oauth/authorize?...",
                "flow_state",
            )

            # Mock token exchange
            mock_credentials = Mock()
            mock_flow_instance.fetch_token.return_value = None
            mock_flow_instance.credentials = mock_credentials

            # Mock user info retrieval
            mock_service = Mock()
            mock_build.return_value = mock_service
            mock_user_data = {
                "id": "123456789",
                "email": "test@example.com",
                "name": "Test User",
                "picture": "https://example.com/photo.jpg",
                "verified_email": True,
            }
            mock_service.userinfo.return_value.get.return_value.execute.return_value = (
                mock_user_data
            )

            # Test complete flow
            auth_url, state = service.get_authorization_url()
            credentials = service.exchange_code_for_tokens("auth_code", state)
            user_info = service.get_user_info(credentials)

            assert auth_url.startswith("https://accounts.google.com/oauth")
            assert state == "flow_state"
            assert credentials == mock_credentials
            assert user_info.google_id == "123456789"
            assert user_info.email == "test@example.com"
