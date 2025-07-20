# ABOUTME: Makefile for common development tasks and Docker operations
# ABOUTME: Provides convenient shortcuts for building, running, and testing the application

.PHONY: help build up down logs test clean setup dev-setup db-migrate

# Default target
help: ## Show this help message
	@echo "🐳 Snowflake MCP Lambda - Development Commands"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🔒 Note: All cleanup commands only affect this project's Docker resources"

# Docker operations
build: ## Build all Docker containers
	docker compose build

up: ## Start all services in development mode
	docker compose up -d

down: ## Stop all services
	docker compose down

logs: ## View logs from all services
	docker compose logs -f

logs-backend: ## View backend logs only
	docker compose logs -f backend

logs-frontend: ## View frontend logs only
	docker compose logs -f frontend

# Development setup
setup: ## Initial setup - copy .env.example to .env with security reminders
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env file from .env.example"; \
		echo ""; \
		echo "🔒 SECURITY REMINDERS:"; \
		echo "1. Generate a secure PostgreSQL password"; \
		echo "2. Generate a secure JWT secret: python -c \"import secrets; print(secrets.token_hex(32))\""; \
		echo "3. Add your Google OAuth credentials"; \
		echo "4. Add your Gemini API key"; \
		echo "5. NEVER commit the .env file to version control"; \
		echo ""; \
		echo "📝 Please edit .env with your actual configuration values before running 'make up'"; \
	else \
		echo ".env file already exists"; \
	fi

dev-setup: setup build up ## Complete development setup
	@echo "Development environment is starting up..."
	@echo "Backend will be available at: http://localhost:8000"
	@echo "Frontend will be available at: http://localhost:3000"
	@echo "API docs will be available at: http://localhost:8000/docs"

# Database operations
db-migrate: ## Run database migrations
	docker compose exec backend poetry run alembic upgrade head

db-reset: ## Reset database (WARNING: destroys project database data only)
	docker compose stop backend frontend
	docker compose rm -f backend frontend
	docker volume rm snowflake-mcp-lambda_postgres_data || true
	docker volume rm snowflake-mcp-lambda_redis_data || true
	docker compose up -d postgres redis
	@echo "Waiting for database to be ready..."
	sleep 10
	docker compose exec backend poetry run alembic upgrade head
	@echo "✅ Database reset complete"

# Testing
test: ## Run backend tests
	docker compose exec backend poetry run pytest

test-cov: ## Run backend tests with coverage
	docker compose exec backend poetry run pytest --cov=app --cov-report=html

# Cleanup
clean: ## Stop containers and remove project volumes (WARNING: destroys project data only)
	docker compose down -v
	docker compose rm -f
	@echo "✅ Cleaned up project containers and volumes"
	@echo "ℹ️  To also remove project images, run: make clean-images"

clean-images: ## Remove project Docker images
	docker compose down
	docker compose rm -f
	@echo "Removing project images..."
	@docker images --filter=reference="snowflake-mcp-lambda*" -q | xargs -r docker rmi -f
	@docker images --filter=reference="*snowflake-mcp*" -q | xargs -r docker rmi -f
	@echo "✅ Cleaned up project images"

clean-all: clean clean-images ## Complete cleanup - removes containers, volumes, and images for this project only
	@echo "✅ Complete project cleanup finished"

restart: ## Restart all services
	docker compose restart

# Health checks
health: ## Check health of all services
	@echo "Checking service health..."
	@curl -f http://localhost:8000/health && echo "✅ Backend healthy" || echo "❌ Backend unhealthy"
	@curl -f http://localhost:3000 && echo "✅ Frontend healthy" || echo "❌ Frontend unhealthy"

# Development helpers
shell-backend: ## Open shell in backend container
	docker compose exec backend bash

shell-frontend: ## Open shell in frontend container
	docker compose exec frontend sh

install-backend: ## Install backend dependencies
	docker compose exec backend poetry install

install-frontend: ## Install frontend dependencies
	docker compose exec frontend npm install
