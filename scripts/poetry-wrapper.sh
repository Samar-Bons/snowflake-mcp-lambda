#!/bin/bash
# ABOUTME: Wrapper script to ensure poetry is in PATH and runs from backend directory
# ABOUTME: Solves the "poetry not found" issue and handles new Poetry file location

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

# Execute poetry with all arguments passed to this script
exec poetry "$@"
