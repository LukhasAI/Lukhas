#!/usr/bin/env python3
"""Create additional Jules sessions for remaining test coverage and improvements."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


# Additional high-value test coverage tasks
ADDITIONAL_TASKS = [
    # Core Infrastructure Tests
    {
        "title": "TEST: core/rate_limiter.py comprehensive tests",
        "prompt": """
Create comprehensive test suite for core/rate_limiter.py.

**File**: core/rate_limiter.py
**Test File**: tests/unit/core/test_rate_limiter.py

**Tests Required** (25+ tests):
1. Rate limiting - basic, sliding window, token bucket
2. Multi-user isolation - separate limits per user
3. Reset mechanisms - time-based, manual reset
4. Burst handling - allow bursts, throttle excess
5. Storage backends - in-memory, Redis mock
6. Concurrent requests - thread safety
7. Edge cases - zero limits, negative values, overflow

**Mock external dependencies**:
```python
from unittest.mock import Mock, patch, AsyncMock
@patch('core.rate_limiter.redis_client', return_value=Mock())
def test_rate_limit_redis(mock_redis):
    ...
```

Target: 75%+ coverage
""",
        "time": "4h"
    },
    {
        "title": "TEST: bridge/llm_wrappers/openai_modulated_service.py",
        "prompt": """
Create comprehensive test suite for OpenAI modulated service.

**File**: bridge/llm_wrappers/openai_modulated_service.py
**Test File**: tests/unit/bridge/llm_wrappers/test_openai_modulated_service.py

**Tests Required** (30+ tests):
1. OpenAI API calls - success, errors, timeouts
2. Modulation strategies - temperature, top_p, frequency_penalty
3. Token counting - accurate estimates, budget enforcement
4. Retry logic - exponential backoff, max retries
5. Streaming responses - chunks, completion
6. Error handling - API errors, network errors
7. Rate limiting integration
8. Cost tracking - token costs, API costs

**Mock OpenAI client**:
```python
from unittest.mock import Mock, AsyncMock, patch
@patch('openai.ChatCompletion.create', return_value=Mock())
async def test_openai_call(mock_create):
    ...
```

Target: 75%+ coverage
""",
        "time": "5h"
    },
    {
        "title": "TEST: lukhas/api/auth_helpers.py authentication",
        "prompt": """
Create comprehensive test suite for authentication helpers.

**File**: lukhas/api/auth_helpers.py
**Test File**: tests/unit/lukhas/api/test_auth_helpers.py

**Tests Required** (30+ tests):
1. JWT token validation - valid, expired, invalid signature
2. API key verification - valid, invalid, revoked
3. User authentication - success, failure, locked accounts
4. Role checking - admin, user, guest permissions
5. Token refresh - success, invalid refresh token
6. Multi-factor authentication - if implemented
7. Rate limiting per user
8. Security edge cases - SQL injection, XSS attempts

**Mock JWT and crypto**:
```python
from unittest.mock import Mock, patch
import jwt
@patch('jwt.decode', return_value={'user_id': 'test', 'role': 'admin'})
def test_jwt_decode(mock_decode):
    ...
```

Target: 75%+ coverage
""",
        "time": "5h"
    },
    # MATRIZ Engine Tests
    {
        "title": "TEST: matriz/core/orchestrator.py",
        "prompt": """
Create comprehensive test suite for MATRIZ orchestrator.

**File**: matriz/core/orchestrator.py
**Test File**: tests/unit/matriz/core/test_orchestrator.py

**Tests Required** (35+ tests):
1. Node orchestration - creation, execution, cleanup
2. Workflow execution - success, partial failure, rollback
3. State management - persistence, recovery
4. Error handling - node failures, timeout handling
5. Concurrency - parallel execution, race conditions
6. Resource management - memory limits, CPU throttling
7. Event broadcasting - subscribers, message delivery
8. Performance - latency < 250ms, throughput > 50 ops/sec

**Mock dependencies**:
```python
from unittest.mock import Mock, AsyncMock, patch
@patch('matriz.core.orchestrator.NodeManager')
async def test_orchestrate_workflow(mock_manager):
    ...
```

Target: 75%+ coverage
""",
        "time": "6h"
    },
    {
        "title": "TEST: matriz/cognitive_dna/symbolic_dna.py",
        "prompt": """
