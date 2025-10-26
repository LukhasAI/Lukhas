# Gemini AI Navigation Context
*This file is optimized for Gemini AI navigation and understanding*

---
title: gemini
slug: gemini.md
source: claude.me
optimized_for: gemini_ai
last_updated: 2025-10-26
---

# guardian Module

**LUKHAS guardian module implementing specialized guardian functionality with 6 components for integrated system operations.**

**Lane**: L2
**Schema**: 3.0.0
**Entrypoints**: 6
**Dependencies**: None

## Quick Reference

```python
# Import from guardian
from guardian.emit import emit_confidence_metrics
from guardian.emit import emit_exemption
from guardian.emit import emit_guardian_action_with_exemplar
from guardian.emit import emit_guardian_decision
from guardian.emit import redact_pii_for_exemplars
```

## Components (6 entrypoints)

- `guardian.emit.emit_confidence_metrics`
- `guardian.emit.emit_exemption`
- `guardian.emit.emit_guardian_action_with_exemplar`
- `guardian.emit.emit_guardian_decision`
- `guardian.emit.redact_pii_for_exemplars`
- `guardian.emit.validate_dual_approval`

## Module Metadata

- **Lane**: L2
- **Schema Version**: 3.0.0
- **Tags**: guardian
- **Dependencies**: None (foundational)
- **OpenTelemetry**: 1.37.0

## Related Systems



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
