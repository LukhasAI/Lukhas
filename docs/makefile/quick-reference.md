---
status: wip
type: documentation
owner: unknown
module: makefile
redirect: false
moved_to: null
---

# LUKHAS Makefile Quick Reference

## Essential Commands

| Command | Description | Use Case |
|---------|-------------|----------|
| `make help` | Auto-discovered intelligent help | Get overview of available targets |
| `make doctor` | T4-style repository health scan | Quick system diagnostics |
| `make quick` | Fix issues and run tests | Rapid development validation |
| `make test` | Run full test suite | Comprehensive validation |
| `make security` | Complete security audit | Security compliance check |

## Target Categories

### 🔧 Setup & Installation
```bash
make install        # Install dependencies
make setup-hooks    # Configure pre-commit hooks  
make bootstrap      # Complete environment setup
```

### 🚀 Development
```bash
make dev           # Start development server
make api           # Launch API server
make lane-guard    # Enforce architectural boundaries
make quick         # Fix + test workflow
```

### 🧪 Testing
```bash
make test                  # Full test suite
make test-cov             # Tests with coverage
make smoke                # Lightweight validation
make test-tier1-matriz    # MATRIZ Tier-1 tests
make test-advanced        # 0.001% methodology tests
```

### 🔍 CI/CD
```bash
make ci-local      # Full CI pipeline locally
make monitor       # Code quality dashboard
make audit         # Gold-standard audit
make check-scoped  # Minimal CI validation
make promote       # Module promotion (candidate→lukhas)
```

### 🩺 Doctor & Diagnostics
```bash
make doctor              # Health scan
make doctor-strict       # Fail-fast diagnostics
make doctor-json         # Machine-readable output
make doctor-dup-targets  # Detect duplicate targets
```

### 🛡️ Security
```bash
make security                    # Full security suite
make security-scan              # Quick vulnerability check
make security-fix-all           # Auto-remediate issues
make security-comprehensive-scan # Deep security analysis
make security-ollama            # AI-powered security analysis
make security-emergency-patch   # Emergency response
```

### 📋 Policy & Compliance
```bash
make policy           # Policy validation
make policy-brand     # Brand compliance
make policy-tone      # Tone system validation
make audit-nav        # Auditor navigation
make audit-scan       # Compliance validation
```

### 💾 Backup & DR
```bash
make backup-local     # Local backup
make backup-s3        # Cloud backup
make dr-drill         # Disaster recovery test
make restore-local    # Local restore
```

## Fragment Organization

| Fragment | Domain | Key Targets |
|----------|--------|-------------|
| `mk/ci.mk` | CI/CD & Automation | `ci-local`, `monitor`, `audit`, `promote` |
| `mk/audit.mk` | Compliance & Navigation | `audit-nav`, `audit-scan`, `sbom`, `api-serve` |
| `mk/tests.mk` | Testing Infrastructure | `test`, `test-cov`, `test-tier1-matriz`, `test-advanced` |
| `mk/security.mk` | Security Operations | `security`, `security-scan`, `security-fix-all` |
| `mk/help.mk` | Auto-Generated Help | `help` (overrides static help) |

## Common Workflows

### 📝 Development Session
```bash
make bootstrap     # Setup environment
make doctor       # Verify health
make dev          # Start development
# ... develop ...
make quick        # Validate changes
make test-cov     # Full validation
```

### 🔒 Security Maintenance
```bash
make security-scan              # Quick check
make security-update            # Update packages
make security-comprehensive-scan # Deep analysis
make test-security             # Security tests
```

### 🚢 Release Preparation
```bash
make test-advanced    # Advanced testing
make security-audit   # Security validation  
make policy          # Policy compliance
make audit-scan      # Audit validation
make ci-local        # CI simulation
```

### 🆘 Emergency Response
```bash
make doctor-strict              # Diagnose issues
make security-emergency-patch   # Critical fixes
make test                      # Validate fixes
make security-scan             # Verify security
```

## Target Documentation Format

Add descriptions to any target using `##` syntax:

```makefile
target-name: dependencies ## Clear description of purpose
    @echo "Executing target..."
```

**Example:**
```makefile
deploy: test lint security ## Deploy to production (full validation)
    kubectl apply -f k8s/production/
```

## Advanced Usage

### Parameterized Targets
```bash
make promote SRC=candidate/core/module DST=lukhas/core/module
make deploy-env ENV=staging
make release-tag VERSION=1.2.3
```

### Conditional Execution
```bash
CI=true make test-with-coverage    # XML output for CI
ENVIRONMENT=production make test   # Production-safe tests
DEBUG=1 make dev                   # Debug mode
```

### Parallel Operations
```bash
make -j4 lint-parallel    # Parallel linting
make test-matrix         # Multi-version testing
```

## Troubleshooting

### Common Issues

| Issue | Solution | Command |
|-------|----------|---------|
| Target not found | Check if target exists | `make help` |
| Override warnings | Expected behavior | Normal operation |
| Doctor failures | Auto-fix common issues | `make doctor-fix` |
| Missing fragments | Guarded includes prevent errors | System continues |
| Permission errors | Check file permissions | `chmod +x scripts/*` |

### Debug Commands
```bash
make -n help              # Dry run (syntax check)
make -d target-name       # Debug target execution
make doctor-strict        # Strict health validation
```

### Recovery Commands
```bash
make clean               # Clean build artifacts
make deep-clean          # Clean everything including venv
make bootstrap           # Rebuild environment
make doctor-fix          # Auto-fix common issues
```

## Performance Tips

### Fast Commands
```bash
make smoke               # Quick validation (< 30s)
make doctor             # Fast health check (< 60s)
make test-tier1-matriz  # Fast MATRIZ tests (< 2m)
make security-scan      # Quick security check (< 2m)
```

### Parallel Execution
```bash
make -j$(nproc) lint-parallel    # Use all CPU cores
make test-parallel              # Optimal worker count
```

### Caching
```bash
make analyze-cached             # Use cached analysis
make docker-build              # Docker layer caching
```

## Integration Points

### Git Integration
```bash
make git-hooks          # Install Git hooks
make release-tag        # Create release tags
```

### Docker Integration  
```bash
make docker-build       # Build images
make docker-test        # Test in containers
make docker-clean       # Clean artifacts
```

### External Tools
```bash
make format-all         # Multi-tool formatting
make security-ollama    # AI-powered analysis
```

## System Architecture Quick Facts

- **Modular Design**: Domain-specific fragments in `mk/*.mk`
- **Guarded Includes**: Graceful degradation if fragments missing
- **Auto-Discovery**: Help system discovers existing targets
- **Late Override**: Help fragment safely overrides static help
- **Zero Maintenance**: Documentation updates automatically
- **T4-Grade**: Fast execution, intelligent behavior, robust error handling

## Getting Help

```bash
make help                    # Intelligent auto-discovered help
make doctor                  # System health diagnostics
make audit-nav              # Navigation for auditors
grep -r "## " mk/*.mk       # Find all documented targets
```

For detailed documentation, see:
- `docs/makefile/README.md` - Comprehensive user guide
- `docs/makefile/examples.md` - Examples and best practices
- `mk/*.mk` - Fragment source code with inline documentation