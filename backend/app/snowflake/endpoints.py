# ABOUTME: Snowflake connection management API endpoints
# ABOUTME: Provides secure connection testing, storage, and management functionality

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.snowflake.connection_service import (
    ConnectionParams,
    SnowflakeConnectionService,
)

router = APIRouter(prefix="/snowflake", tags=["snowflake"])

# Initialize connection service
connection_service = SnowflakeConnectionService()


class ConnectionParamsRequest(BaseModel):
    """Request model for connection parameters."""

    account: str
    user: str
    password: str
    warehouse: str
    database: str
    schema_name: str = Field(..., alias="schema")


@router.post("/test-connection")
async def test_connection(params: ConnectionParamsRequest) -> dict[str, Any]:
    """Test Snowflake connection parameters."""
    connection_params = ConnectionParams(
        account=params.account,
        user=params.user,
        password=params.password,
        warehouse=params.warehouse,
        database=params.database,
        schema=params.schema_name,
    )

    result = await connection_service.test_connection(connection_params)

    return {
        "success": result.success,
        "message": result.message,
        "response_time_ms": result.response_time_ms,
    }
