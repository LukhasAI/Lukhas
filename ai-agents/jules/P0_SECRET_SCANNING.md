# Jules Task: Add Secret Scanning (SC003)

**Task ID**: SC003
**Priority**: P0 (Critical - Security)
**Effort**: Small (<4 hours)
**Owner**: Jules
**Branch**: `security/gitleaks-secret-scanning`

---

## Objective

Integrate **Gitleaks** secret scanning into CI/CD pipeline to prevent accidental commit of secrets, API keys, and credentials.

---

## Context

Currently no automated secret scanning in CI/CD pipeline. Need to:
1. Add Gitleaks to GitHub Actions workflow
2. Scan all commits for secrets
3. Block PRs containing secrets
4. Create baseline for existing secrets (if any)
5. Add pre-commit hook for local scanning

**Security Impact**: Critical - prevents credential leaks, API key exposure

---

## Implementation Requirements

### 1. Add Gitleaks GitHub Action

**File**: `.github/workflows/security-scan.yml` (create new or add to existing)

```yaml
name: Security Scanning

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]
  schedule:
    # Run daily at 2 AM UTC
    - cron: '0 2 * * *'

jobs:
  secret-scan:
    name: Gitleaks Secret Scan
    runs-on: ubuntu-latest

    permissions:
      contents: read
      pull-requests: write
      security-events: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for comprehensive scan

      - name: Run Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}  # Optional for pro features

      - name: Upload SARIF report
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif
          category: gitleaks

      - name: Fail on secrets found
        if: steps.gitleaks.outputs.exitCode == 1
        run: |
          echo "::error::Secrets detected in codebase!"
          exit 1
```

### 2. Create Gitleaks Configuration

**File**: `.gitleaks.toml`

```toml
# Gitleaks configuration for LUKHAS AI
title = "LUKHAS Secret Scanning"

[extend]
# Use default ruleset and extend with custom rules
useDefault = true

[[rules]]
# Anthropic API Key
id = "anthropic-api-key"
description = "Anthropic Claude API Key"
regex = '''sk-ant-[a-zA-Z0-9-_]{95}'''
tags = ["key", "anthropic"]

[[rules]]
# OpenAI API Key
id = "openai-api-key"
description = "OpenAI API Key"
regex = '''sk-[a-zA-Z0-9]{48}'''
tags = ["key", "openai"]

[[rules]]
# Google API Key
id = "google-api-key"
description = "Google API Key"
regex = '''AIza[0-9A-Za-z-_]{35}'''
tags = ["key", "google"]

[[rules]]
# AWS Access Key
id = "aws-access-key"
description = "AWS Access Key ID"
regex = '''AKIA[0-9A-Z]{16}'''
tags = ["key", "aws"]

[[rules]]
# GitHub Personal Access Token
id = "github-pat"
description = "GitHub Personal Access Token"
regex = '''ghp_[a-zA-Z0-9]{36}'''
tags = ["key", "github"]

[[rules]]
# Generic High Entropy Strings (catch-all)
id = "high-entropy-string"
description = "High entropy string (possible secret)"
regex = '''[a-zA-Z0-9+/]{40,}'''
entropy = 4.5  # Minimum entropy threshold
tags = ["generic"]

# Allowlist for false positives
[[allowlist]]
# Test fixtures and example configs
paths = [
    '''tests/fixtures/.*\.json''',
    '''examples/.*\.yaml''',
    '''docs/examples/.*'''
]

[[allowlist]]
# Known safe patterns
regexes = [
    # Placeholder values
    '''YOUR_API_KEY_HERE''',
    '''REPLACE_WITH_.*''',
    '''<YOUR_.*>''',
    # Test values
    '''test-api-key-.*''',
    '''fake-.*-key''',
]

[[allowlist]]
# Specific commits (baseline)
commits = [
    # Add commit SHAs of known safe commits with existing "secrets"
    # "abc123def456",
]
```

### 3. Add Pre-commit Hook

**File**: `.pre-commit-config.yaml` (add or create)

```yaml
repos:
  # Gitleaks pre-commit hook
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.4
    hooks:
      - id: gitleaks

  # Other pre-commit hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
```

**Installation Instructions** (`docs/SECURITY_SETUP.md`):

```markdown
## Pre-commit Hook Installation

Install pre-commit hooks to scan for secrets before committing:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

Hooks will now run automatically on `git commit`.
```

### 4. Create Baseline (If Needed)

**Script**: `scripts/security/create_gitleaks_baseline.sh`

