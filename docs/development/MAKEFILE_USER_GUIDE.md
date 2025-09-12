# 📘 LUKHAS AI Makefile User Guide

**Complete Developer Workflow Automation**

The LUKHAS AI Makefile provides a comprehensive build system with over 50 targets for development, testing, security, audit, and deployment workflows. This guide covers all available targets, usage patterns, and integration points.

## 🎯 Quick Reference

```bash
# Essential commands for daily development
make help           # Auto-generated help (see all available targets)
make install        # Install all dependencies
make dev            # Start development server
make test           # Run test suite
make lint           # Run all linters
make audit          # Run comprehensive audit
```

## 🏗️ Architecture Overview

The Makefile uses a modular architecture with specialized include files:

```
LUKHAS Build System
├── Makefile                    # Main targets and coordination
├── mk/help.mk                  # Auto-discovered help system
├── mk/tests.mk                 # Complete test suite
├── mk/ci.mk                    # CI/CD pipeline targets
├── mk/security.mk              # Security scanning and audit
└── mk/audit.mk                 # Audit and compliance validation
```

## 📋 Target Categories

### 🚀 Setup & Installation

| Target | Description | Usage |
|--------|-------------|-------|
| `install` | Install all Python dependencies | `make install` |
| `setup-hooks` | Install git hooks and pre-commit | `make setup-hooks` |
| `bootstrap` | Complete fresh setup (install + hooks + organize) | `make bootstrap` |
| `organize` | Auto-organize imports and code structure | `make organize` |
| `organize-dry` | Preview organize changes without applying | `make organize-dry` |
| `organize-suggest` | Get organization suggestions | `make organize-suggest` |
| `organize-watch` | Watch mode for continuous organization | `make organize-watch` |

#### Setup Examples

```bash
# Fresh project setup
make bootstrap

# Update dependencies only
make install

# Preview code organization
make organize-dry
```

### 🔧 Development

| Target | Description | Usage |
|--------|-------------|-------|
| `dev` | Start development server with hot reload | `make dev` |
| `api` | Start API server | `make api` |
| `openapi` | Generate OpenAPI documentation | `make openapi` |
| `live` | Start live reload development environment | `make live` |
| `colony-dna-smoke` | Run DNA colony smoke tests | `make colony-dna-smoke` |
| `audit-tail` | Tail audit logs in real-time | `make audit-tail` |
| `lane-guard` | Validate import lane boundaries | `make lane-guard` |
| `quick` | Quick development validation | `make quick` |

#### Development Examples

```bash
# Start full development environment
make dev

# API development
make api

# Monitor audit logs
make audit-tail &  # Run in background
```

### 🧪 Testing

| Target | Description | Usage |
|--------|-------------|-------|
| `test` | Run standard test suite | `make test` |
| `test-cov` | Run tests with coverage reporting | `make test-cov` |
| `smoke` | Run smoke tests for critical paths | `make smoke` |
| `test-legacy` | Run legacy compatibility tests | `make test-legacy` |
| `test-tier1-matriz` | Run MATRIZ tier-1 validation tests | `make test-tier1-matriz` |

#### Advanced Testing (0.001% Methodology)

| Target | Description | Usage |
|--------|-------------|-------|
| `test-advanced` | Complete advanced testing suite | `make test-advanced` |
| `test-property` | Property-based testing | `make test-property` |
| `test-chaos` | Chaos engineering tests | `make test-chaos` |
| `test-metamorphic` | Metamorphic testing | `make test-metamorphic` |
| `test-formal` | Formal verification tests | `make test-formal` |
| `test-mutation` | Mutation testing | `make test-mutation` |
| `test-performance` | Performance regression tests | `make test-performance` |
| `test-oracles` | Test oracle validation | `make test-oracles` |
| `test-consciousness` | Consciousness system tests | `make test-consciousness` |
| `test-standalone` | Standalone integration tests | `make test-standalone` |

#### Testing Examples

```bash
# Standard development testing
make test

# Full coverage analysis
make test-cov

# Advanced testing (comprehensive)
make test-advanced

# Specific test category
make test-chaos
```

### 🔍 Code Quality & Linting

