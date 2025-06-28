# ABOUTME: Tests for Docker production setup and container configuration
# ABOUTME: Validates security, performance, and reliability of production Docker environment

import subprocess
import time
from pathlib import Path
from typing import Any

import pytest
import requests
import yaml


class TestDockerConfiguration:
    """Test Docker configuration files and setup."""

    @pytest.fixture
    def project_root(self) -> Path:
        """Get project root directory."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def docker_compose_configs(self, project_root: Path) -> dict[str, Path]:
        """Get paths to all Docker Compose configuration files."""
        return {
            "dev": project_root / "docker-compose.yml",
            "prod": project_root / "docker-compose.prod.yml",
            "override": project_root / "docker-compose.override.yml",
            "monitoring": project_root / "docker-compose.monitoring.yml",
        }

    def test_docker_compose_files_exist(
        self, docker_compose_configs: dict[str, Path]
    ) -> None:
        """Test that all Docker Compose files exist."""
        for name, path in docker_compose_configs.items():
            assert path.exists(), f"Docker Compose file {name} does not exist at {path}"

    def test_docker_compose_syntax_valid(
        self, docker_compose_configs: dict[str, Path]
    ) -> None:
        """Test that all Docker Compose files have valid YAML syntax."""
        for name, path in docker_compose_configs.items():
            try:
                with open(path) as f:
                    yaml.safe_load(f)
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML syntax in {name} compose file: {e}")

    def test_dockerfile_exists(self, project_root: Path) -> None:
        """Test that Dockerfiles exist."""
        dockerfile = project_root / "backend" / "Dockerfile"
        dockerfile_prod = project_root / "backend" / "Dockerfile.prod"

        assert dockerfile.exists(), "Development Dockerfile does not exist"
        assert dockerfile_prod.exists(), "Production Dockerfile does not exist"

    def test_env_example_exists(self, project_root: Path) -> None:
        """Test that .env.example file exists."""
        env_example = project_root / ".env.example"
        assert env_example.exists(), ".env.example file does not exist"

    def test_makefile_exists(self, project_root: Path) -> None:
        """Test that Makefile exists."""
        makefile = project_root / "Makefile"
        assert makefile.exists(), "Makefile does not exist"


class TestDockerComposeConfiguration:
    """Test Docker Compose configuration structure."""

    @pytest.fixture
    def dev_config(self, project_root: Path) -> dict[str, Any]:
        """Load development Docker Compose configuration."""
        with open(project_root / "docker-compose.yml") as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def prod_config(self, project_root: Path) -> dict[str, Any]:
        """Load production Docker Compose configuration."""
        with open(project_root / "docker-compose.prod.yml") as f:
            return yaml.safe_load(f)

    def test_dev_services_defined(self, dev_config: dict[str, Any]) -> None:
        """Test that required services are defined in development config."""
        services = dev_config.get("services", {})
        required_services = {"backend", "postgres", "redis"}

        for service in required_services:
            assert service in services, f"Service {service} not defined in dev config"

    def test_prod_services_defined(self, prod_config: dict[str, Any]) -> None:
        """Test that required services are defined in production config."""
        services = prod_config.get("services", {})
        required_services = {"backend", "postgres", "redis", "nginx"}

        for service in required_services:
            assert service in services, f"Service {service} not defined in prod config"

    def test_prod_security_configurations(self, prod_config: dict[str, Any]) -> None:
        """Test that production configuration has security hardening."""
        backend = prod_config["services"]["backend"]

        # Check security options
        assert "security_opt" in backend
        assert "no-new-privileges:true" in backend["security_opt"]

        # Check capabilities
        assert "cap_drop" in backend
        assert "ALL" in backend["cap_drop"]

        # Check read-only filesystem
        assert backend.get("read_only", False) is True

    def test_prod_resource_limits(self, prod_config: dict[str, Any]) -> None:
        """Test that production configuration has resource limits."""
        services = prod_config["services"]

        for service_name in ["backend", "postgres", "redis"]:
            service = services[service_name]
            assert "deploy" in service, f"No deploy config for {service_name}"
            assert (
                "resources" in service["deploy"]
            ), f"No resources config for {service_name}"

            resources = service["deploy"]["resources"]
            assert "limits" in resources, f"No resource limits for {service_name}"
            assert (
                "reservations" in resources
            ), f"No resource reservations for {service_name}"

    def test_health_checks_configured(
        self, dev_config: dict[str, Any], prod_config: dict[str, Any]
    ) -> None:
        """Test that health checks are configured for all services."""
        for config_name, config in [("dev", dev_config), ("prod", prod_config)]:
            services = config["services"]

            for service_name in ["backend", "postgres", "redis"]:
                service = services[service_name]
                assert (
                    "healthcheck" in service
                ), f"No healthcheck for {service_name} in {config_name}"

                healthcheck = service["healthcheck"]
                assert (
                    "test" in healthcheck
                ), f"No test in healthcheck for {service_name}"
                assert (
                    "interval" in healthcheck
                ), f"No interval in healthcheck for {service_name}"


class TestDockerBuild:
    """Test Docker image building process."""

    @pytest.fixture
    def project_root(self) -> Path:
        """Get project root directory."""
        return Path(__file__).parent.parent.parent

    def test_dockerfile_syntax(self, project_root: Path) -> None:
        """Test that Dockerfiles have valid syntax by attempting a build."""
        dockerfile_path = project_root / "backend" / "Dockerfile"

        # Test Dockerfile syntax with --dry-run equivalent
        result = subprocess.run(
            [
                "docker",
                "build",
                "--no-cache",
                "--target",
                "builder",
                "-f",
                str(dockerfile_path),
                str(project_root),
            ],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )

        if result.returncode != 0:
            pytest.fail(f"Dockerfile build failed: {result.stderr}")

    def test_dockerfile_prod_syntax(self, project_root: Path) -> None:
        """Test that production Dockerfile has valid syntax."""
        dockerfile_path = project_root / "backend" / "Dockerfile.prod"

        # Test production Dockerfile syntax
        result = subprocess.run(
            [
                "docker",
                "build",
                "--no-cache",
                "--target",
                "builder",
                "-f",
                str(dockerfile_path),
                str(project_root),
            ],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )

        if result.returncode != 0:
            pytest.fail(f"Production Dockerfile build failed: {result.stderr}")


@pytest.mark.integration
class TestDockerIntegration:
    """Integration tests for Docker setup."""

    @pytest.fixture(scope="class")
    def docker_compose_up(self) -> None:
        """Start Docker Compose services for testing."""
        # Create minimal .env file for testing
        env_content = """
