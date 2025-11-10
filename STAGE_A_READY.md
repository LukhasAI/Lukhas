# Stage A Test Enrichment - READY TO EXECUTE ✅

**Date**: 2025-11-10
**Status**: 🟢 **ALL SYSTEMS GO**

---

## What's Working

### 1. ✅ Automatic Failure Capture
```bash
cat reports/events.ndjson | jq .
```
**Sample captured events**: 2 failures from smoke tests
- Signature-hashed for deduplication
- Full reproduction commands
- Environment flags recorded
- Frozen time working (2025-01-01 00:00:00)

### 2. ✅ Test Determinism
All tests now run with:
- Seed: 1337 (reproducible random)
- Frozen time: 2025-01-01 00:00:00
- Network blocked: RuntimeError if attempted
- No per-test edits required

### 3. ✅ Delegation Guide Ready
**File**: [reports/stage_a_batch_1.md](reports/stage_a_batch_1.md)

**Target**: 5 critical serve/ modules
1. serve/main.py - Main API endpoints
2. serve/identity_api.py - Auth (PROTECTED)
3. serve/telemetry_collector.py - Metrics
4. serve/health_endpoints.py - Health checks
5. serve/middleware/strict_auth.py - Auth middleware (PROTECTED)

---

## How to Execute

### Option 1: Claude.ai (Recommended for comprehensive tests)

**Copy this prompt** to https://claude.ai:

```
I need comprehensive tests for these 5 critical API modules in serve/:

1. serve/main.py - Main FastAPI endpoints (~500 lines, coverage: 35%)
2. serve/identity_api.py - Identity/auth endpoints (~200 lines, coverage: 20%) [PROTECTED FILE]
3. serve/telemetry_collector.py - Telemetry collection (~150 lines, coverage: 10%)
4. serve/health_endpoints.py - Health check endpoints (~100 lines, coverage: 50%)
5. serve/middleware/strict_auth.py - Auth middleware (~120 lines, coverage: 30%) [PROTECTED FILE]

For EACH module:
1. Read the source code from /Users/agi_dev/LOCAL-REPOS/Lukhas/serve/
2. Create a test file in tests/serve/test_<module>.py
3. Use FastAPI TestClient pattern
4. Test:
   - Happy paths (expected behavior)
   - Edge cases (empty, None, boundary values)
   - Error cases (401, 400, 500)
   - Rate limiting (if applicable)
   - Mock external dependencies (db, redis, external APIs)
5. Use deterministic inputs (PYTEST_SEED=1337, no random values)
6. Aim for 80%+ coverage per module
7. Run pytest after each file to verify all tests pass

Rules:
- Max 2 test files per PR
- No production code changes (tests only)
- PROTECTED FILES: No changes to serve/identity_api.py or serve/middleware/strict_auth.py (tests only)
- Use existing fixtures from tests/conftest.py (auto time freezing, network blocking)

Example test structure:
```python
from fastapi.testclient import TestClient
from serve.main import app
import pytest

client = TestClient(app)

