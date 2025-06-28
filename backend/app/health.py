# ABOUTME: Health check endpoints for monitoring application status
# ABOUTME: Provides readiness and liveness probes for deployment environments

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


def get_health_status() -> dict[str, Any]:
    """
    Get basic health status of the application.

    Returns:
        Dict containing health status information
    """
    logger.info("Health check requested")

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "snowflake-mcp-lambda",
        "version": "0.1.0",
    }


def get_readiness_status() -> dict[str, Any]:
    """
    Get readiness status indicating if service can accept requests.

    Returns:
        Dict containing readiness status information
    """
    logger.info("Readiness check requested")

    # TODO: Add actual dependency checks (database, redis, etc.)
    dependencies_ready = True

    return {
        "ready": dependencies_ready,
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": {
            "database": "pending",
            "redis": "pending",
            "snowflake": "pending",
        },
    }
