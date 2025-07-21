# Data Chat MVP - Technical Specification

---

## ✅ Overview

**Goal:** A web application with a chat interface that allows **non-technical users** to interact with **CSV files and databases** using **natural language** queries.
Users can **upload CSV files OR connect databases**, interact with their data using a **Gemini-based LLM**, and receive **tabular and/or natural language outputs**.

---

## ✅ Key Features

### 👤 User Onboarding

* **CSV File Upload** as primary entry point (no login required for MVP)
* **Google OAuth login** (secure and familiar) - optional for MVP
* Alternative: **Database connection** via step-by-step form (future feature)
* **Immediate data preview** after CSV upload or connection
* Auto-detected schema with user confirmation option

### 📁 File Upload Experience (MVP Priority)

* **Drag-and-drop interface** with visual feedback
* **File validation** - CSV format, size limits (100MB max)
* **Auto-detection** of delimiters, headers, encoding
* **Schema preview** showing detected columns and data types
* **Sample data display** - first 10 rows for user confirmation
* **Error handling** for malformed files with clear guidance

### 💬 Chat Interface

* Chat UI like ChatGPT
* **Context-aware** for uploaded CSV data
* Users select **preferred output type**: Table, Natural Language, or Both
* **Schema hints** in chat (collapsible, unobtrusive)
* **Query suggestions** based on detected data patterns

### 🔐 Query Execution

* **LLM (Gemini) translates** NL → SQL (SQLite-optimized)
* Show SQL in a **non-intrusive confirmation box** before execution
* Allow user to enable **auto-run toggle** (stored per session)
* Read-only queries only in v1 (SELECT statements)
* **500 row limit** with option to adjust

### 📊 Result Display

* Tabular results with:
  * ✅ Pagination
  * ✅ Column sorting
  * ✅ Value/range filters
* Option to **export results as CSV**
* **Soft row limit** (e.g., 500 rows) with notice and adjustable setting
* **Visual indicators** for data types (numbers right-aligned, dates formatted)

### 🧠 Query History & Session Management

* **Per-session history** of:
  * User input
  * Generated SQL
  * Output snapshots
* **Temporary data storage** - cleanup after session expires
* **File management** - show currently loaded CSV files
* Ability to **clear session** and start fresh

### ⚙️ Settings Panel

* **Row limit adjustment** (100, 500, 1000, 5000)
* **Auto-run toggle** (skip SQL confirmation)
* **Download options** (CSV, JSON export formats)
* **Session cleanup** controls

---

## ✅ Architecture

### 📦 Tech Stack

| Component  | Tech Stack                                                    |
| ---------- | ------------------------------------------------------------- |
| Frontend   | React + Vite + TypeScript + Tailwind CSS (dark mode)         |
| Backend    | FastAPI (Python) + Poetry                                     |
| Database   | PostgreSQL (users), SQLite (uploaded CSV data)               |
| Session    | Redis (session management)                                    |
| Auth       | Google OAuth (optional for MVP)                              |
| LLM        | Gemini API (BYOK - user provides API key)                    |
| File Processing | pandas, openpyxl (CSV/Excel support)                    |
| Deployment | Docker + Docker Compose                                       |
| Logging    | `structlog` → external log service                           |
| Testing    | `pytest`, `vitest`, `cypress`                                |

### 🔧 Updated Folder Structure

```
backend/
├── app/
│   ├── api/                # FastAPI routes
│   │   ├── auth/           # OAuth endpoints
│   │   ├── chat/           # Chat and query endpoints
│   │   └── data/           # File upload endpoints (NEW)
│   ├── models/             # Pydantic request/response models
│   ├── services/
│   │   ├── llm_service.py      # Gemini integration
│   │   ├── csv_processor.py    # CSV → SQLite conversion (NEW)
│   │   ├── query_engine.py     # SQLite query execution (NEW)
│   │   └── file_manager.py     # Temp file handling (NEW)
│   ├── db/                 # Database clients
│   │   ├── sqlite_client.py    # SQLite operations (NEW)
│   │   └── redis_client.py     # Session storage
│   ├── core/               # config, security, env
│   ├── utils/              # formatters, validators
│   └── tests/              # Full test coverage

frontend/
├── src/
│   ├── components/
│   │   ├── upload/         # File upload components (NEW)
│   │   ├── chat/           # Chat interface components
│   │   ├── data/           # Data preview components (NEW)
│   │   └── auth/           # Authentication components
│   ├── hooks/              # React hooks
│   ├── services/           # API clients
│   └── types/              # TypeScript definitions
```

