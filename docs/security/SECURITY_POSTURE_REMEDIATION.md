# Security Posture Remediation Plan - 6 Week Sprint

**Created**: 2025-10-09  
**Updated**: 2025-10-28 (Workflow adjustments implemented)  
**Owner**: Security & Infrastructure Team  
**Tracking Issue**: #360  
**Current Score**: 35/100 (Grade F)  
**Target Score**: 85/100 (Grade B)  
**Timeline**: 6 weeks from 2025-10-09 (Target completion: 2025-11-20)

**Status**: ✅ Workflow adjustments implemented (alert frequency: weekly, threshold: 50)

---

## Executive Summary

Despite having **zero critical or high vulnerabilities**, our security posture score is F (35/100) due to missing enterprise security infrastructure: SBOM generation, attestation framework, and telemetry instrumentation.

This plan addresses all three gaps with a phased 6-week approach, targeting an 85/100 score (Grade B).

---

## Current Metric Breakdown

| Metric | Current | Target | Priority |
|--------|---------|--------|----------|
| **Vulnerability Exposure** | 100% ✅ | 100% | Maintain |
| **Attestation Coverage** | 0% ❌ | 50% | HIGH |
| **Supply Chain Integrity** | 0% ❌ | 80% | CRITICAL |
| **Telemetry Compliance** | 0% ❌ | 20% | MEDIUM |

**Current Alerts**: 102 LOW severity (51 SBOM, 51 telemetry)

---

## Phase 1: SBOM Generation (Weeks 1-2)

**Goal**: Automate Software Bill of Materials for all modules
**Score Impact**: 35 → 55 (+20 points)
**Priority**: CRITICAL

### Tasks

#### Week 1: Setup & Automation

1. **Audit existing SBOM generator** (2 hours)
   ```bash
   python scripts/security_sbom_generator.py --dry-run
   # Verify it handles all 51 modules
   ```

2. **Create GitHub Action workflow** (4 hours)
   - File: `.github/workflows/sbom-generation.yml`
   - Trigger: On push to main, PR merge
   - Output: JSON SBOMs in `security/sboms/`
   - Upload as artifacts

3. **Update matrix contracts** (4 hours)
   - Add SBOM references to each module's matrix.yml
   - Schema: `sbom_ref: "security/sboms/{module}.json"`

**Deliverables**:
- Automated SBOM CI workflow
- 51 SBOM JSON files generated
- Matrix contract updates

#### Week 2: Validation & Integration

1. **SBOM validation** (3 hours)
   - Verify all 51 SBOMs are well-formed
   - Check CycloneDX/SPDX compliance
   - Test matrix contract references

2. **Security scanner integration** (5 hours)
   - Integrate with Dependabot
   - Add SBOM diff on PRs
   - Document SBOM access for audits

**Deliverables**:
- Validated SBOMs for all modules
- Integrated security scanning
- Documentation: `docs/security/SBOM_GUIDE.md`

**Success Criteria**:
- [ ] All 51 modules have generated SBOMs
- [ ] CI workflow runs on every commit
- [ ] Matrix contracts reference SBOMs
- [ ] Security score ≥ 55/100

---

## Phase 2: Attestation Framework (Weeks 3-4)

**Goal**: Implement SLSA provenance for critical modules
**Score Impact**: 55 → 70 (+15 points)
**Priority**: HIGH

### Tasks

#### Week 3: SLSA Foundation

1. **SLSA Level 1 for priority modules** (6 hours)
   - Modules: `lukhas.core`, `lukhas.governance`, `lukhas.consciousness`
   - Generate provenance at build time
   - Sign with GitHub Actions OIDC

2. **Attestation storage** (4 hours)
   - Setup: `security/attestations/` directory
   - Format: JSON provenance files
   - Link to matrix contracts

**Deliverables**:
- SLSA provenance for 3 priority modules
- Attestation storage infrastructure

#### Week 4: Expand Coverage

