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

    # Check database health
    database_status = "pending"
    database_health = {"status": "pending"}

    try:
        from app.core.database import get_database_manager

        db_manager = get_database_manager()
        database_health = db_manager.health_check()
        database_status = database_health["status"]
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        database_status = "error"
        database_health = {"status": "error", "error": str(e)}

    # TODO: Add actual dependency checks (redis, snowflake, etc.)
    dependencies_ready = database_status == "healthy"

    return {
        "ready": dependencies_ready,
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": {
            "database": database_status,
            "redis": "pending",
            "snowflake": "pending",
        },
        "database_health": database_health,
    }
