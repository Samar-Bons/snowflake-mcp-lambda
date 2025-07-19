# ABOUTME: Tests for Gemini LLM service wrapper
# ABOUTME: Tests natural language to SQL conversion and API integration

from unittest.mock import Mock, patch

import pytest

from app.config import Settings
from app.llm.gemini_service import GeminiService, GeminiServiceError


class TestGeminiService:
    """Test suite for Gemini LLM service wrapper."""

    @pytest.fixture
    def mock_settings(self) -> Settings:
        """Create mock settings for testing."""
        settings = Settings()
        settings.GEMINI_API_KEY = "test_api_key"
        settings.GEMINI_MODEL = "gemini-1.5-flash"
        settings.GEMINI_MAX_TOKENS = 1000
        settings.GEMINI_TEMPERATURE = 0.1
        settings.GEMINI_TIMEOUT_SECONDS = 30
        return settings

    @pytest.fixture
    def gemini_service(self, mock_settings: Settings) -> GeminiService:
        """Create GeminiService instance for testing."""
        with patch('app.llm.gemini_service.genai.configure'):
            return GeminiService(settings=mock_settings)

    def test_gemini_service_initialization(self, mock_settings: Settings) -> None:
        """Test that GeminiService initializes correctly."""
        with patch('app.llm.gemini_service.genai.configure'):
            service = GeminiService(settings=mock_settings)

        assert service.settings == mock_settings
        assert service.model == "gemini-1.5-flash"
        assert service.max_tokens == 1000
        assert service.temperature == 0.1
        assert service.timeout_seconds == 30

    def test_gemini_service_initialization_without_api_key(self) -> None:
        """Test that GeminiService raises error when API key is missing."""
        settings = Settings()
        settings.GEMINI_API_KEY = ""

        with pytest.raises(GeminiServiceError) as exc_info:
            GeminiService(settings=settings)

        assert "API key is required" in str(exc_info.value)

    @patch('app.llm.gemini_service.genai.GenerativeModel')
    def test_translate_nl_to_sql_success(
        self,
        mock_generative_model: Mock,
        gemini_service: GeminiService,
    ) -> None:
        """Test successful natural language to SQL translation."""
        # Mock the Gemini API response
        mock_model_instance = Mock()
        mock_response = Mock()
        mock_response.text = "SELECT * FROM customers WHERE age > 25;"
        mock_model_instance.generate_content.return_value = mock_response
        mock_generative_model.return_value = mock_model_instance

        schema_context = "Table: customers (id, name, age, email)"
        natural_language = "Show me all customers older than 25"

        result = gemini_service.translate_nl_to_sql(
            natural_language=natural_language,
            schema_context=schema_context
        )

        assert result == "SELECT * FROM customers WHERE age > 25;"
        mock_generative_model.assert_called_once_with("gemini-1.5-flash")
        mock_model_instance.generate_content.assert_called_once()

    @patch('app.llm.gemini_service.genai.GenerativeModel')
    def test_translate_nl_to_sql_api_error(
        self,
        mock_generative_model: Mock,
        gemini_service: GeminiService,
    ) -> None:
        """Test handling of Gemini API errors."""
        # Mock the Gemini API to raise an exception
        mock_model_instance = Mock()
        mock_model_instance.generate_content.side_effect = Exception("API Error")
        mock_generative_model.return_value = mock_model_instance

        schema_context = "Table: customers (id, name, age, email)"
        natural_language = "Show me all customers older than 25"

        with pytest.raises(GeminiServiceError) as exc_info:
            gemini_service.translate_nl_to_sql(
                natural_language=natural_language,
                schema_context=schema_context
            )

        assert "Failed to generate SQL" in str(exc_info.value)
        assert "API Error" in str(exc_info.value)

    @patch('app.llm.gemini_service.genai.GenerativeModel')
    def test_translate_nl_to_sql_empty_response(
        self,
        mock_generative_model: Mock,
        gemini_service: GeminiService,
    ) -> None:
        """Test handling of empty response from Gemini API."""
        # Mock the Gemini API to return empty response
        mock_model_instance = Mock()
        mock_response = Mock()
        mock_response.text = ""
        mock_model_instance.generate_content.return_value = mock_response
        mock_generative_model.return_value = mock_model_instance

        schema_context = "Table: customers (id, name, age, email)"
        natural_language = "Show me all customers older than 25"

        with pytest.raises(GeminiServiceError) as exc_info:
            gemini_service.translate_nl_to_sql(
                natural_language=natural_language,
                schema_context=schema_context
            )

        assert "Received empty response" in str(exc_info.value)

    def test_build_prompt_with_context(self, gemini_service: GeminiService) -> None:
        """Test that prompt is built correctly with schema context."""
        schema_context = "Table: customers (id, name, age, email)"
        natural_language = "Show me all customers older than 25"

        prompt = gemini_service._build_prompt(
            natural_language=natural_language,
            schema_context=schema_context
        )

        assert "You are an expert SQL generator" in prompt
        assert "Snowflake SQL syntax" in prompt
        assert schema_context in prompt
        assert natural_language in prompt
        assert "SELECT" in prompt  # Should mention SELECT-only queries

    def test_build_prompt_without_context(self, gemini_service: GeminiService) -> None:
        """Test that prompt is built correctly without schema context."""
        natural_language = "Show me all customers older than 25"

        prompt = gemini_service._build_prompt(
            natural_language=natural_language,
            schema_context=None
        )

        assert "You are an expert SQL generator" in prompt
        assert "Snowflake SQL syntax" in prompt
        assert natural_language in prompt
        assert "No schema context provided" in prompt

    def test_extract_sql_from_response(self, gemini_service: GeminiService) -> None:
        """Test SQL extraction from various response formats."""
        # Test SQL with code block
        response_with_code_block = """
        Here's the SQL query:
        ```sql
        SELECT * FROM customers WHERE age > 25;
        ```
        """

        result = gemini_service._extract_sql_from_response(response_with_code_block)
        assert result == "SELECT * FROM customers WHERE age > 25;"

        # Test SQL without code block
        response_without_code_block = "SELECT * FROM customers WHERE age > 25;"

        result = gemini_service._extract_sql_from_response(response_without_code_block)
        assert result == "SELECT * FROM customers WHERE age > 25;"

        # Test SQL with multiple lines
        response_multiline = """
        SELECT id, name, email
        FROM customers
        WHERE age > 25
        ORDER BY name;
        """

        result = gemini_service._extract_sql_from_response(response_multiline)
        assert "SELECT id, name, email" in result
        assert "FROM customers" in result
        assert "WHERE age > 25" in result
        assert "ORDER BY name" in result

    def test_validate_sql_query_valid_select(self, gemini_service: GeminiService) -> None:
        """Test validation of valid SELECT queries."""
        valid_queries = [
            "SELECT * FROM customers;",
            "SELECT id, name FROM customers WHERE age > 25;",
            "SELECT COUNT(*) FROM orders GROUP BY customer_id;",
            "  select * from customers  ",  # With whitespace
            "SELECT * FROM customers; -- with comment",
        ]

        for query in valid_queries:
            # Should not raise an exception
            gemini_service._validate_sql_query(query)

    def test_validate_sql_query_invalid_non_select(self, gemini_service: GeminiService) -> None:
        """Test validation rejects non-SELECT queries."""
        invalid_queries = [
            "INSERT INTO customers VALUES (1, 'John', 30);",
            "UPDATE customers SET age = 31 WHERE id = 1;",
            "DELETE FROM customers WHERE id = 1;",
            "CREATE TABLE test (id INT);",
            "DROP TABLE customers;",
            "ALTER TABLE customers ADD COLUMN phone VARCHAR(20);",
        ]

        for query in invalid_queries:
            with pytest.raises(GeminiServiceError) as exc_info:
                gemini_service._validate_sql_query(query)

            assert "Only SELECT queries are allowed" in str(exc_info.value)

    def test_validate_sql_query_empty_query(self, gemini_service: GeminiService) -> None:
        """Test validation of empty or whitespace-only queries."""
        invalid_queries = ["", "  ", "\n\t  \n"]

        for query in invalid_queries:
            with pytest.raises(GeminiServiceError) as exc_info:
                gemini_service._validate_sql_query(query)

            assert "Query cannot be empty" in str(exc_info.value)

    def test_get_generation_config(self, gemini_service: GeminiService) -> None:
        """Test that generation configuration is set correctly."""
        config = gemini_service._get_generation_config()

        assert config.max_output_tokens == 1000
        assert config.temperature == 0.1
        assert config.candidate_count == 1
