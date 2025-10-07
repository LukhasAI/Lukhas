---
status: wip
type: documentation
owner: unknown
module: development
redirect: false
moved_to: null
---

# LUKHAS  Diagnostic Issues Resolution Guide

## Problem Summary

You're seeing "unresolved diagnostics" messages during commits because:
1. **17,048 linting errors** exist across the codebase
2. **Pre-commit hooks are configured** but not installed
3. **Backup directories** weren't excluded from linting (fixed in pyproject.toml)

## Root Causes

### 1. Missing Directory Exclusions
The `pyproject.toml` didn't exclude backup directories, causing thousands of false positives:
- `.event_bus_backup*`
- `.hygiene_backup*`
- `._cleanup_archive`
- `archive/`

**Status**: ✅ FIXED - Added exclusions to pyproject.toml

### 2. Active File Issues
Your modified files have real linting errors:
- `monitoring/bio_symbolic_coherence_monitor.py` - 45 errors (mostly long lines)
- `monitoring/endocrine_observability_engine.py` - 21 errors (mostly long lines)

### 3. Pre-commit Not Installed
The `.pre-commit-config.yaml` exists but pre-commit isn't installed/configured:
```bash
# To install pre-commit hooks:
pip install pre-commit
pre-commit install
```

## Quick Fixes

### Fix All Current Issues
```bash
# Auto-fix what's possible
python3 -m ruff check . --fix

# Format with black
python3 -m black .

# Check remaining issues
python3 -m ruff check . --statistics
```

### Fix Specific Files
```bash
# Fix monitoring files
python3 -m ruff check monitoring/ --fix
python3 -m black monitoring/

# Fix long lines in specific file
python3 -m black monitoring/bio_symbolic_coherence_monitor.py --line-length 88
```

### Ignore Long Lines Selectively
Add `# noqa: E501` to lines that must be long:
```python
long_variable_name = "some very long string that exceeds 88 characters"  # noqa: E501
```

## Diagnostic Helper Script

I've created `/fix_diagnostics.sh` to help:
```bash
# Run diagnostic checker
./fix_diagnostics.sh

# Shows:
# - Total errors in codebase
# - Errors in modified files
# - Auto-fixes what it can
# - Provides specific recommendations
```

## Permanent Solution

### 1. Install Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Test on all files
pre-commit run --all-files
```

### 2. Configure IDE/Editor
Add to VS Code settings.json:
```json
{
  "python.linting.ruffEnabled": true,
  "python.linting.enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.linting.ruffArgs": ["--config", "pyproject.toml"]
}
```

### 3. CI/CD Integration
Add to GitHub Actions:
```yaml
- name: Lint with ruff
  run: |
    python -m pip install ruff
    python -m ruff check . --exit-non-zero-on-fix
```

## Current Status

After fixes applied:
- **Reduced from 47,086 to 17,048 errors** (64% reduction)
- Backup directories now excluded
- Monitoring files have unused imports removed
- Long lines remain (need manual review)

## Recommended Actions

1. **Immediate**: Run `./fix_diagnostics.sh` before each commit
2. **Short-term**: Fix long lines in monitoring files
3. **Long-term**: Install pre-commit hooks for automatic checking

## Why This Matters

Clean code = fewer bugs = faster development
- Linting catches real issues (undefined variables, unused imports)
- Consistent formatting improves readability
- Pre-commit hooks prevent bad code from entering repository

---

*Generated: August 2025*
*Tool versions: ruff 0.12.8, black 25.1.0, flake8 7.3.0*
