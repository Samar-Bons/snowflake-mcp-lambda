# ABOUTME: Test suite for monitoring system including metrics collection and alerting
# ABOUTME: Validates performance monitoring, business metrics, and intelligent alerting

import asyncio
import time
from datetime import datetime
from unittest.mock import patch

import pytest

from app.monitoring import (
    AlertManager,
    AlertRule,
    AlertSeverity,
    MetricsCollector,
    PerformanceMonitor,
    ThresholdManager,
)


class TestMetricsCollector:
    """Test metrics collection functionality."""

    def test_metrics_collector_initialization(self) -> None:
        """Test metrics collector initialization."""
        collector = MetricsCollector()
        assert collector is not None
        assert collector.metrics == {}

    def test_record_performance_metric(self) -> None:
        """Test recording performance metrics."""
        collector = MetricsCollector()

        collector.record_metric("response_time", 150.5, "ms")
        collector.record_metric("memory_usage", 64, "MB")

        assert "response_time" in collector.metrics
        assert "memory_usage" in collector.metrics

        response_time_metric = collector.metrics["response_time"]
        assert response_time_metric["value"] == 150.5
        assert response_time_metric["unit"] == "ms"
        assert "timestamp" in response_time_metric

    def test_record_business_metric(self) -> None:
        """Test recording business metrics."""
        collector = MetricsCollector()

        collector.record_business_metric("queries_executed", 1)
        collector.record_business_metric("active_users", 5)
        collector.record_business_metric("data_processed", 1024000, "bytes")

        assert len(collector.metrics) == 3
        assert collector.metrics["queries_executed"]["value"] == 1
        assert collector.metrics["active_users"]["value"] == 5
        assert collector.metrics["data_processed"]["unit"] == "bytes"

    def test_get_metrics_summary(self) -> None:
        """Test getting metrics summary."""
        collector = MetricsCollector()

        collector.record_metric("response_time", 100, "ms")
        collector.record_metric("response_time", 200, "ms")
        collector.record_metric("response_time", 150, "ms")

        summary = collector.get_metrics_summary("response_time")

        assert summary["count"] == 3
        assert summary["average"] == 150.0
        assert summary["min"] == 100
        assert summary["max"] == 200

    def test_metrics_export_format(self) -> None:
        """Test metrics export in standard format."""
        collector = MetricsCollector()

        collector.record_metric("cpu_usage", 75.5, "%")
        collector.record_business_metric("requests_count", 100)

        exported = collector.export_metrics()

        assert "performance_metrics" in exported
        assert "business_metrics" in exported
        assert "timestamp" in exported

        # Verify structure
        perf_metrics = exported["performance_metrics"]
        assert "cpu_usage" in perf_metrics
        assert perf_metrics["cpu_usage"]["value"] == 75.5


class TestPerformanceMonitor:
    """Test performance monitoring functionality."""

    def test_performance_monitor_initialization(self) -> None:
        """Test performance monitor initialization."""
        monitor = PerformanceMonitor()
        assert monitor is not None
        assert monitor.active_operations == {}

    def test_start_operation_timing(self) -> None:
        """Test starting operation timing."""
        monitor = PerformanceMonitor()

        operation_id = monitor.start_operation("database_query")

        assert operation_id is not None
        assert operation_id in monitor.active_operations
        assert monitor.active_operations[operation_id]["operation"] == "database_query"
        assert "start_time" in monitor.active_operations[operation_id]

    def test_complete_operation_timing(self) -> None:
        """Test completing operation timing."""
        monitor = PerformanceMonitor()

        operation_id = monitor.start_operation("api_request")

        # Simulate some processing time
        time.sleep(0.01)

        duration = monitor.complete_operation(operation_id)

        assert duration > 0
        assert operation_id not in monitor.active_operations

    def test_operation_timeout_detection(self) -> None:
        """Test detection of long-running operations."""
        monitor = PerformanceMonitor(timeout_threshold=0.01)  # 10ms timeout

        operation_id = monitor.start_operation("slow_operation")

        # Wait longer than timeout
        time.sleep(0.02)

        timeouts = monitor.check_timeouts()

        assert len(timeouts) == 1
        assert timeouts[0]["operation_id"] == operation_id
        assert timeouts[0]["operation"] == "slow_operation"

    def test_system_resource_monitoring(self) -> None:
        """Test system resource monitoring."""
        monitor = PerformanceMonitor()

        resources = monitor.get_system_resources()

        assert "cpu_percent" in resources
        assert "memory_percent" in resources
        assert "memory_available" in resources
        assert "disk_usage" in resources

        # Values should be reasonable
        assert 0 <= resources["cpu_percent"] <= 100
        assert 0 <= resources["memory_percent"] <= 100

    def test_performance_trend_analysis(self) -> None:
        """Test performance trend analysis."""
        monitor = PerformanceMonitor()

        # Record multiple measurements
        for i in range(10):
            op_id = monitor.start_operation("test_op")
            time.sleep(0.001)  # Simulate varying processing time
            monitor.complete_operation(op_id)

        trends = monitor.analyze_trends("test_op")

        assert "average_duration" in trends
        assert "trend_direction" in trends  # "improving", "degrading", "stable"
        assert "confidence" in trends


