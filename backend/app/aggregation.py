# ABOUTME: External log aggregation service integration for shipping logs to external providers
# ABOUTME: Supports multiple aggregation services like Datadog, New Relic, CloudWatch, and custom endpoints

import asyncio
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

import aiohttp
from pydantic import BaseModel, Field

from .logging import get_logger


class LogEntry(BaseModel):
    """Standardized log entry format for external aggregation."""

    timestamp: str
    level: str
    message: str
    logger_name: str
    correlation_id: str | None = None
    user_id: str | None = None
    request_path: str | None = None
    operation: str | None = None
    duration_ms: float | None = None
    error_details: dict[str, Any] | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    service_name: str = "snowflake-mcp-lambda"
    environment: str = "production"

    def to_datadog_format(self) -> dict[str, Any]:
        """Convert to Datadog log format."""
        return {
            "timestamp": self.timestamp,
            "level": self.level.upper(),
            "message": self.message,
            "service": self.service_name,
            "ddsource": "python",
            "ddtags": f"env:{self.environment}",
            "logger": {
                "name": self.logger_name,
            },
            "correlation_id": self.correlation_id,
            "user_id": self.user_id,
            "request_path": self.request_path,
            "operation": self.operation,
            "duration_ms": self.duration_ms,
            "error": self.error_details,
            **self.context,
        }

    def to_newrelic_format(self) -> dict[str, Any]:
        """Convert to New Relic log format."""
        return {
            "timestamp": int(
                datetime.fromisoformat(
                    self.timestamp.replace("Z", "+00:00")
                ).timestamp()
                * 1000
            ),
            "message": self.message,
            "logtype": "application",
            "service": self.service_name,
            "environment": self.environment,
            "level": self.level.upper(),
            "logger.name": self.logger_name,
            "correlation_id": self.correlation_id,
            "user_id": self.user_id,
            "request_path": self.request_path,
            "operation": self.operation,
            "duration_ms": self.duration_ms,
            **self.context,
        }

    def to_cloudwatch_format(self) -> dict[str, Any]:
        """Convert to CloudWatch log format."""
        return {
            "timestamp": int(
                datetime.fromisoformat(
                    self.timestamp.replace("Z", "+00:00")
                ).timestamp()
                * 1000
            ),
            "message": json.dumps(
                {
                    "level": self.level.upper(),
                    "message": self.message,
                    "service": self.service_name,
                    "environment": self.environment,
                    "logger": self.logger_name,
                    "correlation_id": self.correlation_id,
                    "user_id": self.user_id,
                    "request_path": self.request_path,
                    "operation": self.operation,
                    "duration_ms": self.duration_ms,
                    "error": self.error_details,
                    **self.context,
                }
            ),
        }


class AggregationConfig(BaseModel):
    """Configuration for log aggregation service."""

    service_type: str = Field(
        description="Type of service: datadog, newrelic, cloudwatch, custom"
    )
    endpoint_url: str = Field(description="Service endpoint URL")
    api_key: str | None = None
    headers: dict[str, str] = Field(default_factory=dict)
    batch_size: int = Field(default=100, description="Number of logs to batch")
    flush_interval: int = Field(default=30, description="Seconds between flushes")
    retry_attempts: int = Field(default=3, description="Number of retry attempts")
    retry_backoff: float = Field(
        default=1.0, description="Backoff multiplier for retries"
    )
    timeout: int = Field(default=30, description="Request timeout in seconds")
    enable_compression: bool = Field(
        default=True, description="Enable gzip compression"
    )


class LogAggregator(ABC):
    """Abstract base class for log aggregators."""

    def __init__(self, config: AggregationConfig):
        self.config = config
        self.logger = get_logger(f"aggregator.{config.service_type}")
        self.buffer: list[LogEntry] = []
        self.flush_task: asyncio.Task | None = None
        self._running = False

    @abstractmethod
    async def send_logs(self, logs: list[LogEntry]) -> bool:
        """Send logs to external service."""
        pass

    async def add_log(self, log_entry: LogEntry) -> None:
        """Add a log entry to the buffer."""
        self.buffer.append(log_entry)

        if len(self.buffer) >= self.config.batch_size:
            await self.flush()

    async def flush(self) -> None:
        """Flush buffered logs to external service."""
        if not self.buffer:
            return

        logs_to_send = self.buffer.copy()
        self.buffer.clear()

        success = await self.send_logs(logs_to_send)

        if not success:
            # Put logs back in buffer for retry (up to limit)
            self.buffer.extend(logs_to_send[-self.config.batch_size :])

        self.logger.info(
            "Log flush completed",
            logs_sent=len(logs_to_send),
            success=success,
            buffer_size=len(self.buffer),
        )

    async def start(self) -> None:
        """Start the aggregator with periodic flushing."""
        self._running = True
        self.flush_task = asyncio.create_task(self._flush_periodically())
        self.logger.info(
            "Log aggregator started", service_type=self.config.service_type
        )

    async def stop(self) -> None:
        """Stop the aggregator and flush remaining logs."""
        self._running = False

        if self.flush_task:
            self.flush_task.cancel()
            try:
                await self.flush_task
            except asyncio.CancelledError:
                pass

        # Final flush
        await self.flush()
        self.logger.info("Log aggregator stopped")

    async def _flush_periodically(self) -> None:
        """Periodically flush logs."""
        while self._running:
            try:
                await asyncio.sleep(self.config.flush_interval)
                await self.flush()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Error in periodic flush", error=str(e))


