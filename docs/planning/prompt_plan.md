Below is a **complete implementation plan** followed by **nested task breakdowns** and a **ready-to-copy set of code-generation prompts** you can paste into your favorite LLM (e.g., GitHub Copilot Chat or ChatGPT-Code Interpreter).
The flow intentionally starts small, adds tests immediately, and never leaves orphaned code.

---

## 1 — End-to-End Blueprint (high-level)

| Phase                         | What We Deliver                                                                             | Why It’s First                                                   |
| ----------------------------- | ------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| **P0 – Foundation**           | Git repo, pre-commit, CI pipeline, Docker skeleton, “hello world” FastAPI & React           | Ensures repeatable dev environment and green pipeline from day 1 |
| **P1 – Backend Core**         | Config loader, Snowflake client (read-only), health + ping routes, minimal domain models    | Validates DB connectivity early; isolates infra risks            |
| **P2 – Auth & Sessions**      | Google OAuth, PostgreSQL user store, Redis sessions, login guard on protected routes        | Turns skeleton into a true multi-user app                        |
| **P3 – LLM + Query Pipeline** | Gemini service wrapper, schema cache, NL→SQL plumbing, confirmation step, stubbed execution | Core differentiator; still CLI / cURL only                       |
| **P4 – Frontend MVP**         | Chat UI, schema explorer, result table w/ pagination                                        | User-visible loop from prompt to data                            |
| **P5 – History & Settings**   | Persisted query history, favorites, settings panel                                          | Adds stickiness & power features                                 |
| **P6 – Ops & Observability**  | Structlog JSON, external log sink, Docker Compose prod profile                              | Readiness for demo / pilot users                                 |

*Each phase contains many micro-steps; see below.*

---

## 2 — Iterative Chunking (first pass)

1. **Chunk A:** Repo, Tooling, CI
2. **Chunk B:** Backend skeleton & health test
3. **Chunk C:** Snowflake client + config validation
4. **Chunk D:** Auth stack (Google OAuth, PostgreSQL, Redis)
5. **Chunk E:** LLM wrapper + NL→SQL pipeline (no UI)
6. **Chunk F:** Frontend skeleton with auth flow
7. **Chunk G:** Chat panel, schema sidebar, result renderer
8. **Chunk H:** History, favorites, settings
9. **Chunk I:** Logging, metrics, Compose prod profile

*Validate after every chunk via unit + integration tests.*

---

## 3 — Micro-Tasks (second pass)

Below is Chunk A fully expanded.
We applied the same granularity to all later chunks (kept concise here to save space).

### Chunk A — Repo & Tooling

| #  | Task                                                           | Acceptance Test                      |
| -- | -------------------------------------------------------------- | ------------------------------------ |
| A1 | `git init`, add MIT LICENSE & README                           | Repo exists, CI passes “no code yet” |
| A2 | Create `backend/` & `frontend/` dirs with `.gitkeep`           | CI still green                       |
| A3 | Add `pyproject.toml` (Poetry) w/ FastAPI, Uvicorn              | `poetry install` succeeds locally    |
| A4 | Add Dockerfile.dev (backend) + `.dockerignore`                 | `docker build` completes             |
| A5 | `.pre-commit-config.yaml` (black, ruff, isort, mypy, pytest)   | `pre-commit run --all-files` passes  |
| A6 | GitHub Actions workflow: lint + tests on push                  | Red until A8 passes                  |
| A7 | Write failing pytest for `/health` returning `{"status":"ok"}` | Test marked `xfail`                  |
| A8 | Implement minimal FastAPI & make test pass                     | CI goes green                        |

### Chunk B — Backend Skeleton

B1 Config loader, env switching
B2 Snowflake DSN Pydantic model
B3 Snowflake ping function (mocked in tests)
B4 `/ping` route calling ping

### Chunk C — DB Connectivity

C1 CLI util `snowflake validate …`
C2 Unit tests with `pytest-snowflake-mock`
C3 Error mapping to friendly message

*(Chunks D–I similarly decomposed; omitted for brevity in this doc—you’ll still see them inside the prompts below.)*

---

## 4 — Right-Sizing Review

* ✅  **No task > \~2 hours** for a solo dev
* ✅  **Each introduces at least one new test**
* ✅  **Every task leaves repo in deployable state** (`docker compose up backend` works)
* ✅  **Early vertical slice:** By end of Chunk E a user can `curl /chat` and get results
* ✅  **No dead code:** each stub is either used immediately or guarded by an explicit test