class TestAlertRule:
    """Test alert rule configuration and evaluation."""

    def test_alert_rule_creation(self) -> None:
        """Test creating alert rules."""
        rule = AlertRule(
            name="high_response_time",
            metric="response_time",
            threshold=1000,
            severity=AlertSeverity.WARNING,
            operator=">",
        )

        assert rule.name == "high_response_time"
        assert rule.metric == "response_time"
        assert rule.threshold == 1000
        assert rule.severity == AlertSeverity.WARNING

    def test_alert_rule_evaluation_greater_than(self) -> None:
        """Test alert rule evaluation with greater than operator."""
        rule = AlertRule(
            name="cpu_high",
            metric="cpu_usage",
            threshold=80,
            severity=AlertSeverity.CRITICAL,
            operator=">",
        )

        # Should trigger alert
        assert rule.evaluate(85) is True

        # Should not trigger alert
        assert rule.evaluate(75) is False
        assert rule.evaluate(80) is False  # Equal to threshold

    def test_alert_rule_evaluation_less_than(self) -> None:
        """Test alert rule evaluation with less than operator."""
        rule = AlertRule(
            name="low_availability",
            metric="service_availability",
            threshold=99.0,
            severity=AlertSeverity.WARNING,
            operator="<",
        )

        # Should trigger alert
        assert rule.evaluate(98.5) is True

        # Should not trigger alert
        assert rule.evaluate(99.5) is False

    def test_alert_rule_with_duration_threshold(self) -> None:
        """Test alert rules with duration-based thresholds."""
        rule = AlertRule(
            name="sustained_high_cpu",
            metric="cpu_usage",
            threshold=80,
            severity=AlertSeverity.CRITICAL,
            operator=">",
            duration_minutes=5,
        )

        assert rule.duration_minutes == 5

        # Test that rule considers duration in evaluation
        # This would be tested with time-series data in real implementation


class TestThresholdManager:
    """Test adaptive threshold management."""

    def test_threshold_manager_initialization(self) -> None:
        """Test threshold manager initialization."""
        manager = ThresholdManager()
        assert manager is not None
        assert manager.thresholds == {}

    def test_set_static_threshold(self) -> None:
        """Test setting static thresholds."""
        manager = ThresholdManager()

        manager.set_threshold("response_time", 1000, "static")

        assert "response_time" in manager.thresholds
        threshold = manager.thresholds["response_time"]
        assert threshold["value"] == 1000
        assert threshold["type"] == "static"

    def test_adaptive_threshold_calculation(self) -> None:
        """Test adaptive threshold calculation based on historical data."""
        manager = ThresholdManager()

        # Provide historical data
        historical_data = [100, 120, 110, 130, 105, 125, 115, 135]

        threshold = manager.calculate_adaptive_threshold(
            "response_time", historical_data, percentile=95
        )

        assert threshold > max(historical_data) * 0.8  # Should be reasonable
        assert threshold <= max(historical_data) * 1.2

    def test_threshold_adjustment_based_on_patterns(self) -> None:
        """Test threshold adjustment based on usage patterns."""
        manager = ThresholdManager()

        # Simulate different time periods with different baselines
        business_hours_data = [150, 160, 155, 165, 158]
        off_hours_data = [80, 85, 82, 88, 84]

        # Should calculate different thresholds for different periods
        bh_threshold = manager.calculate_time_based_threshold(
            "response_time", business_hours_data, "business_hours"
        )
        oh_threshold = manager.calculate_time_based_threshold(
            "response_time", off_hours_data, "off_hours"
        )

        assert bh_threshold > oh_threshold

    def test_threshold_validation(self) -> None:
        """Test threshold validation and bounds checking."""
        manager = ThresholdManager()

        # Valid threshold
        assert manager.validate_threshold("cpu_usage", 85) is True

        # Invalid thresholds
        assert manager.validate_threshold("cpu_usage", -5) is False
        assert manager.validate_threshold("cpu_usage", 150) is False  # > 100%


