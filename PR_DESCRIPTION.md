# LUKHAS Core Wiring - Production Launch Ready

## Overview

This PR completes the LUKHAS core wiring plan (Tasks 1-9 of 10), connecting `core/` and `labs/` consciousness/dream/glyph systems into the `lukhas/` production lane with comprehensive safety, testing, and documentation.

**Status**: ✅ **9/10 Tasks Complete** (90% - Task 10 SLSA already merged to main)

---

## What's Included

### 🔌 Task 2: Wrapper Modules (Commit 819ca783a)

**Files**: 5 files, 1,363 lines

Production-safe wrapper modules that expose core functionality:

- **lukhas/consciousness/** - Wraps `labs.core.consciousness`
  - Feature flag: `LUKHAS_CONSCIOUSNESS_ENABLED` (default: OFF)
  - Functions: `get_consciousness_state`, `create_state`, `get_orchestrator`

- **lukhas/dream/** - Wraps dream engine
  - Feature flags: `LUKHAS_DREAMS_ENABLED`, `LUKHAS_PARALLEL_DREAMS` (default: OFF)
  - Functions: `simulate_dream`, `parallel_dream_mesh`, `get_dream_by_id`

- **lukhas/glyphs/** - Wraps `labs.core.glyph`
  - Feature flag: `LUKHAS_GLYPHS_ENABLED` (default: OFF)
  - Functions: `encode_concept`, `bind_glyph`, `validate_glyph`

- **tests/unit/lukhas/test_wrappers.py** - 35+ tests for wrapper behavior
- **docs/wrappers/WRAPPER_MODULES.md** - Comprehensive documentation

---

### 🚀 Task 3: Production API Routes (Commit 1bb39c77d)

**Files**: 6 files, 1,939 lines

FastAPI endpoints with feature flag gating and Pydantic validation:

#### Dreams API (`lukhas_website/lukhas/api/dreams.py`)
- `POST /api/v1/dreams/simulate` - Simulate dream with seed/context
- `POST /api/v1/dreams/mesh` - Parallel dream mesh with consensus ✅ (Task 4)
- `GET /api/v1/dreams/{dream_id}` - Retrieve dream by ID
- `GET /api/v1/dreams/` - Health check

#### GLYPHs API (`lukhas_website/lukhas/api/glyphs.py`)
- `POST /api/v1/glyphs/encode` - Encode concept to GLYPH
- `POST /api/v1/glyphs/bind` - Bind GLYPH to memory with auth ✅ (Task 6)
- `GET /api/v1/glyphs/bindings/{binding_id}` - Retrieve binding
- `POST /api/v1/glyphs/validate` - Validate GLYPH data (always available)
- `GET /api/v1/glyphs/stats` - Get subsystem statistics
- `GET /api/v1/glyphs/` - Health check

#### Drift Monitoring API (`lukhas_website/lukhas/api/drift.py`)
- `POST /api/v1/drift/update` - Update drift with intent/action vectors ✅ (Task 5)
- `GET /api/v1/drift/{user_id}` - Get current drift score
- `GET /api/v1/drift/{user_id}/trends` - Get paginated trend history
- `GET /api/v1/drift/config/{lane}` - Get lane configuration (always available)
- `GET /api/v1/drift/` - Health check

**Wired into `serve/main.py`** with feature flag checks and graceful degradation.

- **tests/unit/lukhas/test_api_routes.py** - 30+ tests for all endpoints
- **docs/api/CORE_WIRING_API.md** - Complete API reference with examples

---

### ⚡ Task 9: Performance Testing (Commit c0f3eb367)

**Files**: 4 files, 1,029 lines

Comprehensive performance infrastructure:

- **tests/performance/test_core_wiring_benchmarks.py** (420 lines)
  - Dreams benchmarks: simulate < 250ms, mesh throughput
  - GLYPHs benchmarks: encode < 100ms, bind < 150ms, validate < 10ms
  - Drift benchmarks: update < 50ms, large vectors (768-dim)
  - End-to-end: API overhead < 10ms
  - Memory tests: bounded memory, no leaks

- **tests/smoke/test_core_wiring_smoke.py** (290 lines)
  - Fast CI tests (< 10 seconds total)
  - Feature flag validation
  - Health checks, imports, error handling

- **docs/testing/PERFORMANCE_TESTING.md**
  - Performance budgets and targets
  - Running benchmarks and smoke tests
  - CI integration, load testing, chaos engineering
  - Memory profiling and troubleshooting

- **.benchmarks/README.md** - Benchmark results directory guide

---

## Already Merged to Main

These tasks were completed by other contributors and are already on main:

- ✅ **Task 1**: Global initialization (commit df111b0dd)
- ✅ **Task 7**: QRG specification (commit a5ab777e8)
- ✅ **Task 8**: Observability & Prometheus (commit d90d81a7b)
- ✅ **Task 10**: SLSA/Provenance (commit 4b42ac947)

---

## Key Safety Features

✅ **All feature flags default to OFF (0)**
✅ **Safe imports** - won't crash if core modules missing
✅ **Input validation** - Pydantic models, length checks, range validation
✅ **Authorization support** - Bearer tokens for bind operations
✅ **Graceful degradation** - 503 responses when disabled
✅ **Comprehensive error handling** - Consistent error formats across APIs
✅ **Performance budgets** - Enforced via pytest-benchmark
✅ **Memory bounds** - Drift monitor window size limited
✅ **Request validation** - Vector length matching, emotion ranges, concept length

---

## Statistics

### Code Added
- **Total Lines**: 4,331 (wrappers + API + tests + docs)
- **Production Code**: 2,635 lines
- **Test Code**: 1,065 lines (100+ tests)
- **Documentation**: 631 lines

### Test Coverage
- **Wrapper Tests**: 35+ tests (feature flags, API consistency, degradation)
- **API Tests**: 30+ tests (endpoints, validation, error handling)
- **Performance Tests**: 13 benchmarks + 30+ smoke tests
- **Total Tests**: 100+ tests

### API Endpoints
- **13 Production Endpoints** (4 dreams + 5 glyphs + 4 drift)
- **All feature-flag gated** with health checks
- **OpenAPI/Swagger compatible**

### Feature Flags
- `LUKHAS_CONSCIOUSNESS_ENABLED` (default: 0)
- `LUKHAS_DREAMS_ENABLED` (default: 0)
- `LUKHAS_PARALLEL_DREAMS` (default: 0)
- `LUKHAS_GLYPHS_ENABLED` (default: 0)
- `LUKHAS_DRIFT_ENABLED` (default: 0)

---

## Testing

### Run All Tests

```bash
# Unit tests for wrappers
pytest tests/unit/lukhas/test_wrappers.py -v

# Unit tests for API routes
pytest tests/unit/lukhas/test_api_routes.py -v

# Smoke tests (fast, < 10s)
pytest tests/smoke/test_core_wiring_smoke.py -v

# Performance benchmarks
pytest tests/performance/test_core_wiring_benchmarks.py --benchmark-only
```

### Manual API Testing

```bash
# Start server
export LUKHAS_DREAMS_ENABLED=1
export LUKHAS_GLYPHS_ENABLED=1
export LUKHAS_DRIFT_ENABLED=1
python serve/main.py

# Test dreams API
curl -X POST http://localhost:8000/api/v1/dreams/simulate \
  -H "Content-Type: application/json" \
  -d '{"seed": "test", "context": {"mood": "calm"}}'

# Test glyphs API
curl -X POST http://localhost:8000/api/v1/glyphs/encode \
  -H "Content-Type: application/json" \
  -d '{"concept": "gratitude", "emotion": {"joy": 0.8}}'

# Test drift API
curl -X POST http://localhost:8000/api/v1/drift/update \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "intent": [1.0, 0.0], "action": [0.9, 0.1]}'
```

---

## Deployment Checklist

### Pre-deployment
- [ ] All tests pass locally
- [ ] Performance benchmarks meet budgets
- [ ] Feature flags verified OFF by default
- [ ] Documentation reviewed
- [ ] Security review completed (Task 10 already done)

### Staging Deployment
- [ ] Deploy with all flags OFF
- [ ] Verify health checks return 200
- [ ] Verify 503 responses when disabled
- [ ] Enable flags one by one and test
- [ ] Run smoke tests in staging
- [ ] Monitor error rates and latency

### Production Canary (1%)
- [ ] Deploy to 1% with flags OFF
- [ ] Monitor for 24h
- [ ] Enable features gradually
- [ ] Run synthetic smoke tests
- [ ] Check performance metrics

### Production Rollout
- [ ] Increase to 10% if canary successful
- [ ] Monitor for 24h
- [ ] Increase to 50%
- [ ] Monitor for 24h
- [ ] Increase to 100%
- [ ] Two-key approval for consciousness features

---

## Rollback Plan

If issues occur:

1. **Disable via feature flags** (no redeployment needed):
   ```bash
   export LUKHAS_DREAMS_ENABLED=0
   export LUKHAS_GLYPHS_ENABLED=0
   export LUKHAS_DRIFT_ENABLED=0
   ```

2. **Revert code** if flags don't work:
   ```bash
   git revert <commit-hash>
   ```

---

## Documentation

- [Wrapper Modules Guide](./docs/wrappers/WRAPPER_MODULES.md)
- [API Reference](./docs/api/CORE_WIRING_API.md)
- [Performance Testing Guide](./docs/testing/PERFORMANCE_TESTING.md)

---

## Review Guidance

### Key Areas to Review
1. **Feature Flag Safety**: Verify all flags default OFF
2. **Input Validation**: Check Pydantic models are comprehensive
3. **Error Handling**: Ensure consistent error responses
4. **Performance**: Review benchmark budgets are reasonable
5. **Documentation**: Verify examples are accurate

### Testing Checklist
- [ ] Run wrapper tests
- [ ] Run API tests
- [ ] Run smoke tests
- [ ] Run benchmarks
- [ ] Manual API testing with curl

---

## Thank You!

This PR represents the core wiring infrastructure for LUKHAS production launch. All work follows the 5-7 day plan and includes comprehensive safety, testing, and documentation.

**Total Effort**: ~4,300 lines of production code + tests + docs across 15 files.

Ready for review! 🚀
