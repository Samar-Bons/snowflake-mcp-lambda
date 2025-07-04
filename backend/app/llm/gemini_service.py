# ABOUTME: Gemini LLM service for natural language to SQL conversion
# ABOUTME: Handles API integration and prompt engineering for query generation

import re

import google.generativeai as genai
from google.generativeai import GenerationConfig

from app.config import Settings


class GeminiServiceError(Exception):
    """Custom exception for Gemini service errors."""

    pass


class GeminiService:
    """Service for converting natural language to SQL using Google Gemini API."""

    def __init__(self, settings: Settings) -> None:
        """Initialize Gemini service with configuration.

        Args:
            settings: Application settings containing Gemini configuration

        Raises:
            GeminiServiceError: If API key is not provided
        """
        self.settings = settings

        if not settings.GEMINI_API_KEY:
            raise GeminiServiceError("Gemini API key is required for LLM service")

        self.model = settings.GEMINI_MODEL
        self.max_tokens = settings.GEMINI_MAX_TOKENS
        self.temperature = settings.GEMINI_TEMPERATURE
        self.timeout_seconds = settings.GEMINI_TIMEOUT_SECONDS

        # Configure Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)

    def translate_nl_to_sql(
        self, natural_language: str, schema_context: str | None = None
    ) -> str:
        """Convert natural language to SQL query.

        Args:
            natural_language: Natural language description of the query
            schema_context: Optional schema context for better query generation

        Returns:
            Generated SQL query as string

        Raises:
            GeminiServiceError: If API call fails or response is invalid
        """
        try:
            # Build the prompt with context
            prompt = self._build_prompt(natural_language, schema_context)

            # Create model instance
            model = genai.GenerativeModel(self.model)

            # Generate content with configuration
            response = model.generate_content(
                prompt,
                generation_config=self._get_generation_config(),
                request_options={"timeout": self.timeout_seconds},
            )

            # Extract SQL from response
            if not response.text:
                raise GeminiServiceError("Received empty response from Gemini API")

            sql_query = self._extract_sql_from_response(response.text)

            # Validate the generated SQL
            self._validate_sql_query(sql_query)

            return sql_query

        except Exception as e:
            if isinstance(e, GeminiServiceError):
                raise
            raise GeminiServiceError(f"Failed to generate SQL: {e!s}") from e

    def _build_prompt(
        self, natural_language: str, schema_context: str | None = None
    ) -> str:
        """Build the prompt for Gemini API.

        Args:
            natural_language: User's natural language query
            schema_context: Optional database schema context

        Returns:
            Formatted prompt string
        """
        base_prompt = """You are an expert SQL generator specialized in Snowflake SQL syntax.

Your task is to convert natural language queries into valid Snowflake SQL SELECT statements.

IMPORTANT CONSTRAINTS:
- Generate ONLY SELECT statements (no INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, etc.)
- Use proper Snowflake SQL syntax and functions
- Include appropriate WHERE clauses, JOINs, GROUP BY, ORDER BY as needed
- Return only the SQL query without explanations or formatting
- If the query cannot be safely converted to a SELECT statement, return an error message

"""

        if schema_context:
            base_prompt += f"""SCHEMA CONTEXT:
{schema_context}

"""
        else:
            base_prompt += "No schema context provided. Generate SQL based on common table structures.\n\n"

        base_prompt += f"""NATURAL LANGUAGE QUERY:
{natural_language}

SQL QUERY:"""

        return base_prompt

    def _extract_sql_from_response(self, response_text: str) -> str:
        """Extract SQL query from Gemini response.

        Args:
            response_text: Raw response text from Gemini API

        Returns:
            Cleaned SQL query string
        """
        # Remove code block markers if present
        sql_pattern = r"```sql\s*(.*?)\s*```"
        match = re.search(sql_pattern, response_text, re.DOTALL | re.IGNORECASE)

        if match:
            sql_query = match.group(1).strip()
        else:
            # If no code block, assume the entire response is SQL
            sql_query = response_text.strip()

        # Remove any leading/trailing whitespace and normalize
        sql_query = " ".join(sql_query.split())

        return sql_query

    def _validate_sql_query(self, sql_query: str) -> None:
        """Validate that the SQL query is safe and allowed.

        Args:
            sql_query: SQL query to validate

        Raises:
            GeminiServiceError: If query is invalid or not allowed
        """
        if not sql_query or sql_query.strip() == "":
            raise GeminiServiceError("Query cannot be empty")

        # Normalize query for validation
        normalized_query = sql_query.strip().upper()

        # Check that it starts with SELECT
        if not normalized_query.startswith("SELECT"):
            raise GeminiServiceError(
                "Only SELECT queries are allowed. Generated query must start with SELECT."
            )

        # Check for dangerous keywords that shouldn't be in SELECT queries
        dangerous_keywords = [
            "INSERT",
            "UPDATE",
            "DELETE",
            "CREATE",
            "DROP",
            "ALTER",
            "TRUNCATE",
            "GRANT",
            "REVOKE",
            "EXEC",
            "EXECUTE",
        ]

        for keyword in dangerous_keywords:
            if keyword in normalized_query:
                raise GeminiServiceError(
                    f"Only SELECT queries are allowed. Found prohibited keyword: {keyword}"
                )

    def _get_generation_config(self) -> GenerationConfig:
        """Get generation configuration for Gemini API.

        Returns:
            GenerationConfig object with model parameters
        """
        return GenerationConfig(
            max_output_tokens=self.max_tokens,
            temperature=self.temperature,
            candidate_count=1,
        )