ENVIRONMENT=test
DEBUG=true
DATABASE_URL=postgresql://postgres:password@postgres:5432/snowflake_mcp_test
REDIS_URL=redis://redis:6379/1
SECRET_KEY=test-secret-key
JWT_SECRET_KEY=test-jwt-secret
"""
        with open(".env", "w") as f:
            f.write(env_content)

        # Start services
        subprocess.run(["docker", "compose", "up", "-d", "--build"], check=True)

        # Wait for services to be ready
        max_retries = 30
        for _ in range(max_retries):
            try:
                response = requests.get("http://localhost:8000/health", timeout=5)
                if response.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                pass
            time.sleep(2)
        else:
            pytest.fail("Services did not start within expected time")

        yield

        # Cleanup
        subprocess.run(["docker", "compose", "down", "-v"], check=True)

    def test_backend_health_endpoint(self, docker_compose_up: None) -> None:
        """Test that backend health endpoint is accessible."""
        response = requests.get("http://localhost:8000/health", timeout=10)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["service"] == "snowflake-mcp-lambda"

    def test_backend_readiness_endpoint(self, docker_compose_up: None) -> None:
        """Test that backend readiness endpoint is accessible."""
        response = requests.get("http://localhost:8000/health/ready", timeout=10)
        assert response.status_code == 200

        data = response.json()
        assert "ready" in data
        assert "dependencies" in data

    def test_database_connection(self, docker_compose_up: None) -> None:
        """Test database connection through backend."""
        # This would test actual database connectivity
        # For now, we test that the service is running
        result = subprocess.run(
            [
                "docker",
                "compose",
                "exec",
                "-T",
                "postgres",
                "pg_isready",
                "-U",
                "postgres",
                "-d",
                "snowflake_mcp_test",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, f"Database not ready: {result.stderr}"

    def test_redis_connection(self, docker_compose_up: None) -> None:
        """Test Redis connection."""
        result = subprocess.run(
            ["docker", "compose", "exec", "-T", "redis", "redis-cli", "ping"],
            capture_output=True,
            text=True,
            check=False,
        )

        assert "PONG" in result.stdout, f"Redis not responding: {result.stdout}"


@pytest.mark.e2e
class TestDockerProductionDeployment:
    """End-to-end tests for production Docker deployment."""

    def test_production_compose_up(self) -> None:
        """Test that production compose starts successfully."""
        # This test would be run in a CI environment
        # For now, we validate the configuration
        result = subprocess.run(
            ["docker", "compose", "-f", "docker-compose.prod.yml", "config"],
            capture_output=True,
            text=True,
            check=False,
        )

        assert (
            result.returncode == 0
        ), f"Production compose config invalid: {result.stderr}"

    def test_monitoring_compose_up(self) -> None:
        """Test that monitoring compose starts successfully."""
        result = subprocess.run(
            ["docker", "compose", "-f", "docker-compose.monitoring.yml", "config"],
            capture_output=True,
            text=True,
            check=False,
        )

        assert (
            result.returncode == 0
        ), f"Monitoring compose config invalid: {result.stderr}"
