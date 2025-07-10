# ABOUTME: FastAPI application entry point and server configuration
# ABOUTME: Provides health checks and basic API structure for MCP Lambda

import logging
from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.auth.endpoints import router as auth_router
from app.config import get_settings
from app.health import get_health_status, get_readiness_status
from app.llm.endpoints import router as chat_router
from app.snowflake.endpoints import router as snowflake_router

# Get configuration
settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app instance
app = FastAPI(
    title="Snowflake MCP Lambda",
    description="A remote Model Context Protocol Server for Snowflake deployed as AWS Lambda",
    version="0.1.0",
    debug=settings.DEBUG,
)

# Include routers
app.include_router(auth_router)
app.include_router(chat_router, prefix=settings.API_V1_PREFIX)
app.include_router(snowflake_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health() -> JSONResponse:
    """Health check endpoint for liveness probes."""
    status_data = get_health_status()
    return JSONResponse(content=status_data, status_code=200)


@app.get("/readiness")
async def readiness() -> JSONResponse:
    """Readiness check endpoint for deployment readiness."""
    status_data = get_readiness_status()
    status_code = 200 if status_data["ready"] else 503
    return JSONResponse(content=status_data, status_code=status_code)


@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint providing API information."""
    return {
        "service": "snowflake-mcp-lambda",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "readiness": "/readiness",
            "chat": "/api/v1/chat",
            "auth": "/api/v1/auth",
            "docs": "/docs",
        },
    }
