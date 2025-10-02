# Ollama Security Integration for LUKHAS AI

## Overview

LUKHAS AI now includes automated security vulnerability analysis and fixing powered by local Ollama models. This integration provides:

- 🤖 **AI-powered vulnerability analysis** using local LLMs
- 🔧 **Automated fix generation** with intelligent recommendations
- 🛡️ **Pre-commit security checks** to prevent vulnerable code
- 📊 **Post-commit security reports** for audit trails
- 🚀 **Zero external API calls** - everything runs locally

## Quick Start

### 1. Initial Setup

```bash
# Install and setup Ollama security
make security-ollama-setup

# This will:
# - Install Ollama if not present (via Homebrew)
# - Start the Ollama service
# - Pull the deepseek-coder:6.7b model for analysis
```

### 2. Run Security Analysis

```bash
# Run AI-powered security analysis
make security-ollama

# This will:
# - Scan for vulnerabilities using pip-audit and safety
# - Analyze each vulnerability with Ollama
# - Generate detailed risk assessments
# - Provide fix recommendations
# - Create a fix script
```

### 3. Auto-Fix Vulnerabilities

```bash
# Automatically fix vulnerabilities
make security-ollama-fix

# This will:
# - Analyze vulnerabilities
# - Generate fix commands
# - Optionally execute fixes (with confirmation)
```

## Git Hooks Integration

### Pre-commit Hook

The pre-commit hook automatically runs on every commit to:

1. **Check if Ollama is running** (starts it if not)
2. **Scan for critical vulnerabilities**
3. **Block commits with critical security issues**
4. **Warn about high-severity issues**
5. **Check for sensitive data** (API keys, secrets)

If vulnerabilities are found, the commit is blocked with helpful fix instructions.

### Post-commit Hook

The post-commit hook (on main branch only):

1. **Generates security reports** in background
2. **Logs commit info** for security audit
3. **Saves reports** to `.lukhas_audit/security-reports/`

## How It Works

### 1. Vulnerability Detection

The system uses two tools for comprehensive scanning:
- **pip-audit**: Checks Python packages against PyPI vulnerability database
- **safety**: Checks against Safety DB vulnerability database

### 2. Ollama Analysis

For each vulnerability, Ollama provides:
- **Risk Assessment**: Brief evaluation of the security impact
- **Fix Command**: Exact pip command to resolve the issue
- **Breaking Changes**: Potential compatibility issues
- **Alternatives**: Suggested alternative packages if needed

### 3. Fix Generation

Ollama generates a complete bash script that:
- Creates backups of requirements files
- Updates vulnerable packages safely
- Tests imports after updates
- Provides rollback capability

## Configuration

### Ollama Model Selection

The default model is `deepseek-coder:6.7b`, optimized for code analysis. You can change it in `scripts/ollama_security_analyzer.py`:

```python
self.model = "deepseek-coder:6.7b"  # Change to your preferred model
```

### Recommended Models

| Task | Model | Size | Speed |
|------|-------|------|-------|
| Code Analysis | deepseek-coder:6.7b | 4GB | Fast |
| Quick Fixes | qwen2.5-coder:1.5b | 1GB | Very Fast |
| Detailed Analysis | codellama:13b | 8GB | Moderate |

### Security Thresholds

Edit the pre-commit hook (`.git/hooks/pre-commit`) to adjust:

```bash
# Currently blocks on CRITICAL, warns on HIGH
# Adjust these checks as needed
```

## Manual Usage

### Command Line Interface

```bash
# Scan for vulnerabilities
python3 scripts/ollama_security_analyzer.py scan

# Auto-fix vulnerabilities
python3 scripts/ollama_security_analyzer.py fix

# Pre-commit mode (quick check)
python3 scripts/ollama_security_analyzer.py pre-commit
```

### Options

```bash
# Save report to file
python3 scripts/ollama_security_analyzer.py scan --save-report report.json

# Output as JSON
python3 scripts/ollama_security_analyzer.py scan --json-output
```

## Security Reports

Reports are automatically saved to `.lukhas_audit/security-reports/` with:

- Timestamp
- Vulnerability count by severity
- Detailed Ollama analysis
- Generated fix scripts
- Commit association (if from post-commit)

### Report Structure

```json
{
  "status": "vulnerable",
  "count": 5,
  "critical": 1,
  "high": 2,
  "analyses": {
    "package-name": {
      "risk_assessment": "...",
      "fix_command": "pip install --upgrade package-name==2.0.0",
      "breaking_changes": "...",
      "alternatives": ["..."]
    }
  },
  "fix_script": "#!/bin/bash\n...",
  "timestamp": "2025-08-21T20:30:00"
}
```

## Troubleshooting

### Ollama Not Running

```bash
# Start Ollama manually
ollama serve

# Or use our setup command
make security-ollama-setup
```

### Model Not Available

```bash
# Pull model manually
ollama pull deepseek-coder:6.7b
```

### Hook Not Working

```bash
# Ensure hooks are executable
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/post-commit

# Test pre-commit hook
.git/hooks/pre-commit
```

### Slow Analysis

For faster analysis, use a smaller model:

```bash
# Edit scripts/ollama_security_analyzer.py
self.model = "qwen2.5-coder:1.5b"  # Faster, smaller model
```

## Best Practices

1. **Regular Scans**: Run `make security-ollama` weekly
2. **Review Fix Scripts**: Always review generated scripts before execution
3. **Update Models**: Keep Ollama models updated with `ollama pull`
4. **Audit Reports**: Review security reports in `.lukhas_audit/`
5. **Custom Rules**: Add project-specific security checks to hooks

## Integration with CI/CD

### GitHub Actions

```yaml
- name: Ollama Security Check
  run: |
    # Install Ollama (Linux)
    curl -fsSL https://ollama.ai/install.sh | sh

    # Start Ollama
    ollama serve &
    sleep 5

    # Pull model
    ollama pull deepseek-coder:6.7b

    # Run security check
    make security-ollama
```

### GitLab CI

```yaml
security-check:
  script:
    - apt-get update && apt-get install -y curl
    - curl -fsSL https://ollama.ai/install.sh | sh
    - ollama serve &
    - sleep 5
    - ollama pull deepseek-coder:6.7b
    - make security-ollama
```

## Privacy & Security

- ✅ **100% Local**: All analysis happens on your machine
- ✅ **No Data Sharing**: No vulnerability data sent to external services
- ✅ **Offline Capable**: Works without internet (after model download)
- ✅ **Audit Trail**: All actions logged locally

## Performance

Typical performance on M1 Mac:

| Operation | Time |
|-----------|------|
| Quick Scan | 2-5 seconds |
| Full Analysis (5 vulns) | 30-60 seconds |
| Fix Generation | 10-20 seconds |
| Model Loading | 5-10 seconds (first run) |

## Future Enhancements

- [ ] Support for multiple programming languages
- [ ] Custom vulnerability rules
- [ ] Integration with dependency update bots
- [ ] Vulnerability trend analysis
- [ ] Automated PR creation for fixes

---

**LUKHAS AI Security** - Powered by Local AI 🤖🛡️
*Constellation Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian*
