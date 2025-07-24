# Test Command Comparison Across Environments

## Backend Test Commands

### Pre-commit Hook (.pre-commit-config.yaml)
```bash
./scripts/poetry-wrapper.sh run pytest --cov=app --cov-report=term-missing --cov-fail-under=85
```

### CI Pipeline (.github/workflows/ci.yml)
```bash
cd backend
poetry run pytest --cov=app --cov-report=xml --cov-report=term-missing --cov-fail-under=85
```

### Docker/Makefile (UPDATED)
```bash
# Makefile test command
docker compose exec backend poetry run pytest --cov=app --cov-report=term-missing --cov-fail-under=85

# Makefile test-cov command
docker compose exec backend poetry run pytest --cov=app --cov-report=html --cov-report=term-missing --cov-fail-under=85
```

## Frontend Test Commands

### Pre-commit Hook (.pre-commit-config.yaml)
```bash
# ESLint
cd frontend && npx eslint . --ext ts,tsx --report-unused-disable-directives

# TypeScript
cd frontend && npx tsc --noEmit

# Vitest
cd frontend && npm run test -- --run --reporter=verbose

# Build check
cd frontend && npm run build
```

### CI Pipeline (.github/workflows/ci.yml)
```bash
# ❌ NO FRONTEND TESTS IN CI - NEEDS TO BE ADDED
```

### Docker/Makefile
```bash
# ❌ NO FRONTEND TEST COMMANDS - NEEDS TO BE ADDED
```

## Analysis

### Differences Found:

1. **Working Directory**:
   - Pre-commit: Runs from repo root using wrapper script
   - CI: Changes to `backend/` directory first
   - Docker: Runs inside container where working dir is already `/app`

2. **Coverage Reporting**:
   - Pre-commit: `--cov-report=term-missing` only
   - CI: `--cov-report=xml --cov-report=term-missing` (includes XML for Codecov)
   - Docker: No coverage by default, `--cov-report=html` in test-cov

3. **Coverage Threshold**:
   - Pre-commit: `--cov-fail-under=85` ✅
   - CI: `--cov-fail-under=85` ✅
   - Docker: No threshold enforcement ❌

### Frontend Test Gaps:
1. **CI Pipeline**: No frontend job at all
2. **Docker/Makefile**: No frontend test commands
3. **Pre-commit**: Has comprehensive frontend checks ✅

## Recommendations

### 1. Backend (COMPLETED ✅)
Updated Makefile to match CI and pre-commit:
```makefile
test: ## Run backend tests with coverage
	docker compose exec backend poetry run pytest --cov=app --cov-report=term-missing --cov-fail-under=85

test-cov: ## Run backend tests with detailed coverage report
	docker compose exec backend poetry run pytest --cov=app --cov-report=html --cov-report=term-missing --cov-fail-under=85
```

### 2. Frontend (TODO)

#### Add to CI Pipeline (.github/workflows/ci.yml):
```yaml
frontend-checks:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json

    - name: Install dependencies
      run: |
        cd frontend
        npm ci

    - name: Lint with ESLint
      run: |
        cd frontend
        npm run lint

    - name: Type check with TypeScript
      run: |
        cd frontend
        npx tsc --noEmit

    - name: Run tests with Vitest
      run: |
        cd frontend
        npm run test -- --run --reporter=verbose

    - name: Build verification
      run: |
        cd frontend
        npm run build
```

#### Add to Makefile:
```makefile
# Frontend testing
test-frontend: ## Run frontend tests
	docker compose exec frontend npm run test -- --run --reporter=verbose

test-frontend-watch: ## Run frontend tests in watch mode
	docker compose exec frontend npm run test

test-frontend-coverage: ## Run frontend tests with coverage
	docker compose exec frontend npm run coverage

lint-frontend: ## Run frontend linting
	docker compose exec frontend npm run lint

type-check-frontend: ## Run TypeScript type checking
	docker compose exec frontend npx tsc --noEmit

test-all: test test-frontend ## Run all tests (backend + frontend)
```

This ensures:
- All environments run the same frontend tests
- CI catches frontend issues before merge
- Developers can easily run frontend tests locally
