#!/bin/bash
# ABOUTME: Wrapper script to ensure poetry is in PATH for pre-commit hooks
# ABOUTME: Solves the "poetry not found" issue in git hooks

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

# Execute poetry with all arguments passed to this script
exec poetry "$@"
