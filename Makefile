# ABOUTME: Docker and development automation commands for Snowflake MCP Lambda
# ABOUTME: Provides consistent interface for building, testing, and deploying the application

.PHONY: help build dev prod test clean setup logs shell migrate lint format check-env health

# Default target
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Environment setup
setup: ## Setup development environment
	@echo "Setting up development environment..."
	@if [ ! -f .env ]; then \
		echo "Creating .env from .env.example..."; \
		cp .env.example .env; \
		echo "Please edit .env with your configuration"; \
	fi
	@if [ ! -f backend/tests/fixtures/init.sql ]; then \
		mkdir -p backend/tests/fixtures; \
		touch backend/tests/fixtures/init.sql; \
	fi
	@echo "Setup complete!"

check-env: ## Check if required environment files exist
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Run 'make setup' first."; \
		exit 1; \
	fi

# Docker build commands
build: ## Build all Docker images
	@echo "Building Docker images..."
	docker compose build

build-prod: ## Build production Docker images
	@echo "Building production Docker images..."
	docker compose -f docker-compose.prod.yml build

build-no-cache: ## Build Docker images without cache
	@echo "Building Docker images without cache..."
	docker compose build --no-cache

# Development commands
dev: check-env ## Start development environment
	@echo "Starting development environment..."
	docker compose up -d
	@echo "Services available at:"
	@echo "  - Backend API: http://localhost:8000"
	@echo "  - API Docs: http://localhost:8000/docs"
	@echo "  - PgAdmin: http://localhost:8080"
	@echo "  - PostgreSQL: localhost:5432"
	@echo "  - Redis: localhost:6379"

dev-build: check-env ## Build and start development environment
	@echo "Building and starting development environment..."
	docker compose up -d --build

dev-logs: ## Follow development logs
	docker compose logs -f

dev-down: ## Stop development environment
	@echo "Stopping development environment..."
	docker compose down

dev-clean: ## Stop development environment and remove volumes
	@echo "Cleaning up development environment..."
	docker compose down -v --remove-orphans

# Production commands
prod: check-env ## Start production environment
	@echo "Starting production environment..."
	docker compose -f docker-compose.prod.yml up -d
	@echo "Production services started"
	@echo "  - Application: http://localhost:80"
	@echo "  - Health check: http://localhost:80/health"

prod-build: check-env ## Build and start production environment
	@echo "Building and starting production environment..."
	docker compose -f docker-compose.prod.yml up -d --build

prod-down: ## Stop production environment
	@echo "Stopping production environment..."
	docker compose -f docker-compose.prod.yml down

prod-logs: ## Follow production logs
	docker compose -f docker-compose.prod.yml logs -f

# Monitoring commands
monitoring: ## Start monitoring stack
	@echo "Starting monitoring stack..."
	docker compose -f docker-compose.monitoring.yml up -d
	@echo "Monitoring services available at:"
	@echo "  - Grafana: http://localhost:3000"
	@echo "  - Prometheus: http://localhost:9090"
	@echo "  - AlertManager: http://localhost:9093"
	@echo "  - Jaeger: http://localhost:16686"

monitoring-down: ## Stop monitoring stack
	@echo "Stopping monitoring stack..."
	docker compose -f docker-compose.monitoring.yml down

# Testing commands
test: ## Run tests in Docker container
	@echo "Running tests..."
	docker compose exec backend pytest -v

test-cov: ## Run tests with coverage
	@echo "Running tests with coverage..."
	docker compose exec backend pytest --cov=app --cov-report=html --cov-report=term-missing

test-integration: ## Run integration tests
	@echo "Running integration tests..."
	docker compose exec backend pytest -m integration -v

test-e2e: ## Run end-to-end tests
	@echo "Running end-to-end tests..."
	docker compose exec backend pytest -m e2e -v

# Utility commands
shell: ## Open shell in backend container
	docker compose exec backend /bin/bash

shell-db: ## Open PostgreSQL shell
	docker compose exec postgres psql -U postgres -d snowflake_mcp

shell-redis: ## Open Redis CLI
	docker compose exec redis redis-cli

logs: ## Show logs for all services
	docker compose logs

logs-backend: ## Show backend logs
	docker compose logs backend

logs-db: ## Show database logs
	docker compose logs postgres

logs-redis: ## Show Redis logs
	docker compose logs redis

# Health and status commands
health: ## Check health of all services
	@echo "Checking service health..."
	@curl -s http://localhost:8000/health | jq . || echo "Backend not responding"
	@docker compose ps

status: ## Show status of all containers
	docker compose ps

# Database commands
migrate: ## Run database migrations
	@echo "Running database migrations..."
	docker compose exec backend alembic upgrade head

migrate-create: ## Create new migration
	@read -p "Enter migration message: " msg; \
	docker compose exec backend alembic revision --autogenerate -m "$$msg"

# Code quality commands
lint: ## Run linting checks
	@echo "Running linting checks..."
	docker compose exec backend black --check app tests
	docker compose exec backend ruff check app tests
	docker compose exec backend isort --check-only app tests
	docker compose exec backend mypy app

format: ## Format code
	@echo "Formatting code..."
	docker compose exec backend black app tests
	docker compose exec backend isort app tests
	docker compose exec backend ruff --fix app tests

# Cleanup commands
clean: ## Remove all containers, volumes, and images
	@echo "Cleaning up Docker resources..."
	docker compose down -v --remove-orphans
	docker compose -f docker-compose.prod.yml down -v --remove-orphans
	docker compose -f docker-compose.monitoring.yml down -v --remove-orphans
	docker system prune -a --volumes -f

clean-images: ## Remove Docker images
	@echo "Removing Docker images..."
	docker rmi $$(docker images "snowflake-mcp*" -q) 2>/dev/null || true

# Backup commands
backup-db: ## Backup database
	@echo "Creating database backup..."
	@mkdir -p backups
	docker compose exec postgres pg_dump -U postgres snowflake_mcp > backups/db_backup_$$(date +%Y%m%d_%H%M%S).sql

restore-db: ## Restore database from backup
	@read -p "Enter backup file path: " backup; \
	docker compose exec -T postgres psql -U postgres snowflake_mcp < $$backup

# Security commands
security-scan: ## Run security scan on images
	@echo "Running security scan..."
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
		aquasec/trivy image snowflake-mcp-lambda_backend:latest

# Performance monitoring
perf-test: ## Run performance tests
	@echo "Running performance tests..."
	docker run --rm --network snowflake-mcp-lambda_app-network \
		williamyeh/wrk -t4 -c100 -d30s http://backend:8000/health
