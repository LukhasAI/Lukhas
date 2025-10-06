---
status: wip
type: documentation
---
# CI Module Context - Vendor-Neutral AI Guidance
*This file provides domain-specific context for any AI development tool*
*Also available as claude.me for Claude Desktop compatibility*


**Module**: ci
**Purpose**: Continuous Integration infrastructure and automation
**Lane**: L2 (Integration)
**Language**: Python
**Last Updated**: 2025-10-02

---

## Module Overview

The ci module provides continuous integration infrastructure for LUKHAS AI, coordinating with GitHub Actions workflows to ensure code quality, testing, and deployment automation. While the module itself contains minimal Python code, it serves as a coordination point for CI/CD processes.

### Key Components
- **GitHub Actions Integration**: 50+ workflow files in `.github/workflows/`
- **Test Automation**: Automated test execution across all modules
- **Quality Gates**: Code coverage, linting, and type checking
- **Deployment Automation**: Automated deployment pipelines
- **Security Scanning**: Dependency scanning and vulnerability detection

### Constellation Framework Integration
- **🛡️ Watch Star (Guardian)**: Security scanning and compliance checks
- **✦ Trail Star (Memory)**: Build history and artifact storage
- **⚛️ Anchor Star (Identity)**: Authentication for CI/CD operations

---

## Architecture

### GitHub Actions Workflows

The CI system is primarily implemented through GitHub Actions workflows located in `.github/workflows/`:

#### Core CI Workflows

**ci.yml** (10,786 bytes)
- Main continuous integration workflow
- Runs on all pull requests and commits
- Executes test suites, linting, type checking
- Generates coverage reports

**ci-cd.yml** (12,196 bytes)
- Combined CI/CD pipeline
- Automated deployment on successful builds
- Environment promotion workflows

**advanced-testing.yml** (8,154 bytes)
- Extended test suites
- Performance testing
- Integration testing
- E2E workflows

**enterprise-ci.yml** (16,222 bytes)
- Enterprise-grade CI pipeline
- Extended security scans
- Compliance validation
- Production deployment gates

#### Quality Assurance Workflows

**coverage-gates.yml** (15,812 bytes)
- Code coverage enforcement
- Coverage threshold validation (75%+ requirement)
- Coverage reports and badges

**config-validation.yml** (2,235 bytes)
- Configuration file validation
- Schema conformance checking
- YAML/JSON validation

**dependency-pinning.yml** (11,882 bytes)
- Dependency version management
- Security vulnerability scanning
- Automated dependency updates

#### Specialized Workflows

**constellation-migration-check.yml** (2,162 bytes)
- Constellation Framework migration validation
- Breaking change detection
- API contract verification

**critical-path-approval.yml** (10,058 bytes)
- Production deployment approval process
- Critical path validation
- Rollback procedures

**demo-parity.yml** (7,197 bytes)
- Demo environment synchronization
- Feature parity validation

---

## Module Structure

```
ci/
├── module.manifest.json         # CI module manifest (schema v1.0.0)
├── module.manifest.lock.json    # Locked manifest
├── README.md                    # CI overview
├── config/                      # CI configuration
├── docs/                        # CI documentation
├── schema/                      # CI schemas
└── tests/                       # CI module tests
    ├── conftest.py
    ├── test_ci_unit.py
    └── test_ci_integration.py
```

### GitHub Actions Structure

```
.github/workflows/
├── ci.yml                       # Main CI workflow
├── ci-cd.yml                    # Combined CI/CD
├── advanced-testing.yml         # Extended test suites
├── enterprise-ci.yml            # Enterprise CI pipeline
├── coverage-gates.yml           # Coverage enforcement
├── dependency-pinning.yml       # Dependency management
├── config-validation.yml        # Config validation
├── constellation-migration-check.yml  # Framework validation
├── critical-path-approval.yml   # Production approvals
├── demo-parity.yml              # Demo synchronization
├── dream-expand.yml             # Dream system CI
├── autolabel.yml                # PR auto-labeling
└── (40+ additional workflows)
```