Create comprehensive test suite for symbolic DNA.

**File**: matriz/cognitive_dna/symbolic_dna.py
**Test File**: tests/unit/matriz/cognitive_dna/test_symbolic_dna.py

**Tests Required** (30+ tests):
1. DNA creation - from schema, from dict, validation
2. Gene expression - symbolic operations, mutations
3. Inheritance - parent DNA, gene mixing
4. Evolution - fitness evaluation, selection
5. Serialization - to/from JSON, to/from proto
6. Performance - large DNA structures, deep nesting
7. Edge cases - invalid genes, circular references

**Test symbolic operations**:
```python
def test_dna_mutation():
    dna = SymbolicDNA(genes={'capability': 'test'})
    mutated = dna.mutate(rate=0.1)
    assert mutated.genes != dna.genes
```

Target: 75%+ coverage
""",
        "time": "5h"
    },
    # Memory System Tests
    {
        "title": "TEST: labs/consciousness/reflection/unified_memory_manager.py",
        "prompt": """
Create comprehensive test suite for unified memory manager.

**File**: labs/consciousness/reflection/unified_memory_manager.py
**Test File**: tests/unit/memory/test_unified_memory_manager.py

**Tests Required** (35+ tests):
1. Memory storage - store, retrieve, update, delete
2. User isolation - cross-user access prevention
3. Memory search - semantic search, keyword search
4. Memory consolidation - merge similar memories
5. Forgetting - decay, pruning old memories
6. Memory types - episodic, semantic, procedural
7. Context preservation - conversation context
8. Performance - retrieval < 50ms, storage < 100ms

**Mock storage backend**:
```python
from unittest.mock import Mock, AsyncMock, patch
@patch('memory.storage.VectorDB')
async def test_memory_storage(mock_db):
    mock_db.return_value.search = AsyncMock(return_value=[])
    ...
```

Target: 75%+ coverage
""",
        "time": "6h"
    },
    # API Endpoint Tests
    {
        "title": "TEST: serve/openai_routes.py comprehensive tests",
        "prompt": """
Create comprehensive test suite for OpenAI API routes.

**File**: serve/openai_routes.py
**Test File**: tests/unit/serve/test_openai_routes.py

**Tests Required** (40+ tests):
1. Chat completions - success, streaming, errors
2. Embeddings generation - success, batch processing
3. Authentication - JWT, API keys, missing auth
4. Rate limiting - per user, per endpoint
5. Input validation - max tokens, invalid models
6. Error responses - 400, 401, 403, 429, 500
7. Modulation - temperature, top_p adjustments
8. Cost tracking - token usage, billing
9. Streaming responses - SSE format, disconnection handling

**Mock OpenAI service**:
```python
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

@patch('serve.openai_routes.OpenAIModulatedService')
def test_chat_completion(mock_service):
    mock_service.return_value.chat = AsyncMock(return_value={'response': 'test'})
    ...
```

Target: 75%+ coverage
""",
        "time": "6h"
    },
    {
        "title": "TEST: serve/consciousness_routes.py",
        "prompt": """
Create comprehensive test suite for consciousness API routes.

**File**: serve/consciousness_routes.py
**Test File**: tests/unit/serve/test_consciousness_routes.py

**Tests Required** (35+ tests):
1. Consciousness query endpoints - success, validation
2. State management - save, retrieve, update
3. Context submission - large contexts, streaming
4. Authentication and authorization
5. Rate limiting per user
6. Error handling - timeouts, invalid input
7. User isolation - cross-user state protection
8. Performance - response time < 500ms

**Mock consciousness engine**:
```python
from unittest.mock import AsyncMock, patch
@patch('serve.consciousness_routes.ConsciousnessEngine')
async def test_consciousness_query(mock_engine):
    mock_engine.return_value.process = AsyncMock(return_value={'state': 'active'})
    ...
```

Target: 75%+ coverage
""",
        "time": "5h"
    },
    # Bio-inspired Systems Tests
    {
        "title": "TEST: candidate/bio/ comprehensive module tests",
        "prompt": """
Create comprehensive test suites for bio-inspired modules.

**Files to Test**:
- candidate/bio/adaptation_engine.py
- candidate/bio/evolution_optimizer.py
- candidate/bio/neural_plasticity.py

