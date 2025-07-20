# Snowflake MCP Lambda - Implementation Plan

## Project Overview
A web application with chat interface allowing non-technical users to interact with Snowflake databases using natural language queries via Gemini LLM.

## Implementation Strategy
- **Approach**: Test-Driven Development (TDD) with incremental, iterative phases
- **Risk Management**: Each phase builds safely on previous work
- **Integration**: No orphaned code - everything connects to existing foundation
- **Quality**: 85%+ test coverage, pre-commit hooks, pristine test output

---

## Phase 0: Foundation & Setup ✅ COMPLETED
**Duration**: 1-2 days
**Goal**: Establish solid development foundation

### 0.1: Repository Setup & Standards ✅ COMPLETED
- ✅ Initialize git repository with proper structure
- ✅ Set up pre-commit hooks (ruff, mypy, pytest)
- ✅ Create GitHub Actions CI pipeline
- ✅ Establish code standards and file headers

### 0.2: Project Structure & Dependencies ✅ COMPLETED
- ✅ Create backend folder structure per spec
- ✅ Initialize Poetry with core dependencies
- ✅ Set up pytest with coverage configuration
- ✅ Create basic Docker Compose setup

---

## Phase 1: Backend Core Infrastructure ✅ COMPLETED
**Duration**: 2-3 days
**Goal**: FastAPI foundation with health checks and configuration

### 1.1: FastAPI Application Skeleton ✅ COMPLETED
- ✅ Create FastAPI app with health endpoint
- ✅ Implement structured logging with structlog
- ✅ Add environment-based configuration with Pydantic
- ✅ Basic error handling middleware

### 1.2: Configuration Management ✅ COMPLETED
- ✅ Environment variable loading (.env files)
- ✅ Configuration validation and type safety
- ✅ Separate dev/prod configurations
- ✅ Secret management patterns

### 1.3: Database Foundations ✅ COMPLETED
- ✅ PostgreSQL connection setup with SQLAlchemy
- ❌ Redis connection setup for sessions (JWT used instead)
- ✅ Basic database models for users
- ✅ Connection health checks

---

## Phase 2: Authentication System ✅ COMPLETED
**Duration**: 3-4 days
**Goal**: Complete Google OAuth flow with session management

### 2.1: Google OAuth Integration ✅ COMPLETED
- ✅ OAuth flow implementation
- ✅ Callback handling and token validation
- ✅ User profile extraction
- ✅ Error handling for auth failures

### 2.2: Session Management ✅ COMPLETED
- ✅ JWT token generation and validation (Cookie-based instead of Redis)
- ✅ Session middleware for protected routes
- ✅ 24-hour session expiry

### 2.3: User Management ✅ COMPLETED
- ✅ User model and database operations
- ✅ User registration on first login
- ✅ Profile management endpoints
- ✅ Authentication required decorators

---

## Phase 3: Snowflake Integration ✅ COMPLETED
**Duration**: 3-4 days
**Goal**: Secure Snowflake connectivity with schema caching

### 3.1: Snowflake Client ✅ COMPLETED
- ✅ Snowflake connector setup
- ✅ Connection validation and testing
- ✅ Error handling for connection failures
- ✅ AES-256 encrypted parameter storage

### 3.2: Schema Discovery & Caching ✅ COMPLETED
- ✅ Table and column metadata extraction
- ✅ Schema context building for LLM
- ✅ Performance optimization for large schemas

### 3.3: Query Execution Engine ✅ COMPLETED
- ✅ Read-only query validation
- ✅ SQL execution with row limits (500 default)
- ✅ Result formatting and pagination
- ✅ Query timeout and error handling

---

## Phase 4: LLM Pipeline (Gemini Integration) ✅ COMPLETED
**Duration**: 4-5 days
**Goal**: Natural language to SQL conversion with safety checks

### 4.1: Gemini Service Integration ✅ COMPLETED
- ✅ Gemini API client setup
- ✅ API key management (BYOK)
- ✅ Prompt template system
- ✅ Response parsing and validation

### 4.2: Context Building System ✅ COMPLETED
- ✅ Schema context injection
- ✅ User prompt analysis and enhancement
- ✅ Intent classification for safety
- ✅ Context size optimization

### 4.3: Chat Endpoint Implementation ✅ COMPLETED
- ✅ `/chat` endpoint with full pipeline
- ✅ Natural language → SQL generation
- ✅ SQL confirmation before execution
- ✅ Results formatting (table/NL/both)
- ❌ Query history storage (NOT IMPLEMENTED)

---

## Phase 5: Frontend Foundation 🟡 PARTIALLY STARTED
**Duration**: 4-5 days
**Goal**: React app with authentication and basic chat UI

### 5.1: React Application Setup 🟡 BASIC SETUP ONLY
- ✅ Vite + React + TypeScript setup
- ✅ Tailwind CSS with dark mode
- ✅ Frontend build and dev server
- ❌ Basic routing setup (MISSING)

### 5.2: Authentication Flow ❌ NOT STARTED
- ❌ Google OAuth frontend integration
- ❌ Login/logout UI components
- ❌ Protected route handling
- ❌ User session management

### 5.3: Basic Chat Interface ❌ NOT STARTED
- ❌ Chat UI components (ChatGPT-like)
- ❌ Message history display
- ❌ Input handling and validation
- ❌ Loading states and error handling

---

## Phase 6: Advanced Frontend Features ❌ NOT STARTED
**Duration**: 5-6 days
**Goal**: Complete user experience with all spec features

### 6.1: Schema Explorer Sidebar ❌ NOT STARTED
- ❌ Collapsible schema browser
- ❌ Table/column navigation
- ❌ Search and filtering
- ❌ Integration with chat autocomplete

### 6.2: Results Display System ❌ NOT STARTED
- ❌ Tabular results with pagination
- ❌ Column sorting and filtering
- ❌ Export functionality (CSV/JSON)
- ❌ Row limit controls and warnings

