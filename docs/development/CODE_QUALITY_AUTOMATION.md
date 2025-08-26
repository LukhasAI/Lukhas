# Code Quality Automation Guide

## Overview

This document describes the automated code quality system implemented for LUKHAS . The system provides comprehensive linting, formatting, testing, and monitoring capabilities to maintain high code standards with minimal manual intervention.

## Quick Start

### Initial Setup
```bash
# Install all dependencies and setup hooks
make bootstrap

# Fix all existing issues automatically
make fix

# Run tests to verify
make test
```

### Daily Workflow
```bash
# Before committing - smart fix (safe)
make fix    # Smart fix - won't break code
make lint   # Check for remaining issues
make test   # Run tests

# Quick workflow
make quick  # Runs smart fix + test

# If you need aggressive fixing (rare)
make fix-all  # Aggressive fix - use with caution
```

## Components

### 1. Pre-commit Hooks (`.pre-commit-config.yaml`)

Automatically runs on every `git commit`:
- **Black**: Code formatting (79 char line limit)
- **Ruff**: Fast Python linting with auto-fix
- **isort**: Import sorting
- **MyPy**: Type checking
- **Bandit**: Security scanning
- **File checks**: Trailing whitespace, large files, merge conflicts

**Setup:**
```bash
make setup-hooks
# or manually:
pre-commit install
```

**Run manually:**
```bash
pre-commit run --all-files
```

### 2. Makefile Commands

| Command | Description | When to Use |
|---------|-------------|-------------|
| `make fix` | Auto-fix all possible issues | Before committing |
| `make lint` | Check for issues (no fixes) | CI validation |
| `make format` | Format code with Black | Code cleanup |
| `make fix-imports` | Fix import issues only | Import errors |
| `make test` | Run test suite | Before pushing |
| `make test-cov` | Tests with coverage report | PR validation |
| `make ci-local` | Full CI pipeline locally | Before PR |
| `make monitor` | Generate quality dashboard | Weekly review |
| `make quick` | Fix + test combo | Quick validation |

### 3. Configuration Files

#### `pyproject.toml`
Central configuration for all Python tools:
- Black formatting rules
- Ruff linting rules
- isort import sorting
- MyPy type checking
- pytest settings
- Coverage settings

#### Key Settings:
- Line length: 79 characters
- Python version: 3.9+
- Ignored in `__init__.py`: F401, F403 (unused imports)
- Test markers: unit, integration, security, slow

### 4. GitHub Actions (`.github/workflows/code-quality.yml`)

Automated CI/CD pipeline that runs on:
- Push to main/develop branches
- Pull requests
- Daily schedule (2 AM UTC)

**Jobs:**
1. **Lint**: All linting checks with reports
2. **Test**: Test suite with coverage
3. **Auto-fix**: Automatic fixes on PRs
4. **Quality Gate**: Pass/fail determination

### 5. Auto-fix Script (`tools/scripts/auto_fix_linting.py`)

Comprehensive auto-fixing tool:
```bash
python tools/scripts/auto_fix_linting.py
```

**Features:**
- Removes unused imports
- Sorts imports properly
- Formats with Black
- Fixes Ruff issues
- Generates fix report
- Tracks remaining issues

### 6. Quality Dashboard (`tools/scripts/quality_dashboard.py`)

Interactive HTML dashboard with metrics:
```bash
make monitor
# or
python tools/scripts/quality_dashboard.py
```

**Metrics Tracked:**
- Overall health score (0-100)
- Linting issues (Flake8, Ruff)
- Type errors (MyPy)
- Test coverage
- Code complexity
- Security issues (Bandit)
- Lines of code statistics

**Output:**
- `test_results/quality_dashboard.html` - Visual dashboard
- `test_results/quality_history.json` - Historical data
- `test_results/linting_report.json` - Detailed fix report

## Common Issues and Solutions

### Issue: "Too many linting errors"
**Solution:**
```bash
make fix  # Auto-fix everything possible
make lint # See what remains (manual fix needed)
```

### Issue: "Pre-commit hook failed"
**Solution:**
```bash
# The hook already fixed the issues, just commit again:
git add -A
git commit -m "your message"
```

