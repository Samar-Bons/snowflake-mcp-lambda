# Security Policy

## Vulnerability Scanning

This project uses automated security scanning through GitHub Actions:

### Trivy Vulnerability Scanner
- **Tool**: Aqua Security Trivy
- **Scope**: Filesystem scan for vulnerabilities in dependencies
- **Output**: SARIF format uploaded to GitHub Security tab
- **Frequency**: On every push to main and pull requests

### Required Permissions
The security scanning workflow requires specific GitHub Actions permissions:
- `security-events: write` - Upload SARIF results to Security tab
- `actions: read` - Read workflow metadata
- `contents: read` - Access repository content

### Viewing Security Results
1. Navigate to the **Security** tab in the GitHub repository
2. Click on **Code scanning alerts** to view Trivy findings
3. Review and triage any reported vulnerabilities

## Reporting Security Issues

If you discover a security vulnerability, please:
1. **Do NOT** open a public issue
2. Email security concerns to the maintainers
3. Include detailed steps to reproduce the issue
4. Allow time for assessment and remediation

## Security Best Practices

This project follows security best practices:
- Regular dependency updates
- Automated vulnerability scanning
- Secure secrets management (environment variables)
- Input validation and sanitization
- Least privilege Docker containers
- Regular security audits
