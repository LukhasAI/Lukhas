#!/usr/bin/env python3
"""
Create Jules Batch - HIGH PRIORITY Test Collection & Coverage
Focus: Fix remaining test errors and add critical production module coverage
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient

HIGH_PRIORITY_SESSIONS = [
    # CRITICAL P0 - Fix last remaining test collection error
    {
        "title": "🚨 P0: Fix aioresponses test collection error (LAST ERROR)",
        "prompt": """**CRITICAL P0: Fix Last Remaining Test Collection Error**

**Current Status**: Test collection errors reduced from 84 → 1 (98.8% reduction!)

**The ONLY remaining error**:
```
ERROR collecting tests/bridge/llm_wrappers/test_jules_wrapper.py
ModuleNotFoundError: No module named 'aioresponses'
```

**Task**: Fix this test to eliminate the last test collection error

**Options**:
1. **Preferred**: Refactor test to use `unittest.mock` instead of `aioresponses`
2. Add `aioresponses` to `requirements-dev.txt` (if truly needed)
3. Mark test with `pytest.importorskip("aioresponses")` to skip if not available

**Recommended Approach**:
Use `unittest.mock` to mock aiohttp responses:

```python
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.mark.asyncio
@patch('aiohttp.ClientSession')
async def test_jules_api_call(mock_session):
    # Mock the response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={'session_id': 'test123'})

    # Mock the session.post method
    mock_session.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

    # Test your code
    jules = JulesClient()
    result = await jules.create_session("test prompt")
    assert result['session_id'] == 'test123'
```

**Success Criteria**:
- Test collection: `python3 -m pytest --collect-only 2>&1 | grep "collected"`
- Expected: "185 tests collected, 0 errors"
- ALL tests must collect without errors

**LUKHAS Import Rules**:
- Use `from bridge.llm_wrappers.jules_wrapper import JulesClient`
- Mock ALL external API calls (no real Jules API calls in tests)

**Commit Message**:
```
fix(hygiene): eliminate last test collection error (84 → 0 complete)

Problem:
- tests/bridge/llm_wrappers/test_jules_wrapper.py failed to collect
- Missing aioresponses dependency blocked collection
- Last remaining error after 84 → 1 reduction

Solution:
- Refactored test to use unittest.mock instead of aioresponses
- Removed external test dependency
- All external API calls mocked

Impact:
- Test collection errors: 1 → 0 (100% clean)
- 185 tests collecting successfully
- CI/CD fully unblocked
- No external test dependencies

Tests: python3 -m pytest --collect-only shows 0 errors
```

**Priority**: P0 - CRITICAL - Blocks CI/CD
""",
    },

    # HIGH PRIORITY P1 - Coverage for production API
    {
        "title": "🧪 P1: Add comprehensive test coverage for serve/ (Production API)",
        "prompt": """**HIGH PRIORITY P1: Production API Test Coverage**

**Objective**: Add comprehensive tests for serve/ module (production FastAPI application)

**Priority Files** (Production-critical):
- `serve/main.py` (FastAPI app, routes, middleware stack)
- `serve/openai_schemas.py` (Pydantic models for OpenAI compatibility)
- `serve/api/` endpoints (if exists)

**Target**: 90%+ coverage (production-critical code)

**Test Requirements**:

**1. FastAPI Application Tests**:
```python
import pytest
from fastapi.testclient import TestClient
from serve.main import app

@pytest.fixture
def client():
    return TestClient(app)

class TestOpenAICompatibility:
    def test_chat_completion_basic(self, client):
        '''Test basic chat completion endpoint'''
        response = client.post(
            "/v1/chat/completions",
            headers={"Authorization": "Bearer test_key"},
            json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "Hello"}]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "choices" in data
        assert len(data["choices"]) > 0
```