class DatadogAggregator(LogAggregator):
    """Datadog log aggregator."""

    async def send_logs(self, logs: list[LogEntry]) -> bool:
        """Send logs to Datadog."""
        if not self.config.api_key:
            self.logger.error("Datadog API key not configured")
            return False

        payload = [log.to_datadog_format() for log in logs]

        headers = {
            "Content-Type": "application/json",
            "DD-API-KEY": self.config.api_key,
            **self.config.headers,
        }

        return await self._send_request(payload, headers)

    async def _send_request(
        self, payload: list[dict[str, Any]], headers: dict[str, str]
    ) -> bool:
        """Send HTTP request with retries."""
        for attempt in range(self.config.retry_attempts):
            try:
                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as session:
                    async with session.post(
                        self.config.endpoint_url,
                        json=payload,
                        headers=headers,
                        compress=self.config.enable_compression,
                    ) as response:
                        if response.status == 200:
                            return True
                        else:
                            self.logger.warning(
                                "Datadog request failed",
                                status=response.status,
                                attempt=attempt + 1,
                            )
            except Exception as e:
                self.logger.error(
                    "Datadog request error", error=str(e), attempt=attempt + 1
                )

            # Wait before retry
            if attempt < self.config.retry_attempts - 1:
                await asyncio.sleep(self.config.retry_backoff * (2**attempt))

        return False


class NewRelicAggregator(LogAggregator):
    """New Relic log aggregator."""

    async def send_logs(self, logs: list[LogEntry]) -> bool:
        """Send logs to New Relic."""
        if not self.config.api_key:
            self.logger.error("New Relic API key not configured")
            return False

        # New Relic expects logs in a specific format
        payload = {"logs": [log.to_newrelic_format() for log in logs]}

        headers = {
            "Content-Type": "application/json",
            "Api-Key": self.config.api_key,
            **self.config.headers,
        }

        return await self._send_request(payload, headers)

    async def _send_request(
        self, payload: dict[str, Any], headers: dict[str, str]
    ) -> bool:
        """Send HTTP request with retries."""
        for attempt in range(self.config.retry_attempts):
            try:
                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as session:
                    async with session.post(
                        self.config.endpoint_url,
                        json=payload,
                        headers=headers,
                        compress=self.config.enable_compression,
                    ) as response:
                        if response.status in [200, 202]:
                            return True
                        else:
                            self.logger.warning(
                                "New Relic request failed",
                                status=response.status,
                                attempt=attempt + 1,
                            )
            except Exception as e:
                self.logger.error(
                    "New Relic request error", error=str(e), attempt=attempt + 1
                )

            if attempt < self.config.retry_attempts - 1:
                await asyncio.sleep(self.config.retry_backoff * (2**attempt))

        return False


class CloudWatchAggregator(LogAggregator):
    """AWS CloudWatch log aggregator."""

    def __init__(self, config: AggregationConfig, log_group: str, log_stream: str):
        super().__init__(config)
        self.log_group = log_group
        self.log_stream = log_stream
        self.sequence_token: str | None = None

    async def send_logs(self, logs: list[LogEntry]) -> bool:
        """Send logs to CloudWatch."""
        try:
            import boto3

            client = boto3.client("logs")

            log_events = [log.to_cloudwatch_format() for log in logs]

            # Sort by timestamp
            log_events.sort(key=lambda x: x["timestamp"])

            kwargs = {
                "logGroupName": self.log_group,
                "logStreamName": self.log_stream,
                "logEvents": log_events,
            }

            if self.sequence_token:
                kwargs["sequenceToken"] = self.sequence_token

            response = client.put_log_events(**kwargs)
            self.sequence_token = response.get("nextSequenceToken")

            return True

        except Exception as e:
            self.logger.error("CloudWatch request error", error=str(e))
            return False


class CustomAggregator(LogAggregator):
    """Custom HTTP endpoint aggregator."""

    async def send_logs(self, logs: list[LogEntry]) -> bool:
        """Send logs to custom endpoint."""
        payload = [log.model_dump() for log in logs]

        headers = {
            "Content-Type": "application/json",
            **self.config.headers,
        }

        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        return await self._send_request(payload, headers)

    async def _send_request(
        self, payload: list[dict[str, Any]], headers: dict[str, str]
    ) -> bool:
        """Send HTTP request with retries."""
        for attempt in range(self.config.retry_attempts):
            try:
                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as session:
                    async with session.post(
                        self.config.endpoint_url,
                        json=payload,
                        headers=headers,
                        compress=self.config.enable_compression,
                    ) as response:
                        if 200 <= response.status < 300:
                            return True
                        else:
                            self.logger.warning(
                                "Custom endpoint request failed",
                                status=response.status,
                                attempt=attempt + 1,
                            )
            except Exception as e:
                self.logger.error(
                    "Custom endpoint request error", error=str(e), attempt=attempt + 1
                )

            if attempt < self.config.retry_attempts - 1:
                await asyncio.sleep(self.config.retry_backoff * (2**attempt))

        return False


