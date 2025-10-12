# Fixing Security Vulnerabilities

**Purpose**: Guide for addressing security vulnerabilities detected by automated scans.

**Tools Used**:
- **pip-audit**: CVE vulnerability scanner for Python dependencies
- **bandit**: Python static security analyzer
- **gitleaks**: Secret detection scanner

---

## Pip Audit Findings (CVE Vulnerabilities)

### What It Detects

Pip-audit scans your Python dependencies for known Common Vulnerabilities and Exposures (CVEs) from:
- PyPI Advisory Database
- OSV (Open Source Vulnerabilities)
- GitHub Security Advisories

### How to Review Results

```bash
# Run locally
pip install pip-audit
pip-audit -f json -o docs/audits/pip_audit.json

# Check results
cat docs/audits/pip_audit.json | jq '.vulnerabilities | length'
cat docs/audits/pip_audit.json | jq '.vulnerabilities[]'
```

### Common Fixes

**1. Update Vulnerable Package**

```bash
# Check current version
pip show <package-name>

# Update to patched version
pip install --upgrade <package-name>

# Update requirements
pip freeze | grep <package-name> >> requirements.txt
```

**2. Check for Patches**

Visit the package's security advisories:
- GitHub: `https://github.com/<owner>/<repo>/security/advisories`
- PyPI: `https://pypi.org/project/<package-name>/`

**3. No Fix Available**

If no patched version exists:

1. **Document the Risk**: Add to `.pip-audit-ignore.json`
   ```json
   {
     "vulnerabilities": [
       {
         "id": "CVE-2024-XXXXX",
         "package": "vulnerable-package",
         "version": "1.2.3",
         "reason": "No fix available, risk accepted because...",
         "expires": "2025-12-31"
       }
     ]
   }
   ```

2. **Implement Mitigations**:
   - Use secure configuration options
   - Add input validation
   - Limit exposure surface

3. **Find Alternatives**: Search for safer packages:
   ```bash
   pip search <functionality>
   ```

### Example: Fixing a CVE

```bash
# Vulnerability found: urllib3 < 2.0.0
# Fix: Update to patched version

# 1. Check impact
pip-audit --desc urllib3

# 2. Check dependencies
pip show urllib3

# 3. Update
pip install --upgrade 'urllib3>=2.0.0'

# 4. Verify fix
pip-audit --package urllib3
```

---

## Bandit Findings (Python Security Issues)

### What It Detects

Bandit performs static analysis to find common security issues:
- Hardcoded passwords/secrets
- Insecure functions (e.g., `eval`, `exec`)
- SQL injection risks
- Insecure deserialization (`pickle`)
- Weak cryptography
- Subprocess vulnerabilities

### How to Review Results

```bash
# Run locally
pip install bandit
bandit -r lukhas matriz core -f sarif -o docs/audits/bandit.sarif

# View results (JSON format for parsing)
bandit -r lukhas matriz core -f json -o docs/audits/bandit.json
cat docs/audits/bandit.json | jq '.results[]'

# View in terminal (human-readable)
bandit -r lukhas matriz core
```

### Common Issues & Fixes

#### B101: Assert Used

**Issue**: `assert` statements are removed in optimized Python bytecode (`-O` flag).

**Bad**:
```python
def withdraw(amount):
    assert amount > 0, "Amount must be positive"
    # ... withdraw logic
```

**Good**:
```python
def withdraw(amount):
    if amount <= 0:
        raise ValueError("Amount must be positive")
    # ... withdraw logic
```

#### B301: Pickle Usage

**Issue**: Pickle can execute arbitrary code during deserialization.

**Bad**:
```python
import pickle
data = pickle.loads(untrusted_input)
```

**Good**:
```python
import json
data = json.loads(untrusted_input)
# or for complex objects: use msgpack, protobuf, etc.
```

#### B603: Subprocess Without shell=False

**Issue**: Using `shell=True` can lead to command injection.

**Bad**:
```python
import subprocess
subprocess.run(f"ls {user_input}", shell=True)
```

**Good**:
```python
import subprocess
subprocess.run(["ls", user_input], shell=False, check=True)
```

#### B105/B106: Hardcoded Passwords

**Issue**: Passwords/tokens in source code are easily discovered.

**Bad**:
```python
API_KEY = "sk-1234567890abcdef"
db_password = "secret123"
```

**Good**:
```python
import os
API_KEY = os.getenv("API_KEY")
db_password = os.getenv("DB_PASSWORD")
```

#### B608: SQL Injection

**Issue**: String interpolation in SQL queries allows injection attacks.

**Bad**:
```python
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)
```

**Good**:
```python
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
# or with SQLAlchemy: use parameterized queries
```

### Suppressing False Positives

Use inline comments for legitimate cases:

