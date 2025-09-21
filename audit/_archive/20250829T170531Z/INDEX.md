# 🔍 AUDIT Navigation Hub

**Purpose**: External auditor deep search entry point for LUKHAS AI system analysis.

## Quick Start for Auditors

**Repo Status**: T4-compliant with per-directory indexing
**Lane System**: candidate/ → lukhas/ promotion architecture
**Test Coverage**: 85%+ minimum (targeting 100%)

## 📋 Audit Anchors

### Core System Analysis
- **[System Map](SYSTEM_MAP.md)** - Architecture overview with dependency graphs
- **[MATRIZ Readiness](MATRIZ_READINESS.md)** - Memory-Attention-Thought-Action system contracts
- **[Identity Readiness](IDENTITY_READINESS.md)** - Authentication/authorization protocols

### Technical Specifications
- **[API Documentation](API/)** - OpenAPI specs and endpoint schemas
- **[Data Schemas](SCHEMAS/)** - Event structures and validation rules
- **[Fixtures](../ops/fixtures/)** - Test data and configuration examples

### Deep Search Indexes
Located in `reports/deep_search/`:
- Per-directory source indexes (not overwhelming single files)
- Health flags (symlinks, zero-bytes, import cycles)
- Cross-lane dependency analysis

## 🎯 Key Validation Points

1. **Lane Architecture Compliance** - No candidate/ → lukhas/ violations
2. **Constellation Framework Adherence** - ⚛️🧠🛡️ principles throughout
3. **Test Coverage** - Comprehensive smoke and integration tests
4. **Security Posture** - Guardian System v1.0.0 drift detection
5. **Branding Consistency** - Approved terminology and messaging

## 📊 Metrics Dashboard

Run these commands for current system health:
```bash
make audit-scan    # Full health check
make test-cov      # Test coverage report
npm run policy:all # Brand/policy compliance
```

**Navigation**: Start with [System Map](SYSTEM_MAP.md) for architecture overview, then drill into specific readiness documents based on audit focus areas.
