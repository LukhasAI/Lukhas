# Test Organization - 0.01% Professional Standards

**Purpose**: Transform LUKHAS test suite to match top-tier engineering organizations (Google, Netflix, Amazon, Microsoft Research).

**Created**: 2025-11-09
**Owner**: LUKHAS Core Team
**Status**: Design Phase

---

## Executive Summary

Current state: 391 modules without tests, 207 collection errors, fragmented test organization.

Target state: World-class test suite with:
- **100% collection success** - Zero broken tests
- **80%+ coverage** for production lanes (lukhas/, matriz/)
- **Professional categorization** - Clear test pyramid structure
- **Visual reporting** - Actionable dashboards and insights
- **Developer experience** - Fast feedback loops, easy navigation

---

## 1. Test Pyramid Architecture

### The 0.01% Test Pyramid

```
                    /\
                   /  \          E2E (5%)
                  /____\         - User journeys
                 /      \        - System integration
                /  INTE  \
               /  GRATION \      Integration (15%)
              /____________\     - Component interaction
             /              \    - API contracts
            /      UNIT      \
           /                  \  Unit (70%)
          /____________________\ - Fast, isolated
         /                      \
        /   SMOKE/HEALTH (10%)   \
       /__________________________\
```

**Distribution**:
- **Smoke/Health**: 10% - Critical path validation (15-30 tests, <10s total)
- **Unit**: 70% - Fast, isolated component tests (thousands of tests, <2min total)
- **Integration**: 15% - Cross-component interaction (hundreds of tests, <5min total)
- **E2E**: 5% - Full user journeys (dozens of tests, <10min total)

### Why This Matters

Organizations in the 0.01%:
- Run **smoke tests in <10 seconds** on every commit
- Run **full unit suite in <2 minutes** before PR merge
- Run **integration suite in <5 minutes** in CI pipeline
- Run **E2E suite in <10 minutes** nightly or pre-release

**Speed = Developer Velocity**

---

## 2. Professional Test Directory Structure

### New Structure (Mirrors pytest best practices + LUKHAS lanes)

```
tests/
├── smoke/                          # 10% - Critical health checks (<10s)
│   ├── test_api_health.py         # FastAPI /health endpoint
│   ├── test_matriz_pipeline.py    # MATRIZ can process input
│   ├── test_identity_auth.py      # Identity system functional
│   ├── test_memory_core.py        # Memory operations work
│   └── test_consciousness_core.py # Consciousness engine loads
│
├── unit/                           # 70% - Fast, isolated tests
│   ├── lukhas/                    # Production API layer
│   │   ├── api/
│   │   │   ├── test_features.py
│   │   │   └── test_analytics.py
│   │   ├── identity/
│   │   │   ├── test_webauthn_verify.py
│   │   │   └── test_token_types.py
│   │   └── features/
│   │       └── test_flags_service.py
│   │
│   ├── matriz/                    # Cognitive engine
│   │   ├── consciousness/
│   │   │   ├── test_ethical_reasoning.py
│   │   │   └── test_reflection_layer.py
│   │   ├── memory/
│   │   │   ├── test_unified_memory.py
│   │   │   └── test_temporal_systems.py
│   │   └── core/
│   │       └── test_engine.py
│   │
│   ├── serve/                     # FastAPI routes & middleware
│   │   ├── test_main.py
│   │   ├── test_openai_routes.py
│   │   ├── test_consciousness_api.py
│   │   └── middleware/
│   │       ├── test_strict_auth.py
│   │       └── test_headers.py
│   │
│   └── core/                      # Integration layer
│       ├── orchestration/
│       └── bridges/
│
├── integration/                    # 15% - Component interaction
│   ├── api/
│   │   ├── test_openai_compatibility.py
│   │   ├── test_streaming_pipeline.py
│   │   └── test_feedback_loop.py
│   │
│   ├── matriz/
│   │   ├── test_consciousness_memory.py
│   │   ├── test_ethical_guardian.py
│   │   └── test_bio_adaptation.py
│   │
│   └── identity/
│       ├── test_webauthn_flow.py
│       └── test_jwt_lifecycle.py
│
├── e2e/                            # 5% - Full user journeys
│   ├── test_consciousness_query_journey.py
│   ├── test_identity_onboarding.py
│   ├── test_openai_api_compatibility.py
│   └── test_guardian_ethical_intervention.py
│
├── contract/                       # API contract testing
│   ├── openai/
│   │   └── test_openai_schema_compliance.py
│   └── internal/
│       └── test_matriz_interface.py
│
├── performance/                    # Performance & benchmarks
│   ├── test_matriz_latency.py     # Target: <250ms p95
│   ├── test_memory_throughput.py  # Target: 50+ ops/sec
│   └── test_api_response_time.py  # Target: <100ms p50
│
├── security/                       # Security validation
│   ├── test_authentication.py
│   ├── test_authorization.py
│   └── test_secrets_detection.py
│
└── fixtures/                       # Shared test fixtures
    ├── conftest.py                # Global fixtures
    ├── matriz_fixtures.py         # MATRIZ test data
    ├── api_fixtures.py            # API test clients
    └── golden/                    # Golden file tests
        ├── matriz_outputs/
        └── api_responses/
```

