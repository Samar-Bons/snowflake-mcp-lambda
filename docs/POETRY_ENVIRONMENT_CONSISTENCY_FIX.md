# Poetry Multi-Environment Consistency Fix

## Problem Statement

You are working on a Python project with Poetry dependency management that has **critical environment inconsistencies** causing:
- Pre-commit hooks failing randomly
- Type checking errors appearing/disappearing between environments
- Local development commands failing while Docker/CI works
- Package version mismatches causing unpredictable behavior

## Root Cause Analysis

**ISSUE 1: Missing Local Poetry Environment**
- Local system has Poetry installed but NO virtual environment created
- Poetry configured to use `python` but only `python3` is available
- Pre-commit hooks fail because they can't find packages locally

**ISSUE 2: Version Inconsistencies Across Environments**
```
Environment | Python  | Poetry  | Redis | MyPy   | Status
Local       | 3.10.12 | 2.1.3   | NONE  | NONE   | BROKEN
Docker      | 3.10.18 | 2.1.3   | 5.3.0 | 1.16.1 | Working
CI          | 3.10/11 | "latest"| 5.3.0 | 1.16.1 | Unstable
```

**ISSUE 3: CI Poetry Version Drift**
- CI uses `version: latest` which can break when Poetry updates
- Different Poetry versions have different behavior
- No guarantee CI uses same version as local/Docker

## Step-by-Step Fix Protocol

### Step 1: Diagnostic Commands (Run These First)

```bash
# Check current state
echo "=== LOCAL ENVIRONMENT ==="
which poetry && poetry --version
which python && which python3
cd backend && poetry env info 2>/dev/null || echo "No Poetry env"

echo "=== DOCKER ENVIRONMENT ==="
docker compose exec backend poetry --version
docker compose exec backend python --version
docker compose exec backend poetry show redis mypy ruff | grep version

echo "=== CI CONFIGURATION ==="
grep -A 5 "Install Poetry" .github/workflows/ci.yml
```

### Step 2: Fix Local Poetry Environment

```bash
# Navigate to backend directory where pyproject.toml exists
cd backend

# Configure Poetry to use python3 (not python)
poetry env use python3

# Install all dependencies exactly as locked in poetry.lock
poetry install --no-interaction

# Verify installation
poetry env info
poetry show redis mypy ruff | grep version
```

### Step 3: Fix CI Poetry Version Drift

Edit `.github/workflows/ci.yml`:

```yaml
# BEFORE (causes drift):
- name: Install Poetry
  uses: snok/install-poetry@v1
  with:
    version: latest  # ← REMOVE THIS

# AFTER (locked version):
- name: Install Poetry
  uses: snok/install-poetry@v1
  with:
    version: 2.1.3  # ← EXACT VERSION
    virtualenvs-create: true
    virtualenvs-in-project: true
    virtualenvs-path: backend/.venv
```

### Step 4: Enhanced Poetry Wrapper Script

Update `scripts/poetry-wrapper.sh`:

```bash
#!/bin/bash
# Enhanced wrapper with environment auto-setup

# Add Poetry to PATH
if [ -d "$HOME/.local/bin" ]; then
    export PATH="$HOME/.local/bin:$PATH"
fi

# Check if poetry is available
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry not found in PATH"
    exit 1
fi

# Store original directory and change to backend
ORIGINAL_DIR=$(pwd)
cd "$ORIGINAL_DIR/backend" || exit 1

# Auto-setup Poetry environment if missing
if ! poetry env info &> /dev/null; then
    echo "Setting up Poetry environment..."
    poetry env use python3
    poetry install --no-interaction
fi

# Execute poetry command
exec poetry "$@"
```

### Step 5: Verification Commands

```bash
# Verify all environments now match
echo "=== VERIFYING CONSISTENCY ==="

# Local
cd backend && poetry show redis mypy ruff | grep version

# Docker
docker compose exec backend bash -c "poetry show redis mypy ruff | grep version"

# Check CI file
grep "version:" .github/workflows/ci.yml

# Test pre-commit hooks work
pre-commit run --all-files
```

## Expected Results After Fix

**All environments should show:**
- Poetry: 2.1.3 (exact version locked)
- Redis: 5.3.0
- MyPy: 1.16.1
- Ruff: 0.4.10

**Behavior should be:**
- ✅ Pre-commit hooks run successfully locally
- ✅ Type checking consistent across environments
- ✅ No more "package not found" errors
- ✅ CI builds are reproducible and stable

## Common Failure Points & Solutions

**"Poetry env not found"**
```bash
cd backend && poetry env use python3
```

**"python not found"**
```bash
poetry config virtualenvs.prefer-active-python true
poetry env use $(which python3)
```

**"Package versions differ"**
```bash
poetry lock --no-update  # Regenerate lock file
poetry install --no-interaction
```

**"Pre-commit still fails"**
```bash
pre-commit clean
pre-commit install --install-hooks
```

## Files That Must Be Modified

1. `.github/workflows/ci.yml` - Lock Poetry version to 2.1.3
2. `scripts/poetry-wrapper.sh` - Add auto-environment setup
3. `backend/pyproject.toml` - Verify Python version constraint
4. Local Poetry environment - Must be created and installed

## Validation Checklist

- [ ] `cd backend && poetry env info` shows active environment
- [ ] `poetry show redis` returns version 5.3.0 locally
- [ ] `docker compose exec backend poetry show redis` returns same version
- [ ] `.github/workflows/ci.yml` has `version: 2.1.3` (not latest)
- [ ] `pre-commit run --all-files` passes without package errors
- [ ] MyPy runs successfully in all environments
- [ ] All three environments show identical package versions

This fix ensures **permanent consistency** across local, Docker, and CI environments, eliminating random Poetry-related failures.
