# Development Guide

## Quick Start (5 minutes)

```bash
# 1. Clone and setup
git clone <repo-url>
cd snowflake-mcp-lambda

# 2. Run automated setup
./scripts/setup-dev.sh

# 3. Access services
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
# Health: make health
```

## Prerequisites

- **Docker & Docker Compose**: Version 20.10+
- **Make**: For development commands
- **Git**: For version control
- **Ports Free**: 3000, 5432, 6379, 8000

### Docker Permissions Setup (Recommended)
```bash
# Add your user to docker group to avoid sudo requirements
sudo usermod -aG docker $USER
newgrp docker

# Test Docker access without sudo
docker info
```

### Check Prerequisites
```bash
make check-prereqs  # Will validate everything
# If permission denied, use: sudo make check-prereqs
```

**Note**: Some make commands may require `sudo` if Docker daemon requires root access. Commands will indicate when sudo is needed.

## Architecture Overview

```
project/
├── backend/              # Python FastAPI service
│   ├── pyproject.toml   # Poetry dependencies (MUST be here)
│   ├── poetry.lock      # Locked dependencies
│   ├── app/             # Python package
│   └── Dockerfile.dev   # Development container
├── frontend/            # React + Vite application
│   ├── package.json    # NPM dependencies
│   └── Dockerfile.dev  # Development container (Node 20+)
└── docker-compose.yml  # Development orchestration
```

**Key Architecture Decisions:**
- **Poetry files in `backend/`**: Clean microservices separation
- **Self-contained Docker contexts**: Each service builds independently
- **Node 20+ required**: For Vite 7.x compatibility

## Development Commands

```bash
# Setup & validation
make setup              # Copy .env.example to .env
make validate-config    # Check configuration consistency
make check-prereqs     # Validate development environment

# Service management
make build             # Build all containers
make up                # Start all services
make down              # Stop all services
make health            # Check service health status
make logs              # View all service logs

# Development workflow
make dev-setup         # Complete setup: build + start + validate
make clean-build       # Test clean build (no cache)
make restart           # Restart specific service: make restart SERVICE=backend
```

## Troubleshooting

### Port Conflicts
```bash
# Check what's using ports
sudo lsof -i :5432 -i :6379 -i :8000 -i :3000

# Stop conflicting services
sudo systemctl stop postgresql redis

# Or use different ports in .env
```

### Docker Issues
```bash
# Clean Docker state
docker system prune -af
make clean-build

# Check Docker daemon
sudo systemctl status docker

# Fix permissions (if needed)
sudo usermod -aG docker $USER
newgrp docker
```

### Backend Won't Start
```bash
# Check Poetry configuration
cd backend && poetry check

# Validate dependencies
make logs SERVICE=backend

# Common fixes:
# 1. Poetry files in wrong location (should be in backend/)
# 2. Virtual environment issues (rebuild container)
# 3. Missing environment variables
```

### Frontend Won't Start
```bash
# Check Node version in container
docker compose exec frontend node --version  # Should be 20+

# Check Vite compatibility
cd frontend && npm list vite

# Common fixes:
# 1. Node version too old (update Dockerfile to node:20-alpine)
# 2. npm install issues (clear node_modules, rebuild)
```

## Environment Configuration

### Required Environment Variables
Copy `.env.example` to `.env` and configure:

```bash
# Database (auto-configured for development)
POSTGRES_PASSWORD=your_secure_password

# Authentication (get from Google Cloud Console)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# LLM (get from Google AI Studio)
GEMINI_API_KEY=your-gemini-api-key

# Security (generate with: python -c "import secrets; print(secrets.token_hex(32))")
JWT_SECRET_KEY=your-secure-jwt-secret
```

### Getting API Keys

#### Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 Client ID
5. Add redirect URI: `http://localhost:8000/api/v1/auth/callback`

#### Gemini API Setup
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create new API key
3. Copy to `.env` file

## Testing

```bash
# Backend tests
cd backend && poetry run pytest

# Frontend tests
cd frontend && npm test

# Integration tests
make test-integration

# End-to-end health check
make deep-health-check
```

## Code Quality

```bash
# Backend linting & formatting
cd backend && poetry run ruff check
cd backend && poetry run ruff format

# Type checking
cd backend && poetry run mypy .

# Frontend linting
cd frontend && npm run lint

# All quality checks
make lint
```

## Common Workflows

### Adding New Backend Dependency
```bash
cd backend
poetry add package-name
# Rebuild container
make build SERVICE=backend
make restart SERVICE=backend
```

### Adding New Frontend Dependency
```bash
cd frontend
npm install package-name
# Rebuild container
make build SERVICE=frontend
make restart SERVICE=frontend
```

### Database Changes
```bash
# Create migration
cd backend && poetry run alembic revision --autogenerate -m "description"

# Apply migration
cd backend && poetry run alembic upgrade head

# Or restart services (auto-applies migrations)
make restart
```

## When Things Go Wrong

1. **Start with health check**: `make health`
2. **Check logs**: `make logs` or `make logs SERVICE=backend`
3. **Try clean rebuild**: `make clean-build`
4. **Validate configuration**: `make validate-config`
5. **Check prerequisites**: `make check-prereqs`

### Still stuck?
- Check this guide's troubleshooting section
- Look at service logs for specific errors
- Verify environment variables are set correctly
- Ensure no port conflicts with local services

## Production Differences

Development uses:
- Hot reload and dev servers
- Development environment variables
- Local volumes for rapid iteration
- Debug logging enabled

Production will use:
- Optimized builds and static serving
- Production environment variables
- Persistent volumes and external databases
- Structured logging with external collection
