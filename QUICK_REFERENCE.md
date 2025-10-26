# LUKHAS Quick Reference Guide
*Essential commands and workflows for LUKHAS AI development*

## 🚀 Quick Start

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
source .venv/bin/activate  # Activate virtual environment
make help                   # See all available commands
```

## 📋 Essential Commands

### Development Workflow
```bash
make dev                # Start development environment
make test               # Run comprehensive test suite
make smoke              # Quick smoke tests (15 tests)
make lint               # Lint and type checking
make format             # Format code with Black
```

### Testing
```bash
make smoke              # Smoke tests (fast)
make smoke-matriz       # MATRIZ-specific smoke tests
make test-tier1         # Critical system tests
make test-all           # Full suite (775+ tests)
pytest tests/smoke/     # Basic health checks
pytest tests/integration/ # Integration tests
pytest tests/unit/      # Unit tests
```

### Build & Quality
```bash
make audit              # Comprehensive system audit
make lane-guard         # Validate import boundaries
make imports-guard      # Check import health
make security-scan      # Security validation
make doctor             # System health diagnostics
```

### System Health
```bash
make smoke              # 10 smoke tests (should all pass)
make doctor             # Comprehensive diagnostics
git status              # Check working tree
make clean              # Clean build artifacts
```

## 🏗️ Architecture

### Lane System (3-Lane Development)
```
candidate/    # Development lane (2,877 files) - Experiments
  ↓
core/         # Integration lane (253+ components) - Testing
  ↓
lukhas/       # Production lane (692 components) - Battle-tested
```

**Critical Rule**: `lukhas/` can import from `core/` and `matriz/`, but `candidate/` CANNOT import from `lukhas/`

### Key Directories
```
lukhas/              # Production lane
├── api/            # Public API
├── consciousness/  # Consciousness processing
├── governance/     # Guardian system
├── identity/       # ΛiD authentication
└── core/           # Core coordination

matriz/             # MATRIZ cognitive engine
├── core/           # Core MATRIZ components
├── nodes/          # Cognitive nodes
└── consciousness/  # Consciousness modules

core/               # Integration lane
├── governance/     # Ethics, compliance, auth
├── orchestration/  # Brain orchestration
└── consciousness/  # Consciousness systems

candidate/          # Development lane
├── consciousness/  # Research
├── bio/           # Bio-inspired
├── quantum/       # Quantum-inspired
└── bridge/        # External integrations

tests/             # Test suites
├── smoke/         # Health checks
├── unit/          # Component tests
├── integration/   # Cross-system tests
└── e2e/          # End-to-end workflows
```

## 🧪 Testing Philosophy

### Test Hierarchy
1. **Smoke Tests** (10 tests, <30s) - Basic health
2. **Unit Tests** - Component level
3. **Integration Tests** - System level
4. **E2E Tests** - Full workflows

### Running Specific Tests
```bash
pytest tests/smoke/test_basic_imports.py -v
pytest tests/unit/test_my_component.py -v
pytest -m smoke                    # Run smoke marker
pytest -m "not slow"               # Skip slow tests
pytest --maxfail=1                 # Stop on first failure
```

## 📝 Git Workflow

### T4 Commit Standards
```
<type>(<scope>): <imperative subject ≤72>

<optional body with Problem/Solution/Impact>

<trailers: Closes, Security-Impact, LLM>
```

**Types**: feat, fix, docs, test, chore, refactor, perf, ci, security  
**Scopes**: core, matriz, identity, governance, consciousness, tools, ops

### Examples
```bash
# Good
git commit -m "feat(governance): add WebAuthn passkey support"
git commit -m "fix(matriz): resolve circular import in nodes"

# Bad
git commit -m "BREAKTHROUGH: Fixed everything!!!"
git commit -m "updates"
```

### Branch Management
```bash
git checkout -b feat/my-feature     # Create feature branch
git push origin feat/my-feature     # Push to remote
gh pr create --base main            # Create PR
```

## 🔍 Common Tasks

### Adding a New Module
```bash
# 1. Create in candidate lane first
mkdir -p candidate/my_module
# 2. Implement and test
pytest tests/unit/test_my_module.py
# 3. Validate
make lane-guard
make smoke
# 4. Promote when ready (via integration guide)
```

### Running Integration
```bash
# Follow integration guides
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
# See docs/audits/INTEGRATION_GUIDE_0X.md
make lane-guard     # Verify boundaries
make smoke          # Baseline check
```

### Checking Health
```bash
make doctor                          # Full diagnostics
make smoke                           # Quick health
./scripts/cleanup_stale_branches.sh  # Branch hygiene
```

## 🛠️ Troubleshooting

### Import Errors
```bash
# Check lane boundaries
make lane-guard

# Verify Python path
python3 -c "import sys; print('\n'.join(sys.path))"

# Check imports
make imports-guard
```

### Test Failures
```bash
# Run with verbose output
pytest -vv tests/failing_test.py

# Run with debugging
pytest --pdb tests/failing_test.py

# Check specific marker
pytest -m smoke -v
```

### Build Issues
```bash
make clean          # Clean artifacts
make deep-clean     # Deep clean including caches
make bootstrap      # Fresh setup
```

## 📊 Quality Targets

- **Syntax Health**: >95% files compile
- **Import Health**: <5% circular imports
- **Test Coverage**: 75%+ for production promotion
- **Code Debt**: <1000 TODO/FIXME
- **Security**: 0 hardcoded secrets

## 🔗 Key Resources

### Documentation
- Main: `README.md`
- Architecture: `docs/architecture/README.md`
- Development: `docs/development/README.md`
- MATRIZ: `docs/MATRIZ_GUIDE.md`
- Context Files: 42 distributed `claude.me` files

### Integration Guides
- Batch 1-8: `docs/audits/INTEGRATION_GUIDE_0X.md`
- Summary: `docs/audits/INTEGRATION_MANIFEST_SUMMARY.md`
- Latest: `BATCH5_INTEGRATION_SUMMARY.md`

### Health & Diagnostics
- Health Report: `CODEBASE_HEALTH_REPORT.md`
- Doctor: `make doctor`
- Audit: `make audit`

## 🎯 Current Focus (Oct 2025)

**Active Work**: Hidden Gems Integration (Batches 1-8)
- ✅ Batch 5: 20 modules completed (governance, consciousness)
- 🔲 Batch 6-8: ~120-140 modules remaining
- **Goal**: Promote 193 high-value modules from labs → production

**Recent Completions**:
- Batch 5: Multi-Modal Identity & Ethics (20 modules, ~19K LOC)
- Health Report: Comprehensive diagnostics generated
- Cleanup: Temp files removed, stale branches identified

## 💡 Pro Tips

1. **Always run smoke tests** before committing: `make smoke`
2. **Check lane boundaries** when adding imports: `make lane-guard`
3. **Read context files** before working in new directories
4. **Use T4 commit standards** for all commits
5. **Test in candidate/** before promoting to core/lukhas
6. **Keep branches focused** - one feature per branch
7. **Run `make doctor`** weekly for health monitoring

## 🆘 Getting Help

```bash
make help                    # Show all make targets
pytest --help                # Pytest options
git --help                   # Git help
gh pr --help                 # GitHub CLI help
```

---

**Last Updated**: 2025-10-26  
**Version**: Post Batch-5 Integration  
**Maintainer**: LUKHAS AI Team + Claude Code
