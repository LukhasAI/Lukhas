# Ranked Action Queue

| Rank | Score | Category | File | Fix | Sources |
|---:|---:|---|---|---|---|
| 1 | 1.5 | Identity/Web | serve/main.py | Later - Expand health check to cover database connections or critical subsystems (memory, awareness) status | strategic |
| 2 | 1.25 | MATRIZ Readiness | audit/TIER1.txt | Now - Flesh out contract details (inputs/outputs) and link golden trace tests to actual module behaviors for full coverage | strategic |
| 3 | 1.25 | Import Cycles | candidate/governance/identity/constellation_glyph_integration.py | Later - Refactor IdentitySystem init to break import loop | neutral |
| 4 | 1.25 | Governance vs Code | docs/architecture/LUKHAS_ARCHITECTURE_MASTER.json | Now - Update LUKHAS_ARCHITECTURE_MASTER.json to include the API module listed in Tier-1 docs | strategic |
| 5 | 1.25 | Cross-Lane Imports | lukhas/bridge/llm_wrappers/anthropic_wrapper.py | Now - Remove quarantine layer and refactor cross-lane dependencies | neutral |
| 6 | 1.25 | Cross-Lane Imports | lukhas/core/swarm.py | Now - Remove quarantine layer and refactor cross-lane dependencies | neutral |
| 7 | 1.25 | Syntax Errors | memory/fold_lineage_tracker.py | Now - Define or remove undefined logger references | neutral |
| 8 | 1.25 | Lane Integrity | quarantine/cross_lane/__init__.py | Now - Remove or refactor the quarantine layer. Provide official interfaces in lukhas for any needed functionality from candidate | strategic |
| 9 | 1.25 | MATRIZ Readiness | reports/audit/appendix_delta.md | Later - Implement endpoints to serve these trace JSONs and add tests verifying that each golden trace can be retrieved and matches expected outcomes | strategic |
| 10 | 1.25 | Lane Integrity | reports/audit/appendix_delta.md | Later - Monitor that no new cross-lane imports are introduced (keep CI guard). Plan removal of quarantine/ | strategic |
| 11 | 1.25 | Security Supply Chain | reports/audit/appendix_delta.md | Now - Add the SBOM reference into SECURITY_ARCHITECTURE.json and consider signing build artifacts | strategic |
| 12 | 1.25 | Security Supply Chain | scripts/audit.sh | Later - Add security scan result validation and failure handling | strategic |

> Score = severity(3/2/1) + 0.25×citations − effort(now:-2,later:-1)
