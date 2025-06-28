# ABOUTME: Test suite for structured logging system with correlation IDs
# ABOUTME: Validates logging configuration, context management, and log aggregation

import json
import uuid
from datetime import datetime
from io import StringIO
from unittest.mock import patch

try:
    import pytest
    import structlog

    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False

if DEPS_AVAILABLE:
    from app.logging import (
        LogConfig,
        LogContext,
        get_correlation_id,
        get_logger,
        setup_logging,
        with_correlation_id,
    )


class TestLogConfig:
    """Test logging configuration management."""

    def test_log_config_default_values(self) -> None:
        """Test default logging configuration values."""
        config = LogConfig()
        assert config.level == "INFO"
        assert config.format == "json"
        assert config.enable_correlation_ids is True
        assert config.external_service_url is None

    def test_log_config_custom_values(self) -> None:
        """Test custom logging configuration values."""
        config = LogConfig(
            level="DEBUG",
            format="console",
            enable_correlation_ids=False,
            external_service_url="https://logs.example.com",
        )
        assert config.level == "DEBUG"
        assert config.format == "console"
        assert config.enable_correlation_ids is False
        assert config.external_service_url == "https://logs.example.com"


class TestLogContext:
    """Test logging context management."""

    def test_log_context_initialization(self) -> None:
        """Test log context initialization with default values."""
        context = LogContext()
        assert context.correlation_id is not None
        assert len(context.correlation_id) == 36  # UUID4 length
        assert context.user_id is None
        assert context.request_path is None
        assert context.operation is None

    def test_log_context_with_custom_values(self) -> None:
        """Test log context with custom values."""
        correlation_id = str(uuid.uuid4())
        context = LogContext(
            correlation_id=correlation_id,
            user_id="user123",
            request_path="/api/chat",
            operation="chat_query",
        )
        assert context.correlation_id == correlation_id
        assert context.user_id == "user123"
        assert context.request_path == "/api/chat"
        assert context.operation == "chat_query"

    def test_log_context_to_dict(self) -> None:
        """Test log context serialization to dictionary."""
        context = LogContext(
            user_id="user123",
            request_path="/api/health",
            operation="health_check",
        )
        context_dict = context.to_dict()

        assert "correlation_id" in context_dict
        assert context_dict["user_id"] == "user123"
        assert context_dict["request_path"] == "/api/health"
        assert context_dict["operation"] == "health_check"
        assert "timestamp" in context_dict


class TestCorrelationIdManagement:
    """Test correlation ID management and context propagation."""

    def test_get_correlation_id_generates_new_id(self) -> None:
        """Test that get_correlation_id generates a new UUID when none exists."""
        correlation_id = get_correlation_id()
        assert correlation_id is not None
        assert len(correlation_id) == 36

    def test_with_correlation_id_context_manager(self) -> None:
        """Test correlation ID context manager."""
        test_id = str(uuid.uuid4())

        with with_correlation_id(test_id):
            current_id = get_correlation_id()
            assert current_id == test_id

    def test_nested_correlation_id_contexts(self) -> None:
        """Test nested correlation ID contexts maintain proper isolation."""
        outer_id = str(uuid.uuid4())
        inner_id = str(uuid.uuid4())

        with with_correlation_id(outer_id):
            assert get_correlation_id() == outer_id

            with with_correlation_id(inner_id):
                assert get_correlation_id() == inner_id

            # Should restore outer context
            assert get_correlation_id() == outer_id


