#!/bin/bash
# ABOUTME: Developer environment setup script that ensures CI parity
# ABOUTME: Installs dependencies and configures pre-commit hooks to match CI exactly

set -euo pipefail

echo "🚀 Setting up development environment for Snowflake MCP Lambda"
echo "============================================================"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.10"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "❌ Error: Python 3.10+ is required (found Python $PYTHON_VERSION)"
    exit 1
fi
echo "✅ Python version check passed ($PYTHON_VERSION)"

# Install Poetry if not present
if ! command -v poetry &> /dev/null; then
    echo "📦 Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi
echo "✅ Poetry is installed"

# Install project dependencies
echo "📚 Installing project dependencies..."
poetry install --with dev

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
poetry run pre-commit install

# Run all pre-commit hooks to verify setup
echo "🧪 Running all pre-commit hooks to verify setup..."
echo "   This will take a few minutes but ensures your environment matches CI exactly."
echo "   Future commits will only run on changed files and be much faster."
echo ""

if poetry run pre-commit run --all-files; then
    echo ""
    echo "✅ Success! Your development environment is ready."
    echo ""
    echo "📝 Important Notes:"
    echo "   - Pre-commit hooks will run automatically on every commit"
    echo "   - This includes: ruff, mypy, pytest with coverage, and security checks"
    echo "   - Commits will be blocked if any check fails (same as CI)"
    echo "   - Use 'git commit --no-verify' to skip checks in emergencies only"
    echo ""
    echo "💡 Tips:"
    echo "   - Run 'poetry run pre-commit run --all-files' to test all files"
    echo "   - Run 'poetry run pytest' to run tests manually"
    echo "   - Run 'poetry run ruff check backend/' to lint manually"
else
    echo ""
    echo "⚠️  Warning: Some pre-commit checks failed."
    echo "   This is expected if there are existing issues in the codebase."
    echo "   Fix the issues above before committing."
fi

echo ""
echo "🎯 Next steps:"
echo "   1. Fix any issues reported above"
echo "   2. Try making a commit - all checks will run automatically"
echo "   3. Your commits will now match CI behavior exactly!"
