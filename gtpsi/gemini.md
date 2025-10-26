# Gemini AI Navigation Context
*This file is optimized for Gemini AI navigation and understanding*

---
title: gemini
slug: gemini.md
source: claude.me
optimized_for: gemini_ai
last_updated: 2025-10-26
---

# gtpsi Module

**Optional MFA/consent factor using gesture recognition for high-risk actions.**

**Lane**: L2
**Schema**: 3.0.0
**Entrypoints**: 11
**Dependencies**: core

## Quick Reference

```python
# Import from gtpsi
from gtpsi import EdgeGestureProcessor
from gtpsi import GestureApproval
from gtpsi import GestureChallenge
from gtpsi import GestureFeatures
from gtpsi import GestureRecognizer
```

## Components (11 entrypoints)

- `gtpsi.EdgeGestureProcessor`
- `gtpsi.GestureApproval`
- `gtpsi.GestureChallenge`
- `gtpsi.GestureFeatures`
- `gtpsi.GestureRecognizer`
- `gtpsi.GestureType`
- `gtpsi.HIGH_RISK_ACTIONS`
- `gtpsi.RiskLevel`
- `gtpsi.get_action_risk_level`
- `gtpsi.get_max_approval_time`
- `gtpsi.requires_gtpsi_approval`

## Module Metadata

- **Lane**: L2
- **Schema Version**: 3.0.0
- **Tags**: gtpsi
- **Dependencies**: core
- **OpenTelemetry**: 1.37.0

## Related Systems

- **core**: Dependency integration

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
