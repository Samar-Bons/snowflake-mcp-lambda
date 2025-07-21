# Data Chat MVP
A web application enabling non-technical users to upload CSV files and query them using natural language via chat interface.

## 📊 Project Status

**Current Phase: CSV Upload MVP Implementation**

### ✅ Completed (85% Backend Foundation)
- **P0 - Foundation**: Git repo, pre-commit hooks, CI pipeline, Docker setup ✅
- **P1 - Backend Core**: FastAPI app, config management, database foundations, health endpoints ✅
- **P2 - Auth & Sessions**: Complete Google OAuth integration with user management ✅
  - User SQLAlchemy model with preferences
  - JWT-based session management
  - Auth endpoints (login, callback, logout, profile, preferences)
  - 103 tests with 89.73% coverage
- **P3 - Data Integration**: LLM pipeline and data processing infrastructure ✅
  - Gemini API service with BYOK model and prompt engineering
  - Schema service ready for SQLite data from CSV uploads
  - Chat endpoints for NL→SQL conversion with autorun support
  - SQL validation and injection prevention
  - 55 tests with 95%+ coverage for new components
- **P4 - Frontend Auth**: Complete authentication flow ✅
  - React app with Google OAuth integration
  - Protected routes and user context
  - Dashboard layout ready for data components

### 🎯 Next Priority: CSV Upload MVP (Prompt 11)
- **Backend**: CSV upload endpoint, file processing, SQLite conversion
- **Frontend**: File upload components, schema preview, chat interface integration
- **Integration**: Complete upload → query → results flow

### 🔮 Future Features (Post-MVP)
- **Multiple file formats**: Excel, JSON, Parquet support
- **Database connections**: PostgreSQL, MySQL, Snowflake integration
- **Advanced features**: Query history, favorites, data visualization
- **Enterprise**: SSO, RBAC, collaboration features

## 🚀 Quick Start with Docker (RECOMMENDED)

**For the fastest development experience:**

```bash
# 1. Clone and setup environment
git clone <your-repo-url>
cd snowflake-mcp-lambda
make setup  # Copies .env.example to .env

# 2. IMPORTANT: Edit .env with required values
# Required: GEMINI_API_KEY (for LLM functionality)
# Optional: GOOGLE_CLIENT_* (for auth), database passwords

# 3. Start everything with one command
make dev-setup
# This builds containers, starts services, and runs migrations

# 4. Access the application
# - Frontend: http://localhost:3000 (React app)
# - Backend API: http://localhost:8000 (FastAPI)
# - API Docs: http://localhost:8000/docs (Interactive API docs)
```

**Common development commands:**
```bash
make help           # Show all available commands
make up             # Start services
make down           # Stop services
make logs           # View all logs
make test           # Run backend tests
make health         # Check service health
make wait-healthy   # Wait for all services to be ready
make clean          # Clean up containers/volumes
```

## 💡 Key Features

### 🎯 MVP User Experience
1. **Upload CSV File** - Drag-and-drop interface with progress indication
2. **Schema Preview** - Auto-detected columns and data types with confirmation
3. **Chat Interface** - Ask questions about your data in natural language
4. **SQL Generation** - Gemini LLM converts questions to SQLite queries
5. **Results Display** - Interactive table with sorting, filtering, export options

### 🔒 Security & Privacy
- **No data persistence** - Files deleted after session ends
- **Read-only queries** - Only SELECT statements allowed
- **User-provided API keys** - Gemini API key never stored server-side
- **File validation** - Size limits, format validation, secure processing

### ⚡ Performance
- **Fast uploads** - Supports files up to 100MB
- **Efficient processing** - CSV → SQLite conversion with schema inference
- **Quick queries** - In-memory SQLite for fast query execution
- **Session-based** - No database dependencies for core functionality

## ⚙️ Configuration

### Required API Keys

#### Gemini API (Required for LLM functionality)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add to your `.env` file: `GEMINI_API_KEY=your-api-key`

