# ABOUTME: FastAPI application entry point and server configuration
# ABOUTME: Provides health checks, monitoring endpoints, and comprehensive logging

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import get_logging_config, get_monitoring_config
from app.health import get_health_status, get_readiness_status
from app.logging import (
    FastAPILoggingMiddleware,
    LogConfig,
    configure_external_logging,
    get_logger,
    setup_logging,
)
from app.monitoring import MonitoringConfig, MonitoringSystem

# Global monitoring system instance
monitoring_system: MonitoringSystem | None = None
monitoring_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager for startup and shutdown tasks."""
    global monitoring_system, monitoring_task
    
    # Startup
    logger = get_logger("app.startup")
    logger.info("Starting Snowflake MCP Lambda application")
    
    try:
        # Initialize logging system
        logging_config = get_logging_config()
        log_config = LogConfig(
            level=logging_config.log_level,
            format=logging_config.log_format,
            enable_correlation_ids=logging_config.enable_correlation_ids,
            external_service_url=logging_config.external_service_url,
        )
        setup_logging(log_config)
        
        # Configure external logging if URL provided
        if logging_config.external_service_url:
            configure_external_logging(logging_config.external_service_url)
            
        logger.info("Logging system initialized", 
                   format=log_config.format, 
                   level=log_config.level)
        
        # Initialize monitoring system
        monitoring_config_settings = get_monitoring_config()
        monitoring_config = MonitoringConfig(
            enable_performance_monitoring=monitoring_config_settings.enable_performance_monitoring,
            enable_business_metrics=monitoring_config_settings.enable_business_metrics,
            alert_webhook_url=monitoring_config_settings.alert_webhook_url,
            metrics_retention_days=monitoring_config_settings.metrics_retention_days,
            performance_sample_interval=monitoring_config_settings.performance_sample_interval,
        )
        
        if monitoring_config.validate():
            monitoring_system = MonitoringSystem(monitoring_config)
            monitoring_task = asyncio.create_task(monitoring_system.start_monitoring())
            logger.info("Monitoring system started")
        else:
            logger.warning("Monitoring system configuration invalid, skipping initialization")
            
        logger.info("Application startup completed successfully")
        
        yield
        
    except Exception as e:
        logger.error("Application startup failed", error=str(e), exc_info=True)
        raise
    finally:
        # Shutdown
        logger.info("Shutting down Snowflake MCP Lambda application")
        
        # Stop monitoring system
        if monitoring_task and not monitoring_task.done():
            monitoring_task.cancel()
            try:
                await monitoring_task
            except asyncio.CancelledError:
                pass
            logger.info("Monitoring system stopped")
            
        logger.info("Application shutdown completed")


# Create FastAPI app instance with lifespan
app = FastAPI(
    title="Snowflake MCP Lambda",
    description="A remote Model Context Protocol Server for Snowflake deployed as AWS Lambda",
    version="0.1.0",
    lifespan=lifespan,
)

# Add logging middleware
app = FastAPILoggingMiddleware(app)


@app.get("/health")
async def health() -> JSONResponse:
    """Health check endpoint for liveness probes with monitoring data."""
    logger = get_logger("app.health")
    
    try:
        # Get basic health status
        status_data = get_health_status()
        
        # Add monitoring system health if available
        if monitoring_system:
            monitoring_health = {
                "monitoring_active": monitoring_task is not None and not monitoring_task.done(),
                "alerts_count": len(monitoring_system.alert_manager.active_alerts),
                "metrics_collected": len(monitoring_system.metrics_collector.metrics),
            }
            status_data["monitoring"] = monitoring_health
            
        logger.info("Health check completed", status="healthy", monitoring_active=status_data.get("monitoring", {}).get("monitoring_active", False))
        return JSONResponse(content=status_data, status_code=200)
        
    except Exception as e:
        logger.error("Health check failed", error=str(e), exc_info=True)
        error_response = {"status": "unhealthy", "error": str(e)}
        return JSONResponse(content=error_response, status_code=500)


@app.get("/readiness")
async def readiness() -> JSONResponse:
    """Readiness check endpoint for deployment readiness with system metrics."""
    logger = get_logger("app.readiness")
    
    try:
        # Get basic readiness status
        status_data = get_readiness_status()
        
        # Add system resource information if monitoring is available
        if monitoring_system:
            try:
                resources = monitoring_system.performance_monitor.get_system_resources()
                # Include key metrics for readiness assessment
                status_data["system_resources"] = {
                    "cpu_percent": resources.get("cpu_percent", 0),
                    "memory_percent": resources.get("memory_percent", 0),
                    "disk_usage": resources.get("disk_usage", 0),
                }
                
                # Check if system is under stress
                high_cpu = resources.get("cpu_percent", 0) > 90
                high_memory = resources.get("memory_percent", 0) > 90
                high_disk = resources.get("disk_usage", 0) > 95
                
                if high_cpu or high_memory or high_disk:
                    status_data["ready"] = False
                    status_data["reason"] = "System under high resource utilization"
                    
            except Exception as resource_error:
                logger.warning("Failed to collect system resources for readiness check", 
                             error=str(resource_error))
        
        status_code = 200 if status_data["ready"] else 503
        logger.info("Readiness check completed", ready=status_data["ready"], 
                   reason=status_data.get("reason", "Ready"))
        
        return JSONResponse(content=status_data, status_code=status_code)
        
    except Exception as e:
        logger.error("Readiness check failed", error=str(e), exc_info=True)
        error_response = {"ready": False, "error": str(e)}
        return JSONResponse(content=error_response, status_code=503)


@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint providing API information."""
    logger = get_logger("app.root")
    logger.info("Root endpoint accessed")
    
    endpoints = {
        "health": "/health",
        "readiness": "/readiness",
        "monitoring": "/monitoring/dashboard",
        "metrics": "/monitoring/metrics",
        "docs": "/docs",
    }
    
    return {
        "service": "snowflake-mcp-lambda",
        "version": "0.1.0",
        "status": "running",
        "endpoints": endpoints,
        "monitoring_enabled": monitoring_system is not None,
    }