---

## ✅ Data Handling

### 📁 CSV File Processing (MVP Priority)

* **File Upload Pipeline:**
  * Drag-and-drop interface with progress indication
  * Support for CSV files up to 100MB
  * Auto-detection of delimiters (comma, tab, semicolon, pipe)
  * Header detection and encoding inference (UTF-8, latin1, etc.)
  * Schema inference (column names, data types, nullable)
  * Conversion to SQLite in-memory database for querying

* **Data Preview & Validation:**
  * Show first 10 rows for user confirmation
  * Display detected schema (column names, types, nullable status)
  * Allow manual schema adjustments if auto-detection fails
  * Error handling for malformed CSV files with specific guidance
  * Warning for files with potential data quality issues

* **Session Management:**
  * Temporary storage during user session (Redis or filesystem)
  * Auto-cleanup after session expiry (configurable timeout)
  * Support for multiple CSV files (future: auto-JOIN capabilities)
  * File replacement workflow (upload new version)

### 🗂️ Database Schema (Future Expansion)

* **Multi-database support:**
  * PostgreSQL, MySQL, SQLite file connections
  * Connection parameter encryption and secure storage
  * Schema caching and refresh capabilities

* **Schema introspection:**
  * Table names, column metadata, relationships
  * Used for autocomplete, prompt context, query validation

### 💬 LLM Pipeline (Model-Context-Protocol)

1. **Intent classification** (detect unsafe or invalid prompts)
2. **Context building** (user prompt + SQLite schema from uploaded CSV)
3. **LLM call** (Gemini API with SQLite-optimized prompts)
4. **SQL validation** (ensure SELECT-only, proper SQLite syntax)
5. **Confirmation** (non-intrusive display of generated SQL)
6. **Execution** (SQLite queries against uploaded CSV data)
7. **Output formatting** (tabular results with proper data types)
8. **Session update** (query history within session scope)

---

## ✅ Error Handling

| Area              | Strategy                                       |
| ----------------- | ---------------------------------------------- |
| CSV upload fail   | Clear error messages + format guidance        |
| File too large    | Size limit warning + compression tips         |
| Schema detection  | Manual override options if auto-detect fails  |
| Malformed CSV     | Specific error location + correction hints     |
| LLM failure       | Retry + fallback message ("try again")        |
| Query error       | Abstracted error summary (not raw SQL)        |
| Memory limits     | Progressive loading for large files           |
| Invalid prompt    | Gentle clarification + example queries        |
| Rate limits       | Soft warnings; API key guidance               |

---

## ✅ Testing Strategy

### 📦 Test Coverage Requirements

* **Backend**: 85%+ coverage with pytest
* **Frontend**: 80%+ coverage with vitest
* **E2E**: Critical user flows with cypress

### 🧪 Unit Tests

* **CSV Processing**:
  * File parsing with various delimiters and encodings
  * Schema detection edge cases
  * SQLite conversion accuracy
  * Error handling for malformed files

* **LLM Service**:
  * Prompt formatting for SQLite context
  * Response parsing and validation
  * Error handling for API failures

* **Query Engine**:
  * SQL generation and validation
  * Result formatting and pagination
  * Security validation (SELECT-only)

### 🔁 Integration Tests

* **Complete Upload Flow**: CSV → SQLite → Schema Preview → Chat Ready
* **Query Execution**: NL → SQL → Confirmation → Results → Export
* **Error Scenarios**: Invalid files, malformed queries, API failures
* **Session Management**: File cleanup, timeout handling

### 🔄 CI/CD

* **GitHub Actions**:
  * Run tests on push/PR to main
  * Build and test Docker images
  * Enforce coverage thresholds
  * Automated security scanning

---

## ✅ MVP User Experience Flow

### 🚀 Primary User Journey