**Test Files**:
- tests/unit/candidate/bio/test_adaptation_engine.py (20 tests)
- tests/unit/candidate/bio/test_evolution_optimizer.py (20 tests)
- tests/unit/candidate/bio/test_neural_plasticity.py (20 tests)

**Tests Required** (60+ total):

**Adaptation Engine**:
1. Environmental sensing and response
2. Fitness evaluation
3. Adaptation strategies - gradual, rapid
4. Homeostasis maintenance

**Evolution Optimizer**:
1. Population management
2. Selection strategies - tournament, roulette
3. Crossover and mutation operations
4. Convergence detection

**Neural Plasticity**:
1. Weight adaptation - Hebbian learning
2. Pruning strategies
3. Growth mechanisms
4. Stability-plasticity balance

Target: 75%+ coverage per module
""",
        "time": "8h"
    },
    # Integration Tests
    {
        "title": "INTEGRATION: End-to-end dream generation flow",
        "prompt": """
Create end-to-end integration test for dream generation workflow.

**Test File**: tests/integration/test_dream_generation_e2e.py

**Tests Required** (15+ tests):
1. Full dream generation pipeline:
   - User authentication → API request → Dream engine → Response
2. Multi-user concurrent dreams - no cross-contamination
3. Dream retrieval and history
4. Error recovery - engine failure, timeout
5. Performance under load - 10 concurrent users
6. State persistence across requests

**Test full stack**:
```python
import pytest
from fastapi.testclient import TestClient
from serve.main import app

@pytest.mark.integration
async def test_dream_generation_e2e():
    client = TestClient(app)

    # Authenticate
    auth_response = client.post('/auth/login', json={'user': 'test'})
    token = auth_response.json()['token']

    # Generate dream
    dream_response = client.post(
        '/api/v1/dreams/simulate',
        headers={'Authorization': f'Bearer {token}'},
        json={'symbols': ['test'], 'depth': 2}
    )

    assert dream_response.status_code == 200
    dream_id = dream_response.json()['dream_id']

    # Retrieve dream
    retrieve_response = client.get(
        f'/api/v1/dreams/{dream_id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert retrieve_response.status_code == 200
```

Target: Complete end-to-end validation
""",
        "time": "5h"
    },
    {
        "title": "INTEGRATION: MATRIZ cognitive pipeline test",
        "prompt": """
Create end-to-end integration test for MATRIZ cognitive pipeline.

**Test File**: tests/integration/test_matriz_cognitive_pipeline.py

**Tests Required** (20+ tests):
1. Complete MATRIZ cycle: Input → Attention → Thought → Action → Decision
2. Multi-node orchestration
3. State preservation across steps
4. Error propagation and recovery
5. Performance validation - < 250ms p95 latency
6. Throughput validation - > 50 ops/sec
7. Memory efficiency - < 100MB per operation

**Test cognitive pipeline**:
```python
import pytest
from matriz.core.orchestrator import Orchestrator
from matriz.cognitive_dna.symbolic_dna import SymbolicDNA

@pytest.mark.integration
async def test_matriz_cognitive_pipeline():
    orchestrator = Orchestrator()
    dna = SymbolicDNA(genes={'capability': 'reasoning'})

    result = await orchestrator.execute_cognitive_cycle(
        input_data={'query': 'test'},
        dna=dna
    )

    assert result['attention'] is not None
    assert result['thought'] is not None
    assert result['action'] is not None
    assert result['decision'] is not None
    assert result['latency_ms'] < 250
```

Target: Complete cognitive cycle validation
""",
        "time": "6h"
    },
    # Security & Performance Tests
    {
        "title": "SECURITY: Comprehensive security audit tests",
        "prompt": """
Create comprehensive security test suite.

**Test File**: tests/security/test_security_audit.py

**Tests Required** (40+ tests):
1. Authentication bypass attempts
2. Authorization escalation attempts
3. SQL injection prevention
4. XSS prevention
5. CSRF protection
6. Rate limiting effectiveness
7. Input validation - all endpoints
8. Secure headers - HSTS, CSP, etc.
9. Token security - JWT expiry, refresh
10. API key security - rotation, revocation
11. Cross-user data isolation
12. Sensitive data exposure prevention