@app.get("/monitoring/dashboard")
async def monitoring_dashboard() -> JSONResponse:
    """Comprehensive monitoring dashboard with all metrics and alerts."""
    logger = get_logger("app.monitoring.dashboard")
    
    try:
        if not monitoring_system:
            logger.warning("Monitoring dashboard accessed but monitoring system not available")
            return JSONResponse(
                content={"error": "Monitoring system not available"}, 
                status_code=503
            )
        
        # Get comprehensive dashboard data
        dashboard_data = monitoring_system.get_monitoring_dashboard_data()
        
        # Add additional operational metrics
        dashboard_data["monitoring_status"] = {
            "system_active": monitoring_task is not None and not monitoring_task.done(),
            "uptime_seconds": (
                monitoring_task.get_coro().cr_frame.f_locals.get("start_time", 0) 
                if monitoring_task and hasattr(monitoring_task.get_coro(), 'cr_frame') 
                else 0
            ),
            "configuration": {
                "performance_monitoring": monitoring_system.config.enable_performance_monitoring,
                "business_metrics": monitoring_system.config.enable_business_metrics,
                "sample_interval": monitoring_system.config.performance_sample_interval,
                "retention_days": monitoring_system.config.metrics_retention_days,
            }
        }
        
        logger.info("Monitoring dashboard data retrieved", 
                   metrics_count=len(dashboard_data.get("current_metrics", {}).get("performance_metrics", {})),
                   alerts_count=len(dashboard_data.get("active_alerts", [])))
        
        return JSONResponse(content=dashboard_data, status_code=200)
        
    except Exception as e:
        logger.error("Failed to retrieve monitoring dashboard data", error=str(e), exc_info=True)
        return JSONResponse(
            content={"error": f"Failed to retrieve dashboard data: {str(e)}"}, 
            status_code=500
        )


@app.get("/monitoring/metrics")
async def monitoring_metrics() -> JSONResponse:
    """Get current system metrics in Prometheus-compatible format."""
    logger = get_logger("app.monitoring.metrics")
    
    try:
        if not monitoring_system:
            return JSONResponse(
                content={"error": "Monitoring system not available"}, 
                status_code=503
            )
        
        # Get current metrics
        current_metrics = monitoring_system.metrics_collector.export_metrics()
        system_resources = monitoring_system.performance_monitor.get_system_resources()
        
        # Format for Prometheus-style metrics
        prometheus_metrics = []
        
        # Add performance metrics
        for name, metric in current_metrics.get("performance_metrics", {}).items():
            prometheus_metrics.append(f"snowflake_mcp_{name} {metric['value']}")
        
        # Add business metrics
        for name, metric in current_metrics.get("business_metrics", {}).items():
            prometheus_metrics.append(f"snowflake_mcp_business_{name} {metric['value']}")
        
        # Add system resources
        for name, value in system_resources.items():
            if isinstance(value, (int, float)) and name != "timestamp":
                prometheus_metrics.append(f"snowflake_mcp_system_{name} {value}")
        
        # Return both JSON and Prometheus formats
        response_data = {
            "json_metrics": {
                "performance": current_metrics.get("performance_metrics", {}),
                "business": current_metrics.get("business_metrics", {}),
                "system": system_resources,
            },
            "prometheus_format": "\n".join(prometheus_metrics),
            "timestamp": current_metrics.get("timestamp"),
        }
        
        logger.info("Metrics endpoint accessed", 
                   performance_metrics=len(current_metrics.get("performance_metrics", {})),
                   business_metrics=len(current_metrics.get("business_metrics", {})))
        
        return JSONResponse(content=response_data, status_code=200)
        
    except Exception as e:
        logger.error("Failed to retrieve metrics", error=str(e), exc_info=True)
        return JSONResponse(
            content={"error": f"Failed to retrieve metrics: {str(e)}"}, 
            status_code=500
        )
