---
status: wip
type: documentation
---
# Matrix Identity Coverage Report
Generated 65 Matrix contracts with full identity integration.

## Summary Statistics
- **Total Contracts**: 65
- **Schema Version**: 1.0.0
- **Tokenization**: Solana (disabled by default)
- **WebAuthn Required**: 36/65 modules

## Tier Distribution
- **guest** (L0): 3 modules
- **visitor** (L1): 6 modules
- **friend** (L2): 30 modules
- **trusted** (L3): 52 modules
- **inner_circle** (L4): 36 modules
- **root_dev** (L5): 18 modules

## Module Identity Matrix
| Module | Required Tiers | Scopes | WebAuthn | Contract File |
|--------|---------------|---------|----------|---------------|
| accepted | guest, visitor | 4 | ❌ | contracts/matrix_accepted.json |
| accepted.bio | guest, visitor | 4 | ❌ | contracts/matrix_accepted_bio.json |
| agents | visitor, friend, trusted | 4 | ❌ | contracts/matrix_agents.json |
| api | visitor, friend, trusted | 4 | ❌ | contracts/matrix_api.json |
| bio | friend, trusted | 4 | ❌ | contracts/matrix_bio.json |
| bio.core | trusted, inner_circle | 4 | ✅ | contracts/matrix_bio_core.json |
| branding | guest, visitor | 4 | ❌ | contracts/matrix_branding.json |
| bridge | friend, trusted | 4 | ❌ | contracts/matrix_bridge.json |
| bridge.llm_wrappers | friend, trusted | 4 | ❌ | contracts/matrix_bridge_llm_wrappers.json |
| consciousness | friend, trusted, inner_circle | 4 | ✅ | contracts/matrix_consciousness.json |
| constellation | friend, trusted | 4 | ❌ | contracts/matrix_constellation.json |
| constellation.triad | friend, trusted | 4 | ❌ | contracts/matrix_constellation_triad.json |
| core | trusted, inner_circle | 4 | ✅ | contracts/matrix_core.json |
| core.bridge | trusted, inner_circle | 4 | ✅ | contracts/matrix_core_bridge.json |
| core.colonies | trusted, inner_circle | 4 | ✅ | contracts/matrix_core_colonies.json |
| core.common | trusted, inner_circle | 4 | ✅ | contracts/matrix_core_common.json |
| core.filesystem | trusted, inner_circle | 4 | ✅ | contracts/matrix_core_filesystem.json |
| core.matriz | trusted, inner_circle | 4 | ✅ | contracts/matrix_core_matriz.json |
| core.policy | trusted, inner_circle | 4 | ✅ | contracts/matrix_core_policy.json |
| core.registry | trusted, inner_circle | 4 | ✅ | contracts/matrix_core_registry.json |
| core.reliability | trusted, inner_circle | 4 | ✅ | contracts/matrix_core_reliability.json |
| core.symbolic | trusted, inner_circle | 4 | ✅ | contracts/matrix_core_symbolic.json |
| core.symbolic.constraints | trusted, inner_circle | 4 | ✅ | contracts/matrix_core_symbolic_constraints.json |
| core.symbolism | trusted, inner_circle | 4 | ✅ | contracts/matrix_core_symbolism.json |
| deployment | trusted, inner_circle | 4 | ✅ | contracts/matrix_deployment.json |
| emotion | friend, trusted | 4 | ❌ | contracts/matrix_emotion.json |
| governance | inner_circle, root_dev | 4 | ✅ | contracts/matrix_governance.json |
| governance.consent_ledger | inner_circle, root_dev | 4 | ✅ | contracts/matrix_governance_consent_ledger.json |
| governance.consent_ledger.providers | inner_circle, root_dev | 4 | ✅ | contracts/matrix_governance_consent_ledger_providers.json |
| governance.ethics | inner_circle, root_dev | 4 | ✅ | contracts/matrix_governance_ethics.json |
| governance.guardian | inner_circle, root_dev | 4 | ✅ | contracts/matrix_governance_guardian.json |
| governance.identity | inner_circle, root_dev | 4 | ✅ | contracts/matrix_governance_identity.json |
| governance.identity.auth_backend | inner_circle, root_dev | 4 | ✅ | contracts/matrix_governance_identity_auth_backend.json |
| governance.security | inner_circle, root_dev | 4 | ✅ | contracts/matrix_governance_security.json |
| identity | trusted, inner_circle, root_dev | 4 | ✅ | contracts/matrix_identity.json |
| identity.auth | trusted, inner_circle, root_dev | 4 | ✅ | contracts/matrix_identity_auth.json |
| identity.facades | trusted, inner_circle, root_dev | 4 | ✅ | contracts/matrix_identity_facades.json |
| identity.oidc | trusted, inner_circle, root_dev | 4 | ✅ | contracts/matrix_identity_oidc.json |
| identity.passkey | trusted, inner_circle, root_dev | 4 | ✅ | contracts/matrix_identity_passkey.json |
| identity.passkey.providers | trusted, inner_circle, root_dev | 4 | ✅ | contracts/matrix_identity_passkey_providers.json |
| identity.qrg | trusted, inner_circle, root_dev | 4 | ✅ | contracts/matrix_identity_qrg.json |
| identity.services | trusted, inner_circle, root_dev | 4 | ✅ | contracts/matrix_identity_services.json |
| identity.wallet | trusted, inner_circle, root_dev | 4 | ✅ | contracts/matrix_identity_wallet.json |
| ledger | friend, trusted | 4 | ❌ | contracts/matrix_ledger.json |
| matriz | friend, trusted | 4 | ❌ | contracts/matrix_matriz.json |
| matriz.runtime | friend, trusted | 4 | ❌ | contracts/matrix_matriz_runtime.json |
| memory | friend, trusted, inner_circle | 4 | ✅ | contracts/matrix_memory.json |
| memory.backends | friend, trusted, inner_circle | 4 | ✅ | contracts/matrix_memory_backends.json |
| memory.emotional | friend, trusted, inner_circle | 4 | ✅ | contracts/matrix_memory_emotional.json |
| observability | friend, trusted | 4 | ❌ | contracts/matrix_observability.json |
| orchestration | friend, trusted | 4 | ❌ | contracts/matrix_orchestration.json |
| orchestration.context | friend, trusted | 4 | ❌ | contracts/matrix_orchestration_context.json |
| orchestration.providers | friend, trusted | 4 | ❌ | contracts/matrix_orchestration_providers.json |
| qi | friend, trusted | 4 | ❌ | contracts/matrix_qi.json |
| rl | friend, trusted | 4 | ❌ | contracts/matrix_rl.json |
| rl.coordination | friend, trusted | 4 | ❌ | contracts/matrix_rl_coordination.json |
| rl.engine | friend, trusted | 4 | ❌ | contracts/matrix_rl_engine.json |
| rl.environments | friend, trusted | 4 | ❌ | contracts/matrix_rl_environments.json |
| rl.experience | friend, trusted | 4 | ❌ | contracts/matrix_rl_experience.json |
| root | friend, trusted | 4 | ❌ | contracts/matrix_root.json |
| security | inner_circle, root_dev | 4 | ✅ | contracts/matrix_security.json |
| tools | visitor, friend | 4 | ❌ | contracts/matrix_tools.json |
| trace | friend, trusted | 4 | ❌ | contracts/matrix_trace.json |
| trinity | friend, trusted | 4 | ❌ | contracts/matrix_trinity.json |
| vivox | friend, trusted | 4 | ❌ | contracts/matrix_vivox.json |

