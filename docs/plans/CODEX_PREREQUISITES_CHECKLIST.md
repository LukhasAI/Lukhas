# Codex Prerequisites Checklist

**Purpose**: One-time setup verification before executing Jules documentation tasks
**Estimated Time**: 5-10 minutes
**Last Updated**: 2025-10-19

---

## ✅ Environment Setup

### Python Tools (Required)

```bash
# Install documentation quality tools
pip install pydocstyle interrogate jsonschema pytest

# Verify installation
pydocstyle --version
interrogate --version
pytest --version
```

**Expected Output**:
```
pydocstyle 6.3.0
interrogate 1.7.0
pytest 8.3.3
```

### npm Tools (Required)

```bash
# Install OpenAPI validation tools
npm i -g @apidevtools/swagger-cli @stoplight/spectral-cli redoc-cli

# Verify installation
swagger-cli --version
spectral --version
redoc-cli --version
```

**Expected Output**:
```
swagger-cli 4.x.x
spectral 6.x.x
redoc-cli 0.x.x
```

---

## ✅ Repository Verification

### CI Workflow Exists

```bash
# Confirm matriz-validate workflow exists
ls -la .github/workflows/matriz-validate.yml
```

**Expected Output**:
```
-rw-r--r-- 1 user group 5432 Oct 19 12:00 .github/workflows/matriz-validate.yml
```

### Git Branch Permissions

```bash
# Verify you can create feature branches
git checkout -b test-branch-permissions
git checkout main
git branch -D test-branch-permissions
```

**Expected Output**: No errors

### Workflow Dispatch Permissions

```bash
# Verify workflow_dispatch capability (requires GitHub CLI)
gh workflow list
```

**Expected Output**: List of workflows including `matriz-validate`

---

## ✅ Python Environment

### Virtual Environment Active

```bash
# Check if virtual environment is activated
python -c "import sys; print('venv' if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 'system')"
```

**Expected Output**: `venv` (not `system`)

If not activated:
```bash
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows
```

### Python Version

```bash
python --version
```

**Expected Output**: `Python 3.9.x` or higher (3.11 recommended)

---

## ✅ Documentation Standards

### Docstring Style Configured

```bash
# Confirm pydocstyle config exists
cat > .pydocstyle <<'EOF'
[pydocstyle]
inherit = false
convention = google
match = .*\.py
ignore = D104,D203
EOF

# Verify configuration
pydocstyle --explain
```

**Expected Output**: Configuration help text (no errors)

### Google Docstring Format

**Verify you understand the format**:
```python
def example_function(param1: str, param2: int = 0) -> bool:
    """
    Brief description of function (imperative, <80 chars).

    Extended description if needed, explaining algorithm or context.

    Args:
        param1 (str): Description of param1.
        param2 (int, optional): Description of param2. Defaults to 0.

    Returns:
        bool: True if successful, False otherwise.

    Raises:
        ValueError: If param1 is empty or invalid.

    Example:
        >>> result = example_function("test", 42)
        >>> print(result)
        True
    """
    pass
```

---

## ✅ Repository Context

### Directory Structure Awareness

```bash
# Verify key directories exist
ls -d docs/openapi docs/apis docs/audits scripts api matriz lukhas
```

**Expected Output**: All directories listed (no errors)

### Phase 5B Flat Structure

```bash
# Confirm NO lukhas/ prefix in module paths
find . -name "module.manifest.json" -path "*/lukhas/*" | head -5
```

**Expected Output**: Empty (no files found under `lukhas/` prefix)

**Why?**: Phase 5B removed `lukhas/` directory nesting. All paths are now flat.

---

## ✅ Testing Infrastructure

### Smoke Tests Runnable

```bash
# Verify smoke tests can execute
pytest -q -m smoke --collect-only
```

**Expected Output**: List of ~15 smoke test files (no collection errors)

### MATRIZ Smoke Tests Runnable

```bash
# Verify MATRIZ smoke tests can execute
pytest -q -m matriz_smoke --collect-only
```

**Expected Output**: List of MATRIZ smoke test files (no collection errors)

---

## ✅ Git Configuration

### User Identity Set

```bash
# Verify git user configured
git config user.name
git config user.email
```

**Expected Output**: Your name and email (not empty)

### Default Branch

```bash
# Verify main branch is default
git symbolic-ref refs/remotes/origin/HEAD
```

**Expected Output**: `refs/remotes/origin/main`

---

## ✅ Task Delegation Documents

### Jules Task Files Present

