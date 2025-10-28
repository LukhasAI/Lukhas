# Security Policy

## Reporting a Vulnerability

**LUKHAS AI takes security seriously.** We appreciate your efforts to responsibly disclose security concerns.

### How to Report

**Email**: security@lukhas.ai

**Do NOT**:
- Open public GitHub issues for security vulnerabilities
- Disclose details publicly before receiving confirmation

**DO**:
- Provide detailed description of the vulnerability
- Include steps to reproduce (if applicable)
- Suggest potential fixes (if you have them)
- Include your contact information for follow-up

### Response Timeline

- **Initial Response**: Within 72 hours of report
- **Status Update**: Within 7 days (assessment complete)
- **Fix Timeline**: Depends on severity (see below)
- **Public Disclosure**: Coordinated with reporter after fix deployed

### Severity Levels

**Critical** (Fix within 24-48 hours):
- Remote code execution
- Privilege escalation to admin/root
- Exposure of secrets/credentials
- Data breach affecting user privacy

**High** (Fix within 7 days):
- Authentication bypass
- Sensitive data exposure
- Denial of service affecting availability

**Medium** (Fix within 30 days):
- CSRF vulnerabilities
- Information disclosure (non-sensitive)
- Rate limit bypass

**Low** (Fix within 90 days):
- Security misconfigurations
- Missing security headers
- Low-impact information leaks

## Security Measures

### Code Security

- **Static Analysis**: CodeQL runs on every PR and weekly schedule
- **Dependency Scanning**: Dependabot monitors for CVEs daily
- **Secret Detection**: detect-secrets + gitleaks on all commits
- **License Compliance**: liccheck enforces approved licenses

### API Security

- **Authentication**: Bearer token required for all write operations
- **Rate Limiting**: Enforced at 20 req/sec (responses), 50 req/sec (embeddings)
- **CORS**: Strict origin validation in production
- **PII Redaction**: Automatic email/token masking in logs

### Operational Security

- **Least Privilege**: Non-root containers, separate service accounts
- **Audit Logging**: All authentication events logged with retention
- **Encrypted Transit**: TLS 1.3 required in production
- **Secure Defaults**: All security features enabled by default

### Supply Chain Security

- **SBOM**: CycloneDX bill of materials generated for all releases
- **Provenance**: GitHub SLSA attestations on release artifacts
- **Pinned Dependencies**: requirements.txt uses exact versions
- **Container Scanning**: Automated vulnerability scanning on Docker images

## Scope

### In Scope

- LUKHAS AI platform code (lukhas/, candidate/, core/, matriz/)
- API endpoints (OpenAI façade, internal APIs)
- Authentication system (ΛiD)
- Guardian policy enforcement
- CI/CD pipelines
- Container images
- Documentation (if it creates security risks)

### Out of Scope

- Third-party services (OpenAI, Anthropic, Google APIs)
- User-provided content/prompts
- Social engineering attacks
- Physical security
- Denial of service (rate limits are enforced)

## Safe Harbor

We support safe harbor for security researchers who:

1. Make good faith effort to avoid privacy violations and service disruption
2. Report vulnerabilities promptly via security@lukhas.ai
3. Allow reasonable time for fixes before public disclosure
4. Do not exploit vulnerabilities beyond proof-of-concept

**We will not pursue legal action** against researchers who follow these guidelines.

## Security Updates

### Current Security Advisories

**🔴 CVE-2025-8869**: pip Arbitrary File Overwrite (HIGH)  
**Status**: Monitoring - Awaiting pip 25.3 release  
**Impact**: LUKHAS uses pip 24.0 (not affected)  
**Action**: Monitor for pip 25.3 release and upgrade when available  
📖 **Details**: [docs/security/CVE-2025-8869-PIP-ADVISORY.md](docs/security/CVE-2025-8869-PIP-ADVISORY.md)

### Update Notifications

- **Critical/High**: Announced via GitHub Security Advisories
- **Medium/Low**: Included in release notes
- **Patches**: Backported to supported versions (current + previous major)

## Bug Bounty

**Status**: Coming soon

We plan to launch a bug bounty program in Q1 2026. Details will be announced on:
- [GitHub Discussions](https://github.com/lukhas-ai/lukhas/discussions)
- security@lukhas.ai mailing list

## Security Team

For security-related questions (non-vulnerabilities):
- **General**: security@lukhas.ai
- **Partnerships**: partnerships@lukhas.ai
- **Compliance**: compliance@lukhas.ai

## PGP Key

Coming soon: security@lukhas.ai PGP public key for encrypted reports.

---

**Last Updated**: 2025-10-12
**Policy Version**: 1.0
