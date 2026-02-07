# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in PitchCube, please report it responsibly:

1. **DO NOT** create a public GitHub issue
2. Email security concerns to: [your-security-email@example.com]
3. Allow reasonable time for response before public disclosure

## Security Best Practices

### Environment Variables

- **NEVER** commit `.env` files to Git
- **ALWAYS** use `.env.example` as a template
- **ROTATE** API keys regularly
- **USE** different keys for different environments

### API Keys Management

```bash
# Generate a secure JWT secret
openssl rand -base64 32

# Generate a secure encryption key
openssl rand -base64 32
```

### Production Deployment

1. Use environment-specific configuration
2. Enable HTTPS only
3. Set secure HTTP headers
4. Use a secrets manager (AWS Secrets Manager, Azure Key Vault, etc.)
5. Enable rate limiting
6. Monitor API key usage

### Pre-commit Security Check

Before committing code, run:

```bash
# Check for common secrets patterns
grep -r "sk-" . --include="*.py" --include="*.js" --include="*.env" 2>/dev/null | grep -v ".example"

# Check for hardcoded passwords
grep -r "password.*=" . --include="*.py" --include="*.js" 2>/dev/null | grep -v "example\|template"
```

## Sensitive Files Checklist

Ensure these files are in `.gitignore`:

- [ ] `.env`
- [ ] `.env.local`
- [ ] `.env.*.local`
- [ ] `*.key`
- [ ] `*.pem`
- [ ] `credentials.json`
- [ ] `secrets/`

## Security Checklist for GitHub

Before pushing to GitHub:

- [ ] No real API keys in code
- [ ] No passwords in configuration files
- [ ] `.gitignore` properly configured
- [ ] `.env.example` provided as template
- [ ] No sensitive data in commit history
- [ ] Dependencies up to date

## Compliance

This project follows security best practices for:
- OWASP Top 10
- API security guidelines
- Data protection standards

Last updated: 2026-02-05
