# Data Chat MVP - Implementation Plan

## Project Overview
A web application with chat interface allowing non-technical users to interact with **CSV files and databases** using natural language queries via Gemini LLM. MVP focuses on CSV file upload and querying with future expansion to multiple database types.

## Implementation Strategy
- **Approach**: Test-Driven Development (TDD) with incremental, iterative phases
- **Visual-Driven Development**: Puppeteer screenshot validation for pixel-perfect UI implementation
- **Backend-First Methodology**: Complete extensible foundation before UI complexity
- **Risk Management**: Each phase builds safely on previous work
- **Integration**: No orphaned code - everything connects to existing foundation
- **Quality**: 85%+ test coverage, pre-commit hooks, pristine test output
- **MVP Focus**: Extensible file processing with visual design system for immediate demos

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
- ✅ Redis connection setup for sessions
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
- ✅ JWT token generation and validation (Cookie-based)
- ✅ Session middleware for protected routes
- ✅ 24-hour session expiry

### 2.3: User Management ✅ COMPLETED
- ✅ User model and database operations
- ✅ User registration on first login
- ✅ Profile management endpoints
- ✅ Authentication required decorators

---

## Phase 3: Data Source Integration ✅ PARTIAL COMPLETED
**Duration**: 3-4 days
**Goal**: File upload processing and database connectivity

### 3.1: Data Processing Infrastructure ✅ COMPLETED
- ✅ Generic database client abstraction ready
- ✅ Schema introspection system (works with SQLite)
- ✅ Read-only query validation and execution
- ✅ Error handling and result formatting

### 3.2: Legacy Database Support ✅ COMPLETED (for reference)
- ✅ Snowflake client with AES-256 encrypted parameter storage
- ✅ Connection testing and validation
- ✅ Schema discovery and metadata caching
- ✅ Performance optimization for large schemas

### 3.3: CSV Upload System ❌ NEEDS IMPLEMENTATION (MVP PRIORITY)
- ❌ CSV file upload endpoint with validation
- ❌ pandas-based CSV processing and schema detection
- ❌ CSV to SQLite conversion pipeline
- ❌ File management and session cleanup
- ❌ Multi-format support preparation (Excel, JSON, Parquet)

---

## Phase 4: LLM Pipeline (Gemini Integration) ✅ COMPLETED
**Duration**: 4-5 days
**Goal**: Natural language to SQL conversion with safety checks

### 4.1: Gemini Service Integration ✅ COMPLETED
- ✅ Gemini API client setup
- ✅ API key management (BYOK)
- ✅ Prompt template system (works with SQLite)
- ✅ Response parsing and validation

### 4.2: Context Building System ✅ COMPLETED
- ✅ Schema context injection (ready for SQLite schemas)
- ✅ User prompt analysis and enhancement
- ✅ Intent classification for safety
- ✅ Context size optimization

### 4.3: Chat Endpoint Implementation ✅ COMPLETED
- ✅ `/chat` endpoint with full pipeline
- ✅ Natural language → SQL generation
- ✅ SQL confirmation before execution
- ✅ Results formatting (table/NL/both)
- ❌ Query history storage (session-only for MVP)

---

## Phase 5: Frontend Foundation ✅ COMPLETED
**Duration**: 4-5 days
**Goal**: React app with authentication and ready for CSV upload

