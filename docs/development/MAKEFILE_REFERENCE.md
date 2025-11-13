# LUKHAS Makefile Reference Guide

**Complete developer command reference for 50+ build system targets**

---

## Table of Contents

- [Quick Start](#quick-start)
- [Architecture Overview](#architecture-overview)
- [Command Categories](#command-categories)
  - [Setup & Installation](#setup--installation)
  - [Development](#development)
  - [Testing](#testing)
  - [Advanced Testing (0.001% Excellence)](#advanced-testing-0001-excellence)
  - [CI/CD](#cicd)
  - [Doctor & Diagnostics](#doctor--diagnostics)
  - [Security](#security)
  - [Policy & Brand](#policy--brand)
  - [SDK Development](#sdk-development)
  - [Backup & Disaster Recovery](#backup--disaster-recovery)
  - [Code Quality](#code-quality)
  - [Performance & Monitoring](#performance--monitoring)
  - [Lane Guard (Import Boundaries)](#lane-guard-import-boundaries)
  - [Hidden Gems Integration](#hidden-gems-integration)
- [Common Workflows](#common-workflows)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

```bash
# First time setup
make bootstrap              # Complete fresh setup (dependencies + hooks)

# Daily development
make dev                    # Start development server
make test                   # Run comprehensive test suite
make lint                   # Run all linters (flake8, ruff, mypy, bandit)

# Quick checks
make help                   # Auto-generated help with all targets
make doctor                 # System health diagnostics
make quick                  # Fix issues and run tests (one command)

# Before committing
make lane-guard             # Validate import boundaries
make test-tier1-matriz      # Run critical system tests
```

---

## Architecture Overview

### Modular Design

LUKHAS uses a **modular Makefile architecture** for maintainability:

```
Makefile                    # Main entry point
├── mk/help.mk             # Auto-discovery help system
├── mk/tests.mk            # Testing framework (comprehensive)
├── mk/ci.mk               # CI/CD helpers
├── mk/audit.mk            # Audit navigation & validation
├── mk/security.mk         # Security operations (11KB)
├── mk/policy.mk           # Policy & branding validation
├── mk/codex.mk            # Code analysis & metrics (8KB)
├── mk/jules.mk            # Jules AI integration (5KB)
├── mk/context.mk          # Context file management
└── mk/Makefile.hidden_gems # Hidden gems integration (10KB)
```

### Auto-Discovery Help System

All targets can add inline descriptions using `##`:

```makefile
quick: fix test ## Fix issues and run tests
```

Run `make help` to see auto-generated documentation organized by category.

---

## Command Categories

### Setup & Installation

#### `make install`
Install all Python dependencies (production + test requirements).

```bash
make install
# Runs:
# - pip install --upgrade pip
# - pip install -r requirements.txt
# - pip install -r requirements-test.txt
```

#### `make bootstrap`
**Complete fresh setup** - dependencies, git hooks, development environment.

```bash
make bootstrap
# Recommended for:
# - First-time setup
# - Clean environment reset
# - Post-git-clone initialization
```

#### `make setup-hooks`
Install git pre-commit and post-commit hooks for automated quality checks.

```bash
make setup-hooks
# Installs:
# - husky for git hooks
# - pre-commit: python3 tools/acceptance_gate.py
# - post-commit: make verify
```

#### `make organize`
Auto-organize imports and file structure according to LUKHAS conventions.

#### `make organize-dry`
Dry run of organize (shows what would change without applying).

---

### Development

#### `make dev`
Start the **development FastAPI server** with hot-reload.

```bash
make dev
# Runs: uvicorn serve.main:app --reload --host 0.0.0.0 --port 8000
# Access at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

#### `make api`
Start the **production API server** (lukhas.api.app).

```bash
make api
# Runs: uvicorn lukhas.api.app:app --reload --port 8000
```

#### `make openapi` / `make openapi-spec`
Export OpenAPI specification to `out/openapi.json`.

```bash
make openapi-spec
# Exports: out/openapi.json
# Server must be running on port 8000
```

#### `make live`
Development workflow with live reload and auto-testing.

#### `make admin`
Open the admin dashboard (http://127.0.0.1:8000/admin).

---

### Testing

The testing system follows **T4/0.01% reliability standards** with comprehensive test orchestration.

#### Core Testing Commands

**`make test`**
Run the **comprehensive test suite** (775+ tests across all categories).

```bash
make test
# Runs: python3 tests/comprehensive_test_suite.py
# Coverage: unit, integration, e2e, smoke
```

**`make test-cov`**
Run tests with **coverage analysis** (90% minimum threshold).

```bash
make test-cov
# Generates:
# - Terminal coverage report
# - HTML coverage report: test_reports/coverage_html/index.html
# Fails if coverage < 90%
```

**`make smoke`**
Quick **smoke tests** for basic system health (15 tests, <30 seconds).

```bash
make smoke
# Runs: pytest -m "smoke or unit" --maxfail=5 -x
# Use for: Quick validation during development
```

**`make test-fast`**
Fast smoke tests (alias for `make smoke`).

#### Component-Specific Tests

**`make test-unit`**
Unit tests only (isolated component testing).

```bash
make test-unit
# Runs: pytest tests/unit/ tests/core/ -m "unit" -v
```

**`make test-integration`**
Integration tests (cross-component validation).

```bash
make test-integration
# Runs: pytest tests/integration/ tests/reliability/ -m "integration" -v
```

**`make test-e2e`**
End-to-end workflow tests (300s timeout).

```bash
make test-e2e
# Runs: pytest tests/e2e/ -m "e2e" -v --timeout=300
```

**`make test-security`**
Security-focused test suite.

```bash
make test-security
# Runs:
# - Package import verification
# - pytest tests/ -k "security" -v
```

**`make test-memory`**
Memory system tests (persistence, recall, context).

```bash
make test-memory
# Runs: pytest tests/memory/ -m "memory" -v
```

**`make test-guardian`**
Guardian safety system tests (constitutional AI).

```bash
make test-guardian
# Runs: pytest tests/integration/test_guardian_dsl.py -m "guardian" -v
```

**`make test-orchestrator`**
MATRIZ orchestrator tests (cognitive processing).

```bash
make test-orchestrator
# Runs:
# - tests/e2e/test_matriz_orchestration.py
# - tests/stress/test_orchestrator.py
```

**`make test-tier1-matriz`**
Critical MATRIZ system tests (production gate).

#### Performance & Advanced Testing

**`make test-performance`**
Performance and stress tests.

```bash
make test-performance
# Runs: pytest tests/performance/ tests/stress/ -m "performance or stress" -v
```

**`make test-parallel`**
Run tests in parallel using all CPU cores.

```bash
make test-parallel
# Runs: pytest -n auto --dist=loadfile
# Skips slow tests for speed
```

**`make test-slow`**
Run slow/stress tests (600s timeout).

```bash
make test-slow
# Runs: pytest -m "slow or stress" -v --timeout=600
```

**`make test-regression`**
Regression and critical tests only.

```bash
make test-regression
# Runs: pytest -m "regression or critical" -v
```

#### CI/CD Testing

**`make test-ci`**
Full CI/CD test pipeline (comprehensive quality gate).

```bash
make test-ci
# Pipeline:
# 1. make lint
# 2. make test-unit
# 3. make test-integration
# 4. make test-security
# 5. make test-coverage
```

**`make test-dev`**
Development test cycle (fast feedback loop).

```bash
make test-dev
# Pipeline:
# 1. make test-fast
# 2. make test-unit
# 3. make lint
```

#### Test Reports & Utilities

**`make reports`**
Generate HTML and JUnit test reports.

```bash
make reports
# Generates:
# - test_reports/report.html (HTML report)
# - test_reports/junit.xml (JUnit format for CI)
```

**`make clean-test-reports`**
Clean all test artifacts and cache.

```bash
make clean-test-reports
# Removes:
# - test_reports/, htmlcov/, .coverage
# - .pytest_cache/, comprehensive_test_report.json
# - __pycache__/ directories
```

**`make install-test-deps`**
Install testing dependencies (pytest, coverage, hypothesis).

---

### Advanced Testing (0.001% Excellence)

LUKHAS implements **property-based, chaos, and formal verification** testing for extreme reliability.

**`make test-advanced`**
Run all advanced testing strategies.

**`make test-property`**
Property-based testing with Hypothesis (generative tests).

**`make test-chaos`**
Chaos engineering tests (fault injection, resilience validation).

**`make test-metamorphic`**
Metamorphic testing (relationship invariants).

**`make test-formal`**
Formal verification tests (mathematical correctness proofs).

**`make test-mutation`**
Mutation testing (test suite effectiveness validation).

**`make test-performance`**
Performance benchmarking with threshold validation.

**`make test-oracles`**
Oracle-based testing (differential testing, cross-validation).

**`make test-consciousness`**
Consciousness module testing (MATRIZ cognitive patterns).

**`make test-standalone`**
Standalone test execution (isolated environment).

---

### CI/CD

#### `make ci-local`
Run local CI pipeline (mimics GitHub Actions).

```bash
make ci-local
# Runs:
# 1. pytest with coverage
# 2. Smoke check with JSON output
# 3. API server smoke test
# 4. OpenAPI spec export
# Artifacts: ./out/
```

#### `make monitor`
Generate code quality dashboard.

```bash
make monitor
# Runs: python tools/scripts/quality_dashboard.py
# Generates: Quality metrics and trends
```

#### `make audit`
Run comprehensive audit script.

```bash
make audit
# Runs: ./scripts/audit.sh
```

#### `make audit-status`
Show current audit status (branch, commits, tools, smoke tests).

```bash
make audit-status
# Displays:
# - Branch status (git status -s)
# - Recent commits (git log --oneline -3)
# - Tool versions (Ruff, Pytest)
# - Smoke test results
# - Deep search reports
# - Lane guard status
```

#### `make audit-nav`
Navigate audit documentation and deep search indexes.

```bash
make audit-nav
# Shows:
# - AUDIT/INDEX.md (entry point)
# - AUDIT/SYSTEM_MAP.md (architecture)
# - AUDIT/MATRIZ_READINESS.md
# - AUDIT/IDENTITY_READINESS.md
# - AUDIT/API/openapi.yaml
# - reports/deep_search/ indexes
```

#### `make audit-scan`
Comprehensive audit scan (import cycles, MATRIZ validation, API schemas).

#### `make promote`
Promote module from candidate lane to production.

```bash
make promote SRC=candidate/core/module DST=lukhas/core/module
# Optional: SHIM=candidate->lukhas (creates import shim)
```

#### `make pc-all`
Run pre-commit hooks on all files.

```bash
make pc-all
# Runs: pre-commit run --all-files
```

---

### Doctor & Diagnostics

#### `make doctor`
**Comprehensive system health diagnostics** (recommended first step for issues).

```bash
make doctor
# Checks:
# - Python environment (version, virtual env)
# - Dependencies (requirements.txt, installed packages)
# - Import boundaries (lane-guard)
# - File permissions
# - Configuration files
# - Database connections
# - API endpoints
```

#### `make doctor-strict`
Doctor with strict validation (fails on warnings).

#### `make doctor-json`
Output doctor results in JSON format (for automation).

#### `make doctor-dup-targets`
Check for duplicate Makefile targets (naming conflicts).

#### `make doctor-dup-targets-strict`
Strict duplicate target check (fails on duplicates).

---

### Security

LUKHAS includes **comprehensive automated security tooling** with Ollama-powered analysis.

#### Core Security Commands

**`make security`**
Full security check suite (scan + audit).

```bash
make security
# Runs:
# 1. make security-audit
# 2. make security-scan
# Reports: security-reports/
```

**`make security-scan`**
Quick security scan (safety + pip-audit).

```bash
make security-scan
# Tools:
# - safety check (vulnerability database)
# - pip-audit (dependency vulnerabilities)
# Reports: Terminal output
```

**`make security-audit`**
**Deep security audit** with JSON reports.

```bash
make security-audit
# Tools:
# - safety check (JSON output)
# - pip-audit (JSON output)
# - bandit (SAST scanner, JSON output)
# Reports: security-reports/
# - safety-report.json
# - pip-audit.json
# - bandit-report.json
```

**`make security-comprehensive-scan`**
Most thorough security analysis (all tools + Ollama).

```bash
make security-comprehensive-scan
# Tools:
# - Safety CLI scan
# - pip-audit
# - Bandit security scan
# - Ollama AI analysis
# Reports: security-reports/
# - safety-scan.json
# - pip-audit.json
# - bandit.json
# - ollama-analysis.txt
```

#### Automated Security Fixes

**`make security-fix-all`**
Fix ALL security vulnerabilities and issues automatically.

```bash
make security-fix-all
# Runs:
# 1. make security-fix-vulnerabilities
# 2. make security-fix-issues
```

**`make security-fix-vulnerabilities`**
Auto-fix known CVE vulnerabilities.

```bash
make security-fix-vulnerabilities
# Runs: python3 scripts/fix_security_vulnerabilities.py
```

**`make security-fix-issues`**
Auto-fix Bandit security findings.

```bash
make security-fix-issues
# Runs: python3 scripts/fix_security_issues.py
```

**`make security-update`**
Automated security updates (no test validation).

```bash
make security-update
# Runs: python3 scripts/security-update.py --auto --no-test
```

#### Ollama-Powered Security

**`make security-ollama`**
AI-powered security analysis using Ollama.

```bash
make security-ollama
# Runs: python3 scripts/ollama_security_analyzer.py scan
# Model: deepseek-coder:6.7b
```

**`make security-ollama-fix`**
Auto-fix vulnerabilities with AI assistance.

```bash
make security-ollama-fix
# Runs: python3 scripts/ollama_security_analyzer.py fix
```

**`make security-ollama-setup`**
Setup Ollama for security analysis.

```bash
make security-ollama-setup
# Installs:
# 1. Ollama (brew install ollama)
# 2. Starts Ollama service
# 3. Pulls deepseek-coder:6.7b model
```

#### Security Automation

**`make security-autopilot`**
Run security autopilot (automated fix workflow).

```bash
make security-autopilot
# Runs: python3 scripts/security-autopilot.py fix
```

**`make security-monitor`**
Continuous security monitoring (runs every hour).

```bash
make security-monitor
# Runs: python3 scripts/security-autopilot.py monitor --continuous --interval 3600
```

**`make security-status`**
Show current security status.

```bash
make security-status
# Runs: python3 scripts/security-autopilot.py status
```

#### Security Scheduling

**`make security-schedule`**
Show security task scheduler status.

**`make security-schedule-3h`**
Schedule security fixes to run in 3 hours.

```bash
make security-schedule-3h
# Runs: python3 scripts/security_scheduler.py schedule fix-all +3h
```

**`make security-schedule-tonight`**
Schedule security fixes for 8 PM today.

```bash
make security-schedule-tonight
# Runs: python3 scripts/security_scheduler.py schedule fix-all 20:00
```

**`make security-schedule-list`**
List all scheduled security tasks.

**`make security-schedule-run`**
Run pending scheduled security tasks.

#### Emergency Security

**`make security-emergency-patch`**
**EMERGENCY MODE** - Auto-fix ALL critical vulnerabilities (interactive prompt).

```bash
make security-emergency-patch
# WARNING: Automatically updates dependencies
# Pipeline:
# 1. make security-fix-vulnerabilities
# 2. pip install -r requirements.txt
# 3. make test-security
```

#### SBOM Generation

**`make sbom`**
Generate Software Bill of Materials (CycloneDX format).

```bash
make sbom
# Generates: reports/sbom/cyclonedx.json
# Tool: syft
```

---

### Policy & Brand

#### `make policy`
Run all policy compliance checks.

#### `make policy-review`
Review policy violations.

#### `make policy-brand`
Validate branding consistency (LUKHAS AI vs Lukhas AGI, etc.).

#### `make policy-tone`
Validate messaging tone (quantum-inspired, bio-inspired, etc.).

#### `make policy-registries`
Check registry compliance.

#### `make policy-routes`
Validate API route naming conventions.

#### `make policy-vocab`
Check vocabulary consistency.

---

### SDK Development

#### Python SDK

**`make sdk-py-install`**
Install Python SDK in editable mode.

```bash
make sdk-py-install
# Runs: cd sdk/python && pip install -e .
```

**`make sdk-py-test`**
Run Python SDK tests.

```bash
make sdk-py-test
# Runs: cd sdk/python && python3 -m pytest -q
```

#### TypeScript SDK

**`make sdk-ts-build`**
Build TypeScript SDK.

```bash
make sdk-ts-build
# Runs: cd sdk/ts && npm i && npm run build
```

**`make sdk-ts-test`**
Run TypeScript SDK tests.

```bash
make sdk-ts-test
# Runs: cd sdk/ts && npm test
```

---

### Backup & Disaster Recovery

#### Backup Operations

**`make backup-local`**
Create local backup (lukhas/ and data/ directories).

```bash
make backup-local
# Backup:
# - Includes: lukhas, data
# - Excludes: *.tmp, *.log
# - Output: .lukhas_backup/out/
# - Manifest: .lukhas_backup/out/backup_create.out.json
```

**`make backup-s3`**
Create backup and upload to S3.

```bash
make backup-s3
# Requires: BACKUP_S3_BUCKET environment variable
# Output: S3 bucket with manifest
```

#### Restore Operations

**`make restore-local`**
Restore from local backup.

```bash
make restore-local MANIFEST=path/to.manifest.json [TARGET=_restore]
# Restores from manifest
# Optional: TARBALL=path/to.tarball.tar.gz
```

**`make restore-s3`**
Restore from S3 backup.

```bash
make restore-s3 MANIFEST=s3://bucket/key.manifest.json [TARGET=_restore]
# Restores from S3 manifest
```

#### Disaster Recovery Drills

**`make dr-drill`**
Run disaster recovery dry run (validates backup without restoring).

```bash
make dr-drill [MANIFEST=path/to.manifest.json]
# Validates:
# - Manifest integrity
# - Tarball accessibility
# - Restoration feasibility
# No actual restoration performed
```

**`make dr-weekly`**
Trigger weekly DR dry run (GitHub Actions).

```bash
make dr-weekly
# Runs: gh workflow run dr-dryrun-weekly.yml
```

**`make dr-monthly`**
Trigger monthly DR dry run.

**`make dr-quarterly`**
Trigger quarterly full restore drill.

```bash
make dr-quarterly
# Runs: gh workflow run dr-full-restore-quarterly.yml
```

---

### Code Quality

#### Linting

**`make lint`**
Run all linters (flake8, ruff, mypy, bandit).

```bash
make lint
# Tools:
# - flake8 (PEP8 compliance)
# - ruff (modern fast linter)
# - mypy (type checking)
# - bandit (security linting)
# Targets: lukhas/, matriz/, core/, serve/
```

**`make lint-status`**
Check linting progress.

```bash
make lint-status
# Runs: python tools/scripts/check_progress.py
```

**`make lint-unused`**
T4 unused imports system (detect and remove unused imports).

#### Formatting

**`make format`**
Format code with Black and isort.

```bash
make format
# Tools:
# - black --line-length 88
# - isort --profile black --line-length 79
# Targets: lukhas/, matriz/, core/, serve/, tests/
```

#### Auto-Fixing

**`make fix`**
Auto-fix common issues (safe fixes only).

```bash
make fix
# Runs:
# - ruff check --fix
# - black formatting
# - isort import sorting
```

**`make fix-imports`**
Fix import issues specifically.

```bash
make fix-imports
# Runs:
# - autoflake (remove unused imports)
# - isort (sort imports)
```

**`make fix-all`**
Aggressive fix mode (90% of issues, use with caution).

```bash
make fix-all
# WARNING: Significant code changes
# Runs: python tools/scripts/aggressive_fix.py
```

**`make fix-ultra`**
**ULTRA FIX MODE** - Maximum aggression (last resort).

```bash
make fix-ultra
# ☠️ WARNING: WILL change code significantly!
# Tools:
# - autoflake --remove-all-unused-imports
# - autopep8 --aggressive --aggressive
# - black --line-length 88
# - ruff check --fix --unsafe-fixes
```

#### Cleaning

**`make clean`**
Clean cache and temporary files.

```bash
make clean
# Removes:
# - __pycache__/
# - .pytest_cache/
# - .mypy_cache/
# - .ruff_cache/
# - *.pyc files
# - .DS_Store files
# - out/ directory
```

**`make deep-clean`**
Deep clean including virtual environments.

```bash
make deep-clean
# Removes:
# - All from 'make clean'
# - venv/, .venv/
# - htmlcov/, .coverage
# - dist/, build/, *.egg-info/
```

---

### Performance & Monitoring

#### `make perf`
Run k6 performance smoke tests.

```bash
make perf
# Runs: k6 run perf/k6_smoke.js
# Output: out/k6_summary.json
# Target: http://127.0.0.1:8000 (configurable with BASE_URL)
```

#### `make metrics-dashboard`
Generate build system performance dashboard.

```bash
make metrics-dashboard
# Runs: python3 tools/ci/build_metrics_dashboard.py
# Output: reports/build_performance_report.md
```

#### `make benchmark`
Run performance benchmarks with pytest-benchmark.

```bash
make benchmark
# Runs: pytest tests/performance/ -m "benchmark" --benchmark-only
```

---

### Lane Guard (Import Boundaries)

**Critical for LUKHAS architecture integrity.**

#### `make lane-guard`
**Validate import boundaries** (forbid lukhas → candidate imports).

```bash
make lane-guard
# Validates:
# - lukhas/ can import from: core/, matriz/, universal_language/
# - candidate/ can import from: core/, matriz/ ONLY
# - NO lukhas → candidate imports allowed
# Tool: lint-imports with .importlinter config
```

**Lane Architecture:**
- **Production Lane** (`lukhas/`): Battle-tested, production-ready
- **Integration Lane** (`core/`): Testing and validation
- **Development Lane** (`candidate/`): Experimental prototypes

**Import Rules:**
```python
# ✅ ALLOWED
from lukhas.core import Component        # lukhas → core
from candidate.core import Component     # candidate → core
from core.matriz import CognitiveNode    # core → matriz

# ❌ FORBIDDEN
from candidate.consciousness import X    # lukhas → candidate (VIOLATION!)
```

**Why Lane Guard Matters:**
- Prevents production code from depending on experimental features
- Enforces architectural boundaries
- Ensures safe promotion workflow (candidate → core → lukhas)
- Catches accidental cross-lane imports in CI

**Integration with CI:**
```yaml
# .github/workflows/ci.yml
- name: Lane Guard
  run: make lane-guard
```

---

### Hidden Gems Integration

**Batch integration automation for moving modules from candidate/labs to production.**

Commands from `mk/Makefile.hidden_gems`:

#### `make -f mk/Makefile.hidden_gems status`
Show hidden gems integration status.

```bash
make -f mk/Makefile.hidden_gems status
# Shows:
# - Module counts (candidate, labs, matriz, core)
# - Import test results
# - MATRIZ schema files
```

#### `make -f mk/Makefile.hidden_gems integrate-next-batch`
Integrate next batch of 25 modules.

#### `make -f mk/Makefile.hidden_gems batch-integrate`
**Complete integration pipeline** for current batch.

```bash
make -f mk/Makefile.hidden_gems batch-integrate
# Pipeline:
# 1. batch-move (move modules)
# 2. batch-fix (fix logger/import issues)
# 3. generate-batch-schemas (MATRIZ schemas)
# 4. create-batch-tests (generate tests)
# 5. validate-all (comprehensive validation)
# 6. report (integration summary)
```

#### `make -f mk/Makefile.hidden_gems test-imports`
Test all module imports.

#### `make -f mk/Makefile.hidden_gems quick-check`
Quick health check of integration.

#### `make -f mk/Makefile.hidden_gems doctor`
Diagnose integration issues.

---

## Common Workflows

### Daily Development Workflow

```bash
# Morning startup
git pull
make bootstrap                    # Update dependencies
make doctor                       # Health check

# Development loop
make dev                          # Start server
make test-fast                    # Quick validation
make lint                         # Code quality check

# Before committing
make lane-guard                   # Validate boundaries
make test-ci                      # Full CI pipeline
git add . && git commit
```

### Feature Development Workflow

```bash
# Start feature in candidate lane
mkdir -p candidate/consciousness/my_feature
cd candidate/consciousness/my_feature

# Develop with testing
make test-dev                     # Fast feedback loop

# Ready for integration
make promote SRC=candidate/consciousness/my_feature DST=core/consciousness/my_feature
make test-integration

# Ready for production
make promote SRC=core/consciousness/my_feature DST=lukhas/consciousness/my_feature
make test-ci
```

### Security Update Workflow

```bash
# Check current status
make security-status

# Run comprehensive scan
make security-comprehensive-scan

# Review findings
cat security-reports/safety-scan.json
cat security-reports/bandit.json
cat security-reports/ollama-analysis.txt

# Option 1: Fix immediately
make security-fix-all
make test-security

# Option 2: Schedule for later
make security-schedule-tonight

# Emergency mode (critical CVE)
make security-emergency-patch
```

### Testing Workflow

```bash
# Development (fast feedback)
make test-fast                    # Smoke tests
make test-unit                    # Component tests

# Integration validation
make test-integration             # Cross-component
make test-e2e                     # Full workflows

# Pre-release (comprehensive)
make test-ci                      # CI pipeline
make test-coverage                # Coverage validation
make test-performance             # Performance benchmarks

# Production gate (0.001% excellence)
make test-advanced                # Property-based, chaos, formal
make test-regression              # Critical tests
```

### Disaster Recovery Workflow

```bash
# Regular backups (automated)
make backup-local                 # Local backup
make backup-s3                    # S3 backup

# Validate backups (weekly)
make dr-drill                     # Dry run validation

# Disaster scenario (restore)
make restore-s3 MANIFEST=s3://bucket/backup-20250108.manifest.json TARGET=/tmp/restore
# Validate restored system
cd /tmp/restore && make doctor
# If valid, promote to production
```

---

## Troubleshooting

### Common Issues

#### "Module not found" errors

```bash
# Check Python environment
make doctor

# Reinstall dependencies
make bootstrap

# Validate imports
make lane-guard
```

#### Test failures

```bash
# Run specific test category
make test-unit                    # Isolate to unit tests
make test-integration             # Check integration

# Increase verbosity
pytest tests/ -vv --tb=long

# Check test reports
make reports
open test_reports/report.html
```

#### Import boundary violations

```bash
# Validate boundaries
make lane-guard

# Find violating imports
grep -r "from candidate" lukhas/  # Should be empty!

# Auto-fix imports
make fix-imports
```

#### Security vulnerabilities

```bash
# Comprehensive scan
make security-comprehensive-scan

# Review AI analysis
cat security-reports/ollama-analysis.txt

# Auto-fix (safe)
make security-fix-all

# Emergency patch (critical CVE)
make security-emergency-patch
```

#### Performance issues

```bash
# Run performance tests
make test-performance

# Generate metrics dashboard
make metrics-dashboard
cat reports/build_performance_report.md

# Run k6 load test
make perf
cat out/k6_summary.json
```

#### Duplicate Makefile targets

```bash
# Check for conflicts
make doctor-dup-targets

# Strict validation
make doctor-dup-targets-strict
```

### Debug Modes

#### Verbose test output

```bash
pytest tests/ -vv --tb=long --log-cli-level=DEBUG
```

#### Doctor diagnostics in JSON

```bash
make doctor-json > doctor-report.json
cat doctor-report.json | jq '.checks[] | select(.status == "FAIL")'
```

#### Audit status

```bash
make audit-status                 # Quick overview
make audit-scan                   # Comprehensive scan
make audit-nav                    # Navigate documentation
```

---

## Configuration

### Environment Variables

```bash
# Testing
TEST_TIMEOUT=300                  # Test timeout in seconds
COVERAGE_MIN=90                   # Minimum coverage percentage
PARALLEL_WORKERS=auto             # Parallel test workers

# Performance
BASE_URL=http://127.0.0.1:8000   # k6 performance test target

# Backup & DR
BACKUP_S3_BUCKET=my-bucket        # S3 bucket for backups
BACKUP_INCLUDE="lukhas data"      # Directories to backup
BACKUP_PREFIX="s3"                # Backup prefix

# Security
OLLAMA_MODEL=deepseek-coder:6.7b  # Ollama model for security analysis
```

### Python Configuration

From `mk/Makefile.testing`:

```makefile
PYTHON := python3
PYTEST := $(PYTHON) -m pytest
COVERAGE := $(PYTHON) -m coverage

TEST_TIMEOUT := 300
COVERAGE_MIN := 90
PARALLEL_WORKERS := auto
```

---

## Advanced Usage

### Custom Test Markers

```bash
# Run tests by marker
pytest -m "smoke"                 # Smoke tests only
pytest -m "slow"                  # Slow tests only
pytest -m "security"              # Security tests
pytest -m "matriz"                # MATRIZ cognitive tests
pytest -m "consciousness"         # Consciousness module tests

# Exclude markers
pytest -m "not slow"              # Skip slow tests
pytest -m "not external"          # Skip external API tests
```

### Parallel Testing Strategies

```bash
# Auto-detect CPU cores
make test-parallel

# Specific worker count
pytest -n 4 --dist=loadfile       # 4 workers, distribute by file

# Distributed testing (pytest-xdist)
pytest -n auto --dist=loadgroup   # Group tests by class
```

### Coverage Threshold

```bash
# Default (90%)
make test-coverage

# Custom threshold
coverage report --fail-under=95

# Coverage by module
coverage report -m
```

### Integration with CI/CD

**GitHub Actions:**

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Bootstrap
        run: make bootstrap

      - name: Lane Guard
        run: make lane-guard

      - name: CI Pipeline
        run: make test-ci

      - name: Upload Coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./test_reports/coverage.xml
```

---

## Performance Targets

From LUKHAS architecture:

- **Test Execution**: <2 minutes for smoke tests, <10 minutes for full suite
- **Coverage**: 90%+ minimum (fail_under=90 in pyproject.toml)
- **MATRIZ Performance**: <250ms p95 latency, 50+ ops/sec throughput
- **Build System**: <30s for lint, <5s for format, <10s for lane-guard

---

## Related Documentation

- **Architecture**: [docs/architecture/README.md](../architecture/README.md) - Deep dive into LUKHAS design
- **Testing Guide**: [docs/testing/README.md](../testing/README.md) - Comprehensive testing documentation
- **MATRIZ Guide**: [docs/MATRIZ_GUIDE.md](../MATRIZ_GUIDE.md) - Cognitive engine documentation
- **Task Manager**: [docs/architecture/TASK_MANAGER_GUIDE.md](../architecture/TASK_MANAGER_GUIDE.md) - Orchestration guide
- **Prometheus Monitoring**: [docs/operations/PROMETHEUS_MONITORING_GUIDE.md](../operations/PROMETHEUS_MONITORING_GUIDE.md) - Metrics guide
- **Dream Engine API**: [docs/consciousness/DREAM_ENGINE_API.md](../consciousness/DREAM_ENGINE_API.md) - Dream processing API

---

## Contributing

### Adding New Makefile Targets

1. **Choose the right module** (`mk/*.mk`) for your target
2. **Add inline documentation** with `##` comment
3. **Follow naming conventions**:
   - `test-*` for testing targets
   - `security-*` for security operations
   - `fix-*` for auto-fixing targets
   - `*-status` for status checks
4. **Test your target**:
   ```bash
   make your-target
   make help  # Verify auto-generated help
   ```

**Example:**

```makefile
# In mk/tests.mk
test-myfeature: ## Test my new feature
	@echo "🧪 Testing my feature..."
	$(PYTEST) tests/myfeature/ -v
```

### Makefile Best Practices

- **Use `.PHONY`** for targets that don't create files
- **Echo progress** with emojis (🚀 🧪 ✅ ❌ 🔍)
- **Handle errors gracefully** with `|| true` for non-critical commands
- **Provide defaults** for environment variables: `${VAR:-default}`
- **Check prerequisites** before running commands
- **Document dependencies** between targets

---

## Version History

- **v2.0** (2025-01-08): Complete modular architecture with 50+ targets
- **v1.5** (2024-12): Added security automation, Ollama integration
- **v1.0** (2024-11): Initial comprehensive Makefile system

---

**Last Updated**: 2025-01-08
**Makefile Version**: 2.0 (Comprehensive Modular System)
**Documentation Owner**: Development + DevOps Teams

🤖 Generated with Claude Code