### 6.3: Query Management ❌ NOT STARTED
- ❌ Query history UI
- ❌ Favorites system
- ❌ Query renaming and organization
- ❌ Search and filtering of history

---

## Phase 7: Settings & Configuration ❌ NOT STARTED
**Duration**: 2-3 days
**Goal**: User configuration and preferences

### 7.1: Settings Panel ❌ NOT STARTED
- ❌ Snowflake connection management
- ❌ Auto-run toggle configuration
- ❌ Row limit preferences
- ❌ Schema refresh controls

### 7.2: User Preferences ❌ NOT STARTED
- ❌ Output format preferences
- ❌ UI customization options
- ❌ Session preference persistence
- ❌ Configuration validation

---

## Phase 8: Production Readiness ❌ NOT STARTED
**Duration**: 3-4 days
**Goal**: Production deployment and monitoring

### 8.1: Docker & Deployment ❌ NOT STARTED
- ❌ Production Docker Compose setup
- ❌ Environment configuration
- ❌ Health checks and monitoring
- ❌ Performance optimization

### 8.2: Logging & Monitoring 🟡 BASIC STRUCTLOG ONLY
- ✅ Structured logging throughout
- ❌ External log service integration
- ❌ Error tracking and alerting
- ❌ Performance metrics

### 8.3: Security Hardening ❌ NOT STARTED
- ❌ Security headers and CORS
- ❌ Input validation and sanitization
- ❌ Rate limiting implementation
- ❌ Security audit and testing

---

## Phase 9: Testing & Quality Assurance 🟡 BACKEND TESTS ONLY
**Duration**: 2-3 days
**Goal**: Comprehensive testing and quality checks

### 9.1: Test Suite Completion 🟡 BACKEND ONLY
- ✅ Unit test coverage >85% (backend: 91%)
- ✅ Integration test scenarios (backend)
- ❌ End-to-end testing
- ❌ Performance testing

### 9.2: Quality Assurance 🟡 PARTIAL
- ✅ Code review and refactoring (backend)
- 🟡 Documentation completion (partial)
- ❌ Security testing
- ❌ User acceptance testing prep

---

## Implementation Prompts

Each phase below contains detailed prompts for LLM-assisted implementation:

### Phase 0.1 Prompt: Repository Setup & Standards

```
Create the foundation for a Snowflake MCP Lambda project with the following requirements:

1. Initialize git repository with proper .gitignore for Python/Node.js
2. Set up pre-commit hooks with:
   - black (Python formatting)
   - ruff (Python linting)
   - isort (import sorting)
   - mypy (type checking)
   - pytest (test runner)

3. Create .pre-commit-config.yaml with all hooks configured
4. Set up GitHub Actions workflow (.github/workflows/ci.yml) that:
   - Runs on push/PR to main
   - Installs dependencies with Poetry
   - Runs pre-commit hooks
   - Executes pytest with coverage >85%
   - Reports results

5. Create backend folder structure:
   ```
   backend/
   ├── app/
   │   ├── __init__.py
   │   ├── api/
   │   ├── models/
   │   ├── services/
   │   ├── db/
   │   ├── schemas/
   │   ├── core/
   │   ├── utils/
   │   └── tests/
   ```

6. Add proper file headers to all Python files:
   ```python
   # ABOUTME: [Brief description of file purpose]
   # ABOUTME: [Second line of description]
   ```

Requirements:
- Follow TDD principles
- All files must have headers
- No hanging or orphaned code
- Everything should integrate properly
```

### Phase 0.2 Prompt: Project Structure & Dependencies

```
Set up the core project dependencies and structure building on the previous foundation:

1. Initialize Poetry in backend/ with pyproject.toml including:
   - FastAPI
   - uvicorn[standard]
   - pydantic[email]
   - sqlalchemy
   - alembic
   - redis
   - snowflake-connector-python
   - google-auth
   - google-auth-oauthlib
   - structlog
   - pytest
   - pytest-cov
   - pytest-asyncio
   - httpx (for testing)

2. Create pytest.ini with:
   - Test discovery settings
   - Coverage configuration
   - Async test support
   - Minimum coverage threshold 85%

3. Set up basic Docker Compose (docker-compose.yml) with:
   - redis service
   - postgres service
   - Environment variable templates

4. Create .env.example with all required environment variables:
   - Database URLs
   - Redis URL
   - Google OAuth credentials
   - Gemini API settings
   - Snowflake connection params

5. Write your first test in backend/app/tests/test_main.py that:
   - Tests a simple health check endpoint
   - Follows TDD - write test first, then make it pass
   - Uses proper pytest patterns

Requirements:
- Start with failing tests
- Make minimal changes to pass tests
- All dependencies properly versioned
- Environment variables documented
```

### Phase 1.1 Prompt: FastAPI Application Skeleton

```
Create the FastAPI application foundation that builds on the Poetry setup:

1. Create backend/app/main.py with:
   - FastAPI app instance
   - CORS middleware configuration
   - Request logging middleware
   - Global exception handlers
   - Health check endpoint at /health

2. Create backend/app/core/config.py with:
   - Pydantic Settings class
   - Environment variable loading
   - Database URL configuration
   - Redis URL configuration
   - Logging level configuration

3. Create backend/app/core/logging.py with:
   - structlog configuration
   - JSON logging for production
   - Console logging for development
   - Request ID tracking

4. Create backend/app/api/__init__.py and backend/app/api/health.py with:
   - Health check router
   - Database connectivity check
   - Redis connectivity check
   - System status reporting

5. Write comprehensive tests in backend/app/tests/:
   - test_health.py for health endpoints
   - test_config.py for configuration loading
   - test_main.py for app initialization

Requirements:
- Follow TDD - write tests first
- Health endpoint returns proper JSON
- Logging works in both dev/prod
- Configuration validates properly
- All tests pass with >85% coverage
```

### Phase 1.2 Prompt: Configuration Management

