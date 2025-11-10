# Endocrine System Audit - November 10, 2025

## Executive Summary

**Audit Date**: 2025-11-10
**Audit Scope**: Bio-inspired hormonal signaling system integration and user_id linkage
**System**: LUKHAS Endocrine System + VIVOX Emotional Regulation Network (ERN)
**Auditor**: Claude Code (Autonomous Agent)

### Key Findings

**🟡 MEDIUM PRIORITY**: Endocrine system well-implemented but **not wired to production API**.

**Integration Status**: **65/100**

**Breakdown**:
- ✅ Core endocrine system fully implemented (100%)
- ✅ 8 hormone types with realistic interactions (100%)
- ✅ VIVOX-ERN integration captures user_id (100%)
- ⚠️  Endocrine system is global singleton (no per-user state) (50%)
- ❌ No production API endpoints for hormone data (0%)
- ❌ No tier-based access control for hormone operations (0%)
- ⚠️  User_id captured in history but not used for isolation (50%)
- ✅ Comprehensive hormone analytics available (80%)

---

## 1. System Overview

### What is the Endocrine System?

The LUKHAS Endocrine System simulates biological hormonal signaling for system-wide behavioral modulation. It provides bio-inspired adaptation patterns that influence:

- **Stress Response**: Cortisol + Adrenaline
- **Reward & Motivation**: Dopamine + Endorphin
- **Mood Stability**: Serotonin
- **Social Bonding**: Oxytocin
- **Rest Cycles**: Melatonin + GABA
- **Neuroplasticity**: Dynamic calculation based on hormone balance

**Architecture**:
```
┌─────────────────────────────────────────┐
│    LUKHAS Endocrine System              │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │  8 Hormone Types                 │   │
│  │  - Cortisol, Dopamine, Serotonin │   │
│  │  - Oxytocin, Adrenaline, GABA    │   │
│  │  - Melatonin, Endorphin          │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │  Hormone Interactions            │   │
│  │  11 bidirectional interactions   │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │  Receptor Registration           │   │
│  │  Modules can subscribe           │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
                    │
                    │ Integration
                    ▼
┌─────────────────────────────────────────┐
│    VIVOX-ERN Endocrine Integration      │
│                                          │
│  - Maps emotional states → hormones     │
│  - 7 emotional patterns                 │
│  - 8 regulation strategies              │
│  - user_id in hormone release history   │
└─────────────────────────────────────────┘
```

---

## 2. Core Implementation Analysis

### 2.1 Hormone System ✅ EXCELLENT

**File**: [core/endocrine/hormone_system.py](../../../core/endocrine/hormone_system.py) (540 lines)

**Strengths**:
- **8 hormone types** with realistic baselines and decay rates (lines 84-140)
- **11 hormone interactions** modeling biological relationships (lines 141-162)
- **4 trigger functions**: stress, reward, social bonding, rest cycle (lines 226-309)
- **Async update loop** with 1-second resolution (lines 181-211)
- **Effect calculation** maps hormones to system behaviors (lines 320-359)
- **Neuroplasticity formula** based on hormone balance (lines 361-380)
- **Receptor pattern** for module subscriptions (lines 387-392, 421-426)
- **Global singleton** with `get_endocrine_system()` (lines 502-511)

**Code Example** (Stress Response):
```python
def trigger_stress_response(self, intensity: float = 0.5):
    """Trigger a stress response"""
    # Boost stress hormones
    self._boost_hormone(HormoneType.CORTISOL, intensity * 0.4)
    self._boost_hormone(HormoneType.ADRENALINE, intensity * 0.3)

    # Log the trigger
    self.effect_history.append({
        "type": "stress_response",
        "intensity": intensity,
        "timestamp": datetime.now(timezone.utc),
        "hormones_affected": ["cortisol", "adrenaline"],
    })
```

**Missing**:
- ❌ No `user_id` parameter in trigger functions
- ❌ Global singleton = single hormone state for entire system
- ❌ No per-user hormone profiles
- ❌ Effect history not keyed by user_id

---

### 2.2 VIVOX-ERN Integration ✅ GOOD (with gaps)