class AggregationManager:
    """Manages multiple log aggregators."""

    def __init__(self):
        self.aggregators: list[LogAggregator] = []
        self.logger = get_logger("aggregation_manager")

    def add_aggregator(self, aggregator: LogAggregator) -> None:
        """Add an aggregator."""
        self.aggregators.append(aggregator)
        self.logger.info(
            "Aggregator added", service_type=aggregator.config.service_type
        )

    async def add_log(self, log_entry: LogEntry) -> None:
        """Add log to all aggregators."""
        for aggregator in self.aggregators:
            try:
                await aggregator.add_log(log_entry)
            except Exception as e:
                self.logger.error(
                    "Error adding log to aggregator",
                    service_type=aggregator.config.service_type,
                    error=str(e),
                )

    async def start_all(self) -> None:
        """Start all aggregators."""
        for aggregator in self.aggregators:
            try:
                await aggregator.start()
            except Exception as e:
                self.logger.error(
                    "Error starting aggregator",
                    service_type=aggregator.config.service_type,
                    error=str(e),
                )

    async def stop_all(self) -> None:
        """Stop all aggregators."""
        for aggregator in self.aggregators:
            try:
                await aggregator.stop()
            except Exception as e:
                self.logger.error(
                    "Error stopping aggregator",
                    service_type=aggregator.config.service_type,
                    error=str(e),
                )

    async def flush_all(self) -> None:
        """Flush all aggregators."""
        for aggregator in self.aggregators:
            try:
                await aggregator.flush()
            except Exception as e:
                self.logger.error(
                    "Error flushing aggregator",
                    service_type=aggregator.config.service_type,
                    error=str(e),
                )


def create_aggregator(config: AggregationConfig, **kwargs) -> LogAggregator:
    """Factory function to create aggregator based on service type."""
    if config.service_type == "datadog":
        return DatadogAggregator(config)
    elif config.service_type == "newrelic":
        return NewRelicAggregator(config)
    elif config.service_type == "cloudwatch":
        return CloudWatchAggregator(
            config,
            kwargs.get("log_group", "snowflake-mcp-lambda"),
            kwargs.get("log_stream", "application"),
        )
    elif config.service_type == "custom":
        return CustomAggregator(config)
    else:
        raise ValueError(f"Unsupported aggregation service type: {config.service_type}")


# Global aggregation manager instance
_global_manager: AggregationManager | None = None


async def initialize_aggregation(
    configs: list[AggregationConfig],
) -> AggregationManager:
    """Initialize global aggregation manager."""
    global _global_manager

    if _global_manager:
        await _global_manager.stop_all()

    _global_manager = AggregationManager()

    for config in configs:
        try:
            aggregator = create_aggregator(config)
            _global_manager.add_aggregator(aggregator)
        except Exception as e:
            logger = get_logger("aggregation_init")
            logger.error(
                "Failed to create aggregator",
                service_type=config.service_type,
                error=str(e),
            )

    await _global_manager.start_all()
    return _global_manager


async def add_log_to_aggregation(log_entry: LogEntry) -> None:
    """Add log entry to global aggregation."""
    if _global_manager:
        await _global_manager.add_log(log_entry)


async def shutdown_aggregation() -> None:
    """Shutdown global aggregation."""
    if _global_manager:
        await _global_manager.stop_all()


# Integration with structlog
class StructlogAggregationProcessor:
    """Structlog processor that sends logs to aggregation service."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.logger = get_logger("structlog_aggregation")

    def __call__(
        self, logger, method_name: str, event_dict: dict[str, Any]
    ) -> dict[str, Any]:
        """Process log event and send to aggregation."""
        if not self.enabled or not _global_manager:
            return event_dict

        try:
            # Convert structlog event to LogEntry
            log_entry = LogEntry(
                timestamp=event_dict.get("timestamp", datetime.utcnow().isoformat()),
                level=event_dict.get("level", "INFO"),
                message=event_dict.get("event", ""),
                logger_name=logger.name if hasattr(logger, "name") else str(logger),
                correlation_id=event_dict.get("correlation_id"),
                user_id=event_dict.get("user_id"),
                request_path=event_dict.get("request_path"),
                operation=event_dict.get("operation"),
                duration_ms=event_dict.get("duration_ms"),
                error_details=event_dict.get("error_details"),
                context={
                    k: v
                    for k, v in event_dict.items()
                    if k
                    not in [
                        "timestamp",
                        "level",
                        "event",
                        "correlation_id",
                        "user_id",
                        "request_path",
                        "operation",
                        "duration_ms",
                        "error_details",
                    ]
                },
            )

            # Send to aggregation (non-blocking)
            asyncio.create_task(add_log_to_aggregation(log_entry))

        except Exception as e:
            # Don't let aggregation break logging
            self.logger.error("Aggregation processor error", error=str(e))

        return event_dict