```
Expand the configuration system to handle all project requirements:

1. Enhance backend/app/core/config.py with:
   - Separate development/production settings classes
   - Google OAuth configuration
   - Snowflake connection settings
   - Gemini API configuration
   - JWT secret and expiry settings
   - Rate limiting configuration

2. Create backend/app/core/security.py with:
   - JWT token creation/validation functions
   - Password hashing utilities (for future use)
   - OAuth token validation
   - Security helper functions

3. Create environment files:
   - .env.development
   - .env.production
   - Update .env.example with all new variables

4. Add configuration validation:
   - Required fields validation
   - URL format validation
   - Numeric range validation
   - Environment-specific defaults

5. Write tests for all configuration scenarios:
   - Valid configuration loading
   - Missing required variables
   - Invalid format handling
   - Environment switching

Requirements:
- Environment-based configuration switching
- Proper validation with clear error messages
- Security settings properly configured
- All configuration testable
- No secrets in code
```

### Phase 1.3 Prompt: Database Foundations

```
Set up database connections and basic models building on the configuration system:

1. Create backend/app/db/database.py with:
   - SQLAlchemy engine setup
   - Session factory configuration
   - Database URL from config
   - Connection pooling settings

2. Create backend/app/db/redis.py with:
   - Redis client setup
   - Connection validation
   - Session management utilities
   - Cache helper functions

3. Create backend/app/schemas/user.py with:
   - User SQLAlchemy model
   - Basic fields: id, email, name, created_at
   - Google OAuth fields: google_id, picture
   - Proper indexes and constraints

4. Create backend/app/db/base.py with:
   - Base model class
   - Common fields (id, created_at, updated_at)
   - Proper imports for all models

5. Set up Alembic for migrations:
   - Initialize alembic configuration
   - Create first migration for user table
   - Migration running utilities

6. Add database utilities in backend/app/db/session.py:
   - Session dependency for FastAPI
   - Transaction management
   - Error handling

7. Write comprehensive tests:
   - Database connection testing
   - Redis connection testing
   - Model creation and querying
   - Migration testing

Requirements:
- Use existing configuration system
- Proper error handling for connection failures
- All database operations tested
- Migrations work correctly
- Connection pooling configured
```

### Phase 2.1 Prompt: Google OAuth Integration

```
Implement Google OAuth authentication building on the database foundation:

1. Create backend/app/services/auth.py with:
   - Google OAuth client setup using config
   - Authorization URL generation
   - Token exchange handling
   - User profile fetching from Google
   - User creation/update logic

2. Create backend/app/api/auth.py with:
   - /auth/login endpoint (redirect to Google)
   - /auth/callback endpoint (handle OAuth callback)
   - /auth/logout endpoint
   - /auth/me endpoint (current user info)

3. Create backend/app/models/auth.py with:
   - Login request/response models
   - User profile models
   - OAuth callback models
   - Error response models

4. Enhance user schema in backend/app/schemas/user.py:
   - Add OAuth-specific fields
   - Add user status and roles
   - Update migration accordingly

5. Create backend/app/core/oauth.py with:
   - OAuth configuration setup
   - Scopes definition
   - Error handling utilities
   - State parameter management

6. Write comprehensive tests:
   - OAuth flow testing with mock Google API
   - User creation on first login
   - User update on subsequent logins
   - Error handling for OAuth failures
   - All endpoints tested

Requirements:
- Use existing database and config systems
- Proper error handling for all OAuth steps
- User data properly stored and updated
- All OAuth endpoints secured
- Tests cover success and failure scenarios
```

### Phase 2.2 Prompt: Session Management

```
Implement Redis-based session management building on the OAuth system:

1. Create backend/app/services/session.py with:
   - Session creation and storage in Redis
   - Session validation and retrieval
   - Session expiry handling (24 hours)
   - Session cleanup utilities
   - User session tracking

2. Create backend/app/core/jwt.py with:
   - JWT token creation with user claims
   - JWT token validation and decoding
   - Token refresh handling
   - Claims extraction utilities

3. Create backend/app/core/dependencies.py with:
   - get_current_user dependency
   - require_auth dependency
   - Optional auth dependency
   - Database session dependency

4. Create session middleware in backend/app/core/middleware.py:
   - Request session validation
   - User context injection
   - Session refresh handling
   - Error handling for expired sessions

5. Update auth endpoints to use sessions:
   - Store session on successful login
   - Clear session on logout
   - Return session info in responses
   - Handle session conflicts

6. Write comprehensive tests:
   - Session creation and retrieval
   - Session expiry testing
   - JWT token validation
   - Middleware functionality
   - Dependency injection testing

Requirements:
- Integrate with existing auth and Redis systems
- 24-hour session expiry enforced
- Proper session cleanup
- All dependencies properly tested
- Session security validated
```

### Phase 2.3 Prompt: User Management

```
Complete the user management system building on sessions and auth:

1. Create backend/app/api/users.py with:
   - GET /users/me (current user profile)
   - PUT /users/me (update profile)
   - DELETE /users/me (delete account)
   - All endpoints require authentication

2. Create backend/app/services/user.py with:
   - User CRUD operations
   - Profile update logic
   - Account deletion handling
   - User preference management

3. Create backend/app/models/user.py with:
   - User profile request/response models
   - User preferences models
   - User update validation models
   - User delete confirmation models

4. Enhance user schema with preferences:
   - Default output format preference
   - Auto-run query preference
   - Row limit preference
   - UI theme preference

5. Add user management utilities:
   - Profile validation
   - Preference serialization
   - Data export for account deletion
   - Audit logging for user actions

6. Write comprehensive tests:
   - All user endpoints
   - Profile update validation
   - Account deletion process
   - User preferences handling
   - Authentication requirement testing

Requirements:
- Use all existing auth and session systems
- Proper validation of user updates
- Secure account deletion process
- All user operations logged
- Complete test coverage
```

### Phase 3.1 Prompt: Snowflake Client

