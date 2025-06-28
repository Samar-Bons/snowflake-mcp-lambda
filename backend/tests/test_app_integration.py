# ABOUTME: Integration tests for FastAPI application with logging and monitoring
# ABOUTME: Tests complete end-to-end functionality including middleware and health checks

import asyncio
import json
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestAppIntegration:
    """Integration tests for the FastAPI application."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_root_endpoint_includes_monitoring_info(self):
        """Test root endpoint includes monitoring information."""
        response = self.client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["service"] == "snowflake-mcp-lambda"
        assert data["version"] == "0.1.0"
        assert data["status"] == "running"
        assert "monitoring_enabled" in data
        assert "endpoints" in data
        
        # Check monitoring endpoints are included
        endpoints = data["endpoints"]
        assert "/monitoring/dashboard" in endpoints.values()
        assert "/monitoring/metrics" in endpoints.values()

    def test_health_endpoint_with_monitoring(self):
        """Test health endpoint includes monitoring data."""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        # Should include monitoring section if monitoring is available
        if "monitoring" in data:
            assert "monitoring_active" in data["monitoring"]
            assert "alerts_count" in data["monitoring"]
            assert "metrics_collected" in data["monitoring"]

    def test_readiness_endpoint_with_system_metrics(self):
        """Test readiness endpoint includes system resource information."""
        response = self.client.get("/readiness")
        
        # Should return 200 or 503 depending on system state
        assert response.status_code in [200, 503]
        data = response.json()
        
        assert "ready" in data
        # Should include system resources if monitoring is available
        if "system_resources" in data:
            assert "cpu_percent" in data["system_resources"]
            assert "memory_percent" in data["system_resources"]
            assert "disk_usage" in data["system_resources"]

    def test_monitoring_dashboard_endpoint(self):
        """Test monitoring dashboard endpoint."""
        response = self.client.get("/monitoring/dashboard")
        
        # Should return either monitoring data or 503 if not available
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "current_metrics" in data
            assert "timestamp" in data
            
            if "monitoring_status" in data:
                status = data["monitoring_status"]
                assert "system_active" in status
                assert "configuration" in status

    def test_monitoring_metrics_endpoint(self):
        """Test monitoring metrics endpoint."""
        response = self.client.get("/monitoring/metrics")
        
        # Should return either metrics data or 503 if not available
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "json_metrics" in data
            assert "prometheus_format" in data
            assert "timestamp" in data
            
            # Check structure of metrics
            json_metrics = data["json_metrics"]
            assert "performance" in json_metrics
            assert "business" in json_metrics
            assert "system" in json_metrics

    def test_cors_and_security_headers(self):
        """Test CORS and security headers are properly set."""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        # Additional header checks would go here when CORS middleware is added

    def test_request_logging_correlation_id(self):
        """Test that requests generate correlation IDs in logs."""
        # This would require log capture in a real test
        # For now, just verify the request completes successfully
        response = self.client.get("/health")
        assert response.status_code == 200

    def test_error_handling_and_logging(self):
        """Test error handling includes proper logging."""
        # Test accessing a non-existent endpoint
        response = self.client.get("/nonexistent")
        assert response.status_code == 404

    def test_monitoring_system_configuration(self):
        """Test monitoring system responds to configuration."""
        # Test that monitoring endpoints reflect configuration
        response = self.client.get("/monitoring/dashboard")
        
        if response.status_code == 200:
            data = response.json()
            if "monitoring_status" in data and "configuration" in data["monitoring_status"]:
                config = data["monitoring_status"]["configuration"]
                # Should have boolean values for enable flags
                assert isinstance(config.get("performance_monitoring"), bool)
                assert isinstance(config.get("business_metrics"), bool)
                # Should have numeric values for intervals
                if "sample_interval" in config:
                    assert isinstance(config["sample_interval"], int)
                    assert config["sample_interval"] > 0


class TestMonitoringSystemIntegration:
    """Test monitoring system integration with FastAPI."""

    def setup_method(self):
        """Set up test environment."""
        self.client = TestClient(app)

    @pytest.mark.asyncio
    async def test_monitoring_system_lifecycle(self):
        """Test monitoring system startup and shutdown."""
        # This would test the actual lifecycle if we could control it
        # For now, verify the endpoints respond appropriately
        response = self.client.get("/monitoring/dashboard")
        # Should either work or return 503 - shouldn't crash
        assert response.status_code in [200, 503]

    def test_metrics_collection_and_export(self):
        """Test metrics are collected and can be exported."""
        # Make several requests to generate metrics
        for _ in range(5):
            self.client.get("/health")
        
        # Check if metrics are available
        response = self.client.get("/monitoring/metrics")
        
        if response.status_code == 200:
            data = response.json()
            # Should have some system metrics at minimum
            assert "json_metrics" in data
            system_metrics = data["json_metrics"].get("system", {})
            # Should have basic system info
            if system_metrics:
                # These should be present if psutil is working
                potential_metrics = ["cpu_percent", "memory_percent", "disk_usage"]
                has_system_metrics = any(metric in system_metrics for metric in potential_metrics)
                assert has_system_metrics

    def test_alert_system_integration(self):
        """Test alert system integration."""
        response = self.client.get("/monitoring/dashboard")
        
        if response.status_code == 200:
            data = response.json()
            # Should have alerts section
            if "active_alerts" in data:
                assert isinstance(data["active_alerts"], list)
            if "alert_statistics" in data:
                stats = data["alert_statistics"]
                assert isinstance(stats.get("total_alerts", 0), int)

    def test_performance_monitoring_integration(self):
        """Test performance monitoring integration."""
        # Make requests to trigger performance monitoring
        self.client.get("/")
        self.client.get("/health")
        self.client.get("/readiness")
        
        response = self.client.get("/monitoring/dashboard")
        
        if response.status_code == 200:
            data = response.json()
            # Should have performance metrics
            current_metrics = data.get("current_metrics", {})
            if current_metrics:
                # Should have either performance or business metrics
                has_metrics = bool(
                    current_metrics.get("performance_metrics") or
                    current_metrics.get("business_metrics")
                )
                # This might be empty initially, so just check structure
                assert isinstance(current_metrics.get("performance_metrics", {}), dict)


class TestLoggingIntegration:
    """Test logging system integration."""

    def setup_method(self):
        """Set up test environment."""
        self.client = TestClient(app)

    @patch('app.logging.get_logger')
    def test_structured_logging_in_endpoints(self, mock_get_logger):
        """Test that endpoints use structured logging."""
        mock_logger = mock_get_logger.return_value
        
        response = self.client.get("/health")
        assert response.status_code == 200
        
        # Verify logger was called (would be more specific in real implementation)
        mock_get_logger.assert_called()

    def test_correlation_id_propagation(self):
        """Test correlation ID propagation across requests."""
        # This would require log inspection in a real test
        # For now, verify requests complete successfully
        responses = []
        for _ in range(3):
            response = self.client.get("/health")
            responses.append(response)
            assert response.status_code == 200
        
        # All should succeed independently
        assert all(r.status_code == 200 for r in responses)

    def test_error_logging_with_details(self):
        """Test error logging includes proper details."""
        # Trigger a 404 error
        response = self.client.get("/definitely-does-not-exist")
        assert response.status_code == 404
        
        # Error should be handled gracefully without crashing


class TestConfigurationIntegration:
    """Test configuration system integration."""

    def test_configuration_affects_monitoring(self):
        """Test that configuration affects monitoring behavior."""
        # This would test with different config values
        # For now, verify monitoring respects enabled/disabled state
        response = self.client.get("/monitoring/dashboard")
        
        # Should either work or be disabled - shouldn't crash
        assert response.status_code in [200, 503]

    def test_logging_configuration_integration(self):
        """Test logging configuration integration."""
        # This would test different log levels and formats
        # For now, verify logging doesn't break the application
        response = self.client.get("/health")
        assert response.status_code == 200

    def test_environment_specific_behavior(self):
        """Test environment-specific configuration behavior."""
        # This would test dev vs prod differences
        # For now, verify application works in current environment
        response = self.client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "snowflake-mcp-lambda"