def test_list_models():
    response = client.get("/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0

def test_list_models_caching():
    # Test model list caching
    r1 = client.get("/v1/models")
    r2 = client.get("/v1/models")
    assert r1.json() == r2.json()

def test_chat_completion():
    response = client.post("/v1/chat/completions", json={
        "model": "lukhas-mini",
        "messages": [{"role": "user", "content": "test"}]
    })
    assert response.status_code == 200
    assert "choices" in response.json()

def test_invalid_auth():
    response = client.get("/v1/models", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401
```

Create PRs when ready:
- PR 1: tests/serve/test_main.py
- PR 2: tests/serve/test_health_endpoints.py
- PR 3: tests/serve/test_identity_api.py
- PR 4: tests/serve/test_strict_auth.py
- PR 5: tests/serve/test_telemetry_collector.py

Title format: "test(serve): add comprehensive tests for <module>"
```

### Option 2: Jules AI (Automated PR creation)

```python
from bridge.llm_wrappers.jules_wrapper import JulesClient

async with JulesClient() as jules:
    session = await jules.create_session(
        prompt="""
        Add comprehensive tests for serve/main.py.

        Read serve/main.py source code, then create tests/serve/test_main.py with:
        - FastAPI TestClient pattern
        - Test all endpoints: /v1/models, /v1/responses, /v1/chat/completions, /v1/completions
        - Test happy paths, edge cases, auth validation, rate limiting
        - Mock external dependencies
        - Use PYTEST_SEED=1337 (deterministic)
        - Aim for 80%+ coverage

        Rules:
        - Max 1 test file (test_main.py)
        - No production code changes
        - Run pytest to verify all pass
        - Create PR with title: "test(serve): add comprehensive tests for main.py"
        """,
        source_id="sources/github/LukhasAI/Lukhas",
        automation_mode="AUTO_CREATE_PR"
    )
```

**Repeat for each of the 5 modules** (max 5 sessions, well within 100/day quota).

---

## Success Criteria

**Batch 1A Complete When**:
- [ ] 5 test files created in tests/serve/
- [ ] All tests pass: `pytest -q tests/serve`
- [ ] Coverage ≥80% for each module: `pytest --cov=serve --cov-report=term`
- [ ] 5 PRs created and merged
- [ ] No production code modified
- [ ] Protected files noted but unchanged

**Metrics**:
- Current coverage: serve/ ~35%
- Target coverage: serve/ ~75%
- Delta: +40 percentage points
- Timeline: 3-5 days

---

## After Batch 1A

### Batch 1B: Remaining serve/ files (15 files)
- serve/middleware/cors.py
- serve/middleware/error_handler.py
- serve/routes/*.py
- serve/utils/*.py

### Batch 2A: matriz/ core modules (10 files)
- matriz/core/engine.py
- matriz/core/context.py
- matriz/nodes/*.py

### Batch 3: lukhas/ production lane (15 files)
- lukhas/api/*.py
- lukhas/core/*.py

---

## Monitoring Progress

### Check test results
```bash
# Run all serve tests
pytest -q tests/serve

# Run with coverage
pytest --cov=serve --cov-report=term tests/serve

# Check events captured
cat reports/events.ndjson | jq -r '.test_id'
```

### Track coverage improvements
```bash
# Before
pytest --cov=serve --cov-report=term tests/serve | grep "^serve/"

# After (expect 75%+ lines)
pytest --cov=serve --cov-report=term tests/serve | grep "^TOTAL"
```

---

## Current Infrastructure Status

| Component | Status | Details |
|-----------|--------|---------|
| **Drop-in hooks** | ✅ ACTIVE | tests/conftest.py (115 lines) |
| **Event capture** | ✅ WORKING | reports/events.ndjson (2 events) |
| **Determinism** | ✅ VERIFIED | Seed 1337, frozen time |
| **Network blocking** | ✅ ACTIVE | ALLOW_NET=0 default |
| **Delegation guides** | ✅ READY | stage_a_batch_1.md |
| **Stage A guardrails** | ✅ ENFORCED | Tests only, max 2 files/PR |
| **Coverage baseline** | 🟡 PARTIAL | Need full coverage run |

---

## Guardrails Reminder

### ✅ Stage A Rules (ACTIVE)
- Only create test files in tests/
- NO production code changes
- NO protected file modifications
- Max 2 test files per PR
- All tests must pass
- Use deterministic inputs (PYTEST_SEED=1337)

### ❌ NOT Allowed (Stage A)
- Modifying serve/*.py files
- Changing protected files (identity_api, strict_auth)
- Adding new dependencies
- Changing API schemas
- Performance optimizations (Stage C only)

---

## Next Steps

1. **Choose delegation method**: Claude.ai (recommended) or Jules AI
2. **Copy prompt** from Option 1 or 2 above
3. **Paste into tool** and start test creation
4. **Review PRs** as they're created
5. **Merge when tests pass** and coverage ≥80%
6. **Track progress** in this document

---

## Questions?

- **What if tests fail?** Debug and fix tests (not production code)
- **Coverage below 80%?** Add more test cases before merging
- **Protected files?** Tests OK, production code changes need 2-key approval
- **Network calls needed?** Use `ALLOW_NET=1` or mock the dependency
- **Time-dependent tests?** Use `FREEZE_TIME=0` or work with frozen time

---

**Status**: 🚀 **READY TO LAUNCH**

All systems operational. Self-evolution Stage A ready for test enrichment.

Start with serve/main.py - it's the highest-value target (500 lines, 35% → 80%).

---

*Generated 2025-11-10 by Claude Code*