```
Create Snowflake connectivity building on the user management system:

1. Create backend/app/db/snowflake.py with:
   - Snowflake connector setup
   - Connection validation function
   - Connection pooling management
   - Error handling and retries
   - Connection testing utilities

2. Create backend/app/services/snowflake.py with:
   - Snowflake connection management per user
   - Connection validation service
   - Connection configuration storage
   - Connection health monitoring

3. Create backend/app/models/snowflake.py with:
   - Snowflake connection config models
   - Connection test request/response models
   - Connection status models
   - Error response models

4. Create backend/app/api/snowflake.py with:
   - POST /snowflake/test-connection
   - POST /snowflake/save-connection
   - GET /snowflake/connection-status
   - DELETE /snowflake/connection

5. Add Snowflake config to user schema:
   - Encrypted connection parameters
   - Connection validation status
   - Last connection test timestamp
   - Connection error tracking

6. Create connection validation utilities:
   - Parameter validation
   - Connection string building
   - Error message abstraction
   - Security validation

7. Write comprehensive tests:
   - Connection establishment
   - Connection validation
   - Error handling scenarios
   - Security parameter handling
   - All API endpoints

Requirements:
- Build on existing user and auth systems
- Secure storage of connection parameters
- Proper error handling and user feedback
- Connection parameters validated
- All operations require authentication
```

### Phase 3.2 Prompt: Schema Discovery & Caching

```
Implement schema discovery and caching building on Snowflake connectivity:

1. Create backend/app/services/schema.py with:
   - Schema discovery from Snowflake
   - Table and column metadata extraction
   - Schema caching in Redis
   - Cache invalidation and refresh
   - Performance optimization for large schemas

2. Create backend/app/models/schema.py with:
   - Database schema models
   - Table metadata models
   - Column information models
   - Schema refresh request/response models

3. Create backend/app/api/schema.py with:
   - GET /schema/tables (list all tables)
   - GET /schema/tables/{table}/columns (table columns)
   - POST /schema/refresh (refresh schema cache)
   - GET /schema/status (cache status)

4. Add schema caching utilities:
   - Redis key generation for schema data
   - Cache expiry management (1 hour default)
   - Incremental cache updates
   - Memory usage optimization

5. Create schema context builders:
   - Schema context for LLM prompts
   - Relevant table/column selection
   - Context size optimization
   - Search and filtering utilities

6. Update Snowflake service to include schema operations:
   - Schema discovery queries
   - Metadata extraction
   - Performance monitoring
   - Error handling

7. Write comprehensive tests:
   - Schema discovery functionality
   - Caching operations
   - Cache refresh and invalidation
   - Context building
   - Performance with large schemas

Requirements:
- Use existing Snowflake and Redis systems
- Efficient caching with proper expiry
- Schema context optimized for LLM
- Performance tested with large datasets
- All schema operations authenticated
```

### Phase 3.3 Prompt: Query Execution Engine

```
Build the query execution engine on top of schema and Snowflake systems:

1. Create backend/app/services/query.py with:
   - SQL query validation (read-only enforcement)
   - Query execution with row limits
   - Result formatting and pagination
   - Query timeout handling
   - Performance monitoring

2. Create backend/app/models/query.py with:
   - Query request models
   - Query result models
   - Pagination models
   - Query execution status models

3. Create backend/app/utils/sql_validator.py with:
   - Read-only SQL validation
   - Dangerous statement detection
   - Query complexity analysis
   - Parameter sanitization

4. Create backend/app/api/query.py with:
   - POST /query/execute (execute SQL)
   - POST /query/validate (validate SQL)
   - GET /query/{id}/results (paginated results)
   - GET /query/{id}/status (execution status)

5. Add query result formatting:
   - JSON serialization for complex types
   - Pagination utilities
   - Export format preparation
   - Data type handling

6. Create query history storage:
   - Query execution logging
   - Result caching (short-term)
   - Performance metrics
   - Error tracking

7. Write comprehensive tests:
   - Read-only validation
   - Query execution
   - Result pagination
   - Row limit enforcement
   - Error handling scenarios
   - Performance testing

Requirements:
- Build on Snowflake and schema systems
- Strict read-only enforcement
- 500 row limit (configurable)
- Proper pagination and formatting
- All query operations logged and authenticated
```

### Phase 4.1 Prompt: Gemini Service Integration

```
Create Gemini LLM integration building on the query execution foundation:

1. Create backend/app/services/llm.py with:
   - Gemini API client setup
   - API key management (BYOK from user)
   - Prompt template system
   - Response parsing and validation
   - Rate limiting and retry logic

2. Create backend/app/models/llm.py with:
   - LLM request/response models
   - Prompt template models
   - Generation configuration models
   - API error models

3. Create backend/app/utils/prompts.py with:
   - Base prompt templates
   - Schema context injection
   - User query enhancement
   - Response format specifications

4. Create backend/app/api/llm.py with:
   - POST /llm/generate-sql (NL to SQL)
   - POST /llm/explain-query (SQL explanation)
   - GET /llm/status (API status)
   - POST /llm/test-key (API key validation)

5. Add user API key management:
   - Encrypted API key storage
   - Key validation utilities
   - Usage tracking
   - Error handling for invalid keys

6. Create prompt engineering utilities:
   - Context size optimization
   - Template variable substitution
   - Response format enforcement
   - Error recovery prompts

7. Write comprehensive tests:
   - API key validation
   - Prompt generation
   - Response parsing
   - Error handling
   - Rate limiting
   - Template rendering

Requirements:
- User provides own Gemini API key
- Secure key storage and usage
- Robust error handling
- Prompt templates are maintainable
- All LLM operations authenticated and logged
```

### Phase 4.2 Prompt: Context Building System

