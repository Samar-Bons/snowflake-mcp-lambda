
---

## ✅ Overview

**Goal:** A web application with a chat interface that allows **non-technical users** to interact with a **Snowflake database** using **natural language** queries.
Users can **connect their own Snowflake DB**, interact with it using a **Gemini-based LLM**, and receive **tabular and/or natural language outputs**.

---

## ✅ Key Features

### 👤 User Onboarding

* **Google OAuth login** (secure and familiar)
* Option to use **demo datasets** without login
* After login: user provides **Snowflake connection** via a **step-by-step form**
* Connection validated **immediately** on submission

### 💬 Chat Interface

* Chat UI like ChatGPT
* Supports **autocomplete** for table/column names
* Users select **preferred output type**: Table, Natural Language, or Both
* Includes a **schema explorer sidebar** (collapsible, unobtrusive)

### 🔐 Query Execution

* **LLM (Gemini) translates** NL → SQL
* Show SQL in a **non-intrusive confirmation box** before execution
* Allow user to enable **auto-run toggle** (stored per session)
* Read-only queries only in v1 (write access disabled)

### 📊 Result Display

* Tabular results with:

  * ✅ Pagination
  * ✅ Column sorting
  * ✅ Value/range filters
* Option to **export as CSV or JSON**
* **Soft row limit** (e.g., 500 rows) with notice and adjustable setting

### 🧠 Query History & Favorites

* Per-session history of:

  * User input
  * Generated SQL
  * Output
* Ability to **rename and favorite** queries for reuse

### ⚙️ Settings Panel

* View/edit Snowflake config
* Toggle auto-run
* Refresh schema
* Adjust row limits

---

## ✅ Architecture

### 📦 Tech Stack

| Component  | Tech Stack                                                    |
| ---------- | ------------------------------------------------------------- |
| Frontend   | React + Tailwind CSS (dark mode only)                         |
| Backend    | FastAPI (Python)                                              |
| Database   | PostgreSQL (user info, roles)                                 |
| Session    | Redis                                                         |
| Auth       | Google OAuth                                                  |
| LLM        | Gemini (BYOK)                                                 |
| Deployment | Docker + Docker Compose                                       |
| Logging    | `structlog` → external log service (e.g., Logtail or Grafana) |
| Testing    | `pytest`, `pre-commit`, GitHub Actions                        |

### 🔧 Folder Structure (`backend/`)

```
backend/
├── app/
│   ├── api/                # FastAPI routes
│   ├── models/             # Pydantic request/response models
│   ├── services/           # llm_service, protocol, query_runner, etc.
│   ├── db/                 # snowflake_client, redis_client
│   ├── schemas/            # SQLAlchemy models for users, roles (optional v1)
│   ├── core/               # config, security, env
│   ├── utils/              # formatters, validators, constants
│   └── tests/              # TDD structure with full coverage
```

---

## ✅ Data Handling

### 🗂️ Snowflake Schema

* On first connect, cache:

  * Table names
  * Columns + data types
* Refreshable manually by user
* Used for:

  * Autocomplete
  * Prompt context
  * Protocol flow

### 💬 LLM Pipeline (Model-Context-Protocol)

1. **Intent classification** (detect unsafe or invalid prompts)
2. **Context building** (user prompt + schema hints)
3. **LLM call** (Gemini API via `llm_service`)
4. **Confirmation** (non-intrusive display of SQL)
5. **Execution** (`snowflake_client`)
6. **Output formatting** (based on preference)
7. **Session update** (history, favorites)

---

## ✅ Error Handling

| Area              | Strategy                               |
| ----------------- | -------------------------------------- |
| Snowflake connect | Friendly inline message + retry button |
| LLM failure       | Retry + fallback message (“try again”) |
| Query error       | Abstracted error summary (not raw SQL) |
| Schema load fail  | Graceful fallback to chat-only         |
| Invalid prompt    | Gentle clarification + examples        |
| Rate limits       | Soft warnings; future config options   |

---

## ✅ Testing Strategy

### 📦 Pre-commit Hooks

* `black`, `flake8` or `ruff`, `isort`, `mypy`, `pytest`
* All enforced via `.pre-commit-config.yaml`

### 🧪 Unit Tests

* `llm_service`: prompt formatting, response parsing
* `query_runner`: SQL validation, output formatters
* `context_builder`: schema injection, field matching
* `snowflake_client`: mock DB connection + execution

### 🔁 Integration Tests

* End-to-end flow: NL → SQL → Confirm → Execute → Display
* Test `/chat` route with:

  * Good prompt
  * Invalid prompt
  * Large output
  * Bad schema

### 🔄 CI/CD

* GitHub Actions:

  * Run tests on push/PR
  * Enforce >80% coverage
  * Optionally build Docker image

---

## ✅ Deployment

### Using Docker Compose:

Services:

* `frontend`: React static app (Netlify optional)
* `backend`: FastAPI app
* `redis`: Session store
* `postgres`: User config storage

### Environments

* `.env.development`, `.env.production`
* Config class auto-loads correct env
* Safe to open-source with secrets in `.env.local`

---

## ✅ Future Extensions (Already Planned for)

* Persistent user history (beyond session)
* Multi-DB support
* Write-query permissions
* Role-based access control (RBAC)
* Hosted SaaS with billing
* External LLM routing layer (OpenAI, Claude, etc.)

---