```bash
# Verify all Jules delegation files exist
ls -l docs/plans/JULES_*.md docs/plans/JULES_TASKS_v2.json
```

**Expected Files**:
- `JULES_COMPLETE_TASK_BRIEF_2025-10-19.md`
- `JULES_EXECUTION_STRATEGY.md`
- `JULES_INITIATION_PROMPT.md`
- `JULES_TASKS_v2.json`
- `CODEX_JULES_TASK_BRIEF.md` (this document)

### Codex Task Brief Accessible

```bash
# Open Codex task brief
cat docs/plans/CODEX_JULES_TASK_BRIEF.md | head -20
```

**Expected Output**: First 20 lines of Codex task brief (header section)

---

## ✅ CI/CD Integration

### GitHub CLI Installed

```bash
# Verify gh CLI installed
gh --version
```

**Expected Output**: `gh version 2.x.x` or higher

If not installed:
```bash
# macOS
brew install gh

# Linux (Debian/Ubuntu)
sudo apt install gh

# Authenticate
gh auth login
```

### Repository Remote Configured

```bash
# Verify origin remote configured
git remote -v | grep origin
```

**Expected Output**:
```
origin  https://github.com/yourusername/lukhas (fetch)
origin  https://github.com/yourusername/lukhas (push)
```

---

## ✅ Optional but Recommended

### act (Local CI Testing)

```bash
# Install act for local workflow testing
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash  # Linux

# Verify installation
act --version
```

**Expected Output**: `act version x.x.x`

**Note**: Optional - allows testing CI workflows locally before push

### Pre-commit Hooks

```bash
# Install pre-commit (optional)
pip install pre-commit

# Set up hooks
pre-commit install

# Verify hooks
pre-commit run --all-files --show-diff-on-failure
```

**Note**: Optional - catches issues before commit

---

## ✅ Final Verification

### Full Environment Check Script

```bash
# Run this comprehensive check
cat > /tmp/codex_env_check.sh <<'BASH'
#!/bin/bash
set -e

echo "=== Codex Environment Check ==="

# Python tools
echo "Python: $(python --version)"
echo "pydocstyle: $(pydocstyle --version 2>&1 | head -1)"
echo "interrogate: $(interrogate --version 2>&1 | head -1)"

# npm tools
echo "swagger-cli: $(swagger-cli --version 2>&1)"
echo "spectral: $(spectral --version 2>&1)"
echo "redoc-cli: $(redoc-cli --version 2>&1 || echo 'installed')"

# Git
echo "Git user: $(git config user.name) <$(git config user.email)>"

# GitHub CLI
echo "GitHub CLI: $(gh --version | head -1)"

# Repository
echo "Branch: $(git branch --show-current)"
echo "Remote: $(git remote get-url origin)"

# Virtual env
python -c "import sys; venv = 'venv' if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 'system'; print(f'Virtual env: {venv}')"

echo ""
echo "✅ All prerequisites met!"
BASH

chmod +x /tmp/codex_env_check.sh
/tmp/codex_env_check.sh
```

**Expected Output**: All tools listed with versions, ending with "✅ All prerequisites met!"

---

## ✅ Troubleshooting

### Common Issues

#### Issue: `pydocstyle: command not found`
**Fix**:
```bash
pip install --upgrade pydocstyle
# or
python -m pip install pydocstyle
```

#### Issue: `npm: command not found`
**Fix**:
```bash
# macOS
brew install node

# Linux (Debian/Ubuntu)
sudo apt install nodejs npm
```

#### Issue: `swagger-cli: command not found`
**Fix**:
```bash
# Ensure npm global bin is in PATH
npm config get prefix  # Note the path
export PATH="$(npm config get prefix)/bin:$PATH"

# Retry installation
npm i -g @apidevtools/swagger-cli
```

#### Issue: `gh: command not found`
**Fix**:
```bash
# macOS
brew install gh

# Linux
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Authenticate
gh auth login
```

#### Issue: Virtual environment not activated
**Fix**:
```bash
# Check if .venv exists
ls -d .venv

# Activate
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Verify
which python  # Should show .venv/bin/python
```

---

## ✅ Ready to Execute

Once all checks pass, you are ready to execute the Codex Jules task brief:

1. **Read**: [CODEX_JULES_TASK_BRIEF.md](CODEX_JULES_TASK_BRIEF.md)
2. **Execute**: Follow the 6-phase runbook sequentially
3. **Coordinate**: Tag Claude Code for J-02 and J-04 semantic reviews

---

**Last Updated**: 2025-10-19
**Contact**: LUKHAS AI Team