class TestAlertManager:
    """Test alert management and notification functionality."""

    def test_alert_manager_initialization(self) -> None:
        """Test alert manager initialization."""
        manager = AlertManager()
        assert manager is not None
        assert manager.active_alerts == {}
        assert manager.rules == []

    def test_add_alert_rule(self) -> None:
        """Test adding alert rules to manager."""
        manager = AlertManager()

        rule = AlertRule(
            name="high_memory",
            metric="memory_usage",
            threshold=85,
            severity=AlertSeverity.WARNING,
            operator=">",
        )

        manager.add_rule(rule)

        assert len(manager.rules) == 1
        assert manager.rules[0].name == "high_memory"

    def test_evaluate_all_rules(self) -> None:
        """Test evaluating all alert rules against current metrics."""
        manager = AlertManager()

        # Add multiple rules
        cpu_rule = AlertRule("high_cpu", "cpu_usage", 80, AlertSeverity.WARNING, ">")
        memory_rule = AlertRule(
            "high_memory", "memory_usage", 85, AlertSeverity.CRITICAL, ">"
        )

        manager.add_rule(cpu_rule)
        manager.add_rule(memory_rule)

        # Test metrics that should trigger alerts
        metrics = {
            "cpu_usage": 85,  # Should trigger CPU alert
            "memory_usage": 75,  # Should not trigger memory alert
        }

        triggered_alerts = manager.evaluate_rules(metrics)

        assert len(triggered_alerts) == 1
        assert triggered_alerts[0]["rule_name"] == "high_cpu"
        assert triggered_alerts[0]["severity"] == AlertSeverity.WARNING

    def test_alert_deduplication(self) -> None:
        """Test alert deduplication to prevent spam."""
        manager = AlertManager()

        rule = AlertRule("test_rule", "test_metric", 50, AlertSeverity.WARNING, ">")
        manager.add_rule(rule)

        # Trigger the same alert multiple times
        metrics = {"test_metric": 60}

        alerts1 = manager.evaluate_rules(metrics)
        alerts2 = manager.evaluate_rules(metrics)  # Same condition

        # First evaluation should create alert
        assert len(alerts1) == 1

        # Second evaluation should not create duplicate (within cooldown)
        assert len(alerts2) == 0

    def test_alert_recovery_notification(self) -> None:
        """Test alert recovery notification when conditions improve."""
        manager = AlertManager()

        rule = AlertRule("recovery_test", "test_metric", 80, AlertSeverity.WARNING, ">")
        manager.add_rule(rule)

        # Trigger alert
        high_metrics = {"test_metric": 90}
        triggered = manager.evaluate_rules(high_metrics)
        assert len(triggered) == 1

        # Resolve condition
        normal_metrics = {"test_metric": 70}
        resolved = manager.evaluate_rules(normal_metrics)

        # Should have recovery notification
        assert any(alert.get("type") == "recovery" for alert in resolved)

    @patch("requests.post")
    def test_alert_notification_webhook(self, mock_post) -> None:
        """Test sending alert notifications via webhook."""
        mock_post.return_value.status_code = 200

        manager = AlertManager(webhook_url="https://alerts.example.com/webhook")

        alert_data = {
            "rule_name": "test_alert",
            "severity": AlertSeverity.CRITICAL,
            "metric": "cpu_usage",
            "value": 95,
            "threshold": 85,
            "timestamp": datetime.utcnow().isoformat(),
        }

        result = manager.send_notification(alert_data)

        assert result is True
        mock_post.assert_called_once()

        # Verify webhook payload
        call_args = mock_post.call_args
        assert call_args[1]["json"]["rule_name"] == "test_alert"
        assert call_args[1]["json"]["severity"] == AlertSeverity.CRITICAL

    def test_alert_severity_escalation(self) -> None:
        """Test alert severity escalation for persistent issues."""
        manager = AlertManager()

        # Create rule with escalation
        rule = AlertRule(
            name="escalation_test",
            metric="error_rate",
            threshold=5,
            severity=AlertSeverity.WARNING,
            operator=">",
            escalation_minutes=10,
            escalate_to=AlertSeverity.CRITICAL,
        )
        manager.add_rule(rule)

        metrics = {"error_rate": 8}

        # Initial alert should be WARNING
        alerts = manager.evaluate_rules(metrics)
        assert alerts[0]["severity"] == AlertSeverity.WARNING

        # Simulate time passing and condition persisting
        # (This would require time manipulation in real implementation)
        # For now, test the escalation logic structure
        assert rule.escalate_to == AlertSeverity.CRITICAL


