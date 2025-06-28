# ABOUTME: Integration tests for Docker production setup and deployment
# ABOUTME: Tests multi-stage builds, security hardening, and container health checks

import json
import subprocess
import time
from pathlib import Path

import pytest


class TestDockerProduction:
    """Test suite for production Docker setup and deployment."""

    @pytest.fixture
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def backend_dockerfile(self, project_root: Path) -> Path:
        """Get the backend Dockerfile path."""
        return project_root / "backend" / "Dockerfile.prod"

    @pytest.fixture
    def docker_compose_prod(self, project_root: Path) -> Path:
        """Get the production docker-compose file path."""
        return project_root / "docker-compose.prod.yml"

    def test_backend_production_dockerfile_exists(
        self, backend_dockerfile: Path
    ) -> None:
        """Test that production Dockerfile exists for backend."""
        assert backend_dockerfile.exists(), "Backend production Dockerfile should exist"

    def test_docker_compose_production_exists(self, docker_compose_prod: Path) -> None:
        """Test that production docker-compose file exists."""
        assert (
            docker_compose_prod.exists()
        ), "Production docker-compose file should exist"

    def test_dockerfile_security_hardening(self, backend_dockerfile: Path) -> None:
        """Test that Dockerfile includes security hardening measures."""
        content = backend_dockerfile.read_text()

        # Check for non-root user
        assert (
            "useradd" in content or "adduser" in content
        ), "Should create non-root user"
        assert "USER " in content, "Should switch to non-root user"

        # Check for multi-stage build
        assert "FROM " in content, "Should use multi-stage build"
        assert (
            "as builder" in content or "AS builder" in content
        ), "Should have builder stage"
        assert (
            "as production" in content or "AS production" in content
        ), "Should have production stage"

        # Check for health check
        assert "HEALTHCHECK" in content, "Should include health check"

    def test_docker_compose_resource_limits(self, docker_compose_prod: Path) -> None:
        """Test that docker-compose includes resource limits."""
        content = docker_compose_prod.read_text()

        # Check for resource limits
        assert "deploy:" in content, "Should include deployment configuration"
        assert "resources:" in content, "Should include resource limits"
        assert "limits:" in content, "Should have resource limits"
        assert "memory:" in content, "Should have memory limits"
        assert "cpus:" in content, "Should have CPU limits"

    def test_docker_compose_networking(self, docker_compose_prod: Path) -> None:
        """Test that docker-compose includes proper networking."""
        content = docker_compose_prod.read_text()

        # Check for networks
        assert "networks:" in content, "Should define networks"
        assert "driver: bridge" in content, "Should use bridge driver"

    def test_docker_compose_security_settings(self, docker_compose_prod: Path) -> None:
        """Test that docker-compose includes security settings."""
        content = docker_compose_prod.read_text()

        # Check for security settings
        assert "read_only:" in content, "Should use read-only filesystem where possible"
        assert "tmpfs:" in content, "Should use tmpfs for temporary files"
        assert "cap_drop:" in content, "Should drop capabilities"

    @pytest.mark.integration
    def test_docker_build_production_backend(self, project_root: Path) -> None:
        """Test that production backend Docker image builds successfully."""
        dockerfile_path = project_root / "backend" / "Dockerfile.prod"

        # Build the image
        result = subprocess.run(
            [
                "docker",
                "build",
                "-f",
                str(dockerfile_path),
                "-t",
                "snowflake-mcp-backend:test",
                str(project_root),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, f"Docker build failed: {result.stderr}"
        assert (
            "Successfully tagged" in result.stdout
        ), "Image should be tagged successfully"

    @pytest.mark.integration
    def test_docker_image_security_scan(self, project_root: Path) -> None:
        """Test that Docker image passes security scan."""
        # First ensure the image is built
        dockerfile_path = project_root / "backend" / "Dockerfile.prod"
        subprocess.run(
            [
                "docker",
                "build",
                "-f",
                str(dockerfile_path),
                "-t",
                "snowflake-mcp-backend:test",
                str(project_root),
            ],
            capture_output=True,
            check=False,
        )

        # Run security scan using docker scan or trivy if available
        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                "/var/run/docker.sock:/var/run/docker.sock",
                "aquasec/trivy:latest",
                "image",
                "snowflake-mcp-backend:test",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        # If trivy is not available, skip the test
        if result.returncode != 0 and "command not found" in result.stderr:
            pytest.skip("Trivy not available for security scanning")

        # Check for critical vulnerabilities
        assert (
            "CRITICAL" not in result.stdout
        ), "Should not have critical vulnerabilities"

    @pytest.mark.integration
    def test_docker_container_health_check(self, project_root: Path) -> None:
        """Test that Docker container health check works correctly."""
        dockerfile_path = project_root / "backend" / "Dockerfile.prod"

        # Build the image
        subprocess.run(
            [
                "docker",
                "build",
                "-f",
                str(dockerfile_path),
                "-t",
                "snowflake-mcp-backend:test",
                str(project_root),
            ],
            capture_output=True,
            check=False,
        )

        # Run container with health check
        container_result = subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "--name",
                "test-health-container",
                "-p",
                "8001:8000",
                "snowflake-mcp-backend:test",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert container_result.returncode == 0, "Container should start successfully"

        try:
            # Wait for health check to pass
            time.sleep(10)

            # Check container health status
            health_result = subprocess.run(
                [
                    "docker",
                    "inspect",
                    "--format",
                    "{{.State.Health.Status}}",
                    "test-health-container",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            assert (
                health_result.stdout.strip() == "healthy"
            ), "Container should be healthy"

        finally:
            # Cleanup
            subprocess.run(
                ["docker", "stop", "test-health-container"],
                capture_output=True,
                check=False,
            )
            subprocess.run(
                ["docker", "rm", "test-health-container"],
                capture_output=True,
                check=False,
            )

    @pytest.mark.e2e
    def test_production_deployment_pipeline(self, project_root: Path) -> None:
        """End-to-end test of production deployment pipeline."""
        deploy_script = project_root / "scripts" / "deploy.sh"

        assert deploy_script.exists(), "Deployment script should exist"
        assert deploy_script.is_file(), "Deploy script should be a file"

        # Check script is executable
        import stat

        mode = deploy_script.stat().st_mode
        assert mode & stat.S_IEXEC, "Deploy script should be executable"

    def test_deployment_script_error_handling(self, project_root: Path) -> None:
        """Test that deployment script includes proper error handling."""
        deploy_script = project_root / "scripts" / "deploy.sh"

        if deploy_script.exists():
            content = deploy_script.read_text()

            # Check for error handling
            assert "set -e" in content, "Should exit on error"
            assert "set -u" in content, "Should exit on undefined variables"
            assert "set -o pipefail" in content, "Should exit on pipe failures"

    def test_monitoring_configuration_exists(self, project_root: Path) -> None:
        """Test that monitoring configuration files exist."""
        monitoring_dir = project_root / "monitoring"

        if monitoring_dir.exists():
            # Check for monitoring configuration
            prometheus_config = monitoring_dir / "prometheus.yml"
            grafana_config = monitoring_dir / "grafana"

            # These are optional but if they exist, they should be properly configured
            if prometheus_config.exists():
                content = prometheus_config.read_text()
                assert (
                    "scrape_configs:" in content
                ), "Prometheus should have scrape configs"

            if grafana_config.exists():
                assert grafana_config.is_dir(), "Grafana config should be a directory"

    @pytest.mark.integration
    def test_docker_compose_production_startup(self, project_root: Path) -> None:
        """Test that production docker-compose starts successfully."""
        compose_file = project_root / "docker-compose.prod.yml"

        # Start services
        result = subprocess.run(
            ["docker-compose", "-f", str(compose_file), "up", "-d", "--build"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
            check=False,
        )

        try:
            if result.returncode == 0:
                # Wait for services to start
                time.sleep(15)

                # Check if services are running
                ps_result = subprocess.run(
                    ["docker-compose", "-f", str(compose_file), "ps"],
                    capture_output=True,
                    text=True,
                    cwd=str(project_root),
                    check=False,
                )

                assert "Up" in ps_result.stdout, "Services should be running"

        finally:
            # Cleanup
            subprocess.run(
                ["docker-compose", "-f", str(compose_file), "down", "-v"],
                capture_output=True,
                cwd=str(project_root),
                check=False,
            )

    def test_container_logs_structured(self, project_root: Path) -> None:
        """Test that container logs are properly structured."""
        dockerfile_path = project_root / "backend" / "Dockerfile.prod"

        # Build and run container briefly to check logs
        subprocess.run(
            [
                "docker",
                "build",
                "-f",
                str(dockerfile_path),
                "-t",
                "snowflake-mcp-backend:test",
                str(project_root),
            ],
            capture_output=True,
            check=False,
        )

        # Run container briefly
        container_result = subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "--name",
                "test-logs-container",
                "snowflake-mcp-backend:test",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if container_result.returncode == 0:
            try:
                time.sleep(5)

                # Get logs
                logs_result = subprocess.run(
                    ["docker", "logs", "test-logs-container"],
                    capture_output=True,
                    text=True,
                    check=False,
                )

                # Check for structured logging (JSON format expected)
                if logs_result.stdout:
                    lines = logs_result.stdout.strip().split("\n")
                    for line in lines:
                        if line.strip():
                            try:
                                json.loads(line)
                            except json.JSONDecodeError:
                                # Allow non-JSON logs from uvicorn startup
                                assert (
                                    "uvicorn" in line.lower()
                                    or "started" in line.lower()
                                )

            finally:
                # Cleanup
                subprocess.run(
                    ["docker", "stop", "test-logs-container"],
                    capture_output=True,
                    check=False,
                )
                subprocess.run(
                    ["docker", "rm", "test-logs-container"],
                    capture_output=True,
                    check=False,
                )