### Issue: "Import order incorrect"
**Solution:**
```bash
make fix-imports
# or
isort . --profile black --line-length 79
```

### Issue: "Line too long (E501)"
**Solution:**
```bash
make format
# or
black --line-length 79 .
```

### Issue: "Unused imports (F401)"
**Solution:**
```bash
autoflake --in-place --remove-all-unused-imports --recursive .
```

## Best Practices

### 1. Daily Development
- Run `make quick` before pushing code
- Use `make fix` liberally - it's safe and comprehensive
- Check `make monitor` weekly for trends

### 2. Before Pull Requests
```bash
make ci-local  # Run full CI pipeline
make monitor   # Check quality metrics
```

### 3. Code Review
- PR auto-fix will run automatically
- Quality gate must pass for merge
- Check dashboard for improvement areas

### 4. Configuration Updates
- Edit `pyproject.toml` for tool settings
- Update `.pre-commit-config.yaml` for hook versions
- Modify Makefile for new commands

## Quality Standards

### Target Metrics
- **Linting Issues**: < 50 total
- **Type Errors**: 0
- **Test Coverage**: > 80%
- **Complex Functions**: < 10
- **Security Issues**: 0 high, < 5 medium
- **Health Score**: > 80%

### Enforcement Levels

1. **Local Development** (Pre-commit hooks)
   - Auto-fix on commit
   - Non-blocking warnings

2. **Pull Request** (GitHub Actions)
   - Auto-fix applied
   - Quality report generated
   - Blocking for critical issues

3. **Main Branch** (Protected)
   - Must pass quality gate
   - Coverage requirements
   - No security issues

## Monitoring and Reporting

### Dashboard Access
```bash
# Generate latest dashboard
make monitor

# Open in browser
open test_results/quality_dashboard.html
```

### Historical Tracking
- Metrics saved in `test_results/quality_history.json`
- Last 30 runs preserved
- Trend analysis available

### CI/CD Reports
- Artifacts uploaded to GitHub Actions
- PR comments with quality summary
- Daily scheduled reports

## Troubleshooting

### Tools Not Installed
```bash
make install  # Install all dependencies
```

### Pre-commit Not Working
```bash
pre-commit uninstall
make setup-hooks
```

### Dashboard Generation Fails
```bash
# Install missing tools
pip install flake8 ruff mypy bandit coverage pytest

# Retry
python tools/scripts/quality_dashboard.py
```

## Advanced Usage

### Custom Linting Rules

Add to `pyproject.toml`:
```toml
[tool.ruff]
select = ["E", "F", "YOUR_RULE"]
ignore = ["IGNORED_RULE"]
```

### Skip Pre-commit
```bash
git commit --no-verify -m "emergency fix"
```

### Run Specific Checks
```bash
# Just Black
black --check .

# Just Ruff
ruff check .

# Just MyPy
mypy .
```

### Generate Reports
```bash
# Flake8 HTML report
flake8 . --format=html --htmldir=flake8-report

# Coverage HTML report
pytest --cov --cov-report=html
open htmlcov/index.html
```

## Maintenance

### Update Tools
```bash
# Update pre-commit hooks
pre-commit autoupdate

# Update Python tools
pip install --upgrade black ruff isort mypy flake8 bandit
```

### Review Configuration
- Monthly: Check `pyproject.toml` settings
- Quarterly: Update tool versions
- Yearly: Review quality standards

## Integration with IDEs

### VS Code
Install extensions:
- Python
- Pylance
- Black Formatter
- Ruff
- isort

Settings.json:
```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length=79"],
  "editor.formatOnSave": true,
  "python.linting.mypyEnabled": true
}
```

### PyCharm
1. Settings → Tools → File Watchers
2. Add watchers for Black, isort
3. Enable "Reformat on save"

## Summary

The automated code quality system provides:
- ✅ Automatic fixing of 90%+ of issues
- ✅ Pre-commit prevention of bad code
- ✅ CI/CD enforcement and validation
- ✅ Visual dashboard for monitoring
- ✅ Historical tracking of metrics
- ✅ Single command fixes (`make fix`)

Regular use of these tools ensures consistent, high-quality code with minimal manual effort.
