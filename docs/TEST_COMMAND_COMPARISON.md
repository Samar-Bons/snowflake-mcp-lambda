# Test Command Comparison Across Environments

## Current Test Commands

### Pre-commit Hook (.pre-commit-config.yaml)
```bash
./scripts/poetry-wrapper.sh run pytest --cov=app --cov-report=term-missing --cov-fail-under=85
```

### CI Pipeline (.github/workflows/ci.yml)
```bash
cd backend
poetry run pytest --cov=app --cov-report=xml --cov-report=term-missing --cov-fail-under=85
```

### Docker/Makefile
```bash
# Makefile test command
docker compose exec backend poetry run pytest

# Makefile test-cov command
docker compose exec backend poetry run pytest --cov=app --cov-report=html
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

## Recommendations

To ensure consistency, the Docker test commands should match CI:

### Update Makefile:
```makefile
test: ## Run backend tests with coverage
	docker compose exec backend poetry run pytest --cov=app --cov-report=term-missing --cov-fail-under=85

test-cov: ## Run backend tests with detailed coverage report
	docker compose exec backend poetry run pytest --cov=app --cov-report=html --cov-report=term-missing --cov-fail-under=85
```

This ensures:
- All environments enforce the 85% coverage requirement
- Developers see the same output locally as in CI
- Pre-commit hooks match production CI requirements
