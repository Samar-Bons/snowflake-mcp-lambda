# snowflake-mcp-lambda
A remote MCP Server for Snowflake. Deployed as a AWS Lambda Function

## 📊 Project Status

**Current Phase: Ready for P4 - Frontend MVP**

### ✅ Completed
- **P0 - Foundation**: Git repo, pre-commit hooks, CI pipeline, Docker setup
- **P1 - Backend Core**: FastAPI app, config management, database foundations, health endpoints
- **P2 - Auth & Sessions**: Complete Google OAuth integration with user management
  - User SQLAlchemy model with preferences
  - JWT-based session management
  - Auth endpoints (login, callback, logout, profile, preferences)
  - 103 tests with 89.73% coverage
- **P3 - LLM + Query Pipeline**: Complete Gemini integration and Snowflake schema discovery
  - Gemini API service with BYOK model and prompt engineering
  - Snowflake schema service with read-only query execution
  - Chat endpoints for NL→SQL conversion with autorun support
  - SQL validation and injection prevention
  - 55 tests with 95%+ coverage for new components

### 🎯 Next Up
- **P4 - Frontend MVP**: React app, chat interface, schema explorer
- **P5 - History & Settings**: Query history, favorites, user preferences
- **P6 - Ops & Observability**: Logging, monitoring, production deployment

## 🚀 Quick Start with Docker (RECOMMENDED)

**For the fastest development experience:**

```bash
# 1. Clone and setup environment
git clone <your-repo-url>
cd snowflake-mcp-lambda
make setup  # Copies .env.example to .env with security reminders

# 2. IMPORTANT: Edit .env with secure values (see Configuration section below)
# Required: POSTGRES_PASSWORD, JWT_SECRET_KEY, GOOGLE_CLIENT_ID,
#          GOOGLE_CLIENT_SECRET, GEMINI_API_KEY

# 3. Start everything with one command
make dev-setup
# This builds containers, starts services, and runs migrations

# 4. Access the application
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

**Common development commands:**
```bash
make help           # Show all available commands
make up             # Start services
make down           # Stop services
make logs           # View all logs
make test           # Run backend tests
make health         # Check service health
make clean          # Clean up project containers/volumes only
```

**Performance Features:**
- **Fast builds**: `.dockerignore` files exclude unnecessary files
- **Layer caching**: Optimized Dockerfile layer ordering
- **Hot reload**: Both backend and frontend auto-reload on changes
- **Scoped cleanup**: Safe cleanup commands that preserve other projects
- **Volume optimization**: Anonymous volumes preserve dependencies (`.venv`, `node_modules`)

## 🚀 Alternative: Manual Developer Setup

**IMPORTANT**: Our pre-commit hooks exactly mirror CI. This means longer commit times but zero CI failures.

```bash
# One-time setup (takes ~2 minutes)
./scripts/setup-dev.sh

# That's it! All commits will now run the same checks as CI:
# - Ruff linting & formatting
# - MyPy type checking
# - Full pytest suite with 85% coverage requirement
# - Security scanning
```

### Why Full CI Parity in Pre-commit?

1. **No CI Debugging**: Fix issues locally, not through CI logs
2. **Resource Efficiency**: Don't waste CI minutes on preventable failures
3. **Guaranteed Success**: If it commits locally, it passes CI
4. **Better DX**: Immediate feedback, no context switching

Yes, commits take 30-60 seconds. But that's better than 5-10 minute CI debug cycles.

## ⚙️ Configuration

### Required API Keys

Before running the application, you need to obtain these API keys:

#### 1. Google OAuth (for user authentication)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Create OAuth 2.0 Client ID credentials
5. Add authorized redirect URI: `http://localhost:8000/api/v1/auth/callback`
6. Copy Client ID and Client Secret to your `.env` file

#### 2. Gemini API (for LLM functionality)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

#### 3. Snowflake Connection (configured via UI)
- Users can configure their Snowflake connections through the web interface
- Or set default values in `.env` for development/testing

### Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
# Required for authentication
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Required for LLM functionality
GEMINI_API_KEY=your-gemini-api-key

# Generate a secure JWT secret
JWT_SECRET_KEY=your-secure-secret-key

# Optional: Default Snowflake connection
SNOWFLAKE_ACCOUNT=your-account
SNOWFLAKE_USER=your-username
# ... etc
```

### 🤖 Why This Matters for AI Code Assistants

When working with AI code assistants (like Claude), comprehensive pre-commit hooks are **essential**:

#### The Problem
AI assistants can't directly see CI outputs. When CI fails, the human developer must:
1. Navigate to CI logs
2. Copy error messages
3. Paste them back to the AI
4. Wait for a fix
5. Push again
6. Repeat until green ✅

This creates a frustrating **human-in-the-middle** debugging loop that wastes everyone's time.

#### The Solution
With full CI parity in pre-commit hooks:
- AI assistants get **immediate feedback** on their code
- Errors are caught **before** pushing
- The AI can fix issues **in the same conversation**
- No context switching or copy-pasting required

#### Best Practices for AI-Assisted Development
1. **Make pre-commit hooks comprehensive** - Include all CI checks
2. **Fail fast, fail locally** - Better to wait 60 seconds than debug through logs
3. **Clear error messages** - AI assistants can parse and fix clear errors
4. **No surprises** - What passes locally MUST pass in CI

This approach transforms AI code assistants from "helpful but sometimes frustrating" to "genuinely reliable development partners."
