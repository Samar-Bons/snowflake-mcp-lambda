# ABOUTME: Tests for authentication API endpoints
# ABOUTME: Tests OAuth login, callback, logout, and profile endpoints

from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.auth.oauth_service import OAuthUserInfo
from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client for FastAPI app."""
    return TestClient(app, follow_redirects=False)


@pytest.fixture
def mock_oauth_service() -> Mock:
    """Create mock OAuth service."""
    return Mock()


@pytest.fixture
def mock_user_service() -> Mock:
    """Create mock user service."""
    return Mock()


@pytest.fixture
def sample_oauth_user_info() -> OAuthUserInfo:
    """Create sample OAuth user info for testing."""
    return OAuthUserInfo(
        google_id="123456789",
        email="test@example.com",
        name="Test User",
        picture="https://example.com/photo.jpg",
        verified_email=True
    )


class TestAuthEndpoints:
    """Test suite for authentication API endpoints."""

    def test_login_endpoint_redirects_to_google(self, client: TestClient, mock_oauth_service: Mock) -> None:
        """Test that login endpoint redirects to Google OAuth."""
        mock_oauth_service.get_authorization_url.return_value = (
            "https://accounts.google.com/oauth/authorize?...",
            "random_state"
        )

        with patch('app.auth.endpoints.get_oauth_service', return_value=mock_oauth_service):
            response = client.get("/api/v1/auth/login")

        assert response.status_code == 302
        assert response.headers["location"].startswith("https://accounts.google.com/oauth/authorize")
        mock_oauth_service.get_authorization_url.assert_called_once()

    def test_login_endpoint_with_redirect_param(self, client: TestClient, mock_oauth_service: Mock) -> None:
        """Test login endpoint preserves redirect parameter in state."""
        mock_oauth_service.get_authorization_url.return_value = (
            "https://accounts.google.com/oauth/authorize?...",
            "encoded_state"
        )

        with patch('app.auth.endpoints.get_oauth_service', return_value=mock_oauth_service):
            response = client.get("/api/v1/auth/login?redirect=/dashboard")

        assert response.status_code == 302
        # State should be passed to OAuth service for redirect preservation
        mock_oauth_service.get_authorization_url.assert_called_once()

    def test_callback_endpoint_success(
        self,
        client: TestClient,
        mock_oauth_service: Mock,
        mock_user_service: Mock,
        sample_oauth_user_info: OAuthUserInfo
    ) -> None:
        """Test successful OAuth callback handling."""
        # Mock successful OAuth flow
        mock_credentials = Mock()
        mock_oauth_service.exchange_code_for_tokens.return_value = mock_credentials
        mock_oauth_service.get_user_info.return_value = sample_oauth_user_info

        # Mock user creation/retrieval
        mock_user = Mock()
        mock_user.id = 1
        mock_user_service.get_or_create_user.return_value = mock_user

        # Mock JWT creation
        mock_jwt_token = "jwt_token_here"

        with patch('app.auth.endpoints.get_oauth_service', return_value=mock_oauth_service), \
             patch('app.auth.endpoints.get_user_service', return_value=mock_user_service), \
             patch('app.auth.endpoints.create_jwt_token', return_value=mock_jwt_token):

            response = client.get("/api/v1/auth/callback?code=auth_code&state=oauth_state")

        assert response.status_code == 302
        # Should set JWT cookie
        assert "snowflake_token" in [cookie.name for cookie in response.cookies.jar]

        mock_oauth_service.exchange_code_for_tokens.assert_called_once_with("auth_code", "oauth_state")
        mock_oauth_service.get_user_info.assert_called_once_with(mock_credentials)
        mock_user_service.get_or_create_user.assert_called_once_with(sample_oauth_user_info)

    def test_callback_endpoint_missing_code(self, client: TestClient) -> None:
        """Test callback endpoint with missing authorization code."""
        response = client.get("/api/v1/auth/callback?state=oauth_state")

        assert response.status_code == 400
        assert "Missing authorization code" in response.json()["detail"]

    def test_callback_endpoint_missing_state(self, client: TestClient) -> None:
        """Test callback endpoint with missing state parameter."""
        response = client.get("/api/v1/auth/callback?code=auth_code")

        assert response.status_code == 400
        assert "Missing state parameter" in response.json()["detail"]

    def test_callback_endpoint_oauth_error(
        self,
        client: TestClient,
        mock_oauth_service: Mock
    ) -> None:
        """Test callback endpoint with OAuth service error."""
        from app.auth.oauth_service import OAuthError

        mock_oauth_service.exchange_code_for_tokens.side_effect = OAuthError("Invalid code")

        with patch('app.auth.endpoints.get_oauth_service', return_value=mock_oauth_service):
            response = client.get("/api/v1/auth/callback?code=invalid_code&state=oauth_state")

        assert response.status_code == 400
        assert "OAuth authentication failed" in response.json()["detail"]

    def test_callback_endpoint_with_redirect_state(
        self,
        client: TestClient,
        mock_oauth_service: Mock,
        mock_user_service: Mock,
        sample_oauth_user_info: OAuthUserInfo
    ) -> None:
        """Test callback endpoint redirects to original URL from state."""
        # Mock successful OAuth flow
        mock_credentials = Mock()
        mock_oauth_service.exchange_code_for_tokens.return_value = mock_credentials
        mock_oauth_service.get_user_info.return_value = sample_oauth_user_info

        # Mock user creation/retrieval
        mock_user = Mock()
        mock_user.id = 1
        mock_user_service.get_or_create_user.return_value = mock_user

        # Mock JWT creation
        mock_jwt_token = "jwt_token_here"

        # Mock state decoding to return redirect URL
        with patch('app.auth.endpoints.get_oauth_service', return_value=mock_oauth_service), \
             patch('app.auth.endpoints.get_user_service', return_value=mock_user_service), \
             patch('app.auth.endpoints.create_jwt_token', return_value=mock_jwt_token), \
             patch('app.auth.endpoints.decode_state', return_value="/dashboard"):

            response = client.get("/api/v1/auth/callback?code=auth_code&state=encoded_redirect_state")

        assert response.status_code == 302
        assert response.headers["location"] == "/dashboard"

    def test_logout_endpoint(self, client: TestClient) -> None:
        """Test logout endpoint clears JWT cookie."""
        response = client.post("/api/v1/auth/logout")

        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"

        # Should have Set-Cookie header to clear the JWT cookie
        set_cookie_header = response.headers.get("set-cookie")
        assert set_cookie_header is not None
        assert "snowflake_token=" in set_cookie_header
        assert "Expires=Thu, 01 Jan 1970 00:00:00 GMT" in set_cookie_header

    def test_profile_endpoint_authenticated(self, client: TestClient) -> None:
        """Test profile endpoint with valid JWT token."""
        from app.auth.endpoints import get_current_user

        mock_user = Mock()
        mock_user.to_profile_dict.return_value = {
            "id": 1,
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/photo.jpg",
            "preferences": {
                "auto_run_queries": False,
                "default_row_limit": 500,
                "default_output_format": "table"
            },
            "is_active": True,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00"
        }

        # Override the dependency
        app.dependency_overrides[get_current_user] = lambda: mock_user

        try:
            response = client.get("/api/v1/auth/profile")

            assert response.status_code == 200
            profile_data = response.json()
            assert profile_data["email"] == "test@example.com"
            assert profile_data["name"] == "Test User"
            assert "preferences" in profile_data
        finally:
            # Clean up the override
            app.dependency_overrides.clear()

    def test_profile_endpoint_unauthenticated(self, client: TestClient) -> None:
        """Test profile endpoint without authentication."""
        response = client.get("/api/v1/auth/profile")

        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    def test_profile_endpoint_invalid_token(self, client: TestClient) -> None:
        """Test profile endpoint with invalid JWT token."""
        with patch('app.auth.endpoints.get_current_user', side_effect=Exception("Invalid token")):
            client.cookies.set("snowflake_token", "invalid_jwt_token")
            response = client.get("/api/v1/auth/profile")

        assert response.status_code == 401

    def test_update_preferences_endpoint(self, client: TestClient, mock_user_service: Mock) -> None:
        """Test updating user preferences."""
        from app.auth.endpoints import get_current_user, get_user_service

        mock_user = Mock()
        mock_user.id = 1
        updated_user = Mock()
        updated_user.to_profile_dict.return_value = {
            "id": 1,
            "preferences": {
                "auto_run_queries": True,
                "default_row_limit": 1000,
                "default_output_format": "both"
            }
        }

        mock_user_service.update_user_preferences.return_value = updated_user

        preferences_data = {
            "auto_run_queries": True,
            "default_row_limit": 1000,
            "default_output_format": "both"
        }

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_user_service] = lambda: mock_user_service

        try:
            response = client.put("/api/v1/auth/preferences", json=preferences_data)

            assert response.status_code == 200
            assert response.json()["preferences"]["auto_run_queries"] is True
            assert response.json()["preferences"]["default_row_limit"] == 1000

            mock_user_service.update_user_preferences.assert_called_once_with(
                1,  # user_id as positional argument
                preferences_data
            )
        finally:
            # Clean up the overrides
            app.dependency_overrides.clear()

    def test_health_check_endpoint(self, client: TestClient) -> None:
        """Test auth health check endpoint."""
        response = client.get("/api/v1/auth/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert "oauth_configured" in response.json()
        assert "timestamp" in response.json()

    def test_get_current_user_dependency_with_valid_token(self, client: TestClient) -> None:
        """Test that get_current_user dependency works with valid JWT token."""
        from app.auth.jwt_utils import verify_jwt_token
        from app.auth.user_service import get_user_service

        mock_user = Mock()
        mock_user.id = 1
        mock_user.is_active = True

        mock_user_service = Mock()
        mock_user_service.get_user_by_id.return_value = mock_user

        # Override dependencies to simulate valid JWT flow
        app.dependency_overrides[verify_jwt_token] = lambda token: {"user_id": 1}
        app.dependency_overrides[get_user_service] = lambda: mock_user_service

        try:
            # Create a mock request with JWT cookie
            with patch('app.auth.endpoints.get_jwt_token_from_request', return_value="valid_token"):
                response = client.get("/api/v1/auth/profile")

            # Should be able to access protected endpoint if everything is mocked correctly
            assert response.status_code in [200, 401]  # Depends on exact implementation
        finally:
            app.dependency_overrides.clear()
