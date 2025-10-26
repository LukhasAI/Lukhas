# Gemini AI Navigation Context
*This file is optimized for Gemini AI navigation and understanding*

---
title: gemini
slug: gemini.md
source: claude.me
optimized_for: gemini_ai
last_updated: 2025-10-26
---

# config Module

**LUKHAS config module implementing specialized config functionality with 81 components for integrated system operations.**

**Lane**: L2
**Schema**: 3.0.0
**Entrypoints**: 5
**Dependencies**: memory

## Quick Reference

```python
# Import from config
from config.audit_safety_defaults import AuditSafetyConfig
from config.audit_safety_defaults import SafetyDefaultsManager
from config.audit_safety_defaults import create_audit_safety_manager
from config.env import EnvironmentConfig
from config.env import LUKHASConfig
```

## Components (5 entrypoints)

- `config.audit_safety_defaults.AuditSafetyConfig`
- `config.audit_safety_defaults.SafetyDefaultsManager`
- `config.audit_safety_defaults.create_audit_safety_manager`
- `config.env.EnvironmentConfig`
- `config.env.LUKHASConfig`

## Module Metadata

- **Lane**: L2
- **Schema Version**: 3.0.0
- **Tags**: config
- **Dependencies**: memory
- **OpenTelemetry**: 1.37.0

## Related Systems

- **memory**: Dependency integration

---

**Documentation Status**: ✅ Complete
**Last Updated**: 2025-10-18
**Maintainer**: LUKHAS Core Team


## 🚀 GA Deployment Status

**Current Status**: 66.7% Ready (6/9 tasks complete)

### Recent Milestones
- ✅ **RC Soak Testing**: 60-hour stability validation (99.985% success rate)
- ✅ **Dependency Audit**: 196 packages, 0 CVEs
- ✅ **OpenAI Façade**: Full SDK compatibility validated
- ✅ **Guardian MCP**: Production-ready deployment
- ✅ **OpenAPI Schema**: Validated and documented

### New Documentation
- docs/GA_DEPLOYMENT_RUNBOOK.md - Comprehensive GA deployment procedures
- docs/DEPENDENCY_AUDIT.md - 196 packages, 0 CVEs, 100% license compliance
- docs/RC_SOAK_TEST_RESULTS.md - 60-hour stability validation (99.985% success)

### Recent Updates
- E402 linting cleanup - 86/1,226 violations fixed (batches 1-8)
- OpenAI façade validation - Full SDK compatibility
- Guardian MCP server deployment - Production ready
- Shadow diff harness - Pre-audit validation framework
- MATRIZ evaluation harness - Comprehensive testing

**Reference**: See [GA_DEPLOYMENT_RUNBOOK.md](./docs/GA_DEPLOYMENT_RUNBOOK.md) for deployment procedures.

---
