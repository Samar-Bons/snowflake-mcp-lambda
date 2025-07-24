# Docker + Local Poetry Environment Separation Fix

## Problem Statement

You are working on a Python project that uses Poetry for dependency management with both Docker and local development environments. You're experiencing **critical permission conflicts** where:

- Docker creates `.venv` directory with root permissions
- Local Poetry tries to use same `.venv` directory with user permissions
- Results in "Permission denied" errors when trying to remove/recreate environments
- Requires constant `sudo` usage and forced directory removal
- Environment breaks repeatedly when switching between Docker and local development

## Root Cause Analysis

**ANTI-PATTERN**: Sharing the same virtual environment directory between Docker (root user) and local development (user permissions).

```bash
# Current broken setup:
backend/.venv/  ← Docker creates with root:root
backend/.venv/  ← Local Poetry tries to use with user:user
# Result: Permission conflicts, broken environments
```

**Why This Happens:**
1. Docker runs as root and creates `/app/.venv` (mounted to local `backend/.venv`)
2. Local Poetry configured with `virtualenvs.in-project = true` uses same directory
3. Permission mismatch causes environment corruption
4. Manual fixes with `sudo` create security risks and poor developer experience

## Best Practice Solution

### Step 1: Separate Environment Paths

**Configure Poetry to use system-managed virtual environments (NOT in-project):**

```bash
# Navigate to backend directory
cd backend

# Configure Poetry for separate local environments
poetry config virtualenvs.in-project false
poetry config virtualenvs.path ~/.cache/pypoetry/virtualenvs

# Verify configuration
poetry config --list | grep virtualenvs
```

**Expected output:**
```
virtualenvs.in-project = false
virtualenvs.path = "/home/[user]/.cache/pypoetry/virtualenvs"
```

### Step 2: Clean Up Existing Broken Environment

```bash
# Remove broken .venv directory (may require sudo if corrupted)
sudo rm -rf .venv 2>/dev/null || echo "No .venv to remove"

# Create fresh Poetry environment in system location
poetry env remove --all  # Remove any existing environments
poetry install --no-interaction

# Verify environment location
poetry env info
```

**Expected result:** Path should be `~/.cache/pypoetry/virtualenvs/[project-name]-[hash]`

### Step 3: Update Docker Configuration (Optional Enhancement)

**In `backend/Dockerfile` or `docker-compose.yml`, explicitly set Docker environment path:**

```dockerfile
# Add to Dockerfile to make Docker path explicit
ENV POETRY_VENV_PATH=/app/.docker-venv
```

**Or in docker-compose.yml:**
```yaml
services:
  backend:
    environment:
      - POETRY_VENV_PATH=/app/.docker-venv
```

### Step 4: Update Poetry Wrapper Script

**Enhance `scripts/poetry-wrapper.sh` to handle separated environments:**

```bash
#!/bin/bash
# Enhanced wrapper with separated environment handling

# Add Poetry to PATH
if [ -d "$HOME/.local/bin" ]; then
    export PATH="$HOME/.local/bin:$PATH"
fi

# Check if poetry is available
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry not found in PATH"
    exit 1
fi

# Change to backend directory
ORIGINAL_DIR=$(pwd)
cd "$ORIGINAL_DIR/backend" || exit 1

# Ensure proper Poetry configuration for local development
if [ -z "$DOCKER_ENV" ]; then
    # Only configure for local (not in Docker)
    poetry config virtualenvs.in-project false >/dev/null 2>&1
    poetry config virtualenvs.path ~/.cache/pypoetry/virtualenvs >/dev/null 2>&1
fi

# Auto-setup environment if missing
if ! poetry env info >/dev/null 2>&1; then
    echo "Setting up Poetry environment in system location..."
    poetry install --no-interaction || {
        echo "Error: Poetry install failed"
        exit 1
    }
    echo "Poetry environment setup complete"
fi

# Execute poetry command
exec poetry "$@"
```

### Step 5: Verification Commands

**Run these commands to verify the fix:**

```bash
# 1. Check local Poetry configuration
cd backend
poetry config --list | grep virtualenvs

# 2. Verify environment location (should NOT be in project)
poetry env info | grep Path

# 3. Test package versions match Docker
echo "LOCAL:"
poetry show redis mypy ruff | grep version

echo "DOCKER:"
docker compose exec backend poetry show redis mypy ruff | grep version

# 4. Test pre-commit hooks work locally
cd ..
./scripts/poetry-wrapper.sh run mypy --version

# 5. Verify no permission issues
ls -la backend/ | grep -v "root.*root"
```

## Expected Results After Fix

### ✅ Proper Environment Separation:
```
Local Poetry Environment:
├── Path: ~/.cache/pypoetry/virtualenvs/snowflake-mcp-lambda-[hash]
├── Permissions: user:user
└── Managed by: Poetry system

Docker Poetry Environment:
├── Path: /app/.docker-venv (or /app/.venv)
├── Permissions: root:root
└── Managed by: Docker container
```

### ✅ Behavior Changes:
- **No more permission errors** when switching between environments
- **No sudo required** for Poetry operations
- **Environments don't interfere** with each other
- **Pre-commit hooks work** consistently
- **Package versions remain consistent** across environments

## Validation Checklist

- [ ] `poetry config virtualenvs.in-project` returns `false`
- [ ] `poetry env info` shows path in `~/.cache/pypoetry/virtualenvs/`
- [ ] `ls -la backend/` shows no `.venv` directory with root permissions
- [ ] `poetry show redis` works without permission errors
- [ ] Docker environment still works: `docker compose exec backend poetry --version`
- [ ] Pre-commit hooks pass: `pre-commit run --all-files`
- [ ] No `sudo` required for any Poetry operations

## Why This Solution Works

### 🎯 **Separation of Concerns:**
- **Local development** uses Poetry's standard environment management
- **Docker containers** use isolated container-specific environments
- **No shared directories** that cause permission conflicts

### 🔒 **Security Benefits:**
- **No sudo required** for development tasks
- **Proper file permissions** maintained
- **No root-owned files** in development directory

### 🚀 **Developer Experience:**
- **Consistent behavior** across team members
- **Standard Poetry workflows** work as expected
- **No manual permission fixes** required
- **Faster environment setup** and switching

## Common Failure Points & Solutions

**"poetry env info fails"**
```bash
cd backend && poetry install --no-interaction
```

**"Still seeing .venv in project"**
```bash
poetry config virtualenvs.in-project false
poetry env remove --all
poetry install --no-interaction
```

**"Docker environment broken"**
```bash
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

**"Pre-commit still fails"**
```bash
pre-commit clean
pre-commit install --install-hooks
```

This solution follows **industry best practices** for multi-environment Python development and eliminates the permission conflicts permanently.
