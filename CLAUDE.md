# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Snowflake MCP Lambda** - A remote Model Context Protocol Server for Snowflake deployed as AWS Lambda. Enables non-technical users to interact with Snowflake databases through natural language queries via chat interface.

## Architecture (Planned Implementation)

**Core Stack:**
- Backend: FastAPI (Python) with Poetry dependency management
- Frontend: React + Vite + TypeScript + Tailwind CSS (dark mode)
- Auth: Google OAuth with JWT cookies
- Data: PostgreSQL (users), Redis (sessions), Snowflake (queries)
- LLM: Gemini API (BYOK - user provides API key)
- Deploy: Docker + Docker Compose, AWS Lambda target

**Key Flow:**
1. Google OAuth → user session in Redis
2. User configures Snowflake connection via step-by-step form
3. Natural language input → Gemini LLM → SQL generation
4. SQL confirmation modal → read-only execution → paginated results
5. Query history/favorites stored per user

## Development Commands

**Current Status:** Planning phase - no implementation exists yet.

**Expected commands when implementation begins:**
```bash
# Setup
poetry install                    # Install Python dependencies
npm install                      # Install frontend dependencies (when added)

# Development
uvicorn app.main:app --reload    # Run backend server
npm run dev                      # Run frontend dev server (when added)

# Testing (TDD approach required)
pytest                          # Run all tests
pytest -k test_name             # Run specific test
pytest --cov=backend            # Run with coverage (target: 85%+)

# Quality
pre-commit run --all-files      # Lint/format (black, ruff, isort, mypy)
mypy --strict backend/          # Type checking

# Docker
docker compose up               # Development environment
docker compose -f prod.yml up  # Production environment
```

## Implementation Phases

Based on `prompt_plan.md`, follow this sequence:

**Phase 0-1:** Foundation + Backend Core
- Git setup, pre-commit hooks, CI pipeline
- FastAPI skeleton with health routes
- Config system with Pydantic + environment support
- Snowflake client with connection validation

**Phase 2:** Auth Stack
- Google OAuth flow with callback handling
- PostgreSQL user model + SQLAlchemy
- Redis session management with 24h expiry
- JWT middleware for route protection

**Phase 3:** LLM Pipeline
- Gemini service wrapper with API key injection
- Context builder for schema metadata
- `/chat` endpoint: NL → SQL → confirmation → execution
- Read-only query validation + 500 row limit

**Phase 4-5:** Frontend + Features
- React app with auth flow and chat UI
- Schema explorer sidebar, result table with pagination
- Query history CRUD, favorites, settings panel

**Phase 6:** Production Readiness
- Structured JSON logging with external sink
- Docker Compose production profile
- GitHub Actions for image builds

## Code Standards

**File Headers:** All code files start with:
```python
# ABOUTME: [Brief description of file purpose]
# ABOUTME: [Second line of description]
```

**Testing Philosophy:**
- TDD required: Write failing test → minimal implementation → refactor
- All test types mandatory: unit, integration, end-to-end
- Real data/APIs only - no mocking
- Pristine test output required to pass

**Security Constraints:**
- Read-only Snowflake queries only (SELECT statements)
- Intent classification to detect unsafe prompts
- No sensitive data in logs or commits
- Connection validation before query execution

## Key Files to Reference

- `planning/spec.md` - Complete feature requirements and UX flows
- `planning/prompt_plan.md` - Detailed implementation prompts for each phase
- `README.md` - Basic project description
