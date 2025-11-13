# Known Limitation: Endocrine System Per-User State

**Status**: DOCUMENTED - Post-Launch Implementation
**Priority**: P2 OPTIONAL
**Estimated Effort**: 35 hours
**Tracking Issue**: TBD
**Last Updated**: 2025-11-10

## Summary

The LUKHAS Endocrine System is currently implemented as a **global singleton**, meaning all users share the same hormonal state. This prevents per-user hormone tracking and personalization but does not block MVP launch.

## Current State

**Implementation Quality**: ✅ EXCELLENT
- 8 hormone types with realistic baselines and decay rates
- 11 hormone interactions modeling biological relationships
- 4 trigger functions for stress, reward, bonding, and rest
- Async update loop with 1-second resolution
- Comprehensive effect calculations for system behavior modulation
- Neuroplasticity formula based on hormone balance

**Integration Status**: 65/100
- ✅ Core endocrine system fully implemented
- ✅ 8 hormone types with realistic interactions
- ✅ VIVOX-ERN integration captures user_id
- ⚠️ Endocrine system is global singleton (no per-user state)
- ❌ No production API endpoints for hormone data
- ❌ No tier-based access control for hormone operations
- ⚠️ user_id captured in history but not used for isolation

## Impact on MVP

**User Experience Impact**: LOW
- System-wide hormone modulation still provides bio-inspired adaptation
- Shared hormone state means collective system behavior (not per-user)
- Cannot provide personalized hormone-based recommendations
- Hormone analytics show aggregated data across all users

**Security Impact**: MEDIUM
- Hormone data is health-adjacent sensitive information
- No per-user isolation means potential cross-contamination
- Addressed by NOT exposing hormone data in production API yet

**Functional Impact**: LOW for MVP
- All hormone simulation functionality works
- System-wide stress/reward responses function correctly
- Bio-inspired modulation patterns operate normally
- Only missing: per-user personalization and tracking

## Comprehensive Documentation

A **complete audit** of the endocrine system was conducted on 2025-11-10:

📄 **[Endocrine System Audit](../audits/systems/ENDOCRINE_SYSTEM_AUDIT_2025-11-10.md)** (624 lines)

This audit provides:
- Detailed analysis of current implementation
- Complete gap analysis with specific line references
- 4-phase implementation roadmap with time estimates
- Security and privacy considerations
- Testing requirements and migration path
- Code examples and recommendations

## Post-Launch Implementation Plan

### Phase 1: Per-User Hormone State (8 hours) 🔥 REQUIRED
**Priority**: HIGH - Foundation for user isolation

1. **Refactor to per-user singleton** (4 hours)
   - Change `get_endocrine_system(user_id: str)` signature
   - Add user_id to EndocrineSystem.__init__()
   - Store per-user systems in dict
   - Add LRU cache for inactive user systems (memory management)

2. **Update VIVOX integration** (2 hours)
   - Make user_id required (not optional)
   - Pass user_id to `get_endocrine_system(user_id)`
   - Validate user_id before hormone processing

3. **Add user_id to trigger functions** (2 hours)
   ```python
   async def trigger_stress(user_id: str, intensity: float = 0.5):
       system = get_endocrine_system(user_id)
       system.trigger_stress_response(intensity)
   ```

### Phase 2: Production API Endpoints (14 hours) 🚀
**Priority**: HIGH - Enable access to hormone data

1. **Create `serve/endocrine_api.py`** (8 hours)
   - GET `/v1/endocrine/hormones/{user_id}` - Hormone levels
   - GET `/v1/endocrine/profile/{user_id}` - Full profile with summary
   - GET `/v1/endocrine/effects/{user_id}` - Active behavioral effects
   - GET `/v1/endocrine/analytics/{user_id}` - VIVOX analytics
   - POST `/v1/endocrine/trigger` - Manual hormone triggers (admin only)
   - GET `/v1/endocrine/neuroplasticity/{user_id}` - Learning capacity score

2. **Apply tier-based access control** (4 hours)
   - Tier 2+ required for hormone endpoints
   - Validate user can only access own data (or is admin)
   - Admin tier can access all users' hormone data
   - Rate limiting per user (10 req/min)

3. **Add authentication middleware integration** (2 hours)
   - Extract user_id from request.state (set by StrictAuthMiddleware)
   - Return 401 if no valid user_id
   - Log all hormone data access for audit

### Phase 3: System Integrations (14 hours) 🔗
**Priority**: MEDIUM - Connect to other systems