---

## 5 — Copy-Ready Code-Generation Prompts

> **Usage:** Copy **one prompt at a time** into your LLM.
> Commit the generated code, run tests, then move to the next prompt.

### Prompt 1 — Initialize Repo & Tooling

```text
You are a senior Python / DevOps engineer.
Create the initial repository structure for a full-stack project named **snowchat**.

**Deliverables**
1. `.gitignore`, MIT `LICENSE`, `README.md` with project summary.
2. `backend/` and `frontend/` directories each containing only a `.gitkeep`.
3. `pyproject.toml` using Poetry 1.8 with deps: `fastapi`, `uvicorn[standard]`, `pytest`, `pytest-asyncio`, `ruff`, `black`, `isort`, `mypy`, `structlog`.
4. `Dockerfile.dev` for backend (multi-stage, slim) and `.dockerignore`.
5. `.pre-commit-config.yaml` running black, ruff, isort, mypy, and pytest.
6. GitHub Actions workflow `.github/workflows/ci.yml`:
   * Matrix Python {3.10, 3.11}
   * Steps: checkout, setup Python, cache Poetry, install, run pre-commit.

**Constraints**
* No application logic yet.
* Commands must pass locally: `pre-commit run --all-files`, `pytest` (should show 0 tests).

Return a list of files with full contents.
```

### Prompt 2 — Add FastAPI Skeleton & Health Test

```text
Extend the existing repo.

**Tasks**
1. Under `backend/app/` create `main.py` starting FastAPI with route `GET /health` returning `{"status":"ok"}`.
2. Add `backend/app/core/__init__.py` (empty) to make namespace.
3. Add `backend/app/tests/test_health.py` with an async pytest using `httpx.AsyncClient` + `asgi_lifespan`.
4. Update `pyproject.toml` dev deps: `pytest-httpx`, `asgi-lifespan`.
5. Update Dockerfile.dev to run `uvicorn app.main:app --port 8000 --reload`.

**Acceptance**
* `pytest` green.
* `docker compose up backend` shows service responsive on `/health`.

Output only the changed / new files.
```

### Prompt 3 — Config Loader & Snowflake DSN Model

```text
Goal: robust config system.

**Deliverables**
1. `backend/app/core/config.py`:
   * Uses `pydantic.BaseSettings`
   * Fields: `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_DATABASE`, `SNOWFLAKE_SCHEMA`, `ENV` (default="development").
   * `.env` support.

2. `backend/app/models/snowflake.py`:
   * Pydantic model `SnowflakeDSN` combining above fields.
   * `dsn()` method returning snowflake connector kwargs.

3. Unit tests ensuring `.env` overrides and that missing required field raises `ValidationError`.

No Snowflake network calls yet. Keep tests isolated.
```

### Prompt 4 — Snowflake Client Stub & Ping Route

```text
Add a minimal read-only Snowflake client with dependency injection.

**Tasks**
1. Add optional dep `snowflake-connector-python` to Poetry (extras).
2. `backend/app/services/snowflake_client.py`
   * Class `SnowflakeClient` with async `ping()` returning `True` if connection succeeds.
   * Accepts a `SnowflakeDSN` object in ctor.
3. In `backend/app/api/ping.py` add route `GET /ping` which:
   * Reads config, instantiates client, calls `await ping()`.
   * Returns `{ "snowflake":"ok" }` or error message.
4. Write unit tests using `pytest-monkeypatch` to patch connector and force deterministic result.

Ensure health test still passes.
```

### Prompt 5 — Google OAuth & User Model

