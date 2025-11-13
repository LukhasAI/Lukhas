#!/usr/bin/env python3
"""
Create Jules sessions with conservative rate limiting (2-5 min delays).

Usage:
  python3.11 scripts/create_jules_sessions_slow.py

This script respects Jules' aggressive rate limits by waiting 3 minutes between each session creation.
Estimated time for 5 sessions: ~15 minutes
"""

import asyncio
import sys
from datetime import datetime

sys.path.insert(0, '/Users/agi_dev/LOCAL-REPOS/Lukhas')

from bridge.llm_wrappers.jules_wrapper import JulesClient

# High-priority tasks for batch 2
TASKS = [
    {
        "name": "[IDENTITY] Complete test coverage for lukhas/identity/",
        "prompt": """# Task: Comprehensive Test Coverage for lukhas/identity/

## 🎯 Goal
Achieve 90%+ test coverage for the entire lukhas/identity/ module including:
- lid_manager.py (ΛiD system core)
- auth_service.py (authentication)
- credential_store.py (credential management)
- session_manager.py (session handling)

## 📚 LUKHAS Context
- Lane: lukhas/ (production lane)
- Import Rules: Can import from core/, matriz/, universal_language/
- Constellation Star: ⚛️ Identity (authentication, ΛiD, secure access)

## ✅ Requirements
1. Unit tests for all public methods (pytest with asyncio support)
2. Integration tests for auth flows (token generation, validation, refresh)
3. Mock external dependencies (Redis, secrets manager)
4. Test edge cases and error handling
5. Security testing (token validation, injection prevention, timing attacks)

## 📝 Test Files to Create/Enhance
```
tests/unit/lukhas/identity/
├── test_lid_manager.py         # ΛiD core operations
├── test_auth_service.py        # Authentication flows
├── test_credential_store.py    # Credential management
└── test_session_manager.py     # Session handling

tests/integration/lukhas/identity/
└── test_auth_flows.py          # End-to-end auth workflows
```

## 🎯 Acceptance Criteria
- [ ] 90%+ line coverage for lukhas/identity/
- [ ] All critical auth paths tested (login, logout, token refresh, validation)
- [ ] Security edge cases covered (expired tokens, invalid signatures, replay attacks)
- [ ] Async tests properly structured with pytest-asyncio
- [ ] All tests pass with pytest -v tests/unit/lukhas/identity/
"""
    },
    {
        "name": "[SECURITY] API security hardening & penetration tests",
        "prompt": """# Task: API Security Hardening & Penetration Tests

## 🎯 Goal
Create security-focused tests for lukhas/api/:
- Authentication bypass attempts
- Authorization boundary tests
- Input validation (XSS, SQL injection, command injection)
- Rate limiting enforcement
- CORS policy validation

## 📚 LUKHAS Context
- Module: lukhas/api/ (public API surface)
- Critical: External attack surface - must be secure
- Lane: Production (lukhas/)
- Framework: FastAPI with JWT authentication

## ✅ Requirements
1. **Authentication/Authorization Tests**
   - Token tampering attempts
   - Missing/invalid authorization headers
   - Expired token handling
   - Role-based access control (RBAC) violations

2. **Input Validation Tests (OWASP Top 10)**
   - XSS attempts in JSON payloads
   - SQL injection patterns (parameterized queries)
   - Command injection via user inputs
   - Path traversal attempts
   - Mass assignment vulnerabilities

3. **Rate Limiting Tests**
   - Verify rate limits enforced per endpoint
   - Test different rate limit tiers
   - Verify 429 responses

4. **CORS Policy Tests**
   - Verify allowed origins
   - Test preflight requests
   - Validate headers

## 📝 Test Files to Create
```
tests/security/api/
├── test_authentication_bypass.py    # Auth bypass attempts
├── test_input_validation.py         # OWASP Top 10 input tests
├── test_authorization_boundaries.py # RBAC and permission tests
└── test_rate_limiting.py            # Rate limit enforcement
```

## 🎯 Acceptance Criteria
- [ ] All OWASP Top 10 categories tested
- [ ] No authentication bypass possible
- [ ] Input sanitization verified for all endpoints
- [ ] Rate limits enforced correctly
- [ ] CORS policies validated
- [ ] All security tests pass
"""
    },
    {
        "name": "[GUARDIAN] Comprehensive contract enforcement tests",
        "prompt": """# Task: Guardian Constitutional AI Contract Tests

## 🎯 Goal
Create comprehensive tests for the Guardian system's contract enforcement:
- Contract parsing and validation
- Ethical violation detection
- Multi-contract priority handling
- Audit trail generation

## 📚 LUKHAS Context
- Module: lukhas/governance/guardian/
- Constellation Star: 🛡️ Guardian (constitutional AI, ethical enforcement)
- Critical: Production safety system - must never fail

## ✅ Requirements
1. **Contract Testing**
   - Test all 5 default contracts:
     * harm_prevention
     * manipulation_prevention
     * autonomy_preservation
     * transparency_requirement
     * accountability_enforcement
   - Custom contract creation and validation
   - Contract syntax validation
   - Contract priority ordering

2. **Violation Detection**
   - Detect violations in real-time
   - Multi-contract conflict resolution
   - Severity level handling (info, warning, critical)
   - Audit trail completeness

3. **Performance Testing**
   - Contract checks <10ms (critical SLO)
   - Concurrent violation detection
   - Memory usage under load

## 📝 Test Files to Create
```
tests/unit/lukhas/governance/guardian/
├── test_contract_engine.py          # Contract parsing and execution
├── test_violation_detector.py       # Violation detection logic
└── test_audit_trail.py              # Audit trail completeness

tests/integration/lukhas/governance/guardian/
└── test_multi_contract.py           # Multi-contract scenarios
```

## 🎯 Acceptance Criteria
- [ ] 90%+ coverage for guardian/
- [ ] All 5 default contracts tested
- [ ] Conflict resolution verified
- [ ] Performance: contract checks <10ms
- [ ] Audit trail complete and queryable
- [ ] All tests pass
"""
    },
    {
        "name": "[MEMORY] Comprehensive memory system test coverage",
        "prompt": """# Task: Comprehensive Memory System Test Coverage

## 🎯 Goal
Achieve 85%+ coverage for lukhas/memory/ including:
- memory_manager.py (core memory operations)
- recall_engine.py (retrieval)
- consolidation.py (memory strengthening)
- forgetting_engine.py (decay)

## 📚 LUKHAS Context
- Module: lukhas/memory/
- Constellation Star: ✦ Memory (persistent state, context preservation)
- SLO: <100ms recall latency (critical)
- Architecture: Fold-based memory with hierarchical organization

## ✅ Requirements
1. **Memory Operations Testing**
   - Store: save memories with metadata
   - Recall: retrieve by ID, tag, timestamp
   - Update: modify existing memories
   - Forget: decay and deletion

2. **Integration Tests**
   - Full memory lifecycle (store → consolidate → recall → forget)
   - Multi-fold memory organization
   - Temporal memory patterns

3. **Performance Tests**
   - Recall latency <100ms (SLO verification)
   - Concurrent access safety
   - Memory capacity limits

4. **Edge Cases**
   - Empty memory store
   - Duplicate memory handling
   - Invalid memory IDs
   - Race conditions in concurrent access

## 📝 Test Files to Create
```
tests/unit/lukhas/memory/
├── test_memory_manager.py      # Core memory operations
├── test_recall_engine.py       # Retrieval logic
├── test_consolidation.py       # Memory strengthening
└── test_forgetting.py          # Decay and deletion

tests/integration/lukhas/memory/
└── test_memory_lifecycle.py    # Full lifecycle tests
```

## 🎯 Acceptance Criteria
- [ ] 85%+ coverage for lukhas/memory/
- [ ] <100ms recall latency verified
- [ ] Concurrent access safe (no race conditions)
- [ ] Memory limits tested (capacity enforcement)
- [ ] All lifecycle stages tested
- [ ] All tests pass
"""
    },
    {
        "name": "[MATRIZ] Performance & load tests for cognitive pipeline",
        "prompt": """# Task: MATRIZ Pipeline Performance & Load Tests

## 🎯 Goal
Create comprehensive performance tests for the MATRIZ cognitive pipeline to verify:
- <250ms p95 latency target
- <100MB memory footprint
- 50+ ops/sec throughput
- Concurrent request handling

## 📚 LUKHAS Context
- Module: matriz/ (MATRIZ cognitive engine)
- Components: Memory-Attention-Thought-Risk-Intent-Action processing
- Performance Targets: Critical system SLOs (production requirements)

## ✅ Requirements
1. **Latency Benchmarks**
   - Measure each pipeline stage (M, A, T, R, I, A)
   - Aggregate pipeline latency
   - p50, p95, p99 percentiles
   - Verify <250ms p95 target

2. **Memory Profiling**
   - Track memory usage during processing
   - Detect memory leaks
   - Verify <100MB footprint

3. **Throughput Tests**
   - Measure ops/sec under load
   - Test concurrent request handling
   - Verify 50+ ops/sec target

4. **Resource Leak Detection**
   - File descriptor leaks
   - Connection pool exhaustion
   - Memory growth over time

## 📝 Test Files to Create
```
tests/performance/matriz/
├── test_pipeline_performance.py     # Latency benchmarks
├── test_memory_profiling.py         # Memory usage tests
└── test_concurrent_processing.py    # Load tests

tests/load/matriz/
└── test_sustained_load.py           # Long-running load tests
```

## 🎯 Acceptance Criteria
- [ ] Performance tests verify all SLO targets:
  * p95 latency <250ms
  * Memory <100MB
  * Throughput >50 ops/sec
- [ ] Load tests handle 100+ concurrent requests
- [ ] Memory profiling shows no leaks
- [ ] Benchmark baseline established for regressions
- [ ] All tests documented with results
"""
    },
]