| Target | Description | Usage |
|--------|-------------|-------|
| `lint` | Run all linters (flake8, ruff, mypy, bandit) | `make lint` |
| `lint-unused` | Annotate unused imports (T4 system) | `make lint-unused` |
| `lint-unused-strict` | Enforce zero unannotated F401s | `make lint-unused-strict` |
| `format` | Format all code (black, isort) | `make format` |
| `fix` | Auto-fix linting issues | `make fix` |
| `fix-all` | Comprehensive auto-fix | `make fix-all` |
| `fix-ultra` | Ultra-comprehensive fixes | `make fix-ultra` |
| `fix-imports` | Fix import organization | `make fix-imports` |

#### Linting Examples

```bash
# Check code quality
make lint

# Auto-fix issues
make fix-all

# T4 unused imports workflow
make lint-unused        # Annotate
make lint-unused-strict # Validate
```

### 🔒 Security

| Target | Description | Usage |
|--------|-------------|-------|
| `security` | Run comprehensive security audit | `make security` |
| `security-scan` | Quick security vulnerability scan | `make security-scan` |
| `security-update` | Update security tools | `make security-update` |
| `security-audit` | Deep security audit with reports | `make security-audit` |
| `security-fix` | Auto-fix security vulnerabilities | `make security-fix` |
| `security-fix-vulnerabilities` | Fix known vulnerabilities | `make security-fix-vulnerabilities` |
| `security-fix-issues` | Fix security issues | `make security-fix-issues` |
| `security-fix-all` | Comprehensive security fixes | `make security-fix-all` |
| `security-ollama` | Security scan with Ollama integration | `make security-ollama` |
| `security-comprehensive-scan` | Full security analysis | `make security-comprehensive-scan` |
| `security-emergency-patch` | Emergency security patching | `make security-emergency-patch` |
| `test-security` | Run security-focused tests | `make test-security` |

#### Security Automation

| Target | Description | Usage |
|--------|-------------|-------|
| `security-autopilot` | Automated security monitoring | `make security-autopilot` |
| `security-monitor` | Real-time security monitoring | `make security-monitor` |
| `security-status` | Current security status | `make security-status` |
| `security-schedule` | Schedule security scans | `make security-schedule` |
| `security-schedule-3h` | Schedule 3-hour security checks | `make security-schedule-3h` |
| `security-schedule-tonight` | Schedule tonight's security scan | `make security-schedule-tonight` |
| `security-schedule-list` | List scheduled security tasks | `make security-schedule-list` |
| `security-schedule-run` | Run scheduled security tasks | `make security-schedule-run` |

#### Security Examples

```bash
# Daily security check
make security

# Emergency response
make security-emergency-patch

# Continuous monitoring
make security-autopilot &
```

### 📊 Audit & Compliance

| Target | Description | Usage |
|--------|-------------|-------|
| `audit` | Run comprehensive system audit | `make audit` |
| `audit-status` | Current audit status | `make audit-status` |
| `audit-nav` | Navigate audit results | `make audit-nav` |
| `audit-scan` | Scan for audit issues | `make audit-scan` |
| `audit-nav-info` | Audit navigation information | `make audit-nav-info` |
| `audit-scan-list` | List audit scan results | `make audit-scan-list` |
| `audit-validate` | Validate audit compliance | `make audit-validate` |
| `api-serve` | Serve audit API | `make api-serve` |
| `api-spec` | Generate audit API specification | `make api-spec` |

#### Audit Management (T4 System)

| Target | Description | Usage |
|--------|-------------|-------|
| `audit-appendix` | Generate audit delta appendix | `make audit-appendix OLD_TAG=v1.0 NEW_TAG=v1.1` |
| `audit-normalize` | Normalize audit data format | `make audit-normalize` |
| `audit-merge` | Merge audit reports | `make audit-merge` |
| `audit-merge-auto` | Auto-merge compatible audit reports | `make audit-merge-auto` |
| `audit-merge-check` | Check audit merge compatibility | `make audit-merge-check` |

#### Audit Examples

```bash
# Full system audit
make audit

# Generate delta report
make audit-appendix OLD_TAG=v2.1.0 NEW_TAG=v2.2.0

# Merge audit reports
make audit-merge-auto
```

### 🎯 CI/CD & Automation

| Target | Description | Usage |
|--------|-------------|-------|
| `ci-local` | Run local CI simulation | `make ci-local` |
| `monitor` | Start monitoring services | `make monitor` |
| `check-scoped` | Scoped validation (lint + tests + types) | `make check-scoped` |
| `promote` | Promote build through pipeline | `make promote` |
| `pc-all` | Run pre-commit on all files | `make pc-all` |
| `lint-scoped` | Scoped linting | `make lint-scoped` |
| `test-contract` | Contract testing | `make test-contract` |
| `type-scoped` | Scoped type checking | `make type-scoped` |