**Security testing patterns**:
```python
import pytest
from fastapi.testclient import TestClient

@pytest.mark.security
def test_sql_injection_prevention():
    client = TestClient(app)

    # Attempt SQL injection
    response = client.get('/api/users?id=1 OR 1=1')
    assert response.status_code == 400  # Should reject

@pytest.mark.security
def test_auth_bypass_attempt():
    client = TestClient(app)

    # Attempt to access protected endpoint without auth
    response = client.get('/api/v1/dreams/123')
    assert response.status_code == 401
```

Target: 100% security vulnerability coverage
""",
        "time": "6h"
    },
    {
        "title": "PERFORMANCE: Load testing and benchmarks",
        "prompt": """
Create comprehensive performance and load testing suite.

**Test File**: tests/performance/test_load_benchmarks.py

**Tests Required** (25+ tests):
1. API endpoint latency - p50, p95, p99
2. Throughput under load - requests per second
3. Concurrent user handling - 10, 50, 100 users
4. Database query performance
5. Memory usage under load
6. CPU utilization patterns
7. Response time degradation curves
8. Rate limiter performance
9. Cache hit/miss ratios
10. WebSocket connection limits

**Performance testing**:
```python
import pytest
import asyncio
from locust import HttpUser, task, between

class LoadTestUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def test_dream_generation(self):
        self.client.post(
            '/api/v1/dreams/simulate',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'symbols': ['test'], 'depth': 2}
        )

@pytest.mark.performance
async def test_api_latency():
    # Benchmark API response times
    times = []
    for _ in range(100):
        start = time.time()
        await call_api()
        times.append(time.time() - start)

    assert np.percentile(times, 95) < 0.250  # p95 < 250ms
```

Target: Complete performance validation
""",
        "time": "6h"
    },
]


async def create_additional_sessions():
    """Create additional Jules sessions."""
    async with JulesClient() as jules:
        source_id = "sources/github/LukhasAI/Lukhas"

        print(f"Creating {len(ADDITIONAL_TASKS)} additional test sessions...\\n")
        print("="*70)

        created_sessions = []

        for idx, task in enumerate(ADDITIONAL_TASKS, 1):
            print(f"\\n[{idx}/{len(ADDITIONAL_TASKS)}] {task['title']}")
            print(f"Estimated time: {task['time']}")

            try:
                session = await jules.create_session(
                    prompt=task["prompt"],
                    source_id=source_id,
                    display_name=task["title"],
                    automation_mode="AUTO_CREATE_PR",
                    require_plan_approval=False  # Auto-approve
                )

                session_id = session.get("name", "").split("/")[-1]
                created_sessions.append({
                    "id": session_id,
                    "title": task["title"],
                    "time": task["time"]
                })

                print(f"  ✅ Session created: {session_id}")
                print(f"  URL: https://jules.google.com/session/{session_id}")

            except Exception as e:
                print(f"  ❌ Error: {e}")
                if "429" in str(e):
                    print("  ⏸️  Rate limit hit - waiting 60 seconds...")
                    await asyncio.sleep(60)
                    # Retry once
                    try:
                        session = await jules.create_session(
                            prompt=task["prompt"],
                            source_id=source_id,
                            display_name=task["title"],
                            automation_mode="AUTO_CREATE_PR",
                            require_plan_approval=False
                        )
                        session_id = session.get("name", "").split("/")[-1]
                        created_sessions.append({
                            "id": session_id,
                            "title": task["title"],
                            "time": task["time"]
                        })
                        print(f"  ✅ Retry successful: {session_id}")
                    except Exception as retry_error:
                        print(f"  ❌ Retry failed: {retry_error}")

        print("\\n" + "="*70)
        print(f"\\n✅ Created {len(created_sessions)} additional test sessions!")

        total_hours = sum(int(s["time"].rstrip("h")) for s in created_sessions)
        print(f"Total estimated work: {total_hours} hours")
        print(f"Expected deliverables:")
        print(f"  - 400+ comprehensive tests")
        print(f"  - 13 test suites")
        print(f"  - 75%+ coverage across core systems")
        print(f"  - Security and performance validation")

        return created_sessions


if __name__ == "__main__":
    asyncio.run(create_additional_sessions())
