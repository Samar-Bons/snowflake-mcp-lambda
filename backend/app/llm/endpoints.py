# ABOUTME: Chat API endpoints for natural language to SQL conversion
# ABOUTME: Provides the main chat interface and query execution endpoints

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.auth.endpoints import get_current_user
from app.config import get_settings
from app.llm.gemini_service import GeminiService, GeminiServiceError
from app.models.user import User
from app.snowflake.schema_service import SchemaService, SchemaServiceError

router = APIRouter(prefix="/chat", tags=["chat"])


# Request/Response Models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    prompt: str = Field(..., min_length=1, description="Natural language query")
    autorun: bool = Field(
        default=False, description="Whether to automatically execute the generated SQL"
    )


class ExecuteSQLRequest(BaseModel):
    """Request model for SQL execution endpoint."""

    sql: str = Field(..., min_length=1, description="SQL query to execute")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    sql: str = Field(..., description="Generated SQL query")
    autorun: bool = Field(..., description="Whether query was auto-executed")
    results: dict[str, Any] | None = Field(
        None, description="Query results if auto-executed"
    )


class ExecuteSQLResponse(BaseModel):
    """Response model for SQL execution endpoint."""

    results: dict[str, Any] = Field(..., description="Query execution results")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(..., description="Service status")
    gemini_configured: bool = Field(..., description="Whether Gemini is configured")
    snowflake_configured: bool = Field(
        ..., description="Whether Snowflake is configured"
    )
    timestamp: datetime = Field(..., description="Health check timestamp")


# Dependency functions
def get_gemini_service() -> GeminiService:
    """Get Gemini service instance."""
    settings = get_settings()
    return GeminiService(settings=settings)


def get_schema_service() -> SchemaService:
    """Get schema service instance."""
    settings = get_settings()
    return SchemaService(settings=settings)


# API Endpoints
@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),  # noqa: B008
    gemini_service: GeminiService = Depends(get_gemini_service),  # noqa: B008
    schema_service: SchemaService = Depends(get_schema_service),  # noqa: B008
) -> ChatResponse:
    """Convert natural language to SQL and optionally execute it.

    Args:
        request: Chat request with natural language prompt
        current_user: Current authenticated user
        gemini_service: Gemini LLM service
        schema_service: Snowflake schema service

    Returns:
        ChatResponse with generated SQL and optional results

    Raises:
        HTTPException: If SQL generation or execution fails
    """
    try:
        # Discover schema for context
        try:
            schema = schema_service.discover_schema()
            schema_context = schema_service.format_schema_context(schema)
        except SchemaServiceError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to discover schema: {e!s}",
            ) from e

        # Generate SQL using Gemini
        try:
            sql_query = gemini_service.translate_nl_to_sql(
                natural_language=request.prompt, schema_context=schema_context
            )
        except GeminiServiceError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to generate SQL: {e!s}",
            ) from e

        # Execute query if autorun is enabled
        results = None
        if request.autorun:
            try:
                results = schema_service.execute_query(sql_query)
            except SchemaServiceError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to execute query: {e!s}",
                ) from e

        return ChatResponse(sql=sql_query, autorun=request.autorun, results=results)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {e!s}",
        ) from e


@router.post("/execute", response_model=ExecuteSQLResponse)
async def execute_sql(
    request: ExecuteSQLRequest,
    current_user: User = Depends(get_current_user),  # noqa: B008
    schema_service: SchemaService = Depends(get_schema_service),  # noqa: B008
) -> ExecuteSQLResponse:
    """Execute a SQL query.

    Args:
        request: SQL execution request
        current_user: Current authenticated user
        schema_service: Snowflake schema service

    Returns:
        ExecuteSQLResponse with query results

    Raises:
        HTTPException: If query execution fails
    """
    try:
        results = schema_service.execute_query(request.sql)
        return ExecuteSQLResponse(results=results)

    except SchemaServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {e!s}",
        ) from e


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check chat service health.

    Returns:
        HealthResponse with service status and configuration info
    """
    settings = get_settings()

    # Check if services are configured
    gemini_configured = bool(settings.GEMINI_API_KEY)
    snowflake_configured = all(
        [
            settings.SNOWFLAKE_ACCOUNT,
            settings.SNOWFLAKE_USER,
            settings.SNOWFLAKE_PASSWORD,
            settings.SNOWFLAKE_WAREHOUSE,
            settings.SNOWFLAKE_DATABASE,
            settings.SNOWFLAKE_SCHEMA,
        ]
    )

    return HealthResponse(
        status="healthy",
        gemini_configured=gemini_configured,
        snowflake_configured=snowflake_configured,
        timestamp=datetime.now(timezone.utc),
    )
