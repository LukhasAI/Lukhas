---
status: wip
type: documentation
---
# LUKHAS AI Context - Vendor-Neutral AI Guidance
*This file provides domain-specific context for any AI development tool*
*Also available as claude.me for Claude Desktop compatibility*

---


# benchmarks Module

**LUKHAS benchmarks module implementing specialized benchmarks functionality with 19 components for integrated system operations.**

**Lane**: L2
**Schema**: 1.0.0
**Entrypoints**: 8
**Dependencies**: memory

## Quick Reference

```python
# Import from benchmarks
from benchmarks.matriz_pipeline import matrizBenchmarks
from benchmarks.memory_performance import MemoryBenchmarks
from benchmarks.memory_performance import run_all_benchmarks
from benchmarks.memory_performance import test_cascade_prevention_benchmark
from benchmarks.memory_performance import test_memory_recall_benchmark
```

## Components (8 entrypoints)

- `benchmarks.matriz_pipeline.MATRIZBenchmarks`
- `benchmarks.memory_performance.MemoryBenchmarks`
- `benchmarks.memory_performance.run_all_benchmarks`
- `benchmarks.memory_performance.test_cascade_prevention_benchmark`
- `benchmarks.memory_performance.test_memory_recall_benchmark`
- `benchmarks.memory_system_benchmarks.MemoryItem`
- `benchmarks.memory_system_benchmarks.MemorySystemBenchmarks`
- `benchmarks.memory_system_benchmarks.MockMemorySystem`

## Module Metadata

- **Lane**: L2
- **Schema Version**: 1.0.0
- **Tags**: benchmarks
- **Dependencies**: memory
- **OpenTelemetry**: 1.37.0

## Related Systems

- **memory**: Dependency integration

---

**Documentation Status**: ✅ Complete
**Last Updated**: 2025-11-07
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
