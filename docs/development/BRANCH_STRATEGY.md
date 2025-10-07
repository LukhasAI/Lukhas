---
status: wip
type: documentation
owner: unknown
module: development
redirect: false
moved_to: null
---

# Branch Consolidation & Promotion Strategy

## Current State (Post-Migration)

After recovering from the bulk migration incident, we have:
- **lukhas/** - Accepted lane with interfaces-only nucleus (importable, production-ready)
- **candidate/** - Staging lane with 2,171+ files awaiting validation
- **archive/** - Historical code and failed experiments

## Branch Strategy

### 1. Promotion Workflow
```
candidate/ → promote/[capability] → main → origin/main
```

Each promotion follows these steps:
1. Create `promote/[capability]` branch
2. Copy implementation from `candidate/` to `lukhas/`
3. Add feature flag (e.g., `CONSENT_LEDGER_ACTIVE`)
4. Create wrapper with dry_run default
5. Add MATRIZ instrumentation
6. Write integration tests
7. Run acceptance gate
8. Merge to main
9. Push to origin when stable

### 2. Branch Naming Convention
- `promote/[capability]` - Capability promotions from candidate to accepted
- `feature/[name]` - New features developed in candidate/
- `fix/[issue]` - Bug fixes
- `docs/[topic]` - Documentation updates
- `experimental/[name]` - High-risk experiments (not for production)

### 3. Completed Promotions
✅ **Consent Ledger** (4dd81575)
- Feature flag: `CONSENT_LEDGER_ACTIVE`
- Location: `lukhas/governance/consent_ledger.py`
- Tests: `tests/test_consent_ledger_integration.py`

✅ **WebAuthn** (343f6a9f)
- Feature flag: `WEBAUTHN_ACTIVE`
- Location: `lukhas/identity/lambda_id.py` + `webauthn.py`
- Tests: `tests/test_webauthn_integration.py`

### 4. Promotion Queue (Priority Order)

#### High Priority (Core Infrastructure)
1. **Context Bus** - Internal messaging and orchestration
   - Source: `candidate/orchestration/symbolic_kernel_bus.py`
   - Dependencies: None (standalone)

2. **MATRIZ Core** - Observability foundation
   - Source: `candidate/MATRIZ/`
   - Partially promoted (decorators in lukhas/observability)

3. **Guardian System** - Safety and drift detection
   - Source: `candidate/governance/guardian/`
   - Critical for safe operation

#### Medium Priority (Core Capabilities)
4. **Memory System** - Fold-based memory with cascade prevention
   - Source: `candidate/memory/`
   - Depends on: MATRIZ

5. **Actor System** - Message passing and concurrency
   - Source: `candidate/core/actor/`
   - Depends on: Context Bus

6. **Consciousness Core** - Awareness and decision systems
   - Source: `candidate/consciousness/`
   - Depends on: Memory, Actor

#### Low Priority (Enhanced Features)
7. **Emotion Module** - VAD affect processing
8. **Bio-Inspired** - Adaptation algorithms
9. **Quantum-Inspired** - QI processing
10. **Dream Engine** - Creative synthesis

### 5. Acceptance Criteria
Each promotion must:
- ✅ No imports from candidate/, quarantine/, or archive/
- ✅ Has MODULE_MANIFEST.json with capabilities
- ✅ Feature flag for gradual rollout
- ✅ Dry-run mode by default
- ✅ MATRIZ instrumentation on key methods
- ✅ Integration tests pass
- ✅ Acceptance gate validates

### 6. Feature Flags
All promoted capabilities use environment variables:
```bash
# Enable specific features
export CONSENT_LEDGER_ACTIVE=true
export WEBAUTHN_ACTIVE=true
export CONTEXT_BUS_ACTIVE=true  # Future
export GUARDIAN_ACTIVE=true      # Future
```

### 7. Testing Strategy
```bash
# Run tests for promoted features
pytest tests/test_*_integration.py

# Run with feature flags
CONSENT_LEDGER_ACTIVE=true pytest tests/test_consent_ledger_integration.py

# Acceptance gate for new promotions
python tools/acceptance_gate.py lukhas/[module]
```

### 8. Rollback Plan
If a promotion causes issues:
1. Disable feature flag immediately
2. Revert commit if necessary
3. Move code back to candidate/
4. Fix issues and re-attempt promotion

### 9. Long-term Goal
Gradually promote all validated capabilities from candidate/ to lukhas/:
- **Phase 1**: Core infrastructure (Context Bus, MATRIZ, Guardian)
- **Phase 2**: Identity & Auth (WebAuthn ✅, OAuth pending)
- **Phase 3**: Consciousness systems (Memory, Awareness, Decision)
- **Phase 4**: Advanced features (Emotion, Bio, QI, Dreams)

### 10. Branch Cleanup
Regularly delete merged branches:
```bash
# After successful merge
git branch -d promote/[capability]

# Check for stale branches
git branch --merged main | grep -v main
```

## Next Steps
1. Promote Context Bus (high priority)
2. Complete MATRIZ promotion
3. Set up Guardian System with drift detection
4. Document each promotion in PROMOTION_LOG.md