### Migration Strategy

**Phase 1**: Organize existing tests (Week 1)
- Move tests to correct pyramid layer
- Fix collection errors (Python 3.9 compatibility)
- Standardize naming conventions

**Phase 2**: Fill critical gaps (Weeks 2-3)
- Tier 1: lukhas/ and serve/ (31 files) → 80%+ coverage
- Add missing smoke tests for critical paths

**Phase 3**: MATRIZ coverage (Weeks 4-6)
- Tier 2: matriz/ (97 files) → 70%+ coverage
- Focus on consciousness, memory, bio-symbolic

**Phase 4**: Integration & E2E (Weeks 7-8)
- Build integration test suite
- Create E2E user journey tests

---

## 3. Test Naming & Organization Standards

### File Naming Conventions

```python
# ✅ GOOD
test_webauthn_verify.py              # Mirrors source: lukhas/identity/webauthn_verify.py
test_ethical_reasoning_system.py     # Mirrors source: matriz/consciousness/reflection/ethical_reasoning_system.py

# ❌ BAD
webauthn_tests.py                    # Unclear what's being tested
test_stuff.py                        # Non-descriptive
```

### Test Function Naming

```python
# ✅ GOOD - Descriptive, behavior-focused
def test_webauthn_verification_succeeds_with_valid_signature():
    """WebAuthn verification returns True for valid authenticator signature."""
    pass

def test_jwt_token_expires_after_configured_duration():
    """JWT tokens become invalid after expiration time."""
    pass

def test_matriz_pipeline_completes_in_under_250ms():
    """MATRIZ cognitive pipeline meets p95 latency target."""
    pass

# ❌ BAD - Unclear what's being tested
def test_webauthn():
    pass

def test_jwt():
    pass
```

### Test Class Organization

```python
# ✅ GOOD - Organize by behavior/feature
class TestWebAuthnRegistration:
    """Tests for WebAuthn credential registration flow."""

    def test_registration_creates_credential(self):
        pass

    def test_registration_fails_with_invalid_challenge(self):
        pass

    def test_registration_prevents_duplicate_credentials(self):
        pass


class TestWebAuthnVerification:
    """Tests for WebAuthn authentication verification."""

    def test_verification_succeeds_with_valid_signature(self):
        pass

    def test_verification_fails_with_expired_challenge(self):
        pass
```

---

## 4. Fixture Organization (0.01% Standards)

### Global Fixtures (conftest.py)

```python
# tests/conftest.py
"""Global test fixtures available to all tests."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

@pytest.fixture
def api_client():
    """FastAPI test client for API testing."""
    from serve.main import app
    return TestClient(app)

@pytest.fixture
def mock_llm():
    """Mock LLM provider (prevents external API calls)."""
    mock = AsyncMock()
    mock.complete.return_value = {"response": "test response"}
    return mock

@pytest.fixture
def matriz_engine_test_mode():
    """MATRIZ engine in test mode (no external dependencies)."""
    from matriz.core.engine import MATRIZEngine
    return MATRIZEngine(mode="test", mock_llm=True)
```