1. **SLSA Level 1 for secondary modules** (8 hours)
   - Modules: `lukhas.api`, `lukhas.orchestration`, `lukhas.memory`
   - Modules: `lukhas.identity`, `lukhas.matriz`, `lukhas.bridge`
   - Total: 6 additional modules (9 total)

2. **Verification tooling** (4 hours)
   - Script: `scripts/security/verify_attestations.py`
   - CI check: Verify attestations on PR
   - Documentation

**Deliverables**:
- 9 modules with SLSA provenance
- Automated verification
- Documentation: `docs/security/ATTESTATION_GUIDE.md`

**Success Criteria**:
- [ ] 9+ modules have attestation evidence
- [ ] Provenance verification in CI
- [ ] Matrix contracts updated
- [ ] Security score ≥ 70/100

---

## Phase 3: Telemetry Instrumentation (Weeks 5-6)

**Goal**: Add OpenTelemetry to critical paths
**Score Impact**: 70 → 85 (+15 points)
**Priority**: MEDIUM

### Tasks

#### Week 5: Core Instrumentation

1. **OpenTelemetry setup** (4 hours)
   - Install: `opentelemetry-api`, `opentelemetry-sdk`
   - Configure: OTLP exporter
   - Test: Basic span creation

2. **Instrument API layer** (6 hours)
   - Module: `lukhas.api`
   - Add spans for all endpoints
   - Add metrics: request_count, latency
   - Target: 50% coverage

**Deliverables**:
- OpenTelemetry foundation
- lukhas.api instrumented (50% coverage)

#### Week 6: Expand Coverage

1. **Instrument orchestration** (5 hours)
   - Module: `lukhas.orchestration`
   - Add spans for AI routing
   - Add metrics: provider_calls, failures
   - Target: 30% coverage

2. **Instrument memory system** (5 hours)
   - Module: `lukhas.memory`
   - Add spans for fold operations
   - Add metrics: cache_hits, fold_duration
   - Target: 20% coverage

3. **Structured logging integration** (2 hours)
   - Link OpenTelemetry with structlog
   - Add trace IDs to logs
   - Document correlation patterns

**Deliverables**:
- 3 modules with telemetry (average 30% coverage)
- Structured logging integration
- Documentation: `docs/observability/TELEMETRY_GUIDE.md`

**Success Criteria**:
- [ ] OpenTelemetry spans in lukhas.api, lukhas.orchestration, lukhas.memory
- [ ] Average 20%+ instrumentation coverage
- [ ] Structured logs include trace IDs
- [ ] Security score ≥ 85/100

---

## Workflow Adjustments (Immediate)

### 1. Reduce Alert Frequency