**File**: [vivox/emotional_regulation/endocrine_integration.py](../../../vivox/emotional_regulation/endocrine_integration.py) (644 lines)

**Strengths**:
- **7 emotional → hormone mappings**: high_stress, joy_happiness, anxiety_fear, sadness_depression, anger_frustration, calm_relaxed, excitement_anticipation (lines 118-191)
- **8 regulation strategy → hormone mappings**: breathing, cognitive, dampening, amplification, stabilization, acceptance, distraction, redirection (lines 193-237)
- **Contextual modulation**: Time of day, environment, stress level (lines 376-415)
- **Hormone feedback mechanisms**: Prevents over-release (lines 417-449)
- **🎯 user_id captured in hormone release history** (line 513):
  ```python
  record = {
      "timestamp": datetime.now(timezone.utc).isoformat(),
      "user_id": context.get("user_id", "unknown"),  # ✅ CAPTURED!
      "regulation_strategy": regulation_response.strategy_used.value,
      "regulation_effectiveness": regulation_response.effectiveness,
      "emotional_state": regulation_response.original_state.to_dict(),
      "hormone_triggers": triggers,
      "context": context,
  }
  ```
- **User analytics available**: `get_hormone_analytics(user_id, hours)` (lines 555-631)

**Issues**:
- ⚠️  user_id is `context.get("user_id", "unknown")` - defaults to "unknown"
- ⚠️  Analytics filter by user_id but don't validate it's present
- ❌ No tier-based access control for hormone analytics
- ❌ Hormone system itself doesn't support per-user isolation

---

## 3. Critical Gaps

### 3.1 No Per-User Hormone State ⚠️ MEDIUM

**Issue**: Endocrine system is a **global singleton**