#### CI Examples

```bash
# Local CI validation
make ci-local

# Pre-deployment check
make check-scoped

# Full pre-commit validation
make pc-all
```

### 📚 Policy & Compliance

| Target | Description | Usage |
|--------|-------------|-------|
| `policy` | Run policy compliance checks | `make policy` |
| `policy-review` | Review policy compliance | `make policy-review` |
| `policy-brand` | Validate branding compliance | `make policy-brand` |
| `policy-tone` | Check tone and messaging | `make policy-tone` |
| `policy-registries` | Validate registry policies | `make policy-registries` |
| `policy-routes` | Check route policies | `make policy-routes` |
| `policy-vocab` | Validate vocabulary compliance | `make policy-vocab` |

### 🩺 Diagnostics & Health

| Target | Description | Usage |
|--------|-------------|-------|
| `doctor` | Comprehensive system health check | `make doctor` |
| `doctor-strict` | Strict diagnostic mode | `make doctor-strict` |
| `doctor-json` | JSON diagnostic report | `make doctor-json` |
| `doctor-dup-targets` | Check for duplicate Makefile targets | `make doctor-dup-targets` |
| `doctor-dup-targets-strict` | Strict duplicate target checking | `make doctor-dup-targets-strict` |
| `doctor-tools` | Validate development tools | `make doctor-tools` |
| `doctor-py` | Python environment diagnostics | `make doctor-py` |
| `doctor-ci` | CI/CD health check | `make doctor-ci` |
| `doctor-lanes` | Import lane validation | `make doctor-lanes` |
| `doctor-tests` | Test system health | `make doctor-tests` |
| `doctor-audit` | Audit system health | `make doctor-audit` |
| `doctor-phony` | PHONY targets validation | `make doctor-phony` |
| `doctor-summary` | Generate health summary | `make doctor-summary` |

#### Diagnostic Examples

```bash
# Full system health check
make doctor

# Focus on specific area
make doctor-py
make doctor-ci

# Generate comprehensive report
make doctor-summary
```

### 🛠️ Development Tools

| Target | Description | Usage |
|--------|-------------|-------|
| `ai-analyze` | AI-powered code analysis | `make ai-analyze` |
| `ai-setup` | Setup AI development tools | `make ai-setup` |
| `ai-workflow` | AI workflow automation | `make ai-workflow` |
| `clean` | Clean build artifacts | `make clean` |
| `deep-clean` | Deep clean all generated files | `make deep-clean` |
| `codex-validate` | Validate with Codex | `make codex-validate` |
| `codex-fix` | Auto-fix with Codex | `make codex-fix` |
| `validate-all` | Comprehensive validation | `make validate-all` |
| `perf` | Performance analysis | `make perf` |

### 💾 Data & Migration

| Target | Description | Usage |
|--------|-------------|-------|
| `migrate-dry` | Dry-run database migrations | `make migrate-dry` |
| `migrate-run` | Execute database migrations | `make migrate-run` |
| `dna-health` | DNA system health check | `make dna-health` |
| `dna-compare` | Compare DNA configurations | `make dna-compare` |
| `admin` | Admin dashboard | `make admin` |
| `lint-status` | Get current linting status | `make lint-status` |

### 📦 SDK & Build Tools

| Target | Description | Usage |
|--------|-------------|-------|
| `sdk-py-install` | Install Python SDK | `make sdk-py-install` |
| `sdk-py-test` | Test Python SDK | `make sdk-py-test` |
| `sdk-ts-build` | Build TypeScript SDK | `make sdk-ts-build` |
| `sdk-ts-test` | Test TypeScript SDK | `make sdk-ts-test` |

### 💾 Backup & Disaster Recovery

| Target | Description | Usage |
|--------|-------------|-------|
| `backup-local` | Create local backup | `make backup-local` |
| `backup-s3` | Backup to S3 | `make backup-s3` |
| `restore-local` | Restore from local backup | `make restore-local` |
| `restore-s3` | Restore from S3 backup | `make restore-s3` |
| `dr-drill` | Disaster recovery drill | `make dr-drill` |
| `dr-weekly` | Weekly DR procedures | `make dr-weekly` |
| `dr-quarterly` | Quarterly DR validation | `make dr-quarterly` |
| `dr-monthly` | Monthly DR maintenance | `make dr-monthly` |

### 🎯 T4 System (Transform Technical Debt)