1. **Landing Page**: "Upload your CSV file to start chatting with your data"
2. **File Upload**: Drag-and-drop CSV → Processing indicator → Schema preview
3. **Data Confirmation**: "Found 1,247 rows with columns: name, date, revenue, region"
4. **Chat Activation**: "Ask me anything about your data!"
5. **Natural Queries**:
   - "What were the top 5 sales last month?"
   - "Show me revenue by region"
   - "Which customers bought more than $10,000?"
6. **SQL Review**: Generated query display with run/edit options
7. **Results**: Paginated table with export options
8. **Follow-up**: Continue conversation with additional queries

### 📱 Responsive Design

* **Desktop**: Full experience with side-by-side upload and chat
* **Tablet**: Stacked layout with collapsible sections
* **Mobile**: Progressive workflow with clear navigation

---

## ✅ Security & Privacy

### 🔒 Data Security

* **File Upload**: Size limits, type validation, virus scanning
* **Temporary Storage**: Session-scoped, auto-cleanup
* **SQL Safety**: SELECT-only queries, parameterized execution
* **API Keys**: User-provided, never stored server-side
* **Session Management**: Secure tokens, configurable expiry

### 🛡️ Privacy Controls

* **No Data Persistence**: Files deleted after session
* **Local Processing**: CSV parsing happens server-side but temporarily
* **User Control**: Clear data, download results, session management
* **Transparent Processing**: Show exactly what data is being processed

---

## ✅ Performance Requirements

### ⚡ Performance Targets

* **File Upload**: 100MB CSV in < 30 seconds
* **Schema Detection**: < 5 seconds for typical files
* **Query Execution**: < 10 seconds for complex queries
* **Chat Response**: < 15 seconds end-to-end (including LLM)
* **Page Load**: < 3 seconds initial load

### 🔧 Optimization Strategies

* **Chunked Upload**: Large files processed in streams
* **Lazy Loading**: Progressive data display
* **Caching**: Schema and query result caching
* **Connection Pooling**: Efficient database connections

---

## ✅ Deployment

### 🐳 Docker Configuration

**Development:**
```yaml
services:
  backend: FastAPI with hot reload
  frontend: Vite dev server
  postgres: User management (optional for MVP)
  redis: Session storage
  file-storage: Temporary volume mount
```

**Production:**
```yaml
services:
  backend: FastAPI with gunicorn
  frontend: Nginx static hosting
  postgres: Managed database service
  redis: Managed Redis service
  file-storage: S3-compatible object storage
```

### 🌐 Environment Configuration

* **Development**: Local file storage, dev database
* **Production**: Cloud storage, managed services
* **Environment Variables**: API keys, storage configs, timeouts

---

## ✅ Future Extensions (Roadmap)

### **Phase 1: Enhanced File Support** (Post-MVP)
* Excel files (.xlsx, .xls)
* JSON arrays and JSON Lines
* Parquet columnar format
* Multi-sheet Excel support

### **Phase 2: Advanced Analytics**
* Automatic chart generation
* Statistical summaries
* Data profiling and quality reports
* Export to various formats (PDF, images)

### **Phase 3: Database Integration**
* PostgreSQL, MySQL, SQLite file connections
* Snowflake integration (original scope)
* Multi-source joins and analysis
* Connection management UI

### **Phase 4: Collaboration Features**
* Shared datasets and queries
* Team workspaces
* Query templates and libraries
* Real-time collaboration

### **Phase 5: Enterprise Features**
* SSO integration
* Role-based access control
* Audit logging and compliance
* API access and integrations

---

## 🎯 Success Metrics

### 📊 MVP Success Criteria

* **User Onboarding**: 90% of users successfully upload and query CSV within 5 minutes
* **Query Success**: 85% of natural language queries produce valid SQL
* **Performance**: 95% of queries complete within performance targets
* **Error Recovery**: Clear error messages help 80% of users resolve issues
* **User Satisfaction**: Intuitive enough for non-technical users to succeed

### 📈 Growth Metrics

* **File Upload Success Rate**: % of uploads that complete successfully
* **Query Complexity**: Average sophistication of user queries over time
* **Session Duration**: Time spent exploring data per session
* **Return Usage**: Users who upload multiple files or return to the app
* **Feature Adoption**: Usage of advanced features (export, settings, etc.)

---

*This specification represents the complete pivot from Snowflake-only to a CSV-first data chat platform, designed to maximize user value while maintaining architectural simplicity and development velocity.*
