# Makefile for Snowflake MCP Lambda development
# Provides convenient commands for common development tasks

.PHONY: help install test lint format clean dev up down logs shell db-shell redis-shell build

# Default target
help: ## Show this help message
	@echo "Snowflake MCP Lambda Development Commands"
	@echo "========================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development setup
install: ## Install dependencies with Poetry
	poetry install
	poetry run pre-commit install

# Testing
test: ## Run all tests
	poetry run pytest

test-cov: ## Run tests with coverage report
	poetry run pytest --cov=backend/app --cov-report=html --cov-report=term-missing

test-unit: ## Run only unit tests
	poetry run pytest -m "not integration and not e2e"

test-integration: ## Run only integration tests
	poetry run pytest -m integration

test-e2e: ## Run only end-to-end tests
	poetry run pytest -m e2e

test-watch: ## Run tests in watch mode
	poetry run pytest-watch

# Code quality
lint: ## Run linting checks
	poetry run ruff check backend/
	poetry run mypy backend/

format: ## Format code
	poetry run black backend/
	poetry run isort backend/
	poetry run ruff check backend/ --fix

pre-commit: ## Run pre-commit hooks
	poetry run pre-commit run --all-files

# Development server
dev: ## Start development server
	poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Docker commands
up: ## Start all services with Docker Compose
	docker-compose up -d

up-build: ## Build and start all services
	docker-compose up -d --build

down: ## Stop all services
	docker-compose down

logs: ## Show logs from all services
	docker-compose logs -f

logs-backend: ## Show logs from backend service only
	docker-compose logs -f backend

# Admin tools (requires --profile admin)
admin-up: ## Start services with admin tools (pgAdmin, Redis Commander)
	docker-compose --profile admin up -d

# Database operations
db-shell: ## Connect to PostgreSQL shell
	docker-compose exec postgres psql -U postgres -d snowflake_mcp

db-reset: ## Reset database (WARNING: destroys all data)
	docker-compose down -v
	docker-compose up -d postgres
	@echo "Waiting for database to be ready..."
	@sleep 10
	@echo "Database reset complete"

# Redis operations
redis-shell: ## Connect to Redis shell
	docker-compose exec redis redis-cli

redis-flush: ## Flush all Redis data
	docker-compose exec redis redis-cli FLUSHALL

# Shell access
shell: ## Access backend container shell
	docker-compose exec backend bash

# Build operations
build: ## Build backend Docker image
	docker-compose build backend

build-prod: ## Build production Docker image
	docker build -t snowflake-mcp-lambda:latest backend/

# Cleanup
clean: ## Clean up development artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -f .coverage coverage.xml

clean-docker: ## Clean up Docker resources
	docker-compose down -v --remove-orphans
	docker system prune -f

# Environment setup
env: ## Copy environment template
	cp .env.example .env
	@echo "Environment file created. Please edit .env with your settings."

# Database migrations (for future use)
migrate: ## Run database migrations
	@echo "Migrations will be implemented in future phases"

migrate-create: ## Create a new migration
	@echo "Migration creation will be implemented in future phases"

# Documentation
docs: ## Generate documentation
	@echo "Documentation generation will be implemented in future phases"

# Production deployment helpers
deploy-check: ## Check if ready for deployment
	poetry run pytest
	poetry run ruff check backend/
	poetry run mypy backend/
	@echo "All checks passed! Ready for deployment."

# Quick development workflow
quick-start: install up ## Quick start for new developers
	@echo "Development environment is ready!"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "Run 'make help' to see all available commands"
