---
title: LUKHAS Developer Guide
status: stable
owner: core-team
last_review: 2025-10-02
tags: [development, manifest-system, t4-standards]
---

# LUKHAS Developer Guide

Welcome to the LUKHAS development guide. This document provides essential information for developers working with the LUKHAS AI platform.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Module Manifest System](#module-manifest-system)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Contributing](#contributing)

## Getting Started

For a quick introduction to LUKHAS, see the [Quick Start Guide](./QUICK_START.md).

## Development Environment

### Prerequisites

- Python 3.9+
- Git
- Docker (optional, for containerized development)

### Setup

```bash
# Clone the repository
git clone https://github.com/LukhasAI/Lukhas.git
cd Lukhas

# Install dependencies
pip install -r requirements.txt

# Run tests
make test
```

## Module Manifest System

LUKHAS uses a self-enforcing manifest system for module metadata and contracts.

- **Manifests:** Human-authored metadata in `module.manifest.json`
- **Registry:** Auto-generated canonical source at `artifacts/module.registry.json`
- **Conformance:** Tests verify declared entrypoints work

### Key Commands

- `make manifests-validate` - Check manifest validity
- `make manifest-system` - Run full pipeline
- See [MANIFEST_SYSTEM.md](./MANIFEST_SYSTEM.md) for details

### Lifecycle

Manifest → Lockfile → Registry → Conformance Tests → CI

### Adding a New Module

1. Create `module.manifest.json` in your module root
2. Validate with `make manifests-validate`
3. Generate lockfile with `make manifest-lock`
4. Update registry with `make manifest-index`
5. Commit both manifest and lockfile

### Schema Properties

The manifest schema supports comprehensive module metadata including:

- **Core**: `schema_version`, `module`, `description`
- **Ownership**: `team`, `codeowners`, `slack_channel`
- **Layout**: `code_layout`, `paths` (code, config, tests, docs, assets)
- **Runtime**: `language`, `entrypoints`
- **Matrix**: `contract`, `lane`, `gates_profile`
- **Identity**: `requires_auth`, `tiers`, `scopes`
- **Links**: `repo`, `docs`, `issues`, `sbom`
- **Observability**: `required_spans`, `otel_semconv_version`
- **Dependencies**: Module dependencies
- **Aliases**: Alternative import names (for legacy support)
- **Deprecations**: Migration timeline for renamed/removed modules

## Code Standards

### T4/0.01% Standards

LUKHAS adheres to T4/0.01% quality standards:

- Comprehensive type hints
- 90%+ test coverage
- Zero critical security vulnerabilities
- Full documentation coverage
- Performance SLOs defined and met

### Commit Messages

Follow the T4 minimal standard:

```
<type>(<scope>): <imperative subject ≤72>

Problem:
- [Describe the problem]

Solution:
- [Describe the solution]

Impact:
- [Describe the impact]
```

**Types**: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert, security

**Scopes**: core, matriz, identity, memory, glyph, api, orchestration, governance, consciousness, interfaces, monitoring, tools, ops, serve, lanes, hygiene, docs

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run specific test suite
pytest tests/unit/
pytest tests/integration/

# Run with coverage
make test-coverage
```

### Test Types

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **Conformance Tests**: Auto-generated from manifest registry
- **E2E Tests**: Test full system workflows

## Contributing

### Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Ensure all tests pass
4. Update documentation
5. Submit PR with clear description
6. Address review feedback

### Code Review

All code must pass:

- Automated tests
- Linting and formatting checks
- Security scans
- Manifest validation
- Code review by maintainers

For detailed contributing guidelines, see [CONTRIBUTING.md](./governance/CONTRIBUTING.md).

## Additional Resources

- [Architecture Documentation](./ARCHITECTURE.md)
- [API Reference](./API_REFERENCE.md)
- [Testing Guide](./TESTING_GUIDE.md)
- [Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Manifest System Documentation](./MANIFEST_SYSTEM.md)

---

**Last Updated**: 2025-10-02
**Maintainers**: LUKHAS Core Team