**2. Pydantic Model Tests**:
```python
from serve.openai_schemas import ChatCompletionRequest, ChatCompletionResponse

class TestOpenAISchemas:
    def test_chat_completion_request_validation(self):
        '''Test request model validation'''
        request = ChatCompletionRequest(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}]
        )
        assert request.model == "gpt-3.5-turbo"

    def test_invalid_temperature_rejected(self):
        '''Test temperature bounds (0-2)'''
        with pytest.raises(ValidationError):
            ChatCompletionRequest(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                temperature=3.0  # Invalid
            )
```

**3. Middleware Tests**:
- Auth middleware (token validation)
- CORS headers
- Request logging
- Error handling middleware

**4. Error Handling**:
- Invalid API keys
- Malformed requests
- Rate limiting
- Service unavailable scenarios

**Create tests in**: `tests/unit/serve/` and `tests/integration/serve/`

**LUKHAS Import Rules**:
- Use `from serve.main import app` (NOT lukhas.serve)
- Use `from serve.openai_schemas import *` for models
- Mock MATRIZ/consciousness dependencies
- Use TestClient for endpoint tests

**Mock External Dependencies**:
```python
@patch('serve.main.get_lukhas_instance')
def test_with_mocked_lukhas(mock_lukhas):
    mock_lukhas.return_value.process.return_value = "Mocked response"
    # Test code here
```

**Verify Coverage**:
```bash
python3 -m pytest tests/unit/serve/ tests/integration/serve/ -v --cov=serve --cov-report=term-missing
```

**Expected**: 90%+ coverage for all serve/ modules

**Commit Message**:
```
test(serve): add comprehensive coverage for production API (90%+)

Problem:
- Production serve/ module lacked test coverage
- OpenAI compatibility untested
- No endpoint integration tests
- Pydantic models unvalidated

Solution:
- Added 50+ tests for serve/ module
- FastAPI endpoint tests with TestClient
- Pydantic model validation tests
- Middleware and error handling coverage

Impact:
- serve/ coverage: <20% → 90%+
- Production API fully tested
- OpenAI compatibility verified
- Safe refactoring enabled

Tests: 50+ tests, all passing, 90%+ coverage
```

**Priority**: P1 - Production-critical infrastructure
""",
    },

    # HIGH PRIORITY P1 - lukhas/governance coverage
    {
        "title": "🧪 P1: Add comprehensive test coverage for lukhas/governance/ (Guardian)",
        "prompt": """**HIGH PRIORITY P1: Guardian System Test Coverage**

**Objective**: Add comprehensive tests for lukhas/governance/ (Constitutional AI, Guardian system)

**Priority Files**:
- `lukhas/governance/guardian.py` (Constitutional AI enforcement)
- `lukhas/governance/drift_detector.py` (Ethical drift detection)
- `lukhas/governance/audit_logger.py` (Security audit trails)
- `lukhas/governance/policy_engine.py` (Policy evaluation)

**Target**: 85%+ coverage (security-critical code)

**Test Requirements**:

**1. Guardian/Constitutional AI Tests**:
```python
import pytest
from lukhas.governance.guardian import Guardian

class TestGuardian:
    @pytest.fixture
    def guardian(self):
        return Guardian()

    def test_policy_violation_detected(self, guardian):
        '''Test that policy violations are caught'''
        result = guardian.evaluate(
            action="delete_all_data",
            context={"user": "guest"}
        )
        assert result.allowed == False
        assert "policy_violation" in result.reasons

    def test_ethical_constraint_enforcement(self, guardian):
        '''Test constitutional constraints'''
        # Should reject harmful requests
        result = guardian.evaluate(
            action="generate_harmful_content",
            context={"content_type": "violence"}
        )
        assert result.allowed == False
```

**2. Drift Detection Tests**:
```python
from lukhas.governance.drift_detector import DriftDetector

class TestDriftDetection:
    def test_behavior_drift_detected(self):
        '''Test detection of ethical drift over time'''
        detector = DriftDetector()

        # Baseline behavior
        detector.record_decision("safe_action", approved=True)

        # Drifting behavior
        for _ in range(10):
            detector.record_decision("questionable_action", approved=True)

        assert detector.check_drift() > 0.5  # Drift detected
```