```python
# nosec B603
subprocess.run(command, shell=True)  # Safe: command is hardcoded constant
```

Or configure in `.bandit`:
```yaml
exclude_dirs:
  - tests/
  - docs/

skips:
  - B101  # Skip assert_used in test files
```

---

## Gitleaks Findings (Secrets Detection)

### What It Detects

Gitleaks scans for accidentally committed secrets:
- API keys (AWS, OpenAI, GitHub, etc.)
- Private keys (SSH, GPG, TLS)
- Database credentials
- OAuth tokens
- Generic secrets (high-entropy strings)

### How to Review Results

Gitleaks outputs SARIF format in CI:

```bash
# Download artifact from CI
gh run download <run-id> -n gitleaks-report

# View results
cat gitleaks-report.sarif | jq '.runs[0].results[]'
```

### Fixing Leaked Secrets

**CRITICAL**: If a real secret was committed:

1. **Rotate the Secret IMMEDIATELY**:
   - Generate new API key/token
   - Update environment variables
   - Revoke old secret

2. **Remove from History** (if in recent commits):
   ```bash
   # Use BFG Repo-Cleaner or git-filter-repo
   pip install git-filter-repo
   git filter-repo --path <file-with-secret> --invert-paths
   ```

3. **Add to .gitignore**:
   ```
   .env
   .env.local
   secrets/
   *.pem
   *.key
   ```

4. **Use Environment Variables**:
   ```python
   # Bad
   API_KEY = "sk-abc123..."
   
   # Good
   import os
   API_KEY = os.getenv("API_KEY")
   if not API_KEY:
       raise ValueError("API_KEY environment variable not set")
   ```

5. **Use Secrets Management**:
   - Development: `.env` + `python-dotenv`
   - Production: AWS Secrets Manager, HashiCorp Vault, etc.
   - CI/CD: GitHub Secrets, encrypted environment variables

### False Positives

Add to `.gitleaksignore`:
```
# Test fixtures
tests/fixtures/fake_key.txt:generic-api-key

# Documentation examples
docs/examples/api_example.py:12:generic-api-key
```

---

## Automation & CI Integration

### Pre-Commit Hook

Install pre-commit hooks to catch issues before commit:

```bash
pip install pre-commit

# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: bandit
        name: Bandit Security Check
        entry: bandit
        language: system
        args: ["-c", ".bandit", "-r", "lukhas", "matriz", "core"]
        types: [python]
      
      - id: gitleaks
        name: Gitleaks Secret Detection
        entry: gitleaks
        language: system
        args: ["protect", "--staged"]
        pass_filenames: false
```

Install hooks:
```bash
pre-commit install
```

### CI Workflow

Security scans run automatically on every PR (see `.github/workflows/matriz-validate.yml`):
- **Gitleaks**: Warn-only, uploads SARIF report
- **Pip Audit**: Warn-only, uploads JSON report
- **Bandit**: Warn-only, uploads SARIF report

To enforce (fail build on findings):
1. Remove `continue-on-error: true`
2. Test locally first: `make security-scan`

---

## Best Practices

### 1. Regular Updates

```bash
# Weekly: Update all dependencies
pip list --outdated
pip install --upgrade -r requirements.txt

# Monthly: Full security audit
make security-scan
```

### 2. Dependency Pinning

**requirements.txt**: Pin exact versions for reproducibility
```
fastapi==0.104.1
pydantic==2.5.0
```

**requirements.in**: Use flexible ranges for development
```
fastapi>=0.104,<0.105
pydantic>=2.5,<3.0
```

### 3. Security Champions

Assign security responsibilities:
- **Security Champion**: Review all security findings
- **Dependency Owner**: Keep dependencies updated
- **Incident Responder**: Handle leaked secrets

### 4. Security Training

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [Supply Chain Security](https://slsa.dev/)

---

## Emergency Response

### Leaked Secret Discovered

1. **Rotate immediately** (within 1 hour)
2. **Audit access logs** for unauthorized use
3. **Remove from history** if in recent commits
4. **Document incident** in security log
5. **Review process** to prevent recurrence

### Critical CVE in Dependency

1. **Assess impact**: Does it affect our usage?
2. **Check for hotfix**: Is there a patched version?
3. **Deploy emergency update** if actively exploited
4. **Document workaround** if no fix available
5. **Monitor vendor** for security updates

---

## Resources

- **Pip Audit**: https://github.com/pypa/pip-audit
- **Bandit**: https://bandit.readthedocs.io/
- **Gitleaks**: https://github.com/gitleaks/gitleaks
- **LUKHAS Security Policy**: [SECURITY.md](../../SECURITY.md)
- **CVE Database**: https://cve.mitre.org/
- **OSV Database**: https://osv.dev/

---

**Last Updated**: 2025-10-12  
**Owner**: Security Team  
**Review Frequency**: Quarterly