### Domain-Specific Fixtures

```python
# tests/fixtures/matriz_fixtures.py
"""MATRIZ-specific test fixtures."""

import pytest

@pytest.fixture
def cognitive_input():
    """Standard cognitive input for MATRIZ tests."""
    return {
        "input": "test query",
        "context": {"user_id": "test-user"},
        "mode": "reasoning"
    }

@pytest.fixture
def memory_state():
    """Pre-populated memory state for testing."""
    return {
        "short_term": ["recent context"],
        "working_memory": {"active_goal": "test"},
        "long_term": ["historical data"]
    }
```

### Fixture Scope Optimization

```python
# Fast tests: function scope (default)
@pytest.fixture
def quick_setup():
    return {"data": "value"}

# Expensive setup: session scope (shared across all tests)
@pytest.fixture(scope="session")
def database_connection():
    """Expensive DB setup - reuse across all tests."""
    db = connect_to_test_db()
    yield db
    db.close()

# Module scope: shared within a test file
@pytest.fixture(scope="module")
def matriz_engine():
    """MATRIZ engine initialization - expensive, reuse per module."""
    engine = MATRIZEngine()
    yield engine
    engine.shutdown()
```

---

## 5. Test Markers & Categorization

### Comprehensive Marker System

```python
# pyproject.toml - Already defined, use them!
[tool.pytest.ini_options]
markers = [
    "smoke: Critical health checks (run on every commit)",
    "unit: Fast, isolated component tests",
    "integration: Component interaction tests",
    "e2e: Full user journey tests",
    "slow: Tests taking >5 seconds",
    "performance: Performance/benchmark tests",
    "security: Security validation tests",
    "matriz: MATRIZ subsystem tests",
    "consciousness: Consciousness system tests",
    "tier1: Critical path tests (blocking release)",
]
```

### Usage Examples

```python
import pytest

@pytest.mark.smoke
@pytest.mark.tier1
def test_api_health_endpoint_returns_200(api_client):
    """API health endpoint is functional."""
    response = api_client.get("/health")
    assert response.status_code == 200

@pytest.mark.unit
@pytest.mark.matriz
def test_memory_retrieval_returns_recent_context(matriz_engine):
    """Memory system retrieves most recent context."""
    result = matriz_engine.memory.retrieve(query="test")
    assert result is not None

@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.consciousness
def test_ethical_reasoning_blocks_harmful_request(matriz_engine):
    """Guardian system blocks ethically harmful requests."""
    result = matriz_engine.process("harmful input")
    assert result.blocked is True
    assert "ethical_violation" in result.reason

@pytest.mark.e2e
@pytest.mark.slow
def test_full_consciousness_query_journey(api_client):
    """Complete user journey: query → consciousness → response."""
    response = api_client.post("/v1/consciousness/query", json={"query": "test"})
    assert response.status_code == 200
    assert "consciousness_state" in response.json()

@pytest.mark.performance
def test_matriz_pipeline_latency_under_250ms(matriz_engine, benchmark):
    """MATRIZ pipeline meets p95 latency target (<250ms)."""
    result = benchmark(matriz_engine.process, "test input")
    assert benchmark.stats.stats.mean < 0.25  # 250ms
```

### Running Specific Test Categories

```bash
# Smoke tests only (run on every commit)
pytest -m smoke

# All unit tests (fast feedback)
pytest -m unit

# Integration tests (pre-merge)
pytest -m integration

# Critical path only (blocking release)
pytest -m tier1

# MATRIZ subsystem tests
pytest -m matriz

# Exclude slow tests (local development)
pytest -m "not slow"

# Smoke + tier1 (essential validation)
pytest -m "smoke or tier1"

# Performance benchmarks only
pytest -m performance --benchmark-only
```