```text
Implement auth (backend only).

**Deliverables**
1. Dependency: `authlib`, `python-jose`, `sqlalchemy`, `asyncpg`.
2. `backend/app/db/postgres.py` engine + session factory.
3. `backend/app/schemas/user.py` SQLAlchemy model (id, email, name, picture, created_at).
4. OAuth flow routes:
   * `GET /login/google` → redirect_uri
   * `GET /auth/google/callback` → exchanges code, creates/gets user, issues JWT cookie.
5. Middleware enforcing auth on `/api/**` (except health, ping, login).

Add tests mocking Google endpoints with `respx`.

**Constraint**: do **not** touch frontend yet.
```

### Prompt 6 — Session Store with Redis

```text
Add Redis for session / rate-limit metadata.

**Tasks**
1. Poetry dep `aioredis`.
2. `backend/app/db/redis_client.py` singleton factory.
3. On successful OAuth callback, store `session:{user_id}` with expiry 24h.
4. Middleware attaches Redis session to `request.state.session`.

Unit test session creation & expiry logic using `fakeredis`.
```

### Prompt 7 — LLM Service Wrapper

```text
Add Gemini integration (stubbed).

**Deliverables**
1. `backend/app/services/llm_service.py`
   * `class GeminiClient` with `async translate_nl_to_sql(prompt: str, schema: str) -> str`
   * Injects API key via config; in tests, patch to return static SQL.
2. `backend/app/services/context_builder.py`
   * Builds schema context from Snowflake meta (mock for now).
3. Unit tests verifying prompt construction and that SQL string returned.

No /chat route yet.
```

### Prompt 8 — Chat Route & End-to-End Pipeline (CLI only)

```text
Expose POST `/chat` that accepts `{ "prompt": "<string>", "output": "table|text|both" }`.

Flow:
1. Validate Redis session.
2. Build context (schema cache).
3. Call LLM translate.
4. Return generated SQL **without executing** for now.

Tests:
* Good prompt returns `sql` key.
* Bad prompt (empty) returns 422.

Update OpenAPI docs accordingly.
```

### Prompt 9 — Execute Read-Only Query

```text
Enhance `/chat`.

1. Add request field `autorun: bool`.
2. If autorun true:
   * Validate SQL is read-only (`SELECT` only) via simple regex + sqlparse.
   * Run against Snowflake, fetch rows (limit 500).
3. Structure response `{ "sql": "...", "rows":[...], "truncated": bool }`.
4. Tests covering autorun true/false and limit truncation.

Extend SnowflakeClient with `run_query(sql, limit)`; mock in tests.
```

### Prompt 10 — Frontend Skeleton w/ Auth Flow

```text
Create React app (Vite + TS) under `frontend/`.

**Features**
1. Tailwind dark-mode baseline.
2. React-Router routes: `/login`, `/app/*`.
3. Google OAuth button hits backend `/login/google`.
4. After auth, store JWT in `httpOnly` cookie; frontend reads `/api/me` to hydrate user context.

Add Cypress e2e test: login redirect and 200 on `/health`.
```

### Prompt 11 — Chat UI Vertical Slice

```text
Add components:

* `ChatWindow`, `MessageBubble`, `PromptInput`.
* Call backend `/chat` endpoint, show SQL confirmation modal, autorun toggle.
* Display table using `react-table` with pagination.

Tests: React Testing Library – renders, sends prompt, shows rows.

Integrate schema sidebar (mocked list).
```

### Prompt 12 — History, Favorites, Settings

```text
Backend:
* `/history` CRUD routes.
* Update `/chat` to write history on success.

Frontend:
* Left drawer list of past queries with star icon.
* Settings modal for row limit, autorun default.

Tests: add integration for favoriting and settings persistence (localStorage).

Ensure existing tests still pass.
```

### Prompt 13 — Logging, Metrics, Compose Prod

```text
1. Add structlog JSON config, log to stdout.
2. Docker Compose `prod.yml` services: backend, nginx static frontend, redis, postgres.
3. Healthcheck definitions for each.
4. GitHub Action: on `main` tag push → build & push images (`ghcr.io/org/snowchat-*`).

Unit test that `structlog.get_logger().info()` outputs valid JSON.

Repo now deployable via `docker compose -f prod.yml up -d`.
```

### Prompt 14 — Polish & Wire-Up

```text
Goals:
* Remove all TODOs.
* Ensure type-checking passes (`mypy --strict`).
* Docs: update README with setup, dev, prod commands.
* Verify 85%+ coverage (`pytest --cov=backend`).

Return only changed files plus a coverage badge snippet for README.
```

*End of prompt series.* 🎉

---

### Next Steps

1. Start with Prompt 1, iterate, commit often.
2. When unfamiliar libraries (e.g., Google OAuth) require secrets, inject ENV placeholders and document in README.
3. After Prompt 14 you have a runnable MVP; future work (RBAC, multi-DB) fits cleanly as additional prompts using the same template.

Happy building!