class TestStructuredLogging:
    """Test structured logging functionality."""

    def setup_method(self) -> None:
        """Set up test environment for each test."""
        # Reset structlog configuration before each test
        structlog.reset_defaults()

    def test_setup_logging_json_format(self) -> None:
        """Test logging setup with JSON format."""
        config = LogConfig(level="DEBUG", format="json")
        logger = setup_logging(config)

        assert logger is not None
        assert structlog.is_configured()

    def test_setup_logging_console_format(self) -> None:
        """Test logging setup with console format."""
        config = LogConfig(level="INFO", format="console")
        logger = setup_logging(config)

        assert logger is not None
        assert structlog.is_configured()

    def test_get_logger_returns_structured_logger(self) -> None:
        """Test that get_logger returns a properly configured structured logger."""
        setup_logging(LogConfig())
        logger = get_logger("test_module")

        assert logger is not None
        # Verify it's a structlog logger
        assert hasattr(logger, "bind")
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")

    def test_logger_includes_correlation_id(self) -> None:
        """Test that logger automatically includes correlation ID in logs."""
        config = LogConfig(format="json", enable_correlation_ids=True)
        setup_logging(config)
        logger = get_logger("test")

        test_id = str(uuid.uuid4())

        # Capture log output
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            with with_correlation_id(test_id):
                logger.info("Test message")

            log_output = mock_stdout.getvalue()

        # Verify correlation ID is included
        assert test_id in log_output

    def test_logger_structured_output(self) -> None:
        """Test that logger produces valid JSON structured output."""
        config = LogConfig(format="json")
        setup_logging(config)
        logger = get_logger("test")

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            logger.info("Test message", user_id="user123", operation="test")
            log_output = mock_stdout.getvalue().strip()

        # Should be valid JSON
        log_data = json.loads(log_output)
        assert log_data["event"] == "Test message"
        assert log_data["user_id"] == "user123"
        assert log_data["operation"] == "test"
        assert "timestamp" in log_data

    def test_logger_with_context_binding(self) -> None:
        """Test logger context binding functionality."""
        setup_logging(LogConfig(format="json"))
        logger = get_logger("test")

        bound_logger = logger.bind(request_id="req123", user_id="user456")

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            bound_logger.info("Bound context test")
            log_output = mock_stdout.getvalue().strip()

        log_data = json.loads(log_output)
        assert log_data["request_id"] == "req123"
        assert log_data["user_id"] == "user456"

    def test_error_logging_with_exception_info(self) -> None:
        """Test error logging includes exception information."""
        setup_logging(LogConfig(format="json"))
        logger = get_logger("test")

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            try:
                raise ValueError("Test exception")
            except ValueError:
                logger.exception("Error occurred")

            log_output = mock_stdout.getvalue().strip()

        log_data = json.loads(log_output)
        assert log_data["event"] == "Error occurred"
        assert "exception" in log_data
        assert "ValueError" in log_data["exception"]


class TestLogAggregation:
    """Test log aggregation and external service integration."""

    def test_external_service_configuration(self) -> None:
        """Test external logging service configuration."""
        config = LogConfig(
            external_service_url="https://logs.example.com/v1/logs", format="json"
        )

        # This would test the configuration is properly set
        assert config.external_service_url == "https://logs.example.com/v1/logs"

    @patch("requests.post")
    def test_external_log_shipping(self, mock_post) -> None:
        """Test shipping logs to external service."""
        from app.logging import LogShipper

        mock_post.return_value.status_code = 200

        shipper = LogShipper("https://logs.example.com/v1/logs")
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": "INFO",
            "message": "Test log",
            "correlation_id": str(uuid.uuid4()),
        }

        result = shipper.ship_log(log_entry)

        assert result is True
        mock_post.assert_called_once()

        # Verify the request was made with correct data
        call_args = mock_post.call_args
        assert call_args[1]["json"] == log_entry
        assert call_args[1]["headers"]["Content-Type"] == "application/json"

    @patch("requests.post")
    def test_external_log_shipping_failure_handling(self, mock_post) -> None:
        """Test handling of external log shipping failures."""
        from app.logging import LogShipper

        mock_post.return_value.status_code = 500

        shipper = LogShipper("https://logs.example.com/v1/logs")
        log_entry = {"message": "Test log"}

        result = shipper.ship_log(log_entry)

        assert result is False


