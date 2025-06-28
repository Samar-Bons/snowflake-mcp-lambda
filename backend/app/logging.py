# ABOUTME: Structured logging system with correlation IDs and external aggregation
# ABOUTME: Provides comprehensive logging infrastructure for monitoring and debugging

import asyncio
import logging
import sys
import time
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
from typing import Any

import requests
import structlog
from pydantic import BaseModel, Field


class LogConfig(BaseModel):
    """Configuration for logging system."""

    level: str = Field(default="INFO", description="Logging level")
    format: str = Field(default="json", description="Log format: json or console")
    enable_correlation_ids: bool = Field(
        default=True, description="Enable correlation ID tracking"
    )
    external_service_url: str | None = Field(
        default=None, description="External log aggregation service URL"
    )


class LogContext(BaseModel):
    """Logging context with correlation ID and request metadata."""

    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str | None = None
    request_path: str | None = None
    operation: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary with timestamp."""
        context = self.model_dump(exclude_none=True)
        context["timestamp"] = datetime.utcnow().isoformat()
        return context


# Thread-local storage for correlation ID
import threading

_context = threading.local()


def get_correlation_id() -> str:
    """Get current correlation ID or generate a new one."""
    if not hasattr(_context, "correlation_id"):
        _context.correlation_id = str(uuid.uuid4())
    return _context.correlation_id


@contextmanager
def with_correlation_id(correlation_id: str) -> Generator[None, None, None]:
    """Context manager for setting correlation ID."""
    old_id = getattr(_context, "correlation_id", None)
    _context.correlation_id = correlation_id
    try:
        yield
    finally:
        if old_id is not None:
            _context.correlation_id = old_id
        elif hasattr(_context, "correlation_id"):
            delattr(_context, "correlation_id")


def add_correlation_id(
    logger: Any, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Processor to add correlation ID to log entries."""
    event_dict["correlation_id"] = get_correlation_id()
    return event_dict


def setup_logging(config: LogConfig) -> structlog.BoundLogger:
    """Set up structured logging with the given configuration."""

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, config.level.upper()),
    )

    # Set up processors
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    # Add correlation ID processor if enabled
    if config.enable_correlation_ids:
        processors.append(add_correlation_id)

    # Add appropriate renderer based on format
    if config.format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.extend(
            [
                structlog.dev.ConsoleRenderer(),
            ]
        )

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, config.level.upper())
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger()


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger for the given module name."""
    return structlog.get_logger(name)


class LogShipper:
    """Ships logs to external aggregation service."""

    def __init__(self, service_url: str, timeout: int = 10):
        self.service_url = service_url
        self.timeout = timeout

    def ship_log(self, log_entry: dict[str, Any]) -> bool:
        """Ship a log entry to external service."""
        try:
            response = requests.post(
                self.service_url,
                json=log_entry,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout,
            )
            return response.status_code == 200
        except Exception:
            # Failed to ship log - should not break application
            return False


@contextmanager
def time_operation(
    operation_name: str, logger: structlog.BoundLogger
) -> Generator[None, None, None]:
    """Context manager to time and log operations."""
    start_time = time.time()
    try:
        yield
    finally:
        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            "Operation completed",
            operation=operation_name,
            duration_ms=round(duration_ms, 2),
        )


def log_performance_metrics(metrics: dict[str, Any]) -> None:
    """Log performance metrics."""
    logger = get_logger("performance")
    logger.info("performance_metrics", **metrics)


def log_query_metrics(query_metrics: dict[str, Any]) -> None:
    """Log Snowflake query execution metrics."""
    logger = get_logger("business.snowflake")
    logger.info("query_execution", **query_metrics)


def log_user_interaction(interaction_data: dict[str, Any]) -> None:
    """Log user interaction metrics."""
    logger = get_logger("business.user")
    logger.info("user_interaction", **interaction_data)


class FastAPILoggingMiddleware:
    """FastAPI middleware for request logging and correlation ID management."""

    def __init__(self, app):
        self.app = app
        self.logger = get_logger("middleware.request")

    async def __call__(self, scope, receive, send):
        """ASGI middleware for request logging and correlation ID."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Generate correlation ID for request
        correlation_id = str(uuid.uuid4())

        with with_correlation_id(correlation_id):
            start_time = time.time()

            # Extract request information
            method = scope["method"]
            path = scope["path"]
            client_ip = scope.get("client", [None])[0] if scope.get("client") else None

            # Log request start
            self.logger.info(
                "Request started",
                method=method,
                path=path,
                client_ip=client_ip,
                correlation_id=correlation_id,
            )

            # Wrap send to capture response
            response_started = False
            status_code = None

            async def send_wrapper(message):
                nonlocal response_started, status_code
                if message["type"] == "http.response.start":
                    response_started = True
                    status_code = message["status"]
                await send(message)

            try:
                await self.app(scope, receive, send_wrapper)

                # Log successful request completion
                duration_ms = (time.time() - start_time) * 1000
                self.logger.info(
                    "Request completed",
                    status_code=status_code,
                    duration_ms=round(duration_ms, 2),
                    correlation_id=correlation_id,
                )

            except Exception as exc:
                # Log request error
                duration_ms = (time.time() - start_time) * 1000
                self.logger.error(
                    "Request failed",
                    error=str(exc),
                    error_type=type(exc).__name__,
                    duration_ms=round(duration_ms, 2),
                    correlation_id=correlation_id,
                    exc_info=True,
                )
                raise


