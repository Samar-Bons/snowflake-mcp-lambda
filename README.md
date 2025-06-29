# snowflake-mcp-lambda
A remote MCP Server for Snowflake. Deployed as a AWS Lambda Function

## 🚀 Developer Setup (REQUIRED)

**IMPORTANT**: Our pre-commit hooks exactly mirror CI. This means longer commit times but zero CI failures.

```bash
# One-time setup (takes ~2 minutes)
./scripts/setup-dev.sh

# That's it! All commits will now run the same checks as CI:
# - Ruff linting & formatting
# - MyPy type checking
# - Full pytest suite with 85% coverage requirement
# - Security scanning
```

### Why Full CI Parity in Pre-commit?

1. **No CI Debugging**: Fix issues locally, not through CI logs
2. **Resource Efficiency**: Don't waste CI minutes on preventable failures
3. **Guaranteed Success**: If it commits locally, it passes CI
4. **Better DX**: Immediate feedback, no context switching

Yes, commits take 30-60 seconds. But that's better than 5-10 minute CI debug cycles.