```bash
#!/bin/bash
# Create baseline of existing "secrets" to ignore

set -e

echo "Creating Gitleaks baseline..."

# Run gitleaks and save results
gitleaks detect \
    --source . \
    --report-format json \
    --report-path gitleaks-baseline.json \
    --no-git \
    --exit-code 0

echo "Baseline created: gitleaks-baseline.json"
echo "Review this file and add safe commits to .gitleaks.toml allowlist"
```

### 5. Add Secret Rotation Documentation

**File**: `docs/security/SECRET_ROTATION.md`

```markdown
# Secret Rotation Procedures

## If Secrets are Detected

1. **Immediately Revoke** the exposed secret
2. **Generate New** secret/API key
3. **Update** application configuration
4. **Verify** old secret no longer works
5. **Notify** security team

## Rotation Checklist

- [ ] Secret revoked in provider (AWS, Anthropic, etc.)
- [ ] New secret generated
- [ ] GitHub Secrets updated
- [ ] Environment variables updated in production
- [ ] Old secret confirmed invalid
- [ ] Incident logged

## Emergency Contacts

- **Security Team**: security@lukhas.ai
- **On-call**: [PagerDuty link]
```

---

## Testing Requirements

### 1. Test Secret Detection

**File**: `tests/security/test_secret_scanning.py`

```python
import subprocess
import pytest
from pathlib import Path

def test_gitleaks_detects_api_keys():
    """Test that Gitleaks detects common API key patterns."""
    # Create temporary file with fake secret
    test_file = Path("test_secret_file.py")
    test_file.write_text("""
# This is a test file with a fake API key
API_KEY = "sk-ant-api03-abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnop"
    """)

    try:
        # Run gitleaks on test file
        result = subprocess.run(
            ["gitleaks", "detect", "--no-git", "--source", str(test_file)],
            capture_output=True,
            text=True
        )

        # Should detect the secret (exit code 1)
        assert result.returncode == 1
        assert "anthropic-api-key" in result.stdout or "api" in result.stdout.lower()

    finally:
        test_file.unlink()

def test_gitleaks_allows_safe_patterns():
    """Test that Gitleaks ignores allowed patterns."""
    test_file = Path("test_safe_file.py")
    test_file.write_text("""
# This is safe - placeholder
API_KEY = "YOUR_API_KEY_HERE"
SECRET = "REPLACE_WITH_YOUR_KEY"
    """)

    try:
        result = subprocess.run(
            ["gitleaks", "detect", "--no-git", "--source", str(test_file)],
            capture_output=True,
            text=True
        )

        # Should NOT detect (exit code 0)
        assert result.returncode == 0

    finally:
        test_file.unlink()
```

### 2. CI/CD Integration Test

**File**: `tests/ci/test_security_workflow.yml`

```yaml
name: Test Security Workflow

on: [push, pull_request]

jobs:
  test-gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Verify Gitleaks config exists
        run: |
          test -f .gitleaks.toml

      - name: Test Gitleaks runs successfully
        run: |
          docker run --rm -v "$PWD:/path" zricethezav/gitleaks:latest \
            detect --source="/path" --config="/path/.gitleaks.toml" --no-git
```

---

## Acceptance Criteria

- [ ] Gitleaks integrated into GitHub Actions workflow
- [ ] `.gitleaks.toml` configuration with LUKHAS-specific rules
- [ ] Pre-commit hook installed and documented
- [ ] PRs blocked if secrets detected
- [ ] SARIF reports uploaded to GitHub Security tab
- [ ] Baseline created for existing "safe" secrets (if any)
- [ ] Secret rotation procedures documented
- [ ] Daily scheduled scans configured
- [ ] Tests validate detection and allowlist

---

## Rollout Plan

1. **Phase 1**: Add workflow in non-blocking mode (warnings only)
2. **Phase 2**: Create baseline and review findings
3. **Phase 3**: Enable blocking mode (fail PRs)
4. **Phase 4**: Add pre-commit hooks team-wide
5. **Phase 5**: Enable daily scheduled scans

---

## Monitoring

**GitHub Actions** will provide:
- Secret detection count per PR
- SARIF reports in Security tab
- Failed builds for PRs with secrets

**Metrics to track**:
- Secrets detected per month
- False positive rate
- Time to resolve detected secrets

---

## References

- **Gitleaks Documentation**: https://github.com/gitleaks/gitleaks
- **GitHub Secret Scanning**: https://docs.github.com/en/code-security/secret-scanning
- **OWASP Secrets Management**: https://owasp.org/www-community/Secrets_Management

---

**Estimated Completion**: 2-3 hours
**PR Target**: Ready for review within 1 day
**Security Impact**: HIGH - Critical for preventing credential leaks