**File**: [core/endocrine/hormone_system.py:502-511](../../../core/endocrine/hormone_system.py#L502-L511)

```python
# Global endocrine system instance
_endocrine_system: Optional[EndocrineSystem] = None

def get_endocrine_system() -> EndocrineSystem:
    """Get the global endocrine system instance"""
    global _endocrine_system
    if _endocrine_system is None:
        _endocrine_system = EndocrineSystem()
    return _endocrine_system
```

**Impact**:
- All users share same hormone levels
- User A's stress triggers affect User B's system state
- Cannot model individual hormone profiles
- Hormone-based personalization impossible

**Recommendation**:
```python
# Per-user endocrine systems
_user_endocrine_systems: dict[str, EndocrineSystem] = {}

def get_endocrine_system(user_id: str) -> EndocrineSystem:
    """Get user-specific endocrine system instance"""
    if user_id not in _user_endocrine_systems:
        _user_endocrine_systems[user_id] = EndocrineSystem(user_id=user_id)
    return _user_endocrine_systems[user_id]
```

---

### 3.2 No Production API Endpoints ❌ HIGH

**Issue**: Endocrine system has **NO REST API** in production

**Search Results**: No endocrine endpoints found in:
- `serve/routes.py` ❌
- `serve/main.py` ❌
- `lukhas/api/` ❌
- `lukhas_website/lukhas/api/` ❌

**Available Functions** (not exposed):
- `get_hormone_levels()` - Current hormone snapshot
- `get_active_effects()` - System behavioral effects
- `get_hormone_profile()` - Comprehensive profile with summary
- `trigger_stress_response()`, `trigger_reward_response()`, etc.
- `get_hormone_analytics(user_id, hours)` (VIVOX-ERN)

**Missing API Routes**:
```python
# Needed endpoints:
GET  /v1/endocrine/hormones/{user_id}     # Get hormone levels
GET  /v1/endocrine/profile/{user_id}      # Get hormone profile
GET  /v1/endocrine/effects/{user_id}      # Get active effects
GET  /v1/endocrine/analytics/{user_id}    # Get analytics (VIVOX)
POST /v1/endocrine/trigger                # Trigger hormone response
GET  /v1/endocrine/neuroplasticity/{user_id}  # Get neuroplasticity score
```

**Recommendation**: Create `serve/endocrine_api.py` with tier-gated endpoints

---

### 3.3 No Tier-Based Access Control ❌ MEDIUM

**Issue**: No access controls on hormone data

**Concerns**:
- Hormone data is sensitive health-adjacent information
- No validation that user can access their own data
- No prevention of cross-user hormone data access
- No tier requirements for hormone analytics

**Recommendation**:
```python
from lukhas_website.lukhas.identity.tier_system import lukhas_tier_required, TierLevel

@router.get("/hormones/{user_id}")
@lukhas_tier_required(TierLevel.AUTHENTICATED, PermissionScope.HEALTH_DATA)
async def get_hormone_levels(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    # Validate user can access this data
    if current_user["user_id"] != user_id and current_user["tier"] < TierLevel.ADMIN:
        raise HTTPException(403, "Cannot access other user's hormone data")

    system = get_endocrine_system(user_id)
    return system.get_hormone_levels()
```

---

### 3.4 Optional user_id in VIVOX Integration ⚠️ MEDIUM

**Issue**: user_id defaults to "unknown"

**File**: [vivox/emotional_regulation/endocrine_integration.py:513](../../../vivox/emotional_regulation/endocrine_integration.py#L513)

```python
"user_id": context.get("user_id", "unknown"),  # ⚠️ Defaults to "unknown"
```

**Impact**:
- Analytics may include data with user_id="unknown"
- Cannot distinguish between missing user_id and actual user
- `get_hormone_analytics(user_id, hours)` at line 555 would return data for "unknown" if passed

**Recommendation**:
```python
user_id = context.get("user_id")
if not user_id:
    raise ValueError("user_id is required for hormone processing")

record = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "user_id": user_id,  # ✅ Required
    # ...
}
```

---

## 4. System Capabilities

### 4.1 Hormone Types & Baselines

| Hormone | Baseline | Primary Effect | Production Rate | Decay Rate |
|---------|----------|----------------|-----------------|------------|
| **Cortisol** | 0.3 | Stress response | 0.2 | 0.08 |
| **Dopamine** | 0.5 | Reward/motivation | 0.15 | 0.1 |
| **Serotonin** | 0.6 | Mood stability | 0.1 | 0.05 |
| **Oxytocin** | 0.4 | Social bonding | 0.12 | 0.06 |
| **Adrenaline** | 0.2 | Fight/flight | 0.3 | 0.15 |
| **Melatonin** | 0.3 | Rest cycles | 0.05 | 0.03 |
| **GABA** | 0.5 | Calming | 0.08 | 0.04 |
| **Endorphin** | 0.3 | Pain relief/pleasure | 0.1 | 0.07 |

### 4.2 Hormone Interactions (11 total)

Examples:
- **Cortisol → Serotonin** (-0.3): Stress suppresses mood
- **Cortisol → Dopamine** (-0.2): Stress reduces motivation
- **Adrenaline → Cortisol** (+0.4): Fight/flight boosts stress
- **Oxytocin → Cortisol** (-0.25): Bonding reduces stress
- **GABA → Cortisol** (-0.2): Calming reduces stress
- **Endorphin → Dopamine** (+0.3): Pleasure boosts motivation

### 4.3 Calculated Effects

**Behavioral Modulation** (from `_calculate_effects()`):
- `stress_level` = cortisol * 0.7 + adrenaline * 0.3
- `mood_valence` = dopamine * 0.4 + serotonin * 0.4 + endorphin * 0.2
- `motivation` = dopamine level
- `emotional_stability` = serotonin level
- `social_engagement` = oxytocin level
- `trust_level` = oxytocin * 0.8
- `empathy` = oxytocin * serotonin
- `processing_speed` = 1.0 - (melatonin * 0.3 + gaba * 0.2)
- `neuroplasticity` = stress_factor * 0.4 + mood_factor * 0.4 + rest_factor * 0.2

### 4.4 VIVOX Emotional Patterns

7 patterns mapped to hormone responses:
1. **high_stress**: Cortisol (0.8) + Adrenaline (0.6) + GABA reduction
2. **joy_happiness**: Dopamine (0.7) + Serotonin (0.5) + Endorphin (0.4)
3. **anxiety_fear**: Cortisol (0.7) + Adrenaline (0.8) + Serotonin/GABA reduction
4. **sadness_depression**: Serotonin reduction (-0.4) + Dopamine reduction (-0.3)
5. **anger_frustration**: Adrenaline (0.9) + Cortisol (0.6) + GABA/Serotonin reduction
6. **calm_relaxed**: GABA (0.6) + Serotonin (0.4) + Cortisol reduction
7. **excitement_anticipation**: Dopamine (0.8) + Adrenaline (0.5) + Endorphin (0.3)

---

## 5. Integration Points

### 5.1 Current Integrations

**Found**:
- ✅ `vivox/emotional_regulation/` - VIVOX-ERN integration (644 lines)
- ✅ `modulation/` - LLM response modulation (3 files)
- ✅ `products/intelligence/monitoring_candidate/` - Monitoring dashboards (9 files)
- ✅ `examples/endocrine_demo.py` - Demo script
- ✅ `tests/core/endocrine/test_hormone_system.py` - Unit tests

**Not Found** (expected but missing):
- ❌ Production API routes
- ❌ lukhas/ production integration
- ❌ Dream system integration
- ❌ Consciousness system integration
- ❌ Memory system modulation

### 5.2 Receptor Pattern

**File**: [core/endocrine/hormone_system.py:421-426](../../../core/endocrine/hormone_system.py#L421-L426)

```python
def register_receptor(self, module_name: str, receptor: Callable):
    """Register a hormone receptor for a module"""
    if module_name not in self.receptors:
        self.receptors[module_name] = []
    self.receptors[module_name].append(receptor)
    logger.info(f"Registered hormone receptor for {module_name}")
```

**Usage**: Modules can subscribe to hormone changes:
```python
system = get_endocrine_system()

async def my_module_receptor(effects: dict[str, Any]):
    """React to hormone effects"""
    if effects["stress_level"] > 0.7:
        # Trigger stress adaptation
        pass

system.register_receptor("my_module", my_module_receptor)
```

**Missing Receptors**:
- Dream system (should modulate dream intensity/type)
- Consciousness processing (should affect awareness depth)
- Memory consolidation (should influence memory formation)
- Learning rate (neuroplasticity feedback)

---

## 6. Recommendations

### Phase 1: Per-User Hormone State (Week 1) 🔥

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

### Phase 2: Production API Endpoints (Week 2) 🚀

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

### Phase 3: System Integrations (Week 3) 🔗

**Priority**: MEDIUM - Connect to other systems

1. **Dream System Integration** (6 hours)
   - Register receptor in dream engine
   - High melatonin + GABA → increase dream frequency
   - High cortisol → increase nightmare probability
   - Dopamine + Endorphin → increase lucid dream chance
   - Modulate dream intensity based on hormone balance

2. **Consciousness System Integration** (4 hours)
   - Register receptor in consciousness engine
   - High stress → reduce awareness depth (defensive mode)
   - High neuroplasticity → increase learning receptivity
   - Mood valence affects thought generation

3. **Memory System Integration** (4 hours)
   - Register receptor in memory consolidation
   - High cortisol → prioritize threat-related memories
   - High neuroplasticity → enhance memory formation
   - Serotonin affects memory retrieval efficiency

### Phase 4: Monitoring & Analytics (Week 4) 📊

**Priority**: LOW - Observability

1. **Hormone Dashboard** (6 hours)
   - Real-time hormone level visualization
   - Historical trends (7-day, 30-day)
   - Hormone interaction graph
   - Dominant state timeline
   - Neuroplasticity score tracking

2. **Alerting** (2 hours)
   - Alert on sustained high cortisol (>0.8 for 30+ min)
   - Alert on low neuroplasticity (<0.3 for 60+ min)
   - Alert on hormone imbalance patterns

3. **Analytics Integration** (2 hours)
   - Export hormone data to analytics pipeline
   - Correlation analysis (hormones ↔ user outcomes)
   - A/B testing on hormone-based features

---

## 7. Testing Requirements

### 7.1 Unit Tests

- [x] Test hormone level initialization (exists)
- [x] Test hormone interactions (exists)
- [x] Test trigger functions (exists)
- [ ] Test per-user hormone isolation
- [ ] Test user_id validation in VIVOX integration
- [ ] Test hormone analytics with user_id filtering

### 7.2 Integration Tests

- [ ] Test endocrine API endpoints with authentication
- [ ] Test tier-based access control on hormone data
- [ ] Test cross-user data isolation
- [ ] Test hormone receptor pattern with dream/consciousness systems
- [ ] Test neuroplasticity calculation affects learning systems

### 7.3 Performance Tests

- [ ] Test 1000 concurrent users with separate hormone states
- [ ] Test hormone update loop performance (1-second resolution)
- [ ] Test LRU cache for inactive user systems
- [ ] Test analytics query performance on 10K+ hormone records

---

## 8. Security & Privacy Considerations

### 8.1 Hormone Data Sensitivity

**Classification**: **Sensitive Health-Adjacent Data**

**Justification**:
- Cortisol levels indicate stress patterns
- Serotonin/Dopamine indicate mood states
- Combined data could reveal mental health information
- Patterns could be used for manipulation

**Protection Requirements**:
- ✅ Store only aggregated/anonymized data long-term
- ❌ NOT IMPLEMENTED: User consent for hormone tracking
- ❌ NOT IMPLEMENTED: Data export/deletion (GDPR right to erasure)
- ❌ NOT IMPLEMENTED: Encryption at rest for hormone histories

### 8.2 Access Control Requirements

**By Tier**:
- **Tier 1 (Public)**: No access to hormone data
- **Tier 2 (Authenticated)**: Access to own hormone levels (current snapshot)
- **Tier 3 (Power User)**: Access to own hormone profile + 7-day history
- **Tier 4 (Pro)**: Access to own hormone analytics + 30-day history
- **Tier 5 (Enterprise)**: API access + custom analytics
- **Tier 6 (Admin/System)**: Access to all users' hormone data

### 8.3 Audit Logging

**Required Events**:
- Hormone data access (who, when, which user's data)
- Hormone trigger execution (who triggered, type, intensity)
- Analytics query execution
- Cross-user access attempts (potential security breach)

**Current Status**: ❌ No audit logging implemented

---

## 9. Migration Path

### 9.1 Breaking Changes

**Changing to per-user state will break**:
- `get_endocrine_system()` → `get_endocrine_system(user_id)`
- All trigger functions need user_id parameter
- Module receptors need to handle per-user state

**Migration Strategy**:
1. Add deprecation warnings to old functions (2 weeks notice)
2. Update all internal callers
3. Update VIVOX integration
4. Update monitoring/modulation systems
5. Remove deprecated functions after migration complete

### 9.2 Backward Compatibility

**Option**: Keep global system for system-level stress (not user-specific)

```python
# Per-user systems
def get_endocrine_system(user_id: str) -> EndocrineSystem:
    """Get user-specific endocrine system"""
    ...

# System-level (optional)
def get_system_endocrine() -> EndocrineSystem:
    """Get global system endocrine state (for non-user operations)"""
    return _global_endocrine_system
```

---

## 10. Conclusion

### Summary

The LUKHAS Endocrine System is **well-designed and fully implemented** but suffers from:

✅ **Strengths**:
- Sophisticated bio-inspired hormone simulation
- Realistic hormone interactions and decay rates
- VIVOX-ERN integration with emotional regulation
- User_id captured in VIVOX hormone history
- Comprehensive analytics functions available
- Receptor pattern for module integration
- Neuroplasticity calculation for learning modulation

❌ **Critical Gaps**:
- Global singleton (no per-user hormone state)
- No production API endpoints
- No tier-based access control
- Optional user_id in VIVOX (defaults to "unknown")
- Not integrated with dream/consciousness/memory systems
- No audit logging for sensitive hormone data

### Recommendation

**Phase 1 REQUIRED** before production launch:
- Per-user hormone state isolation
- Production API endpoints with authentication
- Make user_id required in VIVOX integration

**Phase 2 & 3** can be post-launch:
- System integrations (dream, consciousness, memory)
- Monitoring dashboards
- Analytics pipelines

**Timeline**: 4 weeks (2 weeks CRITICAL for launch)

**Effort**: ~35 hours engineering time

---

**Audit Completed**: 2025-11-10
**Status**: **PARTIALLY READY** - Needs per-user isolation + API endpoints
**Next Steps**: Implement Phase 1 (per-user state + API) before launch