## Critical Modules (WebAuthn Required)
- **bio.core**: trusted, inner_circle
- **consciousness**: friend, trusted, inner_circle
- **core**: trusted, inner_circle
- **core.bridge**: trusted, inner_circle
- **core.colonies**: trusted, inner_circle
- **core.common**: trusted, inner_circle
- **core.filesystem**: trusted, inner_circle
- **core.matriz**: trusted, inner_circle
- **core.policy**: trusted, inner_circle
- **core.registry**: trusted, inner_circle
- **core.reliability**: trusted, inner_circle
- **core.symbolic**: trusted, inner_circle
- **core.symbolic.constraints**: trusted, inner_circle
- **core.symbolism**: trusted, inner_circle
- **deployment**: trusted, inner_circle
- **governance**: inner_circle, root_dev
- **governance.consent_ledger**: inner_circle, root_dev
- **governance.consent_ledger.providers**: inner_circle, root_dev
- **governance.ethics**: inner_circle, root_dev
- **governance.guardian**: inner_circle, root_dev
- **governance.identity**: inner_circle, root_dev
- **governance.identity.auth_backend**: inner_circle, root_dev
- **governance.security**: inner_circle, root_dev
- **identity**: trusted, inner_circle, root_dev
- **identity.auth**: trusted, inner_circle, root_dev
- **identity.facades**: trusted, inner_circle, root_dev
- **identity.oidc**: trusted, inner_circle, root_dev
- **identity.passkey**: trusted, inner_circle, root_dev
- **identity.passkey.providers**: trusted, inner_circle, root_dev
- **identity.qrg**: trusted, inner_circle, root_dev
- **identity.services**: trusted, inner_circle, root_dev
- **identity.wallet**: trusted, inner_circle, root_dev
- **memory**: friend, trusted, inner_circle
- **memory.backends**: friend, trusted, inner_circle
- **memory.emotional**: friend, trusted, inner_circle
- **security**: inner_circle, root_dev

## Schema Validation
All contracts validated against `matrix.schema.template.json`:
- ✅ Required fields: schema_version, module, owner, gates
- ✅ Identity block: requires_auth, tiers, scopes, webauthn
- ✅ Tokenization: Solana placeholder (disabled)
- ✅ Telemetry: OpenTelemetry spans and metrics