#### Google OAuth (Optional for MVP)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create OAuth 2.0 Client ID credentials
3. Add redirect URI: `http://localhost:8000/api/v1/auth/callback`
4. Add to `.env`: `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`

### Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
# Required for core functionality
GEMINI_API_KEY=your-gemini-api-key

# Optional for authentication (can use without login)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Auto-generated secure secrets
JWT_SECRET_KEY=your-secure-secret-key
POSTGRES_PASSWORD=your-db-password
```

## 🏗️ Architecture

### Tech Stack
- **Backend**: FastAPI (Python) + Poetry for dependency management
- **Frontend**: React + Vite + TypeScript + Tailwind CSS
- **Data Processing**: pandas + SQLite for CSV file handling
- **LLM Integration**: Google Gemini API for natural language queries
- **Authentication**: Google OAuth with JWT cookies (optional)
- **Development**: Docker Compose for local development

### File Processing Pipeline
```
CSV Upload → Schema Detection → SQLite Conversion → Query Interface
     ↓              ↓                   ↓               ↓
File validation  Column types    In-memory DB    Natural language
Size limits      Data preview    Fast queries    SQL generation
Error handling   User confirm    Session scope   Results display
```

## 🧪 Testing & Development

### Pre-commit Quality Checks
Our pre-commit hooks run the same checks as CI for immediate feedback:
- **Ruff** - Fast Python linting and formatting
- **MyPy** - Type checking with strict mode
- **Pytest** - Full test suite with 85%+ coverage requirement
- **Security** - Basic vulnerability scanning

```bash
# Setup development environment
./scripts/setup-dev.sh

# All commits now run full CI checks locally
# (30-60 seconds per commit, but zero CI failures)
```

### Test Coverage
- **Backend**: 91%+ coverage with comprehensive unit and integration tests
- **Frontend**: Component tests with vitest + E2E tests with cypress
- **File Processing**: Edge cases for various CSV formats and encodings
- **LLM Integration**: Mocked Gemini responses for reliable testing

## 📋 Development Status

### Implementation Progress
**See `docs/planning/PROJECT_STATUS.md` for detailed status and next steps**

Key files for developers and AI assistants:
- `docs/planning/PROJECT_STATUS.md` - Current status and ready-to-execute prompts
- `docs/planning/spec_v2.md` - Complete feature requirements and architecture
- `DEVELOPMENT.md` - Developer setup and troubleshooting guide
- `CLAUDE.md` - Project context for AI code assistants

### Current Priority: CSV Upload MVP
The next major milestone is implementing CSV file upload capability that allows users to:
1. Upload CSV files without requiring database credentials
2. Preview and validate detected schema
3. Query uploaded data using natural language via chat
4. Export results and manage session data

This creates a complete, demo-ready application that works entirely with user-provided files.

## 🤖 AI-Assisted Development Notes

This project is designed for seamless AI-assisted development:

### Why Comprehensive Pre-commit Hooks?
AI assistants can't directly access CI logs. When CI fails, humans must manually copy error messages back to the AI, creating a frustrating debugging loop. Our solution:

- **Immediate feedback** - AI gets errors instantly, not after CI failure
- **Same environment** - What passes locally passes in CI
- **Faster iteration** - Fix issues in the same conversation
- **No context switching** - AI can resolve issues without human intervention

### AI Assistant Friendly Features
- **Clear documentation** - Comprehensive planning docs in `docs/planning/`
- **Ready-to-execute prompts** - Specific implementation tasks in PROJECT_STATUS.md
- **Modular architecture** - Clean separation of concerns for focused changes
- **Comprehensive tests** - Confidence that changes don't break existing functionality

This approach transforms AI assistants from helpful but sometimes frustrating to genuinely reliable development partners.

---

*Transform your CSV data into insights through natural language conversation. No database setup required - just upload and start asking questions!*
