#!/usr/bin/env python3
"""
Create Jules AI sessions for P0/P1 missions from CLAUDE_CODE_MISSION_PROMPTS.md
High-priority consciousness platform enhancements and safety infrastructure.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


# P0/P1 Mission sessions based on TODO/CLAUDE_CODE_MISSION_PROMPTS.md
MISSION_SESSIONS = [
    {
        "title": "🛡️ P1: Guardian Safety Tag DSL Validation Tests (Mission 4)",
        "prompt": """
**Mission**: Create comprehensive test suite for Guardian constitutional AI safety tag DSL

**Context**:
Guardian uses safety tags (NO_HARM, PRIVACY_PROTECT, CONSENT_REQUIRED) to enforce ethical constraints.
These are the ethical backbone of LUKHAS. Need comprehensive validation tests.

**Files to Create**:
1. tests/unit/lukhas/governance/test_safety_tag_dsl.py (300+ lines)
   - Test safety tag parsing
   - Test policy evaluation
   - Test edge cases (boundary conditions)
   - Test security (injection attempts, bypass attempts)
   - Test performance (tag resolution <10ms)

**Requirements**:
- 50+ tests covering DSL parsing, policy evaluation, edge cases
- Security tests for injection/bypass attempts
- Performance validation (<10ms tag resolution)
- Mock Guardian policies for testing
- Test all safety tag types: NO_HARM, PRIVACY_PROTECT, CONSENT_REQUIRED, NO_DECEPTION

**Success Criteria**:
- 50+ tests pass with 100% coverage of Guardian DSL
- Security tests catch injection attempts
- Performance tests validate <10ms latency
- All edge cases covered (empty tags, invalid syntax, nested policies)

**Import Guidelines**:
- Use `from lukhas.governance.guardian import ...` for Guardian components
- If Guardian DSL doesn't exist, create minimal mock implementation
- Use pytest fixtures for reusable test data
- Use @pytest.mark.security for security tests
""",
        "priority": "P1"
    },
    {
        "title": "📊 P1: Comprehensive Test Coverage for serve/ Module (90%+ target)",
        "prompt": """
**Mission**: Add comprehensive test coverage for serve/ production API module

**Context**:
The serve/ module contains production API endpoints and needs 90%+ test coverage.
This is user-facing infrastructure that must be bulletproof.

**Files to Test**:
- serve/main.py (FastAPI app, endpoints)
- serve/health.py (health checks)
- serve/middleware.py (request/response middleware)
- serve/auth.py (authentication)

**Requirements**:
- Unit tests for each endpoint (200+ tests)
- Integration tests for API workflows
- Auth middleware tests (token validation, expiry)
- Health check tests (startup, liveness, readiness)
- Error handling tests (4xx, 5xx responses)
- 90%+ code coverage target

**Success Criteria**:
- 200+ tests pass covering all serve/ endpoints
- 90%+ code coverage achieved
- All error paths tested
- Auth flows validated
- Health check scenarios covered

**Import Guidelines**:
- Use `from serve import ...` for serve module imports
- Use FastAPI TestClient for API testing
- Mock external dependencies (database, cache)
- Use pytest-asyncio for async tests
""",
        "priority": "P1"
    },
    {
        "title": "🔍 P1: MATRIZ Integration End-to-End Tests",
        "prompt": """
**Mission**: Create end-to-end integration tests for MATRIZ cognitive pipeline

**Context**:
MATRIZ now has complete cognitive nodes (Memory, Attention, Thought, Awareness).
Need integration tests for full cognitive processing workflows.

**Test Coverage Needed**:
1. Full cognitive cycle: Memory → Attention → Thought → Action → Decision → Awareness
2. Performance benchmarks (<250ms p95 end-to-end)
3. Error recovery and fallback behaviors
4. Concurrent processing (multiple streams)
5. State preservation across pipeline stages

**Files to Create**:
- tests/integration/matriz/test_cognitive_pipeline_e2e.py (400+ lines)
- tests/integration/matriz/test_matriz_performance.py (200+ lines)
- tests/integration/matriz/test_matriz_error_recovery.py (200+ lines)

**Requirements**:
- 30+ end-to-end integration tests
- Performance benchmarks with latency tracking
- Error injection and recovery validation
- Concurrent stream processing tests
- State preservation tests

**Success Criteria**:
- All integration tests pass
- <250ms p95 end-to-end latency achieved
- Error recovery works gracefully
- Concurrent processing validated
- No state leakage between streams

**Import Guidelines**:
- Use `from matriz.adapters import ...` for cognitive nodes
- Use `from matriz.orchestration import ...` for pipeline orchestration
- Mock LLM calls for deterministic tests
- Use pytest-benchmark for performance tests
""",
        "priority": "P1"
    },
    {
        "title": "⚡ P1: Performance Benchmarks for Consciousness Stream",
        "prompt": """
**Mission**: Create comprehensive performance benchmarks for 30 FPS consciousness stream

**Context**:
LUKHAS targets 30 FPS consciousness processing with <250ms p95 latency.
Need benchmarks to validate performance across all subsystems.

**Benchmarks Needed**:
1. MATRIZ cognitive pipeline latency
2. Guardian policy evaluation latency
3. Memory retrieval latency
4. Attention mechanism latency
5. End-to-end consciousness frame latency

**Files to Create**:
- tests/performance/bench_consciousness_stream.py
- tests/performance/bench_matriz_nodes.py
- tests/performance/bench_guardian.py
- tests/performance/bench_memory.py

**Requirements**:
- pytest-benchmark integration
- Latency histograms (p50, p95, p99)
- Throughput measurements (frames/second)
- Memory usage profiling
- Performance regression detection

