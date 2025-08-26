# ADR-0001: Code Maturity Lanes Architecture
Date: 2025-08-12
Status: Accepted

## Context
LUKHAS AI has 33,075 Python files requiring systematic organization and migration. Current structure has duplicate directories (20+ bio variants, 20+ memory variants), unclear module boundaries, and blocked test suite due to import path conflicts.

## Decision
Implement 4-lane code maturity system:
- **accepted/** - Production code (in PYTHONPATH, CI tested, versioned APIs)
- **candidate/** - Staging code (feature flags, nightly CI, compat shims)
- **quarantine/** - Legacy/unsafe code (import-disabled in CI, visible in index only)
- **archive/** - Historical code (excluded from install, with ADRs)

## Consequences
**Pros:**
- Clear progression path for code maturity
- No code deletion - everything is classified
- Compatibility shims prevent breaking changes
- Feature flags enable safe experimentation

**Cons:**
- Initial migration complexity
- Temporary duplication during transition
- Maintenance of compatibility shims

**Risks & mitigations:**
- Risk: Import path conflicts during migration
  - Mitigation: Auto-generated compatibility shims with deprecation dates
- Risk: Test suite disruption
  - Mitigation: Canary-first testing approach

## Alternatives Considered
- Big-bang refactor - Rejected: Too risky for 33k files
- Keep current structure - Rejected: Technical debt too high
- Delete duplicates immediately - Rejected: May lose important logic

## Migration Plan
1. Generate code index and import maps
2. Create compatibility shims for all moves
3. Move modules to appropriate lanes incrementally
4. Run canary tests per domain
5. Remove shims after SHIM_CULL_DATE (2025-11-01)

## Rollback Plan
1. Compatibility shims remain functional
2. Git history preserves original structure
3. Feature flags can disable candidate features
4. Quarantine prevents unsafe code execution
