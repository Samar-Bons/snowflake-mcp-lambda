# ABOUTME: Tests for chat API endpoints for natural language to SQL conversion
# ABOUTME: Tests the complete NL→SQL pipeline with Gemini and Snowflake integration

from collections.abc import Generator
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import User


@pytest.fixture
def client() -> TestClient:
    """Create test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_user() -> User:
    """Create mock user for authentication."""
    user = Mock(spec=User)
    user.id = 1
    user.email = "test@example.com"
    user.name = "Test User"
    user.is_active = True
    return user


@pytest.fixture
def mock_services() -> tuple[Mock, Mock, Mock]:
    """Create mock services for testing."""
    # Mock schema service
    mock_schema_service = Mock()
    mock_schema_service.discover_schema.return_value = Mock()
    mock_schema_service.format_schema_context.return_value = "Schema context here"
    mock_schema_service.execute_query.return_value = {
        "columns": ["id", "name"],
        "rows": [[1, "John"], [2, "Jane"]],
        "row_count": 2,
        "truncated": False,
    }

    # Mock Gemini service
    mock_gemini_service = Mock()
    mock_gemini_service.translate_nl_to_sql.return_value = (
        "SELECT id, name FROM customers LIMIT 2;"
    )

    # Mock SQLite service - use spec to make isinstance work
    from app.data.sqlite_adapter import SQLiteSchemaService
    mock_sqlite_service = Mock(spec=SQLiteSchemaService)
    mock_sqlite_service.set_active_file.return_value = True
    mock_sqlite_service.discover_schema.return_value = Mock()
    mock_sqlite_service.format_schema_context.return_value = "Schema context here"
    mock_sqlite_service.execute_query.return_value = {
        "columns": ["id", "name"],
        "rows": [[1, "John"], [2, "Jane"]],
        "row_count": 2,
        "truncated": False,
    }

    return mock_schema_service, mock_gemini_service, mock_sqlite_service


@pytest.fixture
def authenticated_client(
    client: TestClient, mock_user: User, mock_services: tuple[Mock, Mock, Mock]
) -> Generator[TestClient, None, None]:
    """Create authenticated test client with mocked services."""
    from app.auth.endpoints import get_current_user
    from app.llm.endpoints import get_gemini_service, get_schema_service
    from app.data.sqlite_adapter import SQLiteSchemaService

    mock_schema_service, mock_gemini_service, mock_sqlite_service = mock_services

    # Override dependencies
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_schema_service] = lambda: mock_schema_service
    app.dependency_overrides[get_gemini_service] = lambda: mock_gemini_service

    # Create a subclass of SQLiteSchemaService that returns our mock
    class MockSQLiteSchemaService(SQLiteSchemaService):
        def __new__(cls, *args, **kwargs):
            return mock_sqlite_service

    # Patch SQLiteSchemaService at module level with our mock class
    with patch('app.llm.endpoints.SQLiteSchemaService', MockSQLiteSchemaService):
        yield client

    # Clean up the overrides
    app.dependency_overrides.clear()


class TestChatEndpoints:
    """Test suite for chat API endpoints."""

    def test_chat_endpoint_success_with_autorun(
        self, authenticated_client: TestClient, mock_services: tuple[Mock, Mock, Mock]
    ) -> None:
        """Test successful chat endpoint with query auto-execution."""
        mock_schema_service, mock_gemini_service, mock_sqlite_service = mock_services

        # Make request
        request_data = {"prompt": "Show me all customers", "autorun": True, "file_id": "test-file-123"}

        response = authenticated_client.post("/api/v1/chat/", json=request_data)

        if response.status_code != 200:
            print(f"Response: {response.json()}")
        assert response.status_code == 200
        result = response.json()

        assert "sql" in result
        assert "results" in result
        assert result["sql"] == "SELECT id, name FROM customers LIMIT 2;"
        assert result["results"]["columns"] == ["id", "name"]
        assert len(result["results"]["rows"]) == 2
        assert result["autorun"] is True

        # Verify service calls
        mock_sqlite_service.discover_schema.assert_called_once()
        mock_sqlite_service.format_schema_context.assert_called_once()
        mock_gemini_service.translate_nl_to_sql.assert_called_once()
        mock_sqlite_service.execute_query.assert_called_once_with(
            "SELECT id, name FROM customers LIMIT 2;"
        )

    def test_chat_endpoint_success_without_autorun(
        self, authenticated_client: TestClient, mock_services: tuple[Mock, Mock, Mock]
    ) -> None:
        """Test successful chat endpoint without query auto-execution."""
        mock_schema_service, mock_gemini_service, mock_sqlite_service = mock_services

        # Update mock to return different SQL
        mock_gemini_service.translate_nl_to_sql.return_value = (
            "SELECT * FROM customers WHERE age > 25;"
        )

        # Make request
        request_data = {"prompt": "Show me customers older than 25", "autorun": False, "file_id": "test-file-123"}

        response = authenticated_client.post("/api/v1/chat/", json=request_data)

        assert response.status_code == 200
        result = response.json()

        assert "sql" in result
        assert result["results"] is None
        assert result["sql"] == "SELECT * FROM customers WHERE age > 25;"
        assert result["autorun"] is False

        # Verify that query was not executed
        mock_sqlite_service.execute_query.assert_not_called()

    def test_chat_endpoint_gemini_error(
        self, authenticated_client: TestClient, mock_services: tuple[Mock, Mock, Mock]
    ) -> None:
        """Test chat endpoint with Gemini service error."""
        from app.llm.gemini_service import GeminiServiceError

        mock_schema_service, mock_gemini_service, mock_sqlite_service = mock_services

        # Mock Gemini service to raise error
        mock_gemini_service.translate_nl_to_sql.side_effect = GeminiServiceError(
            "API error"
        )

        # Make request
        request_data = {"prompt": "Show me all customers", "autorun": False, "file_id": "test-file-123"}

        response = authenticated_client.post("/api/v1/chat/", json=request_data)

        assert response.status_code == 400
        assert "Failed to generate SQL" in response.json()["detail"]

    def test_chat_endpoint_schema_discovery_error(
        self, authenticated_client: TestClient, mock_services: tuple[Mock, Mock, Mock]
    ) -> None:
        """Test chat endpoint with schema discovery error."""
        from app.data.sqlite_adapter import SQLiteSchemaError

        mock_schema_service, mock_gemini_service, mock_sqlite_service = mock_services

        # Mock schema service to raise error on discover_schema
        mock_sqlite_service.set_active_file.return_value = True
        mock_sqlite_service.discover_schema.side_effect = SQLiteSchemaError(
            "Connection failed"
        )

        # Make request
        request_data = {"prompt": "Show me all customers", "autorun": False, "file_id": "test-file-123"}

        response = authenticated_client.post("/api/v1/chat/", json=request_data)

        assert response.status_code == 400
        assert "Failed to discover file schema" in response.json()["detail"]

    def test_chat_endpoint_query_execution_error(
        self, authenticated_client: TestClient, mock_services: tuple[Mock, Mock, Mock]
    ) -> None:
        """Test chat endpoint with query execution error."""
        from app.data.sqlite_adapter import SQLiteSchemaError

        mock_schema_service, mock_gemini_service, mock_sqlite_service = mock_services

        # Mock schema service to work normally until query execution
        mock_sqlite_service.set_active_file.return_value = True
        mock_sqlite_service.discover_schema.return_value = Mock()
        mock_sqlite_service.format_schema_context.return_value = "Schema context here"
        mock_sqlite_service.execute_query.side_effect = SQLiteSchemaError(
            "Query failed"
        )
        mock_gemini_service.translate_nl_to_sql.return_value = (
            "SELECT * FROM customers;"
        )

        # Make request
        request_data = {"prompt": "Show me all customers", "autorun": True, "file_id": "test-file-123"}

        response = authenticated_client.post("/api/v1/chat/", json=request_data)

        assert response.status_code == 400
        assert "Failed to execute query" in response.json()["detail"]

    def test_chat_endpoint_unauthenticated(self, client: TestClient, mock_services: tuple[Mock, Mock, Mock]) -> None:
        """Test chat endpoint without authentication (should work with anonymous session)."""
        from app.llm.endpoints import get_gemini_service, get_schema_service
        from app.data.sqlite_adapter import SQLiteSchemaService

        mock_schema_service, mock_gemini_service, mock_sqlite_service = mock_services

        # Set up mock returns
        mock_sqlite_service.set_active_file.return_value = True
        mock_sqlite_service.discover_schema.return_value = Mock()
        mock_sqlite_service.format_schema_context.return_value = "Schema context here"
        mock_gemini_service.translate_nl_to_sql.return_value = "SELECT * FROM test;"

        request_data = {"prompt": "Show me all customers", "autorun": False, "file_id": "test-file-123"}

        # Override services to avoid API key errors
        app.dependency_overrides[get_gemini_service] = lambda: mock_gemini_service
        app.dependency_overrides[get_schema_service] = lambda: mock_schema_service

        try:
            # Create a subclass of SQLiteSchemaService that returns our mock
            class MockSQLiteSchemaService(SQLiteSchemaService):
                def __new__(cls, *args, **kwargs):
                    return mock_sqlite_service

            with patch('app.llm.endpoints.SQLiteSchemaService', MockSQLiteSchemaService):
                response = client.post("/api/v1/chat/", json=request_data)

            # Chat endpoint works without authentication (uses anonymous session)
            assert response.status_code == 200
            result = response.json()
            assert result["sql"] == "SELECT * FROM test;"
            assert result["autorun"] is False
            assert result["results"] is None
        finally:
            # Clean up override
            app.dependency_overrides.clear()

    def test_chat_endpoint_invalid_request_empty_prompt(
        self, authenticated_client: TestClient
    ) -> None:
        """Test chat endpoint with empty prompt."""
        request_data = {"prompt": "", "autorun": False, "file_id": "test-file-123"}

        response = authenticated_client.post("/api/v1/chat/", json=request_data)

        assert response.status_code == 422

    def test_chat_endpoint_invalid_request_missing_prompt(
        self, authenticated_client: TestClient
    ) -> None:
        """Test chat endpoint with missing prompt."""
        request_data = {"autorun": False, "file_id": "test-file-123"}

        response = authenticated_client.post("/api/v1/chat/", json=request_data)

        assert response.status_code == 422

    def test_execute_sql_endpoint_success(
        self, authenticated_client: TestClient, mock_services: tuple[Mock, Mock, Mock]
    ) -> None:
        """Test successful SQL execution endpoint."""
        mock_schema_service, mock_gemini_service, mock_sqlite_service = mock_services

        # Update mock to return different results for execution endpoint
        mock_sqlite_service.set_active_file.return_value = True
        mock_sqlite_service.execute_query.return_value = {
            "columns": ["id", "name", "email"],
            "rows": [[1, "John", "john@example.com"], [2, "Jane", "jane@example.com"]],
            "row_count": 2,
            "truncated": False,
        }

        # Make request
        request_data = {"sql": "SELECT id, name, email FROM customers LIMIT 2;", "file_id": "test-file-123"}

        response = authenticated_client.post("/api/v1/chat/execute", json=request_data)

        assert response.status_code == 200
        result = response.json()

        assert "results" in result
        assert result["results"]["columns"] == ["id", "name", "email"]
        assert len(result["results"]["rows"]) == 2
        assert result["results"]["truncated"] is False

    def test_execute_sql_endpoint_invalid_sql(
        self, authenticated_client: TestClient, mock_services: tuple[Mock, Mock, Mock]
    ) -> None:
        """Test SQL execution endpoint with invalid SQL."""
        from app.data.sqlite_adapter import SQLiteSchemaError

        mock_schema_service, mock_gemini_service, mock_sqlite_service = mock_services

        # Mock schema service to work normally until query execution
        mock_sqlite_service.set_active_file.return_value = True
        mock_sqlite_service.execute_query.side_effect = SQLiteSchemaError(
            "Only SELECT queries are allowed"
        )

        # Make request
        request_data = {"sql": "DELETE FROM customers WHERE id = 1;", "file_id": "test-file-123"}

        response = authenticated_client.post("/api/v1/chat/execute", json=request_data)

        assert response.status_code == 400
        assert "Only SELECT queries are allowed" in response.json()["detail"]

    def test_chat_health_endpoint(self, client: TestClient) -> None:
        """Test chat health check endpoint."""
        response = client.get("/api/v1/chat/health")

        assert response.status_code == 200
        result = response.json()

        assert result["status"] == "healthy"
        assert "gemini_configured" in result
        assert "snowflake_configured" in result
        assert "timestamp" in result