1. **Dream System Integration** (6 hours)
   - Register receptor in dream engine
   - High melatonin + GABA → increase dream frequency
   - High cortisol → increase nightmare probability
   - Dopamine + Endorphin → increase lucid dream chance

2. **Consciousness System Integration** (4 hours)
   - Register receptor in consciousness engine
   - High stress → reduce awareness depth (defensive mode)
   - High neuroplasticity → increase learning receptivity

3. **Memory System Integration** (4 hours)
   - Register receptor in memory consolidation
   - High cortisol → prioritize threat-related memories
   - High neuroplasticity → enhance memory formation

### Phase 4: Monitoring & Analytics (10 hours) 📊
**Priority**: LOW - Observability

1. **Hormone Dashboard** (6 hours)
   - Real-time hormone level visualization
   - Historical trends (7-day, 30-day)
   - Hormone interaction graph

2. **Alerting** (2 hours)
   - Alert on sustained high cortisol (>0.8 for 30+ min)
   - Alert on low neuroplasticity (<0.3 for 60+ min)

3. **Analytics Integration** (2 hours)
   - Export hormone data to analytics pipeline
   - Correlation analysis (hormones ↔ user outcomes)

## Testing Requirements

### Unit Tests (Phase 1)
- [ ] Test per-user hormone isolation
- [ ] Test user_id validation in VIVOX integration
- [ ] Test hormone analytics with user_id filtering
- [ ] Test LRU cache for inactive user systems

### Integration Tests (Phase 2)
- [ ] Test endocrine API endpoints with authentication
- [ ] Test tier-based access control on hormone data
- [ ] Test cross-user data isolation
- [ ] Test audit logging for hormone data access

### Performance Tests (Phase 3)
- [ ] Test 1000 concurrent users with separate hormone states
- [ ] Test hormone update loop performance (1-second resolution)
- [ ] Test analytics query performance on 10K+ hormone records

## Security Considerations

**Hormone Data Classification**: Sensitive Health-Adjacent Data

**Protection Requirements**:
- ✅ Store only aggregated/anonymized data long-term
- 🔄 **TODO**: User consent for hormone tracking
- 🔄 **TODO**: Data export/deletion (GDPR integration)
- 🔄 **TODO**: Encryption at rest for hormone histories

**Access Control by Tier**:
- **Tier 1 (Public)**: No access to hormone data
- **Tier 2 (Authenticated)**: Access to own hormone levels (current snapshot)
- **Tier 3 (Power User)**: Access to own hormone profile + 7-day history
- **Tier 4 (Pro)**: Access to own hormone analytics + 30-day history
- **Tier 5 (Enterprise)**: API access + custom analytics
- **Tier 6 (Admin/System)**: Access to all users' hormone data

## Migration Strategy

**Breaking Changes**:
- `get_endocrine_system()` → `get_endocrine_system(user_id)`
- All trigger functions need user_id parameter
- Module receptors need to handle per-user state

**Migration Timeline**:
1. Add deprecation warnings to old functions (2 weeks notice)
2. Update all internal callers
3. Update VIVOX integration
4. Update monitoring/modulation systems
5. Remove deprecated functions after migration complete

## References

- **Primary Documentation**: [Endocrine System Audit](../audits/systems/ENDOCRINE_SYSTEM_AUDIT_2025-11-10.md)
- **Core Implementation**: [core/endocrine/hormone_system.py](../../core/endocrine/hormone_system.py) (540 lines)
- **VIVOX Integration**: [vivox/emotional_regulation/endocrine_integration.py](../../vivox/emotional_regulation/endocrine_integration.py) (644 lines)
- **Bio Implementation**: [qi/bio/endocrine_system.py](../../qi/bio/endocrine_system.py) (180 lines)
- **Tests**: [tests/core/endocrine/test_hormone_system.py](../../tests/core/endocrine/test_hormone_system.py)

## Decision Log

**Date**: 2025-11-10
**Decision**: Document as known limitation for MVP
**Rationale**:
- Comprehensive audit completed documenting all requirements
- System is well-implemented, only needs user isolation refactor
- Non-blocking for MVP launch
- Can be implemented post-launch in 4-week sprint
- Security addressed by not exposing hormone API endpoints yet

**Approved by**: GPT-5 Security Audit Action Plan (Task 4.1 - P2 OPTIONAL)

---

**Next Action**: Create tracking issue for post-launch implementation when prioritizing Phase 2 features