```
Build the context system for LLM prompts using schema and user data:

1. Create backend/app/services/context.py with:
   - Schema context building from cached data
   - User query analysis and enhancement
   - Intent classification for safety
   - Context size optimization
   - Relevant table/column selection

2. Create backend/app/models/context.py with:
   - Context request models
   - Intent classification models
   - Schema context models
   - Safety validation models

3. Create backend/app/utils/intent.py with:
   - Intent classification utilities
   - Unsafe query detection
   - Query type identification
   - Confidence scoring

4. Create context optimization utilities:
   - Schema relevance scoring
   - Context truncation strategies
   - Token counting utilities
   - Priority-based selection

5. Add safety validation:
   - Data modification attempt detection
   - Sensitive information queries
   - Admin/system query detection
   - Rate limiting based on intent

6. Create context caching:
   - Frequently used context caching
   - User-specific context optimization
   - Context versioning
   - Performance monitoring

7. Write comprehensive tests:
   - Context building accuracy
   - Intent classification
   - Safety validation
   - Context optimization
   - Performance with large schemas
   - Edge cases and error handling

Requirements:
- Use existing schema and LLM systems
- Effective intent classification for safety
- Optimized context for better LLM results
- Performance tested with various schema sizes
- All context operations logged
```

### Phase 4.3 Prompt: Chat Endpoint Implementation

```
Create the main chat endpoint that integrates all previous systems:

1. Create backend/app/api/chat.py with:
   - POST /chat (main chat endpoint)
   - WebSocket /chat/ws (real-time chat)
   - GET /chat/history (chat history)
   - POST /chat/favorite (favorite queries)

2. Create backend/app/services/chat.py with:
   - Complete NL → SQL → execution pipeline
   - Query history management
   - Favorites system
   - Session-based chat context

3. Create backend/app/models/chat.py with:
   - Chat message models
   - Chat session models
   - Query history models
   - Favorite query models

4. Implement the full chat pipeline:
   - User message processing
   - Context building with schema
   - LLM query generation
   - SQL validation and confirmation
   - Query execution
   - Result formatting
   - History storage

5. Add chat session management:
   - Session context tracking
   - Multi-turn conversation support
   - Context memory optimization
   - Session cleanup

6. Create output formatting:
   - Table format with pagination
   - Natural language summaries
   - Combined output modes
   - Export format preparation

7. Write comprehensive tests:
   - End-to-end chat flow
   - Error handling at each step
   - Session management
   - History and favorites
   - Output formatting
   - WebSocket functionality

Requirements:
- Integrate all previous systems seamlessly
- Complete pipeline from NL to results
- Proper error handling and user feedback
- Session management for context
- All chat operations authenticated and logged
```

### Phase 5.1 Prompt: React Application Setup

```
Create the React frontend foundation that will connect to the FastAPI backend:

1. Initialize React project with Vite:
   - Set up Vite + React + TypeScript
   - Configure Tailwind CSS with dark mode
   - Set up ESLint and Prettier
   - Configure development and build scripts

2. Create frontend folder structure:
   ```
   frontend/
   ├── src/
   │   ├── components/
   │   ├── pages/
   │   ├── hooks/
   │   ├── services/
   │   ├── types/
   │   ├── utils/
   │   └── styles/
   ```

3. Set up Tailwind CSS configuration:
   - Dark mode configuration
   - Custom color palette
   - Typography and spacing
   - Component utilities

4. Create basic routing with React Router:
   - Login page route
   - Dashboard route
   - Settings route
   - Protected route wrapper

5. Set up API client utilities:
   - Axios configuration
   - Request/response interceptors
   - Error handling
   - Authentication headers

6. Create basic TypeScript types:
   - User types matching backend
   - API response types
   - Component prop types
   - Configuration types

7. Write initial tests:
   - Component rendering tests
   - API client tests
   - Routing tests
   - Utility function tests

Requirements:
- Modern React setup with TypeScript
- Dark mode only (as per spec)
- Proper project structure
- API client ready for backend integration
- All components tested
```

### Phase 5.2 Prompt: Authentication Flow

```
Implement the frontend authentication system connecting to the backend OAuth:

1. Create authentication service in src/services/auth.ts:
   - Login redirect to backend OAuth
   - Token management in localStorage
   - User session validation
   - Logout functionality

2. Create authentication context:
   - User state management
   - Authentication status
   - Login/logout actions
   - Session persistence

3. Create authentication components:
   - Login page component
   - Login button component
   - User profile dropdown
   - Authentication status indicators

4. Create protected route wrapper:
   - Route protection logic
   - Redirect to login
   - Loading states
   - Error handling

5. Implement session management:
   - Token refresh handling
   - Session expiry detection
   - Automatic logout
   - Cross-tab synchronization

6. Create authentication hooks:
   - useAuth hook
   - useAuthRedirect hook
   - useSession hook
   - useUser hook

7. Write comprehensive tests:
   - Authentication flow testing
   - Protected route behavior
   - Session management
   - Component interactions
   - Hook functionality

Requirements:
- Connect to existing backend OAuth system
- Secure token management
- Smooth user experience
- Proper loading and error states
- All authentication functionality tested
```

### Phase 5.3 Prompt: Basic Chat Interface

```
Create the chat interface building on the authentication system:

1. Create chat components in src/components/chat/:
   - ChatContainer (main chat layout)
   - MessageList (scrollable message history)
   - MessageItem (individual message display)
   - ChatInput (message input with controls)

2. Create chat service in src/services/chat.ts:
   - Send message to backend
   - Receive and format responses
   - Handle streaming responses
   - Error handling and retries

3. Create chat state management:
   - Message history state
   - Loading states
   - Error states
   - Input validation

4. Implement message types:
   - User messages
   - System messages
   - SQL confirmation messages
   - Result display messages
   - Error messages

5. Add chat functionality:
   - Message sending
   - Real-time response display
   - Message history scrolling
   - Auto-scroll to bottom

6. Create chat hooks:
   - useChat hook
   - useMessages hook
   - useChatInput hook
   - useChatScroll hook

7. Write comprehensive tests:
   - Chat component rendering
   - Message sending/receiving
   - State management
   - User interactions
   - Error handling

Requirements:
- ChatGPT-like interface as specified
- Connect to backend chat endpoint
- Proper message handling and display
- Smooth user experience
- All chat functionality tested
```