class TestPerformanceLogging:
    """Test performance-related logging functionality."""

    def test_operation_timing_context_manager(self) -> None:
        """Test operation timing context manager."""
        from app.logging import time_operation

        setup_logging(LogConfig(format="json"))
        logger = get_logger("test")

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            with time_operation("test_operation", logger):
                # Simulate some work
                import time

                time.sleep(0.01)

            log_output = mock_stdout.getvalue().strip()

        log_data = json.loads(log_output)
        assert log_data["operation"] == "test_operation"
        assert "duration_ms" in log_data
        assert log_data["duration_ms"] > 0

    def test_performance_metrics_logging(self) -> None:
        """Test performance metrics are properly logged."""
        from app.logging import log_performance_metrics

        setup_logging(LogConfig(format="json"))

        metrics = {
            "response_time_ms": 150,
            "memory_usage_mb": 64,
            "cpu_percent": 25.5,
            "active_connections": 10,
        }

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            log_performance_metrics(metrics)
            log_output = mock_stdout.getvalue().strip()

        log_data = json.loads(log_output)
        assert log_data["event"] == "performance_metrics"
        assert log_data["response_time_ms"] == 150
        assert log_data["memory_usage_mb"] == 64
        assert log_data["cpu_percent"] == 25.5
        assert log_data["active_connections"] == 10


class TestBusinessMetricsLogging:
    """Test business metrics logging functionality."""

    def test_query_execution_metrics(self) -> None:
        """Test logging of Snowflake query execution metrics."""
        from app.logging import log_query_metrics

        setup_logging(LogConfig(format="json"))

        query_metrics = {
            "query_id": "query123",
            "execution_time_ms": 2500,
            "rows_returned": 150,
            "bytes_scanned": 1024000,
            "warehouse": "COMPUTE_WH",
            "success": True,
        }

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            log_query_metrics(query_metrics)
            log_output = mock_stdout.getvalue().strip()

        log_data = json.loads(log_output)
        assert log_data["event"] == "query_execution"
        assert log_data["query_id"] == "query123"
        assert log_data["execution_time_ms"] == 2500
        assert log_data["rows_returned"] == 150
        assert log_data["success"] is True

    def test_user_interaction_metrics(self) -> None:
        """Test logging of user interaction metrics."""
        from app.logging import log_user_interaction

        setup_logging(LogConfig(format="json"))

        interaction_data = {
            "user_id": "user123",
            "action": "chat_query",
            "input_length": 45,
            "response_time_ms": 1200,
            "satisfied": True,
        }

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            log_user_interaction(interaction_data)
            log_output = mock_stdout.getvalue().strip()

        log_data = json.loads(log_output)
        assert log_data["event"] == "user_interaction"
        assert log_data["user_id"] == "user123"
        assert log_data["action"] == "chat_query"
        assert log_data["satisfied"] is True


# Integration tests
class TestLoggingIntegration:
    """Integration tests for logging system."""

    def test_end_to_end_logging_flow(self) -> None:
        """Test complete logging flow with correlation ID propagation."""
        config = LogConfig(format="json", enable_correlation_ids=True)
        setup_logging(config)
        logger = get_logger("integration_test")

        correlation_id = str(uuid.uuid4())

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            with with_correlation_id(correlation_id):
                logger.info("Request started", operation="test_operation")

                # Simulate nested operation
                nested_logger = get_logger("nested_operation")
                nested_logger.info("Processing data", step="validation")

                logger.info("Request completed", status="success")

            log_output = mock_stdout.getvalue()

        log_lines = [line.strip() for line in log_output.split("\n") if line.strip()]
        assert len(log_lines) == 3

        # All log entries should have the same correlation ID
        for line in log_lines:
            log_data = json.loads(line)
            assert log_data.get("correlation_id") == correlation_id

    def test_logging_with_real_fastapi_request(self) -> None:
        """Test logging integration with FastAPI request context."""
        # This test would be implemented once FastAPI integration is ready
        # For now, we'll test the structure
        from app.logging import FastAPILoggingMiddleware

        middleware = FastAPILoggingMiddleware()
        assert middleware is not None
        # Would test actual request processing once FastAPI is integrated