---

## 6. Coverage Standards & Reporting

### Coverage Targets (By Lane)

| Lane | Current | Target | Priority |
|------|---------|--------|----------|
| **lukhas/** | ~20% | 85%+ | 🔴 HIGH |
| **serve/** | ~15% | 85%+ | 🔴 HIGH |
| **matriz/** | ~10% | 75%+ | 🟡 MEDIUM |
| **core/** | ~5% | 60%+ | 🟢 LOW |
| **candidate/** | ~5% | 40%+ | 🟢 LOW |

### Coverage Commands

```bash
# Full coverage report
pytest --cov=lukhas --cov=matriz --cov=serve --cov-report=html --cov-report=term-missing

# Coverage for specific module
pytest tests/unit/lukhas/identity/ --cov=lukhas.identity --cov-report=term-missing

# Coverage diff (what changed in this PR?)
pytest --cov=lukhas --cov-report=diff:origin/main

# Fail if coverage below threshold
pytest --cov=lukhas --cov-fail-under=80
```

### Coverage Reports

```bash
# Generate HTML report (visual, detailed)
pytest --cov=lukhas --cov-report=html
open htmlcov/index.html

# Generate JSON (for CI/CD integration)
pytest --cov=lukhas --cov-report=json

# Generate XML (for Codecov/Coveralls)
pytest --cov=lukhas --cov-report=xml
```

---

## 7. Performance Testing Standards

### MATRIZ Performance Targets

```python
import pytest

@pytest.mark.performance
@pytest.mark.matriz
def test_matriz_p95_latency_under_250ms(matriz_engine, benchmark):
    """MATRIZ cognitive pipeline meets p95 latency target (<250ms).

    Performance Target: <250ms p95 (95th percentile)
    Current: ~180ms average (needs p95 measurement)
    """
    def process():
        return matriz_engine.process("test input")

    result = benchmark.pedantic(process, iterations=100, rounds=10)

    # Assert p95 latency
    assert benchmark.stats.stats.q95 < 0.25  # 250ms


@pytest.mark.performance
@pytest.mark.matriz
def test_memory_throughput_over_50_ops_per_second(memory_system, benchmark):
    """Memory system meets throughput target (50+ ops/sec).

    Performance Target: 50+ operations/second
    Current: ~65 ops/sec average
    """
    def retrieve():
        return memory_system.retrieve(query="test")

    benchmark(retrieve)

    # Calculate ops/sec from mean time
    ops_per_sec = 1 / benchmark.stats.stats.mean
    assert ops_per_sec >= 50


@pytest.mark.performance
def test_api_response_time_p50_under_100ms(api_client, benchmark):
    """API response time meets p50 target (<100ms).

    Performance Target: <100ms p50 (median)
    """
    def make_request():
        return api_client.get("/health")

    result = benchmark.pedantic(make_request, iterations=100, rounds=10)

    # Assert median (p50) response time
    assert benchmark.stats.stats.median < 0.1  # 100ms
```

### Performance Regression Detection

```bash
# Run performance tests with baseline comparison
pytest tests/performance/ --benchmark-autosave --benchmark-compare

# Compare against specific baseline
pytest tests/performance/ --benchmark-compare=0001

# Fail if performance regressed by >10%
pytest tests/performance/ --benchmark-max-time=1.1
```

---

## 8. Continuous Integration Standards

### CI Pipeline Stages

```yaml
# .github/workflows/tests.yml (example)
name: Tests

on: [push, pull_request]

jobs:
  smoke:
    name: Smoke Tests (<10s)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run smoke tests
        run: pytest -m smoke --tb=short
        timeout-minutes: 1

  unit:
    name: Unit Tests (<2min)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run unit tests
        run: pytest -m unit --cov=lukhas --cov=matriz --cov-report=xml
        timeout-minutes: 3
      - name: Upload coverage
        uses: codecov/codecov-action@v4

  integration:
    name: Integration Tests (<5min)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run integration tests
        run: pytest -m integration
        timeout-minutes: 6

  e2e:
    name: E2E Tests (<10min)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run E2E tests
        run: pytest -m e2e
        timeout-minutes: 12
```

### Quality Gates

**Pre-Commit** (local):
- Smoke tests pass (<10s)
- Linters pass (ruff, black, mypy)

**Pre-Push** (local):
- Unit tests pass (<2min)
- Coverage ≥80% for changed files

**Pull Request** (CI):
- Smoke tests pass
- Unit tests pass
- Integration tests pass
- Coverage ≥80% for lukhas/, serve/
- Coverage ≥70% for matriz/
- No security vulnerabilities (bandit)

**Release** (CI):
- All tests pass (smoke + unit + integration + e2e)
- Performance benchmarks within thresholds
- Coverage meets targets
- Security scan clean

---

## 9. Developer Experience (DX)

### Fast Feedback Loops

```bash
# Development workflow (fast iteration)
make test-watch          # Auto-run tests on file changes

# Pre-commit (instant feedback)
pytest -m smoke          # <10 seconds

# Pre-push (quick validation)
pytest -m "smoke or unit"  # <2 minutes

# Pre-PR (full validation)
make test                # Full suite
```

### Test Output Quality

```python
# ✅ GOOD - Clear assertion messages
def test_jwt_token_expires_correctly():
    """JWT token expires after configured duration."""
    token = create_jwt(expires_in=3600)
    time.sleep(3601)

    is_valid = verify_jwt(token)

    assert is_valid is False, (
        f"JWT token should expire after 3600 seconds, "
        f"but is still valid after 3601 seconds. "
        f"Check token expiration logic in lukhas/identity/token_types.py"
    )

# ❌ BAD - Unclear failure
def test_jwt():
    token = create_jwt()
    assert verify_jwt(token) is False
    # Fails with: AssertionError
```

### Test Documentation

```python
def test_matriz_consciousness_ethical_reasoning():
    """MATRIZ consciousness system performs ethical reasoning.

    **Test Scenario:**
    1. User submits potentially harmful query
    2. MATRIZ consciousness processes through ethical reasoning layer
    3. Guardian system evaluates ethical implications
    4. System blocks harmful request and explains reasoning

    **Performance Target:** <250ms p95 latency

    **Related Files:**
    - matriz/consciousness/reflection/ethical_reasoning_system.py:128
    - candidate/governance/guardian/guardian_system.py:245

    **Known Issues:**
    - Ethical reasoning sometimes too conservative (#945)
    - Guardian blocking can be slow for complex scenarios (#1023)
    """
    pass
```

---

## 10. Test Data Management

### Golden File Testing

```python
import pytest
from pathlib import Path

@pytest.fixture
def golden_dir():
    """Directory for golden test files."""
    return Path("tests/fixtures/golden")

def test_matriz_output_matches_golden_file(matriz_engine, golden_dir):
    """MATRIZ output matches expected golden file."""
    input_data = "What is consciousness?"
    result = matriz_engine.process(input_data)

    golden_file = golden_dir / "consciousness_query_response.json"

    # Compare against golden file
    expected = json.loads(golden_file.read_text())
    assert result.output == expected["output"]
    assert result.consciousness_state == expected["consciousness_state"]
```

### Test Data Factories

```python
# tests/fixtures/factories.py
"""Test data factories for generating realistic test data."""

from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class UserFactory:
    """Generate test user data."""

    @staticmethod
    def create(user_id: str = "test-user-123", **overrides) -> Dict[str, Any]:
        """Create test user with sensible defaults."""
        user = {
            "user_id": user_id,
            "email": f"{user_id}@test.lukhas.ai",
            "created_at": "2025-11-09T00:00:00Z",
            "permissions": ["read", "write"],
        }
        user.update(overrides)
        return user


@dataclass
class MATRIZInputFactory:
    """Generate MATRIZ test inputs."""

    @staticmethod
    def create(query: str = "test query", **overrides) -> Dict[str, Any]:
        """Create MATRIZ input with sensible defaults."""
        input_data = {
            "query": query,
            "context": {"user_id": "test-user"},
            "mode": "reasoning",
            "parameters": {"temperature": 0.7, "max_tokens": 1000},
        }
        input_data.update(overrides)
        return input_data

# Usage in tests
def test_matriz_processing(matriz_engine):
    input_data = MATRIZInputFactory.create(
        query="What is consciousness?",
        mode="philosophical_reasoning"
    )
    result = matriz_engine.process(input_data)
    assert result.status == "success"
```

---

## 11. Migration Checklist

### Phase 1: Organization (Week 1)

- [ ] Create new test directory structure
- [ ] Move existing tests to correct pyramid layer
- [ ] Fix 207 collection errors (Python 3.9 compatibility)
- [ ] Standardize test naming conventions
- [ ] Update conftest.py with global fixtures
- [ ] Document test markers and usage

### Phase 2: Critical Coverage (Weeks 2-3)

- [ ] Tier 1 - lukhas/ (11 files → 85%+ coverage)
  - [ ] Batch 1E: Identity & Features
  - [ ] Batch 1F: API & CLI
- [ ] Tier 1 - serve/ (20 files → 85%+ coverage)
  - [ ] Batch 1A: Main API Endpoints
  - [ ] Batch 1B: OpenAI Routes
  - [ ] Batch 1C: Routes & Models
  - [ ] Batch 1D: Middleware

### Phase 3: MATRIZ Coverage (Weeks 4-6)

- [ ] Tier 2 - matriz/ consciousness (top 20 files → 75%+ coverage)
- [ ] Tier 2 - matriz/ memory (top 20 files → 75%+ coverage)
- [ ] Tier 2 - matriz/ core (remaining files → 70%+ coverage)

### Phase 4: Integration & E2E (Weeks 7-8)

- [ ] Build integration test suite (50+ tests)
- [ ] Create E2E user journey tests (20+ tests)
- [ ] Add performance benchmarks (10+ tests)
- [ ] Implement security tests (15+ tests)

### Phase 5: Automation & Reporting (Week 9)

- [ ] Set up Allure reporting
- [ ] Configure Codecov integration
- [ ] Build lukhas.team dashboard
- [ ] Enable automated test analytics

---

## 12. Success Metrics

### Coverage Metrics

- ✅ **90%+ coverage** for lukhas/ (production API)
- ✅ **85%+ coverage** for serve/ (FastAPI routes)
- ✅ **75%+ coverage** for matriz/ (cognitive engine)
- ✅ **60%+ coverage** for core/ (integration layer)

### Performance Metrics

- ✅ **0 collection errors** (all tests can be collected)
- ✅ **<10 seconds** smoke test suite
- ✅ **<2 minutes** unit test suite
- ✅ **<5 minutes** integration test suite
- ✅ **<10 minutes** full E2E suite

### Quality Metrics

- ✅ **Zero flaky tests** (<1% flakiness rate)
- ✅ **Zero skipped tests** (all tests runnable)
- ✅ **100% test pass rate** in main branch
- ✅ **<5% test maintenance burden** (time spent fixing tests vs writing new code)

### Developer Experience Metrics

- ✅ **<1 minute** from commit to smoke test feedback
- ✅ **<5 minutes** from PR to full test results
- ✅ **>90% developer satisfaction** with test suite (survey)

---

## References

- **Pytest Best Practices**: https://pytest-with-eric.com/pytest-best-practices/
- **Google Testing Blog**: https://testing.googleblog.com/
- **Netflix Testing**: https://netflixtechblog.com/testing
- **Microsoft Research**: Testing strategies for ML systems
- **LUKHAS Delegation Guide**: [MISSING_TESTS_DELEGATION_GUIDE.md](../../MISSING_TESTS_DELEGATION_GUIDE.md)

---

**Next Steps**: See [LUKHAS_TEAM_PLATFORM_SPEC.md](LUKHAS_TEAM_PLATFORM_SPEC.md) for visual reporting and developer platform design.