### Phase 6.1 Prompt: Schema Explorer Sidebar

```
Create the schema explorer sidebar building on the chat interface:

1. Create schema components in src/components/schema/:
   - SchemaExplorer (main sidebar container)
   - DatabaseTree (hierarchical database view)
   - TableList (expandable table list)
   - ColumnDetails (column information display)

2. Create schema service in src/services/schema.ts:
   - Fetch schema data from backend
   - Cache schema information
   - Handle schema refresh
   - Search and filter functionality

3. Implement schema navigation:
   - Collapsible sidebar toggle
   - Expandable table nodes
   - Column detail expansion
   - Search within schema

4. Add schema integration with chat:
   - Table/column name insertion
   - Autocomplete suggestions
   - Context-aware suggestions
   - Click-to-insert functionality

5. Create schema state management:
   - Schema data caching
   - Loading states
   - Search state
   - Expansion state

6. Add schema utilities:
   - Data type formatting
   - Search highlighting
   - Fuzzy search matching
   - Performance optimization

7. Write comprehensive tests:
   - Schema component rendering
   - Navigation functionality
   - Search and filtering
   - Chat integration
   - Performance testing

Requirements:
- Collapsible and unobtrusive as specified
- Connect to backend schema endpoints
- Smooth integration with chat autocomplete
- Efficient handling of large schemas
- All schema functionality tested
```

### Phase 6.2 Prompt: Results Display System

```
Create the results display system building on chat and schema components:

1. Create result components in src/components/results/:
   - ResultsTable (main table display)
   - TablePagination (pagination controls)
   - ColumnSorting (sortable column headers)
   - TableFilters (column filtering)
   - ExportControls (CSV/JSON export)

2. Create results service in src/services/results.ts:
   - Fetch paginated results
   - Handle sorting requests
   - Manage filtering state
   - Export functionality

3. Implement table functionality:
   - Column sorting (ascending/descending)
   - Value and range filtering
   - Pagination with page size control
   - Row selection capabilities

4. Add export functionality:
   - CSV export with proper formatting
   - JSON export with structure
   - Export current view vs all data
   - Download handling

5. Create result state management:
   - Table data state
   - Pagination state
   - Sorting state
   - Filter state

6. Add row limit handling:
   - 500 row limit display
   - Warning notices
   - Adjustable limit controls
   - Performance optimization

7. Write comprehensive tests:
   - Table rendering and functionality
   - Pagination behavior
   - Sorting and filtering
   - Export functionality
   - Performance with large datasets

Requirements:
- Full table functionality as specified
- Connect to backend query results
- Efficient handling of large result sets
- Export functionality working correctly
- All results features tested
```

### Phase 6.3 Prompt: Query Management

```
Create query history and management system building on results display:

1. Create query management components in src/components/queries/:
   - QueryHistory (history display)
   - QueryItem (individual query display)
   - FavoritesList (favorites management)
   - QuerySearch (search and filter)

2. Create query service in src/services/queries.ts:
   - Fetch query history
   - Manage favorites
   - Query search and filtering
   - Query organization

3. Implement query history features:
   - Chronological query display
   - Query details expansion
   - Re-run query functionality
   - Query deletion

4. Add favorites system:
   - Add/remove favorites
   - Favorite query organization
   - Quick access to favorites
   - Favorite query editing

5. Create query management state:
   - History pagination
   - Search state
   - Favorites state
   - Selection state

6. Add query utilities:
   - Query naming and renaming
   - Query organization
   - Search highlighting
   - Performance optimization

7. Write comprehensive tests:
   - History display functionality
   - Favorites management
   - Search and filtering
   - Query operations
   - State management

Requirements:
- Connect to backend query history endpoints
- Full CRUD operations for favorites
- Efficient search and filtering
- Query organization capabilities
- All query management tested
```

### Phase 7.1 Prompt: Settings Panel

```
Create the settings panel building on all previous frontend components:

1. Create settings components in src/components/settings/:
   - SettingsPanel (main settings container)
   - ConnectionSettings (Snowflake configuration)
   - PreferencesSettings (user preferences)
   - AccountSettings (user account management)

2. Create settings service in src/services/settings.ts:
   - Fetch/update user settings
   - Manage Snowflake connection
   - Handle preference changes
   - Connection testing

3. Implement connection management:
   - Snowflake connection form
   - Connection testing functionality
   - Connection status display
   - Secure credential handling

4. Add user preferences:
   - Auto-run toggle
   - Default output format
   - Row limit settings
   - UI preferences

5. Create settings state management:
   - Settings form state
   - Validation state
   - Save status
   - Error handling

6. Add settings validation:
   - Connection parameter validation
   - Form validation
   - Real-time feedback
   - Error display

7. Write comprehensive tests:
   - Settings form functionality
   - Connection testing
   - Preference management
   - Validation behavior
   - State management

Requirements:
- Connect to backend settings endpoints
- Secure handling of connection credentials
- Real-time validation and feedback
- All settings functionality working
- Complete test coverage
```

### Phase 7.2 Prompt: User Preferences

```
Complete the user preference system building on settings foundation:

1. Enhance preference management:
   - Output format preferences
   - UI customization options
   - Behavior preferences
   - Performance settings

2. Create preference persistence:
   - Local storage for UI preferences
   - Backend persistence for important settings
   - Cross-device synchronization
   - Default value handling

3. Implement preference application:
   - Dynamic preference loading
   - Real-time preference updates
   - Preference validation
   - Migration handling

4. Add advanced preferences:
   - Query timeout settings
   - Cache duration preferences
   - Export format defaults
   - Notification preferences

5. Create preference hooks:
   - usePreferences hook
   - usePreference hook (individual)
   - usePreferenceUpdate hook
   - usePreferenceReset hook

6. Add preference utilities:
   - Preference validation
   - Default value resolution
   - Preference migration
   - Performance optimization

7. Write comprehensive tests:
   - Preference loading and saving
   - Real-time updates
   - Validation behavior
   - Migration functionality
   - Hook behavior

Requirements:
- Seamless preference management
- Real-time application of changes
- Proper validation and defaults
- Cross-session persistence
- All preference functionality tested
```