**3. Audit Logging Tests**:
```python
from lukhas.governance.audit_logger import AuditLogger

class TestAuditLogger:
    def test_security_event_logged(self):
        '''Test security events are logged'''
        logger = AuditLogger()
        logger.log_event(
            event_type="auth_failure",
            user_id="user123",
            details={"reason": "invalid_token"}
        )

        # Verify event was logged
        events = logger.query_events(event_type="auth_failure")
        assert len(events) > 0

    def test_audit_trail_tamper_proof(self):
        '''Test audit log cannot be modified'''
        logger = AuditLogger()
        logger.log_event(event_type="test", user_id="user1")

        # Attempt to modify should fail
        with pytest.raises(PermissionError):
            logger.modify_event(event_id=1)
```

**4. Policy Engine Tests**:
```python
from lukhas.governance.policy_engine import PolicyEngine

class TestPolicyEngine:
    def test_policy_evaluation(self):
        '''Test policy rules are evaluated correctly'''
        engine = PolicyEngine()
        engine.add_policy("no_admin_delete", rule="action != 'delete' OR role == 'admin'")

        # Should allow admin delete
        assert engine.evaluate(action="delete", role="admin") == True

        # Should block user delete
        assert engine.evaluate(action="delete", role="user") == False
```

**Create tests in**: `tests/unit/lukhas/governance/` and `tests/integration/lukhas/governance/`

**LUKHAS Import Rules**:
- Use `from lukhas.governance import *` (production imports)
- NO imports from `candidate/` (strict lane isolation)
- Mock consciousness/MATRIZ dependencies

**Verify Coverage**:
```bash
python3 -m pytest tests/unit/lukhas/governance/ -v --cov=lukhas/governance --cov-report=term-missing
```

**Expected**: 85%+ coverage for all governance/ modules

**Commit Message**:
```
test(governance): add comprehensive Guardian system tests (85%+)

Problem:
- Guardian/Constitutional AI system untested
- Drift detection unvalidated
- Audit logging not verified
- Policy engine coverage missing

Solution:
- Added 40+ tests for governance/ module
- Constitutional AI constraint tests
- Drift detection algorithm tests
- Tamper-proof audit log tests
- Policy evaluation coverage

Impact:
- governance/ coverage: <15% → 85%+
- Security-critical code tested
- Constitutional AI verified
- Safe for production deployment

Tests: 40+ tests, all passing, 85%+ coverage
```

**Priority**: P1 - Security and ethics critical
""",
    },

    # HIGH PRIORITY P1 - lukhas/api coverage (augment smoke tests)
    {
        "title": "🧪 P1: Add deep unit tests for lukhas/api/ (augment smoke tests)",
        "prompt": """**HIGH PRIORITY P1: Deep Unit Tests for lukhas/api/**

**Context**: We already have 108 smoke tests for lukhas/api/ modules (test_middleware.py, test_healthz_comprehensive.py, test_analytics.py, test_feature_flags.py)

**Objective**: Add DEEPER unit tests to augment smoke tests with 95%+ coverage

**Priority Files**:
- `lukhas/api/analytics.py` (event tracking, batching, privacy)
- `lukhas/api/features.py` (feature flags, percentage rollout)
- `lukhas/api/healthz.py` (health checks, degraded states)
- `lukhas/api/middleware/` (auth, headers, CORS, tracing)

**What's Already Tested** (smoke tests):
- Basic middleware functionality (auth, headers, CORS)
- Health check endpoints (healthz, readyz, metrics)
- Analytics event models and privacy
- Feature flag percentage bounds and privacy

**What STILL NEEDS Testing** (deep unit tests):
- Internal implementation details
- Private methods and helpers
- Complex edge cases
- Error recovery mechanisms
- State management
- Concurrency handling

**Test Requirements**:

**1. Analytics Deep Unit Tests**:
```python
from lukhas.api.analytics import AnalyticsCollector, EventBatcher

class TestAnalyticsCollector:
    def test_event_batching_threshold(self):
        '''Test batch is flushed at size limit'''
        collector = AnalyticsCollector(batch_size=10)

        # Add 9 events - should not flush
        for i in range(9):
            collector.add_event(f"event_{i}")
        assert collector.pending_count() == 9

        # 10th event triggers flush
        collector.add_event("event_10")
        assert collector.pending_count() == 0

    def test_privacy_user_id_hashing(self):
        '''Test user IDs are SHA-256 hashed'''
        from hashlib import sha256
        user_id = "user@example.com"
        expected_hash = sha256(user_id.encode()).hexdigest()

        event = create_analytics_event(user_id=user_id)
        assert event.user_id_hash == expected_hash
        assert user_id not in str(event)  # No PII in event
```

**2. Feature Flags Targeting Logic**:
```python
from lukhas.api.features import FeatureFlagEvaluator

class TestFeatureFlagTargeting:
    def test_percentage_rollout_distribution(self):
        '''Test percentage rollout is evenly distributed'''
        evaluator = FeatureFlagEvaluator()
        evaluator.set_flag("test-flag", percentage=50)

        # Test 1000 users
        enabled_count = 0
        for i in range(1000):
            if evaluator.is_enabled("test-flag", user_id=f"user_{i}"):
                enabled_count += 1

        # Should be approximately 50% (45-55% range acceptable)
        assert 450 <= enabled_count <= 550

    def test_user_id_targeting(self):
        '''Test specific user targeting'''
        evaluator = FeatureFlagEvaluator()
        evaluator.set_flag(
            "vip-feature",
            target_user_ids=["user123", "user456"]
        )

        assert evaluator.is_enabled("vip-feature", user_id="user123") == True
        assert evaluator.is_enabled("vip-feature", user_id="user999") == False
```

**3. Health Check Degraded States**:
```python
from lukhas.api.healthz import HealthChecker

class TestHealthCheckDegradation:
    def test_partial_service_failure(self):
        '''Test health check shows degraded when service fails'''
        checker = HealthChecker()

        # Simulate MATRIZ failure
        checker.register_service("matriz", healthy=False)
        checker.register_service("voice", healthy=True)

        status = checker.get_status()
        assert status.overall == "degraded"
        assert status.services["matriz"] == "unhealthy"
        assert status.services["voice"] == "healthy"
```

**4. Middleware State Management**:
```python
from lukhas.api.middleware.auth import AuthMiddleware

class TestAuthMiddlewareState:
    def test_token_caching(self):
        '''Test valid tokens are cached'''
        middleware = AuthMiddleware()

        # First validation - cache miss
        result1 = middleware.validate_token("valid_token")
        assert middleware.cache_hits == 0

        # Second validation - cache hit
        result2 = middleware.validate_token("valid_token")
        assert middleware.cache_hits == 1
```

**Create tests in**: `tests/unit/lukhas/api/` (separate from smoke tests)

**LUKHAS Import Rules**:
- Use `from lukhas.api import *` (production imports)
- Mock MATRIZ and consciousness dependencies
- Focus on UNIT tests (not integration tests)

**Verify Coverage**:
```bash
python3 -m pytest tests/unit/lukhas/api/ -v --cov=lukhas/api --cov-report=term-missing --cov-fail-under=95
```

**Expected**: 95%+ coverage (combining smoke tests + unit tests)

**Commit Message**:
```
test(api): add deep unit tests for lukhas/api (95%+ coverage)

Problem:
- Smoke tests covered happy paths only
- Internal implementation untested
- Complex edge cases missing
- State management unverified

Solution:
- Added 50+ deep unit tests for lukhas/api/
- Event batching and privacy validation
- Feature flag targeting algorithms
- Health check degradation scenarios
- Middleware state management

Impact:
- lukhas/api/ coverage: 75% → 95%+
- Internal logic fully tested
- Production-critical paths verified
- Safe for refactoring

Tests: 50+ unit tests, all passing, 95%+ coverage
```

**Priority**: P1 - Production API critical
""",
    },

    # HIGH PRIORITY P1 - MATRIZ integration tests
    {
        "title": "🧪 P1: Add MATRIZ integration tests (end-to-end cognitive workflows)",
        "prompt": """**HIGH PRIORITY P1: MATRIZ Cognitive Engine Integration Tests**

**Objective**: Add end-to-end integration tests for MATRIZ cognitive engine workflows

**Scope**: Integration tests (not unit tests) - test full cognitive pipelines

**Test Scenarios**:

**1. Memory-Attention-Thought-Action-Decision Pipeline**:
```python
import pytest
from matriz import MATRIZEngine

@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_cognitive_pipeline():
    '''Test complete MATRIZ cognitive processing'''
    engine = MATRIZEngine()

    # Input -> Memory retrieval
    context = await engine.retrieve_memory("previous conversation")
    assert context is not None

    # Memory -> Attention
    focused_context = await engine.apply_attention(context)
    assert focused_context.attention_score > 0.5

    # Attention -> Thought
    thought = await engine.generate_thought(focused_context)
    assert thought.content is not None

    # Thought -> Action
    action = await engine.plan_action(thought)
    assert action.type in ["respond", "query", "update"]

    # Action -> Decision
    decision = await engine.make_decision(action)
    assert decision.approved == True
```

**2. Context Preservation Across Steps**:
```python
@pytest.mark.integration
async def test_context_preservation():
    '''Test context is preserved through pipeline'''
    engine = MATRIZEngine()

    initial_context = {"user_id": "user123", "session_id": "sess456"}

    # Process through pipeline
    result = await engine.process_with_context(
        input="Hello",
        context=initial_context
    )

    # Context should be preserved
    assert result.context["user_id"] == "user123"
    assert result.context["session_id"] == "sess456"
```

**3. Performance Targets Validation**:
```python
import time

@pytest.mark.integration
@pytest.mark.performance
async def test_performance_targets():
    '''Verify MATRIZ meets <250ms p95 latency target'''
    engine = MATRIZEngine()
    latencies = []

    for _ in range(100):
        start = time.perf_counter()
        await engine.process("test input")
        latency_ms = (time.perf_counter() - start) * 1000
        latencies.append(latency_ms)

    p95 = sorted(latencies)[94]
    assert p95 < 250, f"P95 latency {p95}ms exceeds 250ms target"
```

**4. Concurrent Request Handling**:
```python
import asyncio

@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_requests():
    '''Test MATRIZ handles 10+ parallel requests'''
    engine = MATRIZEngine()

    # Create 20 concurrent requests
    tasks = [
        engine.process(f"request_{i}")
        for i in range(20)
    ]

    # All should complete successfully
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # No exceptions
    errors = [r for r in results if isinstance(r, Exception)]
    assert len(errors) == 0

    # All have valid responses
    assert all(r.output is not None for r in results if not isinstance(r, Exception))
```

**5. Error Recovery and Graceful Degradation**:
```python
@pytest.mark.integration
async def test_error_recovery():
    '''Test MATRIZ recovers from component failures'''
    engine = MATRIZEngine()

    # Simulate memory service failure
    with patch('matriz.memory.retrieve') as mock_memory:
        mock_memory.side_effect = ConnectionError("Memory unavailable")

        # Should gracefully degrade
        result = await engine.process("test input")
        assert result.status == "degraded"
        assert result.output is not None  # Still produces output
        assert "memory_unavailable" in result.warnings
```

**6. Bio-Inspired Adaptation Tests**:
```python
@pytest.mark.integration
async def test_adaptive_behavior():
    '''Test MATRIZ adapts to load patterns'''
    engine = MATRIZEngine()

    # Simulate high load
    for _ in range(100):
        await engine.process("high load request")

    # Check adaptation occurred
    stats = engine.get_stats()
    assert stats.adaptive_mode == "high_load"
    assert stats.batch_size > stats.initial_batch_size
```

**Create tests in**: `tests/integration/matriz/`

**Test Markers**:
```python
pytestmark = [
    pytest.mark.integration,
    pytest.mark.slow,  # Integration tests may be slower
    pytest.mark.matriz
]
```

**Mock Strategy**:
- Mock external LLM API calls (OpenAI, Claude)
- Use real MATRIZ internal components
- Mock external storage/databases if needed

**LUKHAS Import Rules**:
- Use `from matriz import *` for core engine
- Use `from lukhas.core import *` for integration layer
- Use `from unittest.mock import patch` for external dependencies

**Verify Tests**:
```bash
python3 -m pytest tests/integration/matriz/ -v --durations=10
```

**Commit Message**:
```
test(matriz): add comprehensive integration tests for cognitive workflows

Problem:
- No end-to-end tests for MATRIZ pipeline
- Performance targets unvalidated
- Concurrency handling untested
- Error recovery unverified

Solution:
- Added 30+ integration tests for MATRIZ
- Full cognitive pipeline tests (Memory→Attention→Thought→Action→Decision)
- Performance validation (<250ms p95, 50+ ops/sec)
- Concurrent request handling (10+ parallel)
- Error recovery and graceful degradation

Impact:
- MATRIZ integration fully tested
- Performance targets validated
- Production-readiness verified
- Safe for cognitive workload deployment

Tests: 30+ integration tests, all passing, <250ms p95
```

**Priority**: P1 - Core cognitive engine critical
""",
    },
]


async def create_high_priority_batch():
    """Create high-priority Jules sessions"""

    print("\n" + "="*80)
    print("🚨 JULES HIGH PRIORITY BATCH: TEST FIXES & COVERAGE")
    print("="*80)
    print(f"\nCreating {len(HIGH_PRIORITY_SESSIONS)} high-priority sessions:")
    print("  🚨 P0 Critical: 1 session (fix last test error)")
    print("  🧪 P1 Testing: 4 sessions (coverage for critical modules)")
    print(f"\n  TOTAL: {len(HIGH_PRIORITY_SESSIONS)} sessions")
    print("="*80 + "\n")

    created = []

    async with JulesClient() as jules:
        for i, session_config in enumerate(HIGH_PRIORITY_SESSIONS, 1):
            try:
                print(f"\n[{i}/{len(HIGH_PRIORITY_SESSIONS)}] Creating: {session_config['title']}")

                session = await jules.create_session(
                    prompt=session_config['prompt'],
                    source_id="sources/github/LukhasAI/Lukhas",
                    automation_mode="AUTO_CREATE_PR"
                )

                session_id = session['name'].split('/')[-1]
                created.append({
                    'title': session_config['title'],
                    'session_id': session_id
                })

                print(f"✅ Created: {session_id}")
                print(f"   URL: https://jules.google.com/session/{session_id}")

            except Exception as e:
                print(f"❌ Failed: {e}")
                continue

            await asyncio.sleep(1)

    # Summary
    print("\n" + "="*80)
    print("📊 HIGH PRIORITY BATCH SUMMARY")
    print("="*80)
    print(f"\n✅ Created: {len(created)}/{len(HIGH_PRIORITY_SESSIONS)} sessions")
    print(f"🎯 Remaining Quota: ~{88 - len(created)}/100 sessions today")

    print("\n📋 Created Sessions:")
    for s in created:
        print(f"\n• {s['title']}")
        print(f"  ID: {s['session_id']}")
        print(f"  URL: https://jules.google.com/session/{s['session_id']}")

    print("\n" + "="*80 + "\n")

    return created


if __name__ == "__main__":
    try:
        asyncio.run(create_high_priority_batch())
    except KeyboardInterrupt:
        print("\n\n⏸️  Cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