---

## Observability

### Required Spans

```python
# Required span from module.manifest.json
REQUIRED_SPANS = [
    "lukhas.ci.operation",     # CI operations tracking
]
```

### CI Metrics

The CI system tracks:
- **Build Success Rate**: Percentage of successful builds
- **Build Duration**: Time to complete CI pipeline
- **Test Pass Rate**: Percentage of passing tests
- **Coverage Metrics**: Code coverage percentages
- **Deployment Frequency**: Deployments per day/week

---

## Key CI/CD Features

### 1. Automated Testing

```yaml
# Example from ci.yml
- name: Run Tests
  run: |
    pytest tests/ --cov=. --cov-report=html
    pytest tests/consciousness/ -v
    pytest tests/memory/ -v
```

### 2. Coverage Enforcement

```yaml
# Example from coverage-gates.yml
- name: Check Coverage
  run: |
    coverage report --fail-under=75
```

### 3. Security Scanning

```yaml
# Example from dependency-pinning.yml
- name: Security Scan
  run: |
    pip-audit
    safety check
    bandit -r .
```

### 4. Quality Gates

- **Linting**: `ruff`, `black`, `isort`
- **Type Checking**: `mypy` with strict mode
- **Security**: `bandit`, `safety`, `pip-audit`
- **Documentation**: Doc coverage checks

---

## Development Guidelines

### 1. Adding New Workflows

Create workflow files in `.github/workflows/`:

```yaml
name: Custom CI Workflow
on:
  pull_request:
    branches: [main]
jobs:
  custom-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Custom validation
        run: |
          # Custom CI logic
```

### 2. Local CI Testing

```bash
# Run CI checks locally
make lint              # Linting
make test              # Test suite
make coverage          # Coverage report
make security-scan     # Security checks
```

### 3. CI Configuration

Configuration files in `ci/config/`:
- `pytest.ini` - Pytest configuration
- `coverage.rc` - Coverage configuration
- `mypy.ini` - Type checking configuration

---

## MATRIZ Pipeline Integration

This module operates within the MATRIZ cognitive framework:

- **M (Memory)**: Build history and artifact storage
- **A (Attention)**: Focus on failed builds and critical issues
- **T (Thought)**: Decision making in deployment strategies
- **R (Risk)**: Risk assessment for production deployments
- **I (Intent)**: Intent understanding for CI/CD automation
- **A (Action)**: Automated build and deployment actions

---

## Performance Targets

- **CI Pipeline**: <10 minutes for full test suite
- **Quick Tests**: <2 minutes for smoke tests
- **Security Scans**: <5 minutes for dependency scanning
- **Coverage Report**: <3 minutes to generate
- **Deployment**: <5 minutes to production

---

## Dependencies

**Required Modules**: None (infrastructure module)

**GitHub Actions Dependencies**:
- actions/checkout@v3
- actions/setup-python@v4
- codecov/codecov-action@v3
- github/codeql-action@v2

---

## Related Modules

- **Deployment** ([../deployment/](../deployment/)) - Deployment automation
- **Ops** ([../ops/](../ops/)) - Operations management
- **Docker** ([../docker/](../docker/)) - Container infrastructure
- **Monitoring** ([../monitoring/](../monitoring/)) - System monitoring

---

## Documentation

- **README**: [ci/README.md](README.md) - CI overview
- **Docs**: [ci/docs/](docs/) - CI documentation and guides
- **Tests**: [ci/tests/](tests/) - CI module test suites
- **Module Index**: [../MODULE_INDEX.md](../MODULE_INDEX.md#ci)

---

**Status**: Integration Lane (L2)
**Manifest**: ✓ module.manifest.json (schema v1.0.0)
**Team**: Core
**Code Owners**: @lukhas-core
**GitHub Workflows**: 50+ workflow files
**Last Updated**: 2025-10-02