### Phase 8.1 Prompt: Docker & Deployment

```
Create production deployment setup building on the complete application:

1. Create production Docker setup:
   - Multi-stage Dockerfile for backend
   - Optimized Node.js Dockerfile for frontend
   - Docker Compose production configuration
   - Environment variable management

2. Create docker-compose.prod.yml:
   - Production service definitions
   - Proper networking configuration
   - Volume management
   - Health checks

3. Add deployment utilities:
   - Build scripts
   - Deployment scripts
   - Environment validation
   - Service orchestration

4. Create production configuration:
   - Production environment variables
   - Security headers configuration
   - CORS production settings
   - Performance optimizations

5. Add monitoring setup:
   - Health check endpoints
   - Metrics collection
   - Log aggregation
   - Performance monitoring

6. Create deployment documentation:
   - Deployment guide
   - Environment setup
   - Troubleshooting guide
   - Maintenance procedures

7. Write deployment tests:
   - Container build testing
   - Service connectivity testing
   - Health check validation
   - Performance benchmarks

Requirements:
- Production-ready Docker setup
- Proper security configuration
- Monitoring and health checks
- Complete deployment documentation
- All deployment components tested
```

### Phase 8.2 Prompt: Logging & Monitoring

```
Implement comprehensive logging and monitoring building on the deployment setup:

1. Enhance backend logging:
   - Request/response logging
   - Error tracking and alerting
   - Performance metrics
   - Security event logging

2. Add frontend monitoring:
   - Error boundary implementation
   - Performance monitoring
   - User interaction tracking
   - API call monitoring

3. Create log aggregation:
   - Structured log formatting
   - External log service integration
   - Log filtering and searching
   - Retention policies

4. Implement metrics collection:
   - Application metrics
   - Database metrics
   - Cache metrics
   - System metrics

5. Add alerting system:
   - Error rate alerts
   - Performance alerts
   - Security alerts
   - System health alerts

6. Create monitoring dashboards:
   - Application performance dashboard
   - User activity dashboard
   - System health dashboard
   - Error tracking dashboard

7. Write monitoring tests:
   - Log generation testing
   - Metric collection testing
   - Alert functionality testing
   - Dashboard functionality testing

Requirements:
- Comprehensive logging throughout application
- External monitoring service integration
- Effective alerting system
- Useful monitoring dashboards
- All monitoring functionality tested
```

### Phase 8.3 Prompt: Security Hardening

```
Implement security hardening building on logging and monitoring:

1. Add security headers:
   - Content Security Policy
   - HSTS implementation
   - X-Frame-Options
   - Security header middleware

2. Implement rate limiting:
   - API endpoint rate limiting
   - User-based rate limiting
   - IP-based rate limiting
   - Adaptive rate limiting

3. Add input validation and sanitization:
   - SQL injection prevention
   - XSS protection
   - Input validation middleware
   - Output encoding

4. Enhance authentication security:
   - Session security hardening
   - CSRF protection
   - Secure cookie configuration
   - Token security improvements

5. Add security monitoring:
   - Security event logging
   - Intrusion detection
   - Anomaly detection
   - Security alerts

6. Create security utilities:
   - Security testing tools
   - Vulnerability scanning
   - Security configuration validation
   - Incident response procedures

7. Write security tests:
   - Security header testing
   - Rate limiting testing
   - Input validation testing
   - Authentication security testing

Requirements:
- Comprehensive security measures
- Protection against common vulnerabilities
- Security monitoring and alerting
- Regular security testing
- All security features validated
```

### Phase 9.1 Prompt: Test Suite Completion

```
Complete the comprehensive test suite for the entire application:

1. Ensure unit test coverage >85%:
   - All service methods tested
   - All utility functions tested
   - All component methods tested
   - Edge cases covered

2. Create integration test scenarios:
   - End-to-end user flows
   - API integration testing
   - Database integration testing
   - External service integration

3. Add performance testing:
   - Load testing for APIs
   - Frontend performance testing
   - Database query performance
   - Cache performance testing

4. Create end-to-end tests:
   - Complete user workflow testing
   - Cross-browser testing
   - Mobile responsiveness testing
   - Accessibility testing

5. Add test automation:
   - Automated test execution
   - Test reporting
   - Coverage reporting
   - Performance benchmarking

6. Create test utilities:
   - Test data generation
   - Mock service setup
   - Test environment management
   - Test cleanup utilities

7. Write test documentation:
   - Testing guidelines
   - Test execution procedures
   - Test maintenance guide
   - Coverage requirements

Requirements:
- Minimum 85% test coverage
- All critical paths tested
- Performance requirements validated
- Test automation working
- Complete test documentation
```

### Phase 9.2 Prompt: Quality Assurance

```
Final quality assurance and project completion:

1. Code review and refactoring:
   - Code quality assessment
   - Performance optimization
   - Security review
   - Documentation review

2. User acceptance testing preparation:
   - Test scenario creation
   - User guide creation
   - Demo environment setup
   - Feedback collection system

3. Final documentation:
   - API documentation completion
   - User manual creation
   - Deployment guide finalization
   - Maintenance procedures

4. Performance optimization:
   - Frontend bundle optimization
   - Backend performance tuning
   - Database query optimization
   - Cache optimization

5. Security audit:
   - Security testing completion
   - Vulnerability assessment
   - Penetration testing
   - Security documentation

6. Project finalization:
   - Feature completeness verification
   - Bug fixing and stabilization
   - Final testing round
   - Release preparation

7. Handover preparation:
   - Knowledge transfer documentation
   - Support procedures
   - Monitoring setup verification
   - Maintenance schedule

Requirements:
- All features working as specified
- Production-ready quality
- Complete documentation
- Security validated
- Ready for user acceptance testing
```