### 5.1: React Application Setup ✅ COMPLETED
- ✅ Vite + React + TypeScript setup
- ✅ Tailwind CSS with dark mode and custom variables
- ✅ Frontend build and dev server
- ✅ React Router setup with /login and /app/* routes

### 5.2: Authentication Flow ✅ COMPLETED
- ✅ Google OAuth frontend integration with auth service
- ✅ Login/logout UI components (LoginButton, UserMenu)
- ✅ Protected route handling with ProtectedRoute component
- ✅ User session management with useAuth hook and context
- ✅ httpOnly cookie handling via API client

### 5.3: Dashboard Foundation ✅ COMPLETED
- ✅ Dashboard page structure ready for data components
- ✅ Authentication-aware layout with Header component
- ✅ API client infrastructure ready for file upload
- ❌ File upload components (next priority)

---

## Phase 6: MVP Implementation ❌ CURRENT PRIORITY (Prompt 11)
**Duration**: 4-5 days
**Goal**: Backend foundation + Visual design system + React integration

### 6.1: Backend Extensible Foundation ❌ NEEDS IMPLEMENTATION
- ❌ FileProcessor interface and file type registry system
- ❌ CSVProcessor implementation with pandas integration
- ❌ Multi-format POST /data/upload endpoint with type detection
- ❌ SQLite adapter compatible with existing LLM pipeline
- ❌ File management and session cleanup utilities
- ❌ Support for extensible file format architecture

### 6.2: Visual Design Implementation ❌ NEEDS IMPLEMENTATION
- ❌ Design reference collection and specification process
- ❌ Puppeteer-driven HTML template development with screenshot validation
- ❌ Core UI templates: file upload, schema preview, chat interface, results
- ❌ Visual iteration loop with automated regression testing
- ❌ Responsive design testing across multiple viewports

### 6.3: React Component Integration ❌ NEEDS IMPLEMENTATION
- ❌ HTML template to React component conversion
- ❌ State management and API integration with existing auth
- ❌ Visual fidelity maintenance using screenshot validation
- ❌ E2E testing of complete user flow from upload to results
- ❌ Integration with existing ChatWindow, MessageBubble components

---

## Phase 7: Multi-Format File Support ❌ FUTURE (Post-MVP)
**Duration**: 2-3 days
**Goal**: Extend FileProcessor architecture to additional file types

### 7.1: Additional File Processors ❌ FUTURE
- ❌ ExcelProcessor implementation for .xlsx/.xls files with openpyxl
- ❌ JSONProcessor for array and object data processing
- ❌ ParquetProcessor for columnar analytics data
- ❌ Compressed file handlers for ZIP and GZIP formats

### 7.2: Advanced Processing Features ❌ FUTURE
- ❌ Multi-sheet Excel support with sheet selection UI
- ❌ Large file streaming with progress indication and memory management
- ❌ Data type optimization and automatic inference improvements
- ❌ Multi-file relationships and JOIN capabilities across sources

---

## Phase 8: Database Expansion ❌ FUTURE (Phase 2)
**Duration**: 4-5 days
**Goal**: Multiple database connectivity (PostgreSQL, MySQL, Snowflake)

### 8.1: Database Adapter Pattern ❌ FUTURE
- ❌ Generic DatabaseAdapter interface
- ❌ PostgreSQL adapter implementation
- ❌ MySQL adapter implementation
- ❌ SQLite file adapter (in addition to CSV conversion)

### 8.2: Connection Management UI ❌ FUTURE
- ❌ Database connection wizard
- ❌ Connection testing interface
- ❌ Multiple data source management
- ❌ Secure credential handling

---

## Phase 9: Advanced Frontend Features ❌ FUTURE (Phase 2)
**Duration**: 3-4 days
**Goal**: Query history, favorites, and advanced UI features

### 9.1: Query Management ❌ FUTURE
- ❌ Persistent query history (beyond session)
- ❌ Favorites system with organization
- ❌ Query search and filtering
- ❌ Query sharing and export

### 9.2: Advanced UI Components ❌ FUTURE
- ❌ Schema explorer sidebar
- ❌ Advanced results visualization
- ❌ Data export options
- ❌ Settings and preferences panel

---

## Phase 10: Production Readiness ❌ FUTURE (Phase 3)
**Duration**: 3-4 days
**Goal**: Production deployment and monitoring

### 10.1: Production Configuration ❌ FUTURE
- ❌ Production Docker Compose setup
- ❌ Environment configuration optimization
- ❌ Security headers and CORS hardening
- ❌ Performance optimization

### 10.2: Monitoring & Security ❌ FUTURE
- ✅ Structured logging throughout (basic)
- ❌ External log service integration
- ❌ Security hardening and audit
- ❌ Performance metrics and alerting

---

## Updated Architecture for CSV MVP

### Tech Stack Changes
```yaml
# REMOVED (for MVP):
- Snowflake dependency (optional future feature)
- Complex database connection management

# ADDED (for MVP):
- FileProcessor abstraction: Extensible file handling architecture
- pandas: CSV processing and data manipulation foundation
- openpyxl: Ready for Excel support (future expansion)
- Puppeteer: Visual regression testing and screenshot validation
- SQLite: Unified query interface for all processed file types
```

### Data Flow (Extensible MVP)
```
File Upload → Type Detection → Processor Routing → Schema Detection → SQLite Conversion
     ↓             ↓               ↓                    ↓               ↓
Progress UI   Format ID     FileProcessor        Preview UI     Query Interface
     ↓             ↓               ↓                    ↓               ↓
Success → Visual Design → Schema Preview → User Confirmation → Chat Ready
           (Puppeteer)
```

### API Changes (MVP)
```yaml
# NEW ENDPOINTS:
POST /data/upload      # CSV file upload with processing
GET  /data/schema      # Schema info for uploaded files
DELETE /data/cleanup   # File cleanup management

# EXISTING (no changes):
POST /chat            # Works with SQLite from CSV
GET  /health          # System health
POST /auth/login      # Authentication (optional for MVP)
```

---

## Success Metrics (Updated for MVP)

- **MVP Success**: User uploads CSV and gets query results within 60 seconds
- **Test Coverage**: >85% across all components
- **Performance**: CSV processing <30s for 100MB files, queries <10s
- **User Experience**: Works without database credentials or external services
- **Quality**: Pristine test output, no warnings or errors

---

## Risk Mitigation (Updated for MVP)

- **File Processing Issues**: Comprehensive CSV format testing and error handling
- **Memory Usage**: Streaming processing for large files, configurable limits
- **Security**: File validation, size limits, session-based cleanup
- **Performance**: Chunked processing, SQLite optimization
- **User Experience**: Clear error messages, progress indication, format guidance

---

## Implementation Priority (Next Steps)

**IMMEDIATE (Prompt 11 - CSV Upload MVP)**:
1. Backend CSV processing service
2. File upload API endpoint
3. Frontend file upload components
4. Chat interface integration
5. End-to-end testing

**NEAR TERM (Post-MVP)**:
1. Multiple file format support
2. Advanced data preview features
3. Query history and favorites
4. Performance optimizations

**LONG TERM (Future Phases)**:
1. Database connectivity expansion
2. Advanced analytics features
3. Collaboration capabilities
4. Enterprise features

This plan maintains the proven TDD approach while pivoting to a more accessible MVP that works without external database dependencies.