**Success Criteria**:
- <250ms p95 end-to-end latency
- 30+ FPS sustained throughput
- <100MB memory footprint
- Benchmarks run in CI/CD
- Performance regression alerts

**Import Guidelines**:
- Use `pytest-benchmark` for benchmarking
- Use `memory_profiler` for memory tracking
- Profile all critical paths
- Generate performance reports
""",
        "priority": "P1"
    },
    {
        "title": "📚 P2: API Documentation with OpenAPI 3.0 Spec",
        "prompt": """
**Mission**: Create comprehensive OpenAPI 3.0 specification for all LUKHAS APIs

**Context**:
LUKHAS has multiple API surfaces (serve/, matriz/, lukhas/) that need documentation.
OpenAPI spec enables auto-generated docs, client SDKs, and contract testing.

**Files to Create**:
- docs/api/openapi_spec.yaml (1000+ lines)
- docs/api/README.md (API usage guide)
- docs/api/authentication.md (Auth flows)
- docs/api/examples/ (Request/response examples)

**Requirements**:
- OpenAPI 3.0 spec for all endpoints
- Request/response schemas
- Authentication flows documented
- Error response formats
- Rate limiting documentation
- API versioning strategy

**Success Criteria**:
- Complete OpenAPI spec (all endpoints)
- Valid OpenAPI 3.0 schema
- Auto-generated API docs
- Example requests/responses
- Swagger UI integration

**Import Guidelines**:
- Inspect serve/main.py for endpoint definitions
- Extract Pydantic models for schemas
- Document all HTTP methods
- Include authentication headers
""",
        "priority": "P2"
    },
    {
        "title": "🔐 P1: Security Audit Tests for Identity (ΛiD) System",
        "prompt": """
**Mission**: Create security validation tests for ΛiD identity system

**Context**:
ΛiD handles authentication, biometric gates, and zero-knowledge proofs.
Security testing is critical to prevent vulnerabilities.

**Files to Create**:
- tests/security/test_lid_authentication.py
- tests/security/test_lid_biometric_gates.py
- tests/security/test_lid_token_validation.py
- tests/security/test_lid_seed_entropy.py

**Requirements**:
- Authentication bypass attempt tests
- Token tampering/replay attack tests
- Biometric gate security tests
- Seed phrase entropy validation
- GDPR consent validation
- Rate limiting tests

**Success Criteria**:
- 40+ security tests pass
- No authentication bypass possible
- Token tampering detected
- Biometric gates secure
- Seed entropy validated (256+ bits)
- GDPR consent enforced

**Import Guidelines**:
- Use `from lukhas.identity import ...` for ΛiD components
- Test security boundaries
- Attempt common attack vectors
- Validate cryptographic operations
""",
        "priority": "P1"
    },
    {
        "title": "🧪 P2: Chaos Testing for Orchestrator Resilience",
        "prompt": """
**Mission**: Create chaos engineering tests for orchestrator resilience

**Context**:
The orchestrator coordinates async cognitive pipelines and must handle:
- Network failures
- Timeout cascades
- Resource exhaustion
- Partial failures

**Files to Create**:
- tests/chaos/test_orchestrator_network_failures.py
- tests/chaos/test_orchestrator_timeout_cascades.py
- tests/chaos/test_orchestrator_resource_limits.py
- tests/chaos/test_orchestrator_partial_failures.py

**Requirements**:
- Inject network failures (API timeouts)
- Test timeout cascade prevention
- Test memory/CPU limits
- Test partial stage failures
- Validate graceful degradation

**Success Criteria**:
- System degrades gracefully under chaos
- No cascading failures
- Partial results returned
- Metrics track failure modes
- Recovery within 30s

**Import Guidelines**:
- Use `from lukhas.orchestration.timeouts import TimeoutManager`
- Inject failures with mocks
- Test all failure modes
- Validate recovery mechanisms
""",
        "priority": "P2"
    }
]


async def create_sessions():
    """Create all mission sessions"""
    async with JulesClient() as jules:
        source_id = "sources/github/LukhasAI/Lukhas"

        print(f"Creating {len(MISSION_SESSIONS)} Jules sessions for P0/P1 missions...\n")

        created = []
        failed = []

        for idx, session_def in enumerate(MISSION_SESSIONS, 1):
            try:
                print(f"[{idx}/{len(MISSION_SESSIONS)}] Creating: {session_def['title']}")

                session = await jules.create_session(
                    source_id=source_id,
                    prompt=session_def["prompt"],
                    display_name=session_def["title"],
                    automation_mode="AUTO_CREATE_PR"  # Auto-create PRs
                )

                session_id = session.get("id") or session.get("sessionId")
                print(f"  ✅ Created: {session_id}")
                created.append(session_def["title"])

                # Small delay to avoid rate limiting
                await asyncio.sleep(2)

            except Exception as e:
                print(f"  ❌ Failed: {e}")
                failed.append(session_def["title"])

        print(f"\n{'='*70}")
        print(f"SUMMARY:")
        print(f"  Created: {len(created)}/{len(MISSION_SESSIONS)}")
        if failed:
            print(f"  Failed: {len(failed)}")
            for title in failed:
                print(f"    - {title}")
        print(f"{'='*70}\n")

        if created:
            print("✅ Jules sessions created! Monitor at: https://jules.google.com")
            print("\nTo check session status:")
            print("  python3 scripts/check_all_active_jules_sessions.py")

        return created, failed


if __name__ == "__main__":
    created, failed = asyncio.run(create_sessions())

    if failed:
        sys.exit(1)