---

## GitHub Issues

### Phase 0 Issues

**Issue #1: Repository Foundation & CI Setup**
- Set up git repository with proper structure
- Configure pre-commit hooks (black, ruff, isort, mypy)
- Create GitHub Actions CI pipeline
- Establish code standards and file headers
- Initialize backend folder structure

**Issue #2: Project Dependencies & Structure**
- Initialize Poetry with core dependencies
- Set up pytest with coverage configuration
- Create basic Docker Compose setup
- Create environment variable templates
- Write first health check test

### Phase 1 Issues

**Issue #3: FastAPI Application Foundation**
- Create FastAPI app with health endpoint
- Implement structured logging with structlog
- Add environment-based configuration
- Basic error handling middleware
- Health check with system status

**Issue #4: Configuration Management System**
- Environment-based configuration switching
- Google OAuth and Snowflake configuration
- JWT and security settings
- Configuration validation
- Environment file templates

**Issue #5: Database Foundations**
- SQLAlchemy setup with connection pooling
- Redis client setup with utilities
- User model and Alembic migrations
- Database session management
- Connection health checks

### Phase 2 Issues

**Issue #6: Google OAuth Integration**
- OAuth client setup and flow implementation
- Authorization URL generation and token exchange
- User profile fetching and storage
- OAuth error handling
- User creation/update logic

**Issue #7: Session Management System**
- Redis-based session storage with expiry
- JWT token creation and validation
- Session middleware for requests
- Authentication dependencies
- Session cleanup utilities

**Issue #8: User Management API**
- User profile endpoints (CRUD)
- User preferences management
- Account deletion handling
- Profile update validation
- User operation logging

### Phase 3 Issues

**Issue #9: Snowflake Client Integration**
- Snowflake connector setup and validation
- Connection management per user
- Secure parameter storage
- Connection testing API endpoints
- Error handling and abstraction

**Issue #10: Schema Discovery & Caching**
- Schema metadata extraction from Snowflake
- Redis-based schema caching system
- Schema refresh functionality
- Context building for LLM prompts
- Performance optimization for large schemas

**Issue #11: Query Execution Engine**
- Read-only SQL validation
- Query execution with row limits
- Result formatting and pagination
- Query history storage
- Query timeout and error handling

### Phase 4 Issues

**Issue #12: Gemini LLM Integration**
- Gemini API client setup
- User API key management (BYOK)
- Prompt template system
- Response parsing and validation
- Rate limiting and error handling

**Issue #13: Context Building System**
- Schema context injection for prompts
- Intent classification for safety
- Context size optimization
- Relevant table/column selection
- Safety validation utilities

**Issue #14: Chat API Implementation**
- Complete NL → SQL → execution pipeline
- Chat history and favorites management
- WebSocket support for real-time chat
- Session-based chat context
- Output formatting (table/NL/both)

### Phase 5 Issues

**Issue #15: React Application Setup**
- Vite + React + TypeScript setup
- Tailwind CSS with dark mode
- Basic routing with React Router
- API client utilities setup
- TypeScript types and basic tests

**Issue #16: Frontend Authentication Flow**
- Authentication service and context
- Login/logout components
- Protected route wrapper
- Session management
- Authentication hooks

**Issue #17: Chat Interface Components**
- Chat container and message components
- Chat input with controls
- Message history display
- Real-time response handling
- Chat state management

### Phase 6 Issues

**Issue #18: Schema Explorer Sidebar**
- Collapsible schema browser
- Hierarchical database/table/column view
- Search and filtering functionality
- Integration with chat autocomplete
- Performance optimization

**Issue #19: Results Display System**
- Table with pagination and sorting
- Column filtering (value/range)
- Export functionality (CSV/JSON)
- Row limit handling and warnings
- Performance optimization for large datasets

**Issue #20: Query History & Management**
- Query history display and management
- Favorites system with CRUD operations
- Query search and filtering
- Query renaming and organization
- Quick access and re-run functionality

### Phase 7 Issues

**Issue #21: Settings Panel Implementation**
- Snowflake connection management UI
- User preferences configuration
- Real-time validation and feedback
- Settings persistence
- Connection testing interface

**Issue #22: User Preferences System**
- Output format and behavior preferences
- Local and backend preference persistence
- Cross-device synchronization
- Preference validation and migration
- Advanced preference options

### Phase 8 Issues

**Issue #23: Production Docker Setup**
- Multi-stage Dockerfiles for backend/frontend
- Production Docker Compose configuration
- Environment variable management
- Health checks and monitoring
- Deployment scripts and documentation

**Issue #24: Logging & Monitoring Implementation**
- Structured logging throughout application
- External log service integration
- Metrics collection and dashboards
- Alerting system setup
- Performance monitoring

**Issue #25: Security Hardening**
- Security headers and CORS configuration
- Rate limiting implementation
- Input validation and sanitization
- Authentication security hardening
- Security monitoring and testing

### Phase 9 Issues

**Issue #26: Comprehensive Testing**
- Unit test coverage >85%
- Integration and end-to-end testing
- Performance and load testing
- Test automation and reporting
- Testing documentation

**Issue #27: Quality Assurance & Finalization**
- Code review and refactoring
- Performance optimization
- Security audit and validation
- Final documentation completion
- User acceptance testing preparation

---

## Success Metrics

- **Test Coverage**: >85% across all components
- **Performance**: <2s response time for queries
- **Security**: All OWASP top 10 vulnerabilities addressed
- **Documentation**: Complete API docs and user guides
- **Deployment**: One-command production deployment
- **Quality**: Pristine test output, no warnings or errors

---

## Risk Mitigation

- **Technical Debt**: Each phase includes refactoring time
- **Integration Issues**: Continuous integration testing
- **Performance Problems**: Performance testing in each phase
- **Security Vulnerabilities**: Security review in each phase
- **Scope Creep**: Strict adherence to spec requirements