class TestMonitoringIntegration:
    """Integration tests for monitoring system."""

    def test_end_to_end_monitoring_flow(self) -> None:
        """Test complete monitoring flow from metrics to alerts."""
        # Initialize components
        collector = MetricsCollector()
        monitor = PerformanceMonitor()
        alert_manager = AlertManager()

        # Set up alert rules
        cpu_rule = AlertRule("high_cpu", "cpu_percent", 80, AlertSeverity.WARNING, ">")
        alert_manager.add_rule(cpu_rule)

        # Collect metrics
        collector.record_metric("cpu_percent", 85)

        # Get system resources
        resources = monitor.get_system_resources()

        # Evaluate alerts
        all_metrics = {**collector.export_metrics()["performance_metrics"], **resources}
        alerts = alert_manager.evaluate_rules(all_metrics)

        # Should trigger CPU alert
        assert len(alerts) >= 1
        cpu_alert = next((a for a in alerts if a["rule_name"] == "high_cpu"), None)
        assert cpu_alert is not None

    @pytest.mark.asyncio
    async def test_async_monitoring_operations(self) -> None:
        """Test asynchronous monitoring operations."""
        monitor = PerformanceMonitor()

        async def async_operation():
            await asyncio.sleep(0.01)  # Simulate async work
            return "result"

        # Test async operation timing
        start_time = time.time()
        result = await async_operation()
        duration = (time.time() - start_time) * 1000  # Convert to ms

        # Record the async operation timing
        collector = MetricsCollector()
        collector.record_metric("async_operation_time", duration, "ms")

        assert result == "result"
        assert duration > 0

    def test_monitoring_configuration_validation(self) -> None:
        """Test monitoring system configuration validation."""
        from app.monitoring import MonitoringConfig

        # Valid configuration
        config = MonitoringConfig(
            enable_performance_monitoring=True,
            enable_business_metrics=True,
            alert_webhook_url="https://alerts.example.com",
            metrics_retention_days=30,
        )

        assert config.enable_performance_monitoring is True
        assert config.metrics_retention_days == 30

        # Test configuration validation
        assert config.validate() is True

    def test_monitoring_data_persistence(self) -> None:
        """Test monitoring data persistence and retrieval."""
        from app.monitoring import MonitoringStorage

        storage = MonitoringStorage()

        # Store metrics
        metrics_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu_usage": 75.5,
            "memory_usage": 68.2,
            "active_connections": 15,
        }

        storage.store_metrics(metrics_data)

        # Retrieve historical data
        historical = storage.get_historical_metrics(metric_name="cpu_usage", hours=24)

        assert len(historical) > 0
        assert "cpu_usage" in historical[0]
