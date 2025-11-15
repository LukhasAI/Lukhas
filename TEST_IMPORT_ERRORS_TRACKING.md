# Test Import Errors Tracking

## Status: Phase 1 Complete

### Resolved ✅
1. **orchestration.health_monitor** - Fixed import order in test_routing_admin_auth.py
2. **consciousness.awareness.awareness_engine** - Created bridge module

### Remaining Import Errors

#### Unit Tests (1 error)
- [ ] `matriz.adapters` - Nested test directory structure issue

#### Integration Tests (18 errors)
- [ ] `orchestration.multi_ai_router.AIProvider` - Missing export
- [ ] `bio.core.architecture_analyzer.Architecture` - Missing export
- [ ] `aka_qualia.glyphs.GLYPH_KEYS` - Missing export
- [ ] `governance.guardian_serializer.GuardianEnvelopeSerializer` - Missing export
- [ ] `adapters.openai.api` - Module not found
- [ ] `async_manager` - Module not found
- [ ] `bio.energy.spirulina_atp_system` - Module not found
- [ ] `consciousness.consciousness_stream` - Module not found
- [ ] `consciousness.interfaces` - Module not found
- [ ] `core.collective.clusters.consciousness_clusters` - Module not found
- [ ] `core.collective.collective_ad_mind` - Module not found
- [ ] `governance.identity.auth_backend.authentication_server` - Module not found
- [ ] `labs.core.orchestration.async_orchestrator` - Module not found
- [ ] `lukhas.memory.fold_system` - Module not found
- [ ] `lz4` - Missing dependency (install required)
- [ ] `scripts.production_main` - Module not found
- [ ] `slowapi` - Missing dependency (install required)
- [ ] `urllib3.util` - Module not found

#### Contract Tests (1 error)
- [ ] `aka_qualia.core` - Module not found

### Next Steps

**Phase 2: Create Missing Bridge Modules**
1. Create bridges for consciousness modules
2. Create bridges for aka_qualia modules
3. Create bridges for bio modules
4. Create bridges for governance modules
5. Fix nested test directory structure in tests/unit/adapters

**Phase 3: Install Missing Dependencies**
1. Add `lz4` to requirements (optional compression)
2. Add `slowapi` to requirements (rate limiting)

**Phase 4: Fix Module Exports**
1. Export AIProvider from orchestration.multi_ai_router
2. Export Architecture from bio.core.architecture_analyzer
3. Export GLYPH_KEYS from aka_qualia.glyphs
4. Export GuardianEnvelopeSerializer from governance.guardian_serializer

## Test Statistics

- **Total test files**: 1,070
- **Tests successfully collected**: 85 (after Phase 1 fixes)
- **Remaining collection errors**: ~20 import errors
- **Target**: 100% test collection success

## Methodology

Following the lane-based architecture:
- Check if module exists in `candidate/` lane (experimental)
- Fall back to `labs/` lane (development)
- Fall back to `core/` lane (integration)
- Create production bridge in root namespace

All fixes maintain backward compatibility and follow LUKHAS import hierarchy.
