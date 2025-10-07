---
status: wip
type: documentation
owner: unknown
module: development
redirect: false
moved_to: null
---

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# 🚀 LUKHAS AI Quick Reference Card

**Essential Commands for Daily Development**

## ⚡ Quick Start (30 seconds)

```bash
make bootstrap          # Complete fresh setup
make dev               # Start development environment
make test              # Run tests
make lint              # Check code quality
```

## 🎯 Daily Workflow

```bash
# Morning routine
make doctor            # Health check
make install           # Update dependencies

# Development cycle
make lint-unused       # Clean unused imports
make test             # Validate changes
make security-scan    # Quick security check

# Before commit
make pc-all           # Pre-commit validation
make lint-unused-strict # Enforce T4 policy
```

## 🔧 Problem Solving

```bash
# Something broken?
make doctor           # Diagnose issues
make deep-clean       # Nuclear clean
make bootstrap        # Fresh start

# Code quality issues?
make fix-all          # Auto-fix everything
make organize         # Reorganize code structure

# Import problems?
make fix-imports      # Fix import organization
make lint-unused      # Handle unused imports
```

## 🎭 T4 System (Unused Imports)

```bash
make lint-unused      # Annotate unused imports
make lint-unused-strict # Enforce zero unannotated F401s

# Manual T4 operations
python3 tools/ci/unused_imports.py --dry-run
python3 tools/ci/unused_imports.py --paths lukhas MATRIZ --strict
```

## 🔒 Security

```bash
make security         # Full security audit
make security-scan    # Quick vulnerability scan
make security-emergency-patch # Emergency patching
```

## 📊 Monitoring & Health

```bash
make audit           # Comprehensive audit
make monitor         # Start monitoring
make audit-tail      # Watch audit logs
make doctor-summary  # Health report
```

## 🧪 Testing

```bash
make test            # Standard tests
make test-cov        # With coverage
make smoke           # Smoke tests
make test-advanced   # Advanced testing (0.001%)
```

## 🎯 Specialized Workflows

```bash
# CI/CD
make ci-local        # Local CI simulation
make check-scoped    # Scoped validation

# Data & Migration
make migrate-dry     # Preview migrations
make backup-local    # Create backup

# AI & Analysis
make ai-analyze      # AI code analysis
make perf           # Performance analysis
```

## 🆘 Emergency Commands

```bash
make security-emergency-patch  # Security emergency
make dr-drill                 # Disaster recovery test
make deep-clean && make bootstrap  # Complete reset
```

## 📚 Documentation

- [Complete Makefile Guide](docs/development/MAKEFILE_USER_GUIDE.md)
- [T4 System Documentation](docs/development/T4_UNUSED_IMPORTS_SYSTEM.md)
- [Auto-generated Help](https://github.com/LukhasAI/Lukhas) → `make help`

---

**Total Targets**: 50+ • **Last Updated**: Sep 12, 2025 • **Status**: ✅ Production Ready