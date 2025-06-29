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

### 🤖 Why This Matters for AI Code Assistants

When working with AI code assistants (like Claude), comprehensive pre-commit hooks are **essential**:

#### The Problem
AI assistants can't directly see CI outputs. When CI fails, the human developer must:
1. Navigate to CI logs
2. Copy error messages
3. Paste them back to the AI
4. Wait for a fix
5. Push again
6. Repeat until green ✅

This creates a frustrating **human-in-the-middle** debugging loop that wastes everyone's time.

#### The Solution
With full CI parity in pre-commit hooks:
- AI assistants get **immediate feedback** on their code
- Errors are caught **before** pushing
- The AI can fix issues **in the same conversation**
- No context switching or copy-pasting required

#### Best Practices for AI-Assisted Development
1. **Make pre-commit hooks comprehensive** - Include all CI checks
2. **Fail fast, fail locally** - Better to wait 60 seconds than debug through logs
3. **Clear error messages** - AI assistants can parse and fix clear errors
4. **No surprises** - What passes locally MUST pass in CI

This approach transforms AI code assistants from "helpful but sometimes frustrating" to "genuinely reliable development partners."