| Target | Description | Usage |
|--------|-------------|-------|
| `todo-unused` | Annotate unused imports (all lanes) | `make todo-unused` |
| `todo-unused-core` | Annotate core modules only | `make todo-unused-core` |
| `todo-unused-check` | Validate TODO annotations | `make todo-unused-check` |
| `t4-annotate` | Legacy alias for todo-unused | `make t4-annotate` |
| `t4-check` | Legacy alias for todo-unused-check | `make t4-check` |

## 🎨 Advanced Usage Patterns

### Chaining Targets

```bash
# Complete development setup
make install && make setup-hooks && make organize

# Quality gate workflow
make lint && make test && make security

# Pre-deployment validation
make test-cov && make security-comprehensive-scan && make audit

# T4 workflow
make lint-unused && make lint-unused-strict
```

### Parallel Execution

```bash
# Run multiple checks in parallel
make test & make lint & make security-scan & wait

# Background monitoring
make audit-tail &
make security-monitor &
make monitor &
```

### Custom Variables

```bash
# Audit with custom tags
make audit-appendix OLD_TAG=v1.0.0 NEW_TAG=v1.1.0

# Custom test parameters
PYTEST_ARGS="-v -x" make test

# Custom paths
PATHS="lukhas core" make lint-unused
```

## 🔧 Configuration & Customization

### Environment Variables

```bash
# Python interpreter
PYTHON=python3.11 make install

# Test verbosity
PYTEST_ARGS="-v --tb=short" make test

# Coverage threshold
COV_THRESHOLD=90 make test-cov

# Security scan depth
SECURITY_LEVEL=deep make security-scan
```

### Makefile Customization

The modular structure allows for easy customization:

```make
# Custom local targets (add to Makefile)
my-workflow: lint test security
	@echo "✅ Custom workflow complete"

my-deploy: validate-all backup-local
	@echo "🚀 Ready for deployment"
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Permission Errors

```bash
# Fix file permissions
chmod +x scripts/*.sh
make setup-hooks
```

#### 2. Missing Dependencies

```bash
# Reinstall all dependencies
make deep-clean
make install
```

#### 3. Import Issues

```bash
# Validate Python environment
make doctor-py

# Fix import organization
make fix-imports
```

#### 4. Test Failures

```bash
# Verbose test output
PYTEST_ARGS="-v -s" make test

# Test specific category
make test-smoke  # Quick validation
```

### Debug Mode

```bash
# Verbose make output
make -d target-name

# Dry-run mode
make -n target-name

# Keep going on errors
make -k lint test security
```

## 📊 Performance Tips

### Fast Development Workflow

```bash
# Quick validation
make quick

# Focused linting
make lint-scoped

# Smoke tests only
make smoke
```

### Optimized CI Workflow

```bash
# Parallel CI checks
make ci-local

# Scoped validation
make check-scoped

# Contract testing only
make test-contract
```

## 🎯 Integration Points

### With Git Hooks

```bash
# Pre-commit integration
make setup-hooks

# Manual pre-commit run
make pc-all
```

### With CI/CD

```bash
# GitHub Actions integration
make ci-local          # Local CI simulation
make check-scoped      # Scoped validation
make security-scan     # Security validation
```

### With IDE

```bash
# VS Code integration
make doctor-json > .vscode/health.json

# Watch mode for development
make organize-watch &
```

## 📚 Related Documentation

- [T4 Unused Imports System](T4_UNUSED_IMPORTS_SYSTEM.md)
- [Testing Strategy](../testing/TESTING_STRATEGY.md)
- [Security Guidelines](../security/SECURITY_GUIDELINES.md)
- [CI/CD Pipeline](../ci/CICD_PIPELINE.md)
- [Trinity Framework](../trinity/TRINITY_FRAMEWORK.md)

## 🆘 Help & Support

### Built-in Help

```bash
# Auto-generated help with live target discovery
make help

# Show all available targets
make -qp | grep -E '^[a-zA-Z_-]+:' | sort
```

### System Health

```bash
# Complete system diagnosis
make doctor

# JSON health report
make doctor-json
```

### Emergency Procedures

```bash
# Emergency clean and rebuild
make deep-clean && make bootstrap

# Emergency security patch
make security-emergency-patch

# Disaster recovery
make dr-drill
```

---

**Last Updated**: September 12, 2025  
**Total Targets**: 50+ (dynamically discovered)  
**Status**: Production Ready ✅  
**Maintainer**: LUKHAS AI Development Team