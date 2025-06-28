# ABOUTME: FastAPI application entry point and server configuration
# ABOUTME: Provides health checks and basic API structure for MCP Lambda

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .health import get_health_status, get_readiness_status

# Create FastAPI application
app = FastAPI(
    title="Snowflake MCP Lambda",
    description="A remote Model Context Protocol Server for Snowflake deployed as AWS Lambda",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, Any]:
    """Health check endpoint for basic service status."""
    return get_health_status()


@app.get("/health/ready")
async def ready() -> dict[str, Any]:
    """Readiness check endpoint for deployment orchestration."""
    return get_readiness_status()


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with basic service information."""
    return {
        "service": "snowflake-mcp-lambda",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }
