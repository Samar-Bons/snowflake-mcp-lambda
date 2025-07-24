# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Data Chat MVP** - A full-stack web application enabling non-technical users to upload CSV files and query them using natural language via an AI-powered chat interface. The project is essentially complete at ~95% implementation status.

## Architecture

**Core Stack:**
- **Backend**: FastAPI (Python) with Poetry dependency management
- **Frontend**: React + Vite + TypeScript + Tailwind CSS (dark mode)
- **Auth**: Google OAuth with JWT cookies and Redis session management
- **Data**: PostgreSQL (users), Redis (sessions), SQLite (uploaded CSV data)  
- **LLM**: Google Gemini API (BYOK - user provides API key)
- **Deploy**: Docker Compose for development environment

**Key Flow:**
1. User uploads CSV file → auto-conversion to SQLite with schema detection
2. Natural language input → Gemini LLM → SQL generation with confirmation modal
3. SQL execution → paginated results display with export capabilities
4. Session-based temporary data storage (cleanup after session expires)

## Development Commands

**Python Package Management:**
- **Poetry** - Dependency management (backend/pyproject.toml)
- Install deps: `docker compose exec backend poetry install`
- Add packages: `docker compose exec backend poetry add <package>`
- Run scripts: `docker compose exec backend poetry run <script>`
- No requirements.txt needed - packages stored in pyproject.toml

**Development Workflow:**
```bash
# Complete Setup
make dev-setup                  # Full environment setup with health checks
make setup                      # Copy .env.example to .env (edit required)

# Daily Development  
make up                         # Start all services
make down                       # Stop all services
make logs                       # View all logs
make wait-healthy               # Wait for all services ready

# Backend Development
make shell-backend              # Open backend container shell
make logs-backend               # Backend logs only
docker compose exec backend poetry run uvicorn app.main:app --reload

# Frontend Development
make shell-frontend             # Open frontend container shell  
make logs-frontend              # Frontend logs only

# Testing (MUST pass before task completion)
make test                       # Backend tests with 85%+ coverage requirement
make test-frontend              # Frontend tests with Vitest
make test-all                   # All tests (backend + frontend)

# Inside backend container for specific tests:
poetry run pytest -k test_name              # Run specific test
poetry run pytest --cov=app --cov-report=html  # Coverage report

# Quality Checks (MUST pass before task completion)
make lint-frontend              # Frontend ESLint/Prettier
make type-check-frontend        # TypeScript type checking  
pre-commit run --all-files      # All quality checks (Ruff, MyPy, tests)

# Database Operations
make db-migrate                 # Run Alembic migrations
make db-reset                   # Reset database (destroys data)

# Health & Validation
make health                     # Check all service health
make validate-config            # Validate project configuration
make deep-health-check          # Comprehensive health validation
```

## Architecture Details

**Backend Structure (`backend/app/`):**
- `main.py` - FastAPI application entry point with middleware and routing
- `auth/` - Google OAuth, JWT utilities, user management
- `llm/` - Gemini API integration for natural language to SQL conversion
- `data/` - CSV upload, SQLite adapter, file processing pipeline
- `snowflake/` - Snowflake connection management (future expansion)
- `models/` - SQLAlchemy models (User, Connection)
- `core/` - Database configuration and shared utilities

**Frontend Structure (`frontend/src/`):**  
- `main.tsx` - React application entry point
- `pages/` - Main application pages (Landing, Chat)
- `components/` - Reusable UI components organized by feature
- `services/` - API client, authentication, file upload, chat logic
- `hooks/` - Custom React hooks (useAuth)
- `types/` - TypeScript type definitions

**Key Configuration Files:**
- `backend/pyproject.toml` - Poetry dependencies, pytest config, Ruff/MyPy settings
- `docker-compose.yml` - Multi-service development environment
- `Makefile` - Development commands and Docker operations
- `.env` - Environment variables (copy from .env.example)

## Testing Philosophy

**TDD Required:** Write failing test → minimal implementation → refactor
**All test types mandatory:** unit, integration, end-to-end  
**85%+ coverage requirement** enforced by pytest configuration
**Real data/APIs only** - no mocking implementations
**Pristine test output required** - must pass completely before task completion

**Backend Testing (`backend/tests/`):**
- 165+ passing tests with comprehensive coverage
- Test markers: `slow`, `integration`, `e2e`
- Key test files: `test_chat_endpoints.py`, `test_csv_processor.py`, `test_gemini_service.py`

**Frontend Testing (`frontend/src/`):**
- Component tests with React Testing Library
- Service layer tests for API integration  
- Vitest + jsdom testing environment

## Security Constraints

- **Read-only SQL queries** only (SELECT statements enforced)
- **Intent classification** to detect unsafe prompts
- **Secure file upload** validation (size limits, type checking)
- **Session-based temporary data** storage with cleanup
- **User-provided API keys** (BYOK model) - never stored server-side
- **No sensitive data** in logs or commits

## Current Implementation Status

**✅ Completed (95%):**
- Complete backend API with all endpoints functional
- Google OAuth authentication with JWT and Redis sessions
- CSV file upload and processing pipeline with SQLite conversion
- Gemini LLM integration for natural language to SQL conversion  
- React frontend with authentication flow and responsive design
- Docker development environment with health checks
- Comprehensive testing suite with 85%+ coverage

**🔄 Minor Remaining:**
- ~60 TypeScript errors to resolve
- Mobile responsiveness validation  
- Production deployment configuration

## File Headers Standard

All code files must start with:
```python
# ABOUTME: [Brief description of file purpose]
# ABOUTME: [Second line of description]
```

## Key References

- `docs/PROJECT_STATUS.md` - Current implementation status and next steps
- `README.md` - Project overview and quick start guide  
- `DEVELOPMENT.md` - Developer setup and troubleshooting
- `API_CONTRACT.md` - API endpoint specifications
- `MVP_UI_UX_DESIGN_SPEC.md` - UI/UX design requirements

## Next Implementation Priority

**TypeScript Error Resolution** - The primary remaining task is resolving ~60 TypeScript compilation errors to achieve a fully production-ready state. Most errors are type annotation issues that don't affect runtime functionality.