---
status: wip
type: documentation
---
# MATRIZ Audit Report
Generated: 2025-09-27T14:40:40.650949Z

## Executive Summary

- **Total Modules**: 141
- **Modules with Contracts**: 133 (94.3%)
- **Schema Validation Success**: 26 modules
- **Modules with Import Issues**: 2
- **Bad Import Patterns**: 40

## Lane Distribution

- **L5 (Core)**: 0 modules
- **L4 (Accepted)**: 2 modules
- **L3 (Candidate)**: 27 modules
- **L2 (Development)**: 36 modules
- **L1 (Experimental)**: 7 modules
- **L0 (Archive)**: 69 modules

## Module Status Heatmap

| Module | Schema | Identity | OSV | Telemetry | Policy | Lane | Import Issues |
|--------|--------|----------|-----|-----------|--------|------|---------------|
| `accepted` | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | L4 | ✅ |
| `accepted.bio` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L4 | ✅ |
| `agents` | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | L2 | ✅ |
| `api` | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | L3 | ✅ |
| `bio` | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | L3 | ⚠️ |
| `bio.core` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `branding` | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | L3 | ✅ |
| `bridge` | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | L3 | ✅ |
| `bridge.llm_wrappers` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `candidate` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L3 | ⚠️ |
| `cognitive_core` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L1 | ✅ |
| `consciousness` | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | L3 | ✅ |
| `constellation` | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | L2 | ✅ |
| `constellation.triad` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `contracts` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `core` | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | L3 | ✅ |
| `core.bridge` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `core.colonies` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `core.common` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L3 | ✅ |
| `core.filesystem` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `core.matriz` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L3 | ✅ |
| `core.policy` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `core.registry` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `core.reliability` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L3 | ✅ |
| `core.symbolic` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `core.symbolic.constraints` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `core.symbolism` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `deployment` | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | L3 | ✅ |
| `emotion` | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | L2 | ✅ |
| `governance` | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | L3 | ✅ |
| `governance.consent_ledger` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L3 | ✅ |
| `governance.consent_ledger.providers` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `governance.ethics` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `governance.guardian` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `governance.identity` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L3 | ✅ |
| `governance.identity.auth_backend` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `governance.security` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `identity` | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | L3 | ✅ |
| `identity.auth` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `identity.facades` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `identity.oidc` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L3 | ✅ |
| `identity.passkey` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L3 | ✅ |
| `identity.passkey.providers` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `identity.qrg` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `identity.services` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `identity.wallet` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `interfaces` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L1 | ✅ |
| `ledger` | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | L3 | ✅ |
| `lukhas` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L1 | ✅ |
| `lukhas.accepted` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.accepted.bio` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.agents` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.api` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.bio` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.bio.core` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.branding` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.bridge` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.bridge.llm_wrappers` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.consciousness` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.constellation` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.constellation.triad` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.core` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.core.bridge` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.core.colonies` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.core.common` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.core.filesystem` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.core.matriz` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.core.policy` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.core.registry` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.core.reliability` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.core.symbolic` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.core.symbolic.constraints` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.core.symbolism` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.deployment` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.emotion` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.governance` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.governance.consent_ledger` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.governance.consent_ledger.providers` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.governance.ethics` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.governance.guardian` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.governance.identity` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.governance.identity.auth_backend` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.governance.security` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.identity` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.identity.auth` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.identity.facades` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.identity.oidc` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.identity.passkey` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.identity.passkey.providers` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.identity.qrg` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.identity.services` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.identity.wallet` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.ledger` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.matriz` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.matriz.runtime` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.memory` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.memory.backends` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.memory.emotional` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.observability` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.orchestration` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.orchestration.context` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.orchestration.providers` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.qi` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.rl` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.rl.coordination` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.rl.engine` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.rl.environments` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.rl.experience` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.root` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.security` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.tools` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.trace` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.trinity` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `lukhas.vivox` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `matriz` | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | L2 | ✅ |
| `matriz.runtime` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `memory` | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | L3 | ✅ |
| `memory.backends` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L3 | ✅ |
| `memory.emotional` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `observability` | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | L3 | ✅ |
| `orchestration` | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | L3 | ✅ |
| `orchestration.context` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `orchestration.providers` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L3 | ✅ |
| `qi` | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | L2 | ✅ |
| `rl` | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | L3 | ✅ |
| `rl.coordination` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `rl.engine` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `rl.environments` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L2 | ✅ |
| `rl.experience` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L1 | ✅ |
| `root` | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | L3 | ✅ |
| `security` | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | L3 | ✅ |
| `shims` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L1 | ✅ |
| `tests` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L1 | ✅ |
| `tools` | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | L3 | ✅ |
| `trace` | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | L2 | ✅ |
| `tracks.status` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `tracks_slo_report_20250926_121703` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `trinity` | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | L2 | ✅ |
| `utils` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L1 | ✅ |
| `validation_results` | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | L0 | ✅ |
| `vivox` | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | L2 | ✅ |

## Top Issues

### Modules Requiring Attention

- **candidate**: Schema validation failed, Identity validation failed, 36 import issues
- **accepted.bio**: Schema validation failed, Identity validation failed
- **bio.core**: Schema validation failed, Identity validation failed
- **bridge.llm_wrappers**: Schema validation failed, Identity validation failed
- **cognitive_core**: Schema validation failed, Identity validation failed
- **constellation.triad**: Schema validation failed, Identity validation failed
- **contracts**: Schema validation failed, Identity validation failed
- **core.bridge**: Schema validation failed, Identity validation failed
- **core.colonies**: Schema validation failed, Identity validation failed
- **core.common**: Schema validation failed, Identity validation failed

## Suggested Actions

### Phase 1: Critical Fixes
1. Address schema validation failures
2. Fix bad import patterns (`lukhas.lukhas.*`, `lukhas.accepted.*`)
3. Resolve identity configuration issues

### Phase 2: Organization
1. Consolidate modules with multiple paths
2. Move modules to appropriate lanes
3. Add contracts to modules without them

### Phase 3: Quality Assurance
1. Add test coverage to modules lacking tests
2. Implement OSV scanning for security
3. Set up telemetry for monitoring

---
*This report was generated by the MATRIZ audit system.*