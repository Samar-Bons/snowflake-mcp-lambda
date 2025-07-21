# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Data Chat MVP** - A web application enabling non-technical users to upload CSV files and query them using natural language via chat interface. Expandable to support multiple database types in the future.

## Architecture (Current Implementation Status)

**Core Stack:**
- Backend: FastAPI (Python) with Poetry dependency management ✅
- Frontend: React + Vite + TypeScript + Tailwind CSS (dark mode) ✅
- Auth: Google OAuth with JWT cookies (optional for MVP) ✅
- Data: PostgreSQL (users), Redis (sessions), SQLite (uploaded CSV data)
- LLM: Gemini API (BYOK - user provides API key) ✅
- Deploy: Docker + Docker Compose ✅

**MVP Key Flow:**
1. User uploads CSV file → auto-conversion to SQLite
2. Schema detection and preview → ready for queries
3. Natural language input → Gemini LLM → SQL generation
4. SQL confirmation modal → execution → paginated results
5. Session-based data (cleanup after session expires)

## Development Commands

**Current Status:** Backend foundation complete (85%), frontend auth complete, CSV upload MVP next priority.

**Working commands:**
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

## Implementation Phases (Current Status)

**Phase 0-1:** Foundation + Backend Core ✅ COMPLETED
- Git setup, pre-commit hooks, CI pipeline ✅
- FastAPI skeleton with health routes ✅
- Config system with Pydantic + environment support ✅
- Database client abstraction ready for CSV/SQLite ✅

**Phase 2:** Auth Stack ✅ COMPLETED
- Google OAuth flow with callback handling ✅
- PostgreSQL user model + SQLAlchemy ✅
- Redis session management with 24h expiry ✅
- JWT middleware for route protection ✅

**Phase 3:** Data Integration ✅ PARTIAL COMPLETED
- Gemini LLM integration working ✅
- Schema introspection system ready for SQLite ✅
- `/chat` endpoint: NL → SQL → confirmation → execution ✅
- Read-only query validation + 500 row limit ✅
- ⚠️ CSV upload processing (needs implementation for MVP)
- ⚠️ File management and SQLite conversion (needs implementation)

**Phase 4:** Frontend Foundation ✅ COMPLETED
- React app with complete auth flow ✅
- Dashboard layout ready for components ✅
- ⚠️ CSV upload components (next priority)
- ⚠️ Chat interface components (next priority)

**Phase 5:** 🟡 CSV Upload MVP (CURRENT PRIORITY)
- Backend: CSV upload, processing, SQLite conversion
- Frontend: File upload, schema preview, chat interface
- Integration: Complete upload → chat → results flow

**Phase 6:** Future Features (After MVP)
- Multiple file formats (Excel, JSON, Parquet)
- Database connections (PostgreSQL, MySQL)
- Query history, favorites, advanced settings

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
- Read-only SQL queries only (SELECT statements)
- Intent classification to detect unsafe prompts
- Secure file upload validation (size limits, type checking)
- Session-based temporary data storage
- No sensitive data in logs or commits

## Key Files to Reference

- `docs/planning/PROJECT_STATUS.md` - **Primary reference**: Current status and next prompts
- `docs/planning/spec.md` - Complete feature requirements and UX flows
- `DEVELOPMENT.md` - Developer setup and troubleshooting guide
- `README.md` - Basic project description

## Next Implementation Priority

**Prompt 11 - CSV Upload MVP**: Implement file upload backend + frontend components to enable users to upload CSV files and query them via chat interface. This creates a complete MVP that works without external database credentials.

See `docs/planning/PROJECT_STATUS.md` for detailed implementation requirements.

## MCP Servers Configuration

**Active MCP Servers** (configured via `claude mcp list`):

- **GitHub MCP Server** (`github`) - Repository management
  - Manage issues, PRs, commits, and repository operations
  - Usage: Natural language requests for GitHub operations

- **File System MCP Server** (`filesystem`) - Enhanced file operations
  - Advanced file read/write capabilities beyond built-in tools
  - Usage: File management and bulk operations

- **PostgreSQL MCP Server** (`postgres`) - Database integration
  - Direct database querying and management
  - Perfect for data analysis and database operations

- **Docker MCP Server** (`docker`) - Container management
  - Manage Docker containers, images, and compose files
  - Usage: `docker compose up/down`, container operations

- **Puppeteer MCP Server** (`puppeteer`) - Web automation
  - Browser automation and web scraping capabilities
  - Usage: Testing, screenshots, web interactions

**MCP Server Commands:**
```bash
claude mcp list                    # View all configured servers
claude mcp get <server-name>       # Get server details
claude mcp remove <server-name>    # Remove a server
```

**Usage Tips:**
- Reference resources with "@" mentions (e.g., @filename)
- Use slash commands for server-exposed prompts
- Set required API keys/tokens as environment variables
- Test servers with non-sensitive data first