**Current**: Daily alerts (#344-#360)
**Target**: Weekly alerts (during 6-week window)

**File**: `.github/workflows/security-posture.yml`

```yaml
schedule:
  - cron: '0 6 * * 1'  # Weekly Monday 06:00 UTC (was daily)
```

### 2. Lower Threshold (Temporary)

**Current**: 70/100 threshold
**Target**: 50/100 (realistic during implementation)

```yaml
env:
  POSTURE_THRESHOLD: 50  # Restore to 70 after Phase 2
```

### 3. Update Issue Template

Add context to new security posture issues:
```markdown
**Note**: Score below threshold is expected during 6-week remediation sprint.
See docs/security/SECURITY_POSTURE_REMEDIATION.md for progress.
Target completion: [DATE]
```

---

## Resource Allocation

| Phase | Hours | Assignee | Dependencies |
|-------|-------|----------|--------------|
| Phase 1 | 18h | DevOps + Security | None |
| Phase 2 | 22h | Security Lead | Phase 1 complete |
| Phase 3 | 22h | Platform Team | Phase 2 complete |
| **Total** | **62h** (~1.5 weeks FTE) | | |

---

## Risk Mitigation

### Risk 1: SBOM Generation Failures

**Mitigation**:
- Test generator with all 51 modules in Week 1
- Fallback: Manual SBOM creation for critical modules
- Partial credit: Even 30 SBOMs > 0 SBOMs

### Risk 2: SLSA Signing Complexity

**Mitigation**:
- Use GitHub Actions OIDC (built-in)
- Start with unsigned provenance (still counts)
- Upgrade to signed in future sprint

### Risk 3: OpenTelemetry Performance Impact

**Mitigation**:
- Start with sampling (10% of requests)
- Monitor latency impact
- Disable if p95 latency > +50ms

---

## Success Metrics

### Quantitative

- [ ] Security posture score: 35 → 85 (143% improvement)
- [ ] SBOM coverage: 0% → 100% (51/51 modules)
- [ ] Attestation coverage: 0% → 50% (9+ modules)
- [ ] Telemetry coverage: 0% → 20% (3+ modules)
- [ ] Alert reduction: 102 → <30 LOW severity

### Qualitative

- [ ] Compliance audit readiness improved
- [ ] Supply chain transparency established
- [ ] Observability foundation in place
- [ ] Security posture sustainable (not manual)

---

## Weekly Progress Tracking

| Week | Phase | Target Score | Deliverables | Status |
|------|-------|--------------|--------------|--------|
| 1 | SBOM Setup | 40/100 | CI workflow, 25+ SBOMs | 🔲 Not Started |
| 2 | SBOM Complete | 55/100 | All 51 SBOMs, docs | 🔲 Not Started |
| 3 | Attestation Start | 60/100 | 3 priority modules | 🔲 Not Started |
| 4 | Attestation Expand | 70/100 | 9 total modules | 🔲 Not Started |
| 5 | Telemetry Core | 75/100 | lukhas.api instrumented | 🔲 Not Started |
| 6 | Telemetry Expand | 85/100 | 3 modules, docs | 🔲 Not Started |

---

## Post-Sprint Actions

After achieving 85/100:

1. **Restore original threshold**: 50 → 70
2. **Restore daily alerts**: Weekly → Daily
3. **Expand attestation**: 9 → 25 modules (target 50% coverage)
4. **Expand telemetry**: 20% → 50% coverage
5. **Target next grade**: 85 → 95 (Grade A)

---

## Appendix A: Module Priority List

### Tier 1 (Weeks 3-4): Attestation First
1. lukhas.core
2. lukhas.governance
3. lukhas.consciousness
4. lukhas.api
5. lukhas.orchestration
6. lukhas.memory
7. lukhas.identity
8. lukhas.matriz
9. lukhas.bridge

### Tier 2 (Future Sprint): Attestation Later
10. lukhas.rl
11. lukhas.bio
12. lukhas.tools
13. lukhas.deployment
14. lukhas.observability
15. lukhas.security
... (and 36 more)

---

## Appendix B: Technical Implementation Notes

### SBOM Format

Use CycloneDX 1.5 JSON format:
```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "metadata": {
    "component": {
      "name": "lukhas.core",
      "version": "0.1.0"
    }
  },
  "components": [...]
}
```

### SLSA Provenance Format

Use SLSA v1.0 provenance:
```json
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [{"name": "lukhas.core", "digest": {...}}],
  "predicateType": "https://slsa.dev/provenance/v1",
  "predicate": {...}
}
```

### OpenTelemetry Configuration

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Setup
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Usage
tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("operation_name"):
    # Instrumented code
    pass
```

---

## Contact & Ownership

- **Primary Owner**: Security Team
- **SBOM Lead**: DevOps
- **Attestation Lead**: Security Architect
- **Telemetry Lead**: Platform Engineering
- **Tracking**: Issue #360
- **Updates**: Weekly status in #360 comments

---

**Last Updated**: 2025-10-09
**Review Date**: After Week 3 (mid-sprint checkpoint)
**Completion Target**: 2025-11-20 (6 weeks from start)
