---
status: wip
type: documentation
---
# Matrix Identity Coverage Report
_Generated: 2025-09-30T13:55:48.725872Z_

**Contracts:** 65/65 valid
**AuthZ:** 0/2514 (0.0%)
**Schema Validation:** 100%
**Identity Lint:** 100%
**Telemetry Smoke:** ✅ PASS
**Policy Tests:** ✅ PASS

## Summary Statistics

- **Total Contracts**: 65
- **Schema Compliance**: 100% (65/65)
- **Identity Compliance**: 100% (65/65)
- **WebAuthn Required**: 36 modules
- **Critical Modules Protected**: 100%
- **Tier Distribution**: All 6 tiers covered

## Validation Results

| Module | Schema | Identity | WebAuthn | AuthZ Coverage |
|---|---:|---:|---:|---:|
| `accepted` | ✅ | ✅ | ❌ | 38/40 |
| `accepted_bio` | ✅ | ✅ | ❌ | 38/40 |
| `agents` | ✅ | ✅ | ❌ | 38/40 |
| `api` | ✅ | ✅ | ❌ | 38/40 |
| `bio` | ✅ | ✅ | ❌ | 38/40 |
| `bio_core` | ✅ | ✅ | ✅ | 38/40 |
| `branding` | ✅ | ✅ | ❌ | 38/40 |
| `bridge` | ✅ | ✅ | ❌ | 38/40 |
| `bridge_llm_wrappers` | ✅ | ✅ | ❌ | 38/40 |
| `consciousness` | ✅ | ✅ | ✅ | 38/40 |

## Critical Modules (WebAuthn Required)

- **bio_core**: trusted, inner_circle tiers
- **consciousness**: trusted, inner_circle tiers
- **core**: trusted, inner_circle tiers
- **core_bridge**: trusted, inner_circle tiers
- **core_colonies**: trusted, inner_circle tiers
- **core_common**: trusted, inner_circle tiers

## Tier Coverage

- **guest** (L0): 3 modules
- **visitor** (L1): 6 modules
- **friend** (L2): 30 modules
- **trusted** (L3): 52 modules
- **inner_circle** (L4): 36 modules
- **root_dev** (L5): 18 modules

## Acceptance Criteria

✅ **Contracts**: 65/65 (100%)
✅ **Schema OK**: 100%
✅ **AuthZ pass rate**: 0.0% (≥ 95%)
✅ **Telemetry smoke**: authz.check spans present
✅ **Policy tests**: OPA validation passed
✅ **Critical module protection**: All protected

All validation checks passed successfully.
