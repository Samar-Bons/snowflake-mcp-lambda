# ABOUTME: Chat API endpoints for natural language to SQL conversion
# ABOUTME: Provides the main chat interface and query execution endpoints

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.auth.endpoints import get_current_user
from app.config import get_settings
from app.data.sqlite_adapter import SQLiteSchemaError, SQLiteSchemaService
from app.llm.gemini_service import GeminiService, GeminiServiceError
from app.models.user import User
from app.snowflake.schema_service import (
    SchemaService,
    SchemaServiceError,
)

router = APIRouter(prefix="/chat", tags=["chat"])


# Request/Response Models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    prompt: str = Field(..., min_length=1, description="Natural language query")
    autorun: bool = Field(
        default=False, description="Whether to automatically execute the generated SQL"
    )
    file_id: str | None = Field(
        default=None, description="ID of uploaded file to query (if using file data)"
    )


class ExecuteSQLRequest(BaseModel):
    """Request model for SQL execution endpoint."""

    sql: str = Field(..., min_length=1, description="SQL query to execute")
    file_id: str | None = Field(
        default=None, description="ID of uploaded file to query (if using file data)"
    )


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


def _get_schema_service_for_file(
    user_id: str, file_id: str | None, schema_service: SchemaService
) -> tuple[Any, str]:
    """Get appropriate schema service and context for the request."""
    if file_id:
        # Use SQLite data source
        sqlite_service = SQLiteSchemaService(user_id)
        if not sqlite_service.set_active_file(file_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File {file_id} not found or expired",
            )

        try:
            sqlite_schema = sqlite_service.discover_schema()
            schema_context = sqlite_service.format_schema_context(sqlite_schema)
            return sqlite_service, schema_context
        except SQLiteSchemaError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to discover file schema: {e!s}",
            ) from e
    else:
        # Use Snowflake data source (original behavior)
        try:
            snowflake_schema = schema_service.discover_schema()
            schema_context = schema_service.format_schema_context(snowflake_schema)
            return schema_service, schema_context
        except SchemaServiceError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to discover Snowflake schema: {e!s}",
            ) from e


# API Endpoints
@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),  # noqa: B008
    gemini_service: GeminiService = Depends(get_gemini_service),  # noqa: B008
    schema_service: SchemaService = Depends(get_schema_service),  # noqa: B008
) -> ChatResponse:
    """Convert natural language to SQL and optionally execute it."""
    try:
        # Get schema service and context
        active_service, schema_context = _get_schema_service_for_file(
            str(current_user.id), request.file_id, schema_service
        )

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
                if isinstance(active_service, SQLiteSchemaService):
                    results = active_service.execute_query(sql_query)
                else:
                    results = active_service.execute_query(sql_query)
            except (SchemaServiceError, SQLiteSchemaError) as e:
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
        request: SQL execution request with optional file_id
        current_user: Current authenticated user
        schema_service: Snowflake schema service (fallback)

    Returns:
        ExecuteSQLResponse with query results

    Raises:
        HTTPException: If query execution fails
    """
    try:
        # Determine data source
        if request.file_id:
            # Use SQLite data source
            sqlite_service = SQLiteSchemaService(str(current_user.id))
            if not sqlite_service.set_active_file(request.file_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"File {request.file_id} not found or expired",
                )

            try:
                results = sqlite_service.execute_query(request.sql)
            except SQLiteSchemaError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
                ) from e
        else:
            # Use Snowflake data source (original behavior)
            try:
                results = schema_service.execute_query(request.sql)
            except SchemaServiceError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
                ) from e

        return ExecuteSQLResponse(results=results)

    except HTTPException:
        raise
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
