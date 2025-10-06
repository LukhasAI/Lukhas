---
status: wip
type: documentation
---
# TODO: Wave C Critical Implementation Gaps

⚠️ **RESERVED FOR PARALLEL CLAUDE CODE AGENT** - Jules should avoid this directory

## Missing Components from WAVE_C.md Implementation Plan

### 🔴 HIGH PRIORITY - Missing Files

1. **✅ COMPLETED: demo_smoke.py**
   - File: `candidate/aka_qualia/demo_smoke.py` (DONE)
   - Purpose: Smoke testing for scene → policy → hints pipeline
   - Reference: WAVE_C.md lines 178-194
   - Dependencies: oneiric_hook.py (exists), models.py (exists)

2. **TODO[WAVE-C]: Create memory.py client**
   - File: `candidate/aka_qualia/memory.py`
   - Purpose: AkaqMemory class for scene persistence
   - Reference: WAVE_C.md lines 238-247
   - Methods needed: save(), fetch_prev_scene(), history()

3. **TODO[WAVE-C]: Create SQL migrations**
   - File: `candidate/aka_qualia/migrations/001_akaq.sql`
   - Purpose: Database schema for akaq_scene and akaq_glyph tables
   - Reference: WAVE_C.md lines 203-235

### 🟡 MEDIUM PRIORITY - Testing Gaps

4. **TODO[WAVE-C]: Create tests/test_router_contract.py**
   - File: `candidate/aka_qualia/tests/test_router_contract.py`
   - Purpose: Router client contract testing
   - Reference: WAVE_C.md lines 127-131

5. **TODO[WAVE-C]: Create tests/test_glyphs.py**
   - File: `candidate/aka_qualia/tests/test_glyphs.py`
   - Purpose: Glyph mapping idempotency tests
   - Reference: WAVE_C.md lines 96-99

6. **TODO[WAVE-C]: Create ablation tests**
   - File: `candidate/aka_qualia/tests/test_ablation.py`
   - Purpose: Ablation testing with AKAQ_ABLATION=1
   - Reference: WAVE_C.md lines 314-315

### 🔵 LOW PRIORITY - Tools & Utilities

7. **TODO[WAVE-C]: Create migration tool**
   - File: `candidate/aka_qualia/tools/migrate.py`
   - Purpose: Database migration helper
   - Reference: WAVE_C.md line 393

8. **TODO[WAVE-C]: Update Prometheus metrics**
   - Files: Extend existing prometheus_exporter.py
   - Purpose: Add Wave C integration metrics
   - Reference: WAVE_C.md lines 253-261

## Implementation Order
Follow PR sequence: C1 (done) → C2 (done) → C3 (partial) → C4-C7 (pending)

## Critical for Production Readiness
Items 1-3 are REQUIRED before promoting candidate/aka_qualia → lukhas/aka_qualia