# External log aggregation integration
class ExternalLogHandler(logging.Handler):
    """Custom logging handler for shipping logs to external services."""

    def __init__(self, service_url: str):
        super().__init__()
        self.shipper = LogShipper(service_url)

    def emit(self, record: logging.LogRecord) -> None:
        """Emit log record to external service."""
        try:
            log_entry = {
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }

            # Add exception info if present
            if record.exc_info:
                log_entry["exception"] = self.format(record)

            # Ship to external service (non-blocking)
            asyncio.create_task(self._async_ship(log_entry))

        except Exception:
            # Don't let log shipping break the application
            pass

    async def _async_ship(self, log_entry: dict[str, Any]) -> None:
        """Asynchronously ship log entry."""
        await asyncio.to_thread(self.shipper.ship_log, log_entry)


def configure_external_logging(service_url: str) -> None:
    """Configure external log shipping to aggregation service."""
    handler = ExternalLogHandler(service_url)
    handler.setLevel(logging.INFO)

    # Add to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)


# Security and compliance logging
class SecurityLogger:
    """Specialized logger for security events."""

    def __init__(self):
        self.logger = get_logger("security")

    def log_auth_attempt(
        self,
        user_id: str | None,
        success: bool,
        client_ip: str | None = None,
        **kwargs,
    ) -> None:
        """Log authentication attempt."""
        self.logger.info(
            "Authentication attempt",
            user_id=user_id,
            success=success,
            client_ip=client_ip,
            event_type="auth_attempt",
            **kwargs,
        )

    def log_data_access(
        self, user_id: str, table_name: str, operation: str, row_count: int, **kwargs
    ) -> None:
        """Log data access for compliance."""
        self.logger.info(
            "Data access",
            user_id=user_id,
            table_name=table_name,
            operation=operation,
            row_count=row_count,
            event_type="data_access",
            **kwargs,
        )

    def log_security_event(
        self, event_type: str, severity: str, details: dict[str, Any]
    ) -> None:
        """Log general security events."""
        self.logger.warning(
            "Security event", event_type=event_type, severity=severity, **details
        )


# Business metrics logging
class BusinessMetricsLogger:
    """Specialized logger for business metrics and KPIs."""

    def __init__(self):
        self.logger = get_logger("business_metrics")

    def log_user_engagement(
        self,
        user_id: str,
        action: str,
        session_duration: float | None = None,
        **kwargs,
    ) -> None:
        """Log user engagement metrics."""
        self.logger.info(
            "User engagement",
            user_id=user_id,
            action=action,
            session_duration=session_duration,
            metric_type="engagement",
            **kwargs,
        )

    def log_system_performance(
        self, operation: str, duration_ms: float, success: bool, **kwargs
    ) -> None:
        """Log system performance metrics."""
        self.logger.info(
            "System performance",
            operation=operation,
            duration_ms=duration_ms,
            success=success,
            metric_type="performance",
            **kwargs,
        )

    def log_business_kpi(
        self, kpi_name: str, value: float, unit: str, **kwargs
    ) -> None:
        """Log business KPI metrics."""
        self.logger.info(
            "Business KPI",
            kpi_name=kpi_name,
            value=value,
            unit=unit,
            metric_type="kpi",
            **kwargs,
        )
