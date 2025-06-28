# ABOUTME: Comprehensive monitoring system with metrics collection and intelligent alerting
# ABOUTME: Provides performance monitoring, business metrics, and adaptive alerting capabilities

import asyncio
import statistics
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import psutil
import requests
from pydantic import BaseModel, Field

from .logging import get_logger


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class MonitoringConfig(BaseModel):
    """Configuration for monitoring system."""

    enable_performance_monitoring: bool = Field(default=True)
    enable_business_metrics: bool = Field(default=True)
    alert_webhook_url: str | None = None
    metrics_retention_days: int = Field(default=30)
    performance_sample_interval: int = Field(default=60)  # seconds

    def validate(self) -> bool:
        """Validate monitoring configuration."""
        return self.metrics_retention_days > 0 and self.performance_sample_interval > 0


class MetricsCollector:
    """Collects and manages various types of metrics."""

    def __init__(self):
        self.metrics: dict[str, dict[str, Any]] = {}
        self.historical_data: dict[str, list[dict[str, Any]]] = {}
        self.logger = get_logger("metrics_collector")

    def record_metric(self, name: str, value: float, unit: str = "") -> None:
        """Record a performance metric."""
        timestamp = datetime.utcnow()

        metric_entry = {
            "value": value,
            "unit": unit,
            "timestamp": timestamp.isoformat(),
            "type": "performance",
        }

        self.metrics[name] = metric_entry

        # Store in historical data
        if name not in self.historical_data:
            self.historical_data[name] = []

        self.historical_data[name].append(metric_entry)

        # Log the metric
        self.logger.debug("Metric recorded", metric_name=name, value=value, unit=unit)

    def record_business_metric(self, name: str, value: float, unit: str = "") -> None:
        """Record a business metric."""
        timestamp = datetime.utcnow()

        metric_entry = {
            "value": value,
            "unit": unit,
            "timestamp": timestamp.isoformat(),
            "type": "business",
        }

        self.metrics[name] = metric_entry

        # Store in historical data
        if name not in self.historical_data:
            self.historical_data[name] = []

        self.historical_data[name].append(metric_entry)

        # Log the business metric
        self.logger.info(
            "Business metric recorded", metric_name=name, value=value, unit=unit
        )

    def get_metrics_summary(self, metric_name: str) -> dict[str, Any]:
        """Get statistical summary of a metric."""
        if metric_name not in self.historical_data:
            return {}

        values = [entry["value"] for entry in self.historical_data[metric_name]]

        if not values:
            return {}

        return {
            "count": len(values),
            "average": statistics.mean(values),
            "median": statistics.median(values),
            "min": min(values),
            "max": max(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
        }

    def export_metrics(self) -> dict[str, Any]:
        """Export metrics in standard format."""
        performance_metrics = {}
        business_metrics = {}

        for name, metric in self.metrics.items():
            if metric["type"] == "performance":
                performance_metrics[name] = metric
            else:
                business_metrics[name] = metric

        return {
            "performance_metrics": performance_metrics,
            "business_metrics": business_metrics,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def cleanup_old_data(self, retention_days: int = 30) -> None:
        """Clean up old historical data."""
        cutoff_time = datetime.utcnow() - timedelta(days=retention_days)

        for metric_name in self.historical_data:
            self.historical_data[metric_name] = [
                entry
                for entry in self.historical_data[metric_name]
                if datetime.fromisoformat(entry["timestamp"]) > cutoff_time
            ]


class PerformanceMonitor:
    """Monitors system and application performance."""

    def __init__(self, timeout_threshold: float = 30.0):
        self.active_operations: dict[str, dict[str, Any]] = {}
        self.timeout_threshold = timeout_threshold
        self.operation_history: dict[str, list[float]] = {}
        self.logger = get_logger("performance_monitor")

    def start_operation(self, operation_name: str) -> str:
        """Start timing an operation."""
        operation_id = str(uuid.uuid4())

        self.active_operations[operation_id] = {
            "operation": operation_name,
            "start_time": time.time(),
            "timestamp": datetime.utcnow().isoformat(),
        }

        self.logger.debug(
            "Operation started", operation_id=operation_id, operation=operation_name
        )

        return operation_id

    def complete_operation(self, operation_id: str) -> float:
        """Complete timing an operation and return duration."""
        if operation_id not in self.active_operations:
            return 0.0

        operation = self.active_operations[operation_id]
        duration = time.time() - operation["start_time"]
        operation_name = operation["operation"]

        # Remove from active operations
        del self.active_operations[operation_id]

        # Store in history
        if operation_name not in self.operation_history:
            self.operation_history[operation_name] = []

        self.operation_history[operation_name].append(duration)

        # Keep only recent history
        if len(self.operation_history[operation_name]) > 1000:
            self.operation_history[operation_name] = self.operation_history[
                operation_name
            ][-500:]

        self.logger.info(
            "Operation completed",
            operation_id=operation_id,
            operation=operation_name,
            duration_seconds=round(duration, 3),
        )

        return duration

    def check_timeouts(self) -> list[dict[str, Any]]:
        """Check for operations that have exceeded timeout threshold."""
        current_time = time.time()
        timeouts = []

        for operation_id, operation in self.active_operations.items():
            duration = current_time - operation["start_time"]

            if duration > self.timeout_threshold:
                timeout_info = {
                    "operation_id": operation_id,
                    "operation": operation["operation"],
                    "duration": duration,
                    "threshold": self.timeout_threshold,
                }
                timeouts.append(timeout_info)

                self.logger.warning("Operation timeout detected", **timeout_info)

        return timeouts

    def get_system_resources(self) -> dict[str, Any]:
        """Get current system resource usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            resources = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "memory_total": memory.total,
                "disk_usage": disk.percent,
                "disk_free": disk.free,
                "disk_total": disk.total,
                "timestamp": datetime.utcnow().isoformat(),
            }

            self.logger.debug("System resources collected", **resources)
            return resources

        except Exception as e:
            self.logger.error("Failed to collect system resources", error=str(e))
            return {}

    def analyze_trends(self, operation_name: str) -> dict[str, Any]:
        """Analyze performance trends for an operation."""
        if operation_name not in self.operation_history:
            return {}

        durations = self.operation_history[operation_name]

        if len(durations) < 5:
            return {"status": "insufficient_data"}

        # Calculate trends
        recent = durations[-10:]  # Last 10 operations
        historical = durations[:-10]  # All but last 10

        if not historical:
            return {"status": "insufficient_historical_data"}

        recent_avg = statistics.mean(recent)
        historical_avg = statistics.mean(historical)

        # Determine trend direction
        if recent_avg > historical_avg * 1.1:
            trend = "degrading"
        elif recent_avg < historical_avg * 0.9:
            trend = "improving"
        else:
            trend = "stable"

        # Calculate confidence based on standard deviation
        recent_std = statistics.stdev(recent) if len(recent) > 1 else 0
        confidence = max(
            0, min(1, 1 - (recent_std / recent_avg) if recent_avg > 0 else 0)
        )

        return {
            "average_duration": recent_avg,
            "trend_direction": trend,
            "confidence": round(confidence, 2),
            "sample_size": len(durations),
        }


class AlertRule(BaseModel):
    """Defines an alert rule with conditions and thresholds."""

    name: str
    metric: str
    threshold: float
    severity: AlertSeverity
    operator: str = Field(description="Comparison operator: >, <, >=, <=, ==")
    duration_minutes: int | None = Field(
        default=None, description="Required duration for alert"
    )
    escalation_minutes: int | None = Field(
        default=None, description="Time before escalation"
    )
    escalate_to: AlertSeverity | None = Field(
        default=None, description="Escalation severity"
    )
    cooldown_minutes: int = Field(
        default=15, description="Cooldown period between alerts"
    )

    def evaluate(self, value: float) -> bool:
        """Evaluate if the rule condition is met."""
        if self.operator == ">":
            return value > self.threshold
        elif self.operator == "<":
            return value < self.threshold
        elif self.operator == ">=":
            return value >= self.threshold
        elif self.operator == "<=":
            return value <= self.threshold
        elif self.operator == "==":
            return value == self.threshold
        else:
            return False


class ThresholdManager:
    """Manages adaptive thresholds for alerts."""

    def __init__(self):
        self.thresholds: dict[str, dict[str, Any]] = {}
        self.logger = get_logger("threshold_manager")

    def set_threshold(
        self, metric_name: str, value: float, threshold_type: str = "static"
    ) -> None:
        """Set a threshold for a metric."""
        self.thresholds[metric_name] = {
            "value": value,
            "type": threshold_type,
            "updated": datetime.utcnow().isoformat(),
        }

        self.logger.info(
            "Threshold set", metric=metric_name, value=value, type=threshold_type
        )

    def calculate_adaptive_threshold(
        self, metric_name: str, historical_data: list[float], percentile: int = 95
    ) -> float:
        """Calculate adaptive threshold based on historical data."""
        if not historical_data:
            return 0.0

        # Use percentile-based threshold
        sorted_data = sorted(historical_data)
        index = int((percentile / 100) * len(sorted_data))
        threshold = sorted_data[min(index, len(sorted_data) - 1)]

        self.logger.info(
            "Adaptive threshold calculated",
            metric=metric_name,
            threshold=threshold,
            percentile=percentile,
            data_points=len(historical_data),
        )

        return threshold

    def calculate_time_based_threshold(
        self, metric_name: str, data: list[float], time_period: str
    ) -> float:
        """Calculate threshold based on time period patterns."""
        if not data:
            return 0.0

        # For different time periods, use different multipliers
        multipliers = {"business_hours": 1.2, "off_hours": 1.5, "weekend": 1.8}

        base_threshold = statistics.mean(data) + (
            2 * statistics.stdev(data) if len(data) > 1 else 0
        )
        multiplier = multipliers.get(time_period, 1.0)

        threshold = base_threshold * multiplier

        self.logger.info(
            "Time-based threshold calculated",
            metric=metric_name,
            threshold=threshold,
            time_period=time_period,
            multiplier=multiplier,
        )

        return threshold

    def validate_threshold(self, metric_name: str, value: float) -> bool:
        """Validate that a threshold value is reasonable."""
        # Basic validation - could be extended with metric-specific rules
        if value < 0:
            return False

        if metric_name.endswith("_percent") and value > 100:
            return False

        return True


class AlertManager:
    """Manages alert rules, evaluation, and notifications."""

    def __init__(self, webhook_url: str | None = None):
        self.rules: list[AlertRule] = []
        self.active_alerts: dict[str, dict[str, Any]] = {}
        self.alert_history: list[dict[str, Any]] = []
        self.webhook_url = webhook_url
        self.logger = get_logger("alert_manager")

    def add_rule(self, rule: AlertRule) -> None:
        """Add an alert rule."""
        self.rules.append(rule)
        self.logger.info(
            "Alert rule added",
            rule_name=rule.name,
            metric=rule.metric,
            threshold=rule.threshold,
            severity=rule.severity,
        )

    def evaluate_rules(self, metrics: dict[str, Any]) -> list[dict[str, Any]]:
        """Evaluate all rules against current metrics."""
        triggered_alerts = []
        recovered_alerts = []

        for rule in self.rules:
            if rule.metric not in metrics:
                continue

            current_value = metrics[rule.metric]
            is_triggered = rule.evaluate(current_value)
            alert_key = f"{rule.name}_{rule.metric}"

            if is_triggered:
                # Check if this is a new alert or within cooldown
                if alert_key not in self.active_alerts:
                    alert_data = {
                        "rule_name": rule.name,
                        "metric": rule.metric,
                        "value": current_value,
                        "threshold": rule.threshold,
                        "severity": rule.severity,
                        "operator": rule.operator,
                        "timestamp": datetime.utcnow().isoformat(),
                        "type": "trigger",
                    }

                    self.active_alerts[alert_key] = alert_data
                    triggered_alerts.append(alert_data)

                    self.logger.warning("Alert triggered", **alert_data)
            elif alert_key in self.active_alerts:
                recovery_data = {
                    "rule_name": rule.name,
                    "metric": rule.metric,
                    "value": current_value,
                    "threshold": rule.threshold,
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "recovery",
                }

                # Remove from active alerts
                del self.active_alerts[alert_key]
                recovered_alerts.append(recovery_data)

                self.logger.info("Alert recovered", **recovery_data)

        # Store in history
        self.alert_history.extend(triggered_alerts + recovered_alerts)

        # Send notifications
        for alert in triggered_alerts + recovered_alerts:
            if self.webhook_url:
                asyncio.create_task(self._send_async_notification(alert))

        return triggered_alerts + recovered_alerts

    def send_notification(self, alert_data: dict[str, Any]) -> bool:
        """Send alert notification via webhook."""
        if not self.webhook_url:
            return False

        try:
            response = requests.post(
                self.webhook_url,
                json=alert_data,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            success = response.status_code == 200

            if success:
                self.logger.info(
                    "Alert notification sent", rule_name=alert_data.get("rule_name")
                )
            else:
                self.logger.error(
                    "Failed to send alert notification",
                    status_code=response.status_code,
                    rule_name=alert_data.get("rule_name"),
                )

            return success

        except Exception as e:
            self.logger.error(
                "Alert notification error",
                error=str(e),
                rule_name=alert_data.get("rule_name"),
            )
            return False

    async def _send_async_notification(self, alert_data: dict[str, Any]) -> None:
        """Send notification asynchronously."""
        await asyncio.to_thread(self.send_notification, alert_data)

    def get_alert_statistics(self) -> dict[str, Any]:
        """Get alert statistics and insights."""
        total_alerts = len(self.alert_history)

        if total_alerts == 0:
            return {"total_alerts": 0}

        # Count by severity
        severity_counts = {}
        for alert in self.alert_history:
            severity = alert.get("severity", "unknown")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Count by type
        trigger_count = sum(
            1 for alert in self.alert_history if alert.get("type") == "trigger"
        )
        recovery_count = sum(
            1 for alert in self.alert_history if alert.get("type") == "recovery"
        )

        return {
            "total_alerts": total_alerts,
            "active_alerts": len(self.active_alerts),
            "triggers": trigger_count,
            "recoveries": recovery_count,
            "severity_breakdown": severity_counts,
        }


class MonitoringStorage:
    """Handles storage and retrieval of monitoring data."""

    def __init__(self):
        # In-memory storage for now - would use Redis/database in production
        self.metrics_storage: list[dict[str, Any]] = []
        self.logger = get_logger("monitoring_storage")

    def store_metrics(self, metrics_data: dict[str, Any]) -> None:
        """Store metrics data."""
        self.metrics_storage.append(metrics_data)

        # Keep only recent data (limit memory usage)
        if len(self.metrics_storage) > 10000:
            self.metrics_storage = self.metrics_storage[-5000:]

        self.logger.debug("Metrics stored", metric_count=len(metrics_data))

    def get_historical_metrics(
        self, metric_name: str, hours: int = 24
    ) -> list[dict[str, Any]]:
        """Retrieve historical metrics."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        filtered_metrics = []
        for entry in self.metrics_storage:
            if metric_name in entry:
                timestamp = datetime.fromisoformat(entry["timestamp"])
                if timestamp > cutoff_time:
                    filtered_metrics.append(entry)

        self.logger.debug(
            "Historical metrics retrieved",
            metric=metric_name,
            count=len(filtered_metrics),
            hours=hours,
        )

        return filtered_metrics


# Integrated monitoring system
class MonitoringSystem:
    """Main monitoring system that orchestrates all components."""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.metrics_collector = MetricsCollector()
        self.performance_monitor = PerformanceMonitor()
        self.threshold_manager = ThresholdManager()
        self.alert_manager = AlertManager(config.alert_webhook_url)
        self.storage = MonitoringStorage()
        self.logger = get_logger("monitoring_system")

        self._setup_default_alerts()

    def _setup_default_alerts(self) -> None:
        """Set up default alert rules."""
        default_rules = [
            AlertRule(
                name="high_cpu_usage",
                metric="cpu_percent",
                threshold=85,
                severity=AlertSeverity.WARNING,
                operator=">",
            ),
            AlertRule(
                name="critical_cpu_usage",
                metric="cpu_percent",
                threshold=95,
                severity=AlertSeverity.CRITICAL,
                operator=">",
            ),
            AlertRule(
                name="high_memory_usage",
                metric="memory_percent",
                threshold=90,
                severity=AlertSeverity.WARNING,
                operator=">",
            ),
            AlertRule(
                name="slow_response_time",
                metric="response_time_ms",
                threshold=2000,
                severity=AlertSeverity.WARNING,
                operator=">",
            ),
        ]

        for rule in default_rules:
            self.alert_manager.add_rule(rule)

    async def collect_system_metrics(self) -> None:
        """Collect comprehensive system metrics."""
        # Get system resources
        resources = self.performance_monitor.get_system_resources()

        # Record in metrics collector
        for metric_name, value in resources.items():
            if isinstance(value, (int, float)) and metric_name != "timestamp":
                self.metrics_collector.record_metric(metric_name, value)

        # Store in persistent storage
        self.storage.store_metrics(resources)

        # Evaluate alerts
        alerts = self.alert_manager.evaluate_rules(resources)

        if alerts:
            self.logger.info(f"Generated {len(alerts)} alerts", alert_count=len(alerts))

    async def start_monitoring(self) -> None:
        """Start the monitoring system."""
        self.logger.info("Monitoring system started")

        while True:
            try:
                await self.collect_system_metrics()
                await asyncio.sleep(self.config.performance_sample_interval)
            except Exception as e:
                self.logger.error("Monitoring error", error=str(e))
                await asyncio.sleep(60)  # Wait before retrying

    def get_monitoring_dashboard_data(self) -> dict[str, Any]:
        """Get data for monitoring dashboard."""
        return {
            "current_metrics": self.metrics_collector.export_metrics(),
            "system_resources": self.performance_monitor.get_system_resources(),
            "active_alerts": list(self.alert_manager.active_alerts.values()),
            "alert_statistics": self.alert_manager.get_alert_statistics(),
            "timestamp": datetime.utcnow().isoformat(),
        }
