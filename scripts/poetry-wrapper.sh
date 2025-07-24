#!/bin/bash
# ABOUTME: Enhanced wrapper script with auto-environment setup for Poetry
# ABOUTME: Ensures Poetry environment exists and is properly configured across all environments

# Add Poetry to PATH if it exists
if [ -d "$HOME/.local/bin" ]; then
    export PATH="$HOME/.local/bin:$PATH"
fi

# Check if poetry is available
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry not found in PATH"
    echo "Please install Poetry or ensure $HOME/.local/bin is in your PATH"
    exit 1
fi

# Store original directory
ORIGINAL_DIR=$(pwd)

# Change to backend directory where pyproject.toml lives
cd "$ORIGINAL_DIR/backend" || exit 1

# Ensure proper Poetry configuration for local development (not in Docker)
if [ -z "$DOCKER_ENV" ]; then
    # Only configure for local (not in Docker)
    poetry config virtualenvs.in-project false >/dev/null 2>&1
    poetry config virtualenvs.path ~/.cache/pypoetry/virtualenvs >/dev/null 2>&1
fi

# Auto-setup Poetry environment if missing or invalid
if ! poetry env info &> /dev/null; then
    echo "Setting up Poetry environment in system location..."

    # Ensure python link exists (for environments without python symlink)
    if ! command -v python &> /dev/null && command -v python3 &> /dev/null; then
        echo "Note: Creating temporary python alias for Poetry compatibility"
        alias python=python3
    fi

    # Configure and install environment
    poetry env use python3 2>/dev/null || poetry env use python || {
        echo "Error: Could not configure Poetry environment"
        echo "Please ensure Python 3.10+ is installed and accessible"
        exit 1
    }

    poetry install --no-interaction || {
        echo "Error: Poetry install failed"
        exit 1
    }

    echo "Poetry environment setup complete"
fi

# Execute poetry with all arguments passed to this script
exec poetry "$@"