DELAY_SECONDS = 180  # 3 minutes between sessions

async def create_sessions_with_delays():
    """Create Jules sessions with 3-minute delays to respect rate limits."""

    start_time = datetime.now()

    async with JulesClient() as jules:
        # Get source ID
        sources = await jules.list_sources()
        source_id = None
        for source in sources:
            display_name = getattr(source, 'display_name', '') or ''
            if 'Lukhas' in display_name or 'Lukhas' in source.name:
                source_id = source.name
                break

        if not source_id:
            print("❌ Could not find Lukhas source")
            return

        print(f"✅ Found source: {source_id}\n")
        print("🚀 Creating Jules Sessions (Conservative Rate Limiting)")
        print("="*70)
        print(f"⏰ {DELAY_SECONDS}s ({DELAY_SECONDS/60:.1f} min) delay between sessions")
        print(f"📊 Total tasks: {len(TASKS)}")
        print(f"⌛ Estimated time: ~{(len(TASKS)-1) * DELAY_SECONDS / 60:.0f} minutes\n")

        sessions = []

        for i, task in enumerate(TASKS, 1):
            try:
                current_time = datetime.now()
                elapsed = (current_time - start_time).total_seconds() / 60

                print(f"[{i}/{len(TASKS)}] [{elapsed:.1f}min elapsed] Creating: {task['name'][:50]}...")

                session = await jules.create_session(
                    prompt=task['prompt'],
                    source_id=source_id,
                    automation_mode="AUTO_CREATE_PR",
                    display_name=task['name']
                )

                session_id = session.get('name', '').split('/')[-1]
                session_url = f"https://jules.google.com/session/{session_id}"

                print(f"✅ Created: {session_id}")
                print(f"   URL: {session_url}")
                sessions.append(session)

                if i < len(TASKS):
                    next_time = datetime.now()
                    next_time = next_time.replace(second=next_time.second + DELAY_SECONDS)
                    print(f"⏳ Waiting {DELAY_SECONDS}s until {next_time.strftime('%H:%M:%S')}...\n")
                    await asyncio.sleep(DELAY_SECONDS)

            except Exception as e:
                error_str = str(e)
                print(f"❌ Error creating session {i}: {error_str[:100]}")

                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    wait_time = DELAY_SECONDS * 2  # Double the wait on rate limit
                    print(f"⏸️  Rate limit hit - waiting {wait_time}s ({wait_time/60:.1f} min)...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"⏸️  Error - waiting {DELAY_SECONDS}s before retry...")
                    await asyncio.sleep(DELAY_SECONDS)

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() / 60

        print("\n" + "="*70)
        print("✅ Session Creation Complete!")
        print(f"   Created: {len(sessions)}/{len(TASKS)} sessions")
        print(f"   Total time: {total_time:.1f} minutes")
        print("\n📊 Session IDs:")
        for i, s in enumerate(sessions, 1):
            session_id = s.get('name', '').split('/')[-1]
            task_name = TASKS[i-1]['name']
            print(f"   {i}. {session_id} - {task_name[:50]}")

        return sessions

if __name__ == "__main__":
    print(f"Starting at {datetime.now().strftime('%H:%M:%S')}")
    asyncio.run(create_sessions_with_delays())
    print(f"\nFinished at {datetime.now().strftime('%H:%M:%S')}")
