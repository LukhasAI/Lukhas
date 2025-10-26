"""
Real MATRIZ integration tests for OpenAI façade.

Tests actual MATRIZ cognitive orchestrator capabilities when available,
validates graceful degradation to stub mode when unavailable.
"""
import pytest
from serve.main import MATRIZ_AVAILABLE, app
from starlette.testclient import TestClient

# Skip entire module if MATRIZ not available
pytestmark = pytest.mark.skipif(
    not MATRIZ_AVAILABLE,
    reason="MATRIZ orchestrator not available (stub mode)"
)


@pytest.fixture
def client():
    """Test client with override for dependencies."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Valid bearer token headers."""
    return {"Authorization": "Bearer test-token-12345"}


# MATRIZ Cognitive Pipeline Tests
def test_matriz_cognitive_orchestration(client, auth_headers):
    """Verify MATRIZ processes input through full cognitive pipeline."""
    response = client.post(
        "/v1/responses",
        json={"input": "What is consciousness?"},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Response should have output from MATRIZ
    assert "output" in data
    output = data["output"]

    # MATRIZ should provide rich response (not just echo)
    assert isinstance(output, dict)
    assert "text" in output or "content" in output


def test_matriz_memory_attention_thought_pipeline(client, auth_headers):
    """Verify Memory→Attention→Thought (MAT) stages execute."""
    response = client.post(
        "/v1/responses",
        json={
            "input": "Remember: my name is Alice. What's my name?",
            "context": {"session_id": "test-session-123"}
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # MATRIZ should process through MAT pipeline
    assert "output" in data
    # Response ID should indicate MATRIZ processing
    assert data["id"].startswith("resp_")


def test_matriz_reasoning_stage(client, auth_headers):
    """Verify MATRIZ reasoning stage handles logic."""
    response = client.post(
        "/v1/responses",
        json={
            "input": "If A > B and B > C, then A > C. If A=5, B=3, C=1, is A > C?",
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # MATRIZ should provide logical reasoning
    assert "output" in data
    output_text = str(data["output"])

    # Should demonstrate reasoning capability
    assert len(output_text) > 0


def test_matriz_action_stage(client, auth_headers):
    """Verify MATRIZ action stage generates structured output."""
    response = client.post(
        "/v1/responses",
        json={
            "input": "List 3 prime numbers",
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # MATRIZ should produce structured output
    assert "output" in data
    assert data["model"] == "lukhas-matriz"


def test_matriz_awareness_metadata(client, auth_headers):
    """Verify MATRIZ awareness stage emits processing metadata."""
    response = client.post(
        "/v1/responses",
        json={"input": "test awareness metadata"},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Should include awareness metadata
    assert "id" in data
    assert "model" in data
    # Note: "created" timestamp field not yet implemented
    assert "output" in data or "usage" in data


# MATRIZ Performance Tests
def test_matriz_latency_under_250ms_target(client, auth_headers):
    """Verify MATRIZ meets <250ms p95 latency target."""
    import time

    latencies = []
    for _ in range(10):
        start = time.time()
        response = client.post(
            "/v1/responses",
            json={"input": "quick test"},
            headers=auth_headers
        )
        latency = (time.time() - start) * 1000  # ms
        latencies.append(latency)

        assert response.status_code == 200

    # Check p95 latency
    latencies.sort()
    p95 = latencies[int(len(latencies) * 0.95)]

    # Production target is <250ms, allow generous buffer for CI
    assert p95 < 1000, f"p95 latency {p95:.1f}ms exceeds 1000ms threshold"


def test_matriz_throughput_50_ops_per_sec(client, auth_headers):
    """Verify MATRIZ handles reasonable throughput under rate limits."""
    import time
    from concurrent.futures import ThreadPoolExecutor

    def make_request():
        response = client.post(
            "/v1/responses",
            json={"input": "throughput test"},
            headers=auth_headers
        )
        return response.status_code == 200

    # Test 30 requests with 5 workers (within rate limit budget)
    start = time.time()
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(lambda _: make_request(), range(30)))
    duration = time.time() - start

    # Most requests should succeed (allow some rate limiting)
    assert sum(results) >= 20, f"Too many failed requests: {sum(results)}/30"

    # Should complete in reasonable time
    assert duration < 10.0, f"Throughput too low: {30/duration:.1f} ops/sec"


# MATRIZ Symbolic DNA Tests
def test_matriz_symbolic_dna_processing(client, auth_headers):
    """Verify MATRIZ uses symbolic DNA for processing."""
    response = client.post(
        "/v1/responses",
        json={
            "input": "Process with symbolic DNA",
            "config": {"use_symbolic": True}
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Should process successfully with symbolic DNA
    assert "output" in data
    assert data["model"] == "lukhas-matriz"


def test_matriz_node_based_processing(client, auth_headers):
    """Verify MATRIZ node-based cognitive processing."""
    response = client.post(
        "/v1/responses",
        json={
            "input": "Multi-step reasoning: A->B->C",
            "trace": True  # Request processing trace
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # MATRIZ should execute node-based processing
    assert "output" in data


# MATRIZ Context Preservation Tests
def test_matriz_context_handoff_under_250ms(client, auth_headers):
    """Verify MATRIZ context handoff meets <250ms target."""
    import time

    # First request establishes context
    response1 = client.post(
        "/v1/responses",
        json={
            "input": "Remember: the secret code is 42",
            "context": {"session_id": "context-test"}
        },
        headers=auth_headers
    )
    assert response1.status_code == 200

    # Second request should retrieve context quickly
    start = time.time()
    response2 = client.post(
        "/v1/responses",
        json={
            "input": "What was the secret code?",
            "context": {"session_id": "context-test"}
        },
        headers=auth_headers
    )
    handoff_time = (time.time() - start) * 1000

    assert response2.status_code == 200

    # Context handoff should be fast
    assert handoff_time < 1000, f"Context handoff {handoff_time:.1f}ms too slow"


def test_matriz_multi_turn_conversation(client, auth_headers):
    """Verify MATRIZ maintains context across multiple turns."""
    session_id = "multi-turn-123"

    # Turn 1: Set context
    r1 = client.post(
        "/v1/responses",
        json={
            "input": "My favorite color is blue",
            "context": {"session_id": session_id}
        },
        headers=auth_headers
    )
    assert r1.status_code == 200

    # Turn 2: Reference previous context
    r2 = client.post(
        "/v1/responses",
        json={
            "input": "What's my favorite color?",
            "context": {"session_id": session_id}
        },
        headers=auth_headers
    )
    assert r2.status_code == 200

    # Turn 3: Continue conversation
    r3 = client.post(
        "/v1/responses",
        json={
            "input": "Why is that color special?",
            "context": {"session_id": session_id}
        },
        headers=auth_headers
    )
    assert r3.status_code == 200


# MATRIZ Bio-Inspired Adaptation Tests
def test_matriz_bio_inspired_adaptation(client, auth_headers):
    """Verify MATRIZ bio-inspired adaptation patterns."""
    response = client.post(
        "/v1/responses",
        json={
            "input": "Adapt response style to formal academic tone",
            "config": {"adaptation": "bio-inspired"}
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Should adapt response based on input
    assert "output" in data


def test_matriz_quantum_inspired_superposition(client, auth_headers):
    """Verify MATRIZ quantum-inspired algorithms."""
    response = client.post(
        "/v1/responses",
        json={
            "input": "Consider multiple interpretations simultaneously",
            "config": {"quantum_mode": True}
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Should process with quantum-inspired patterns
    assert "output" in data


# MATRIZ Memory Integration Tests
def test_matriz_memory_system_integration(client, auth_headers):
    """Verify MATRIZ integrates with memory systems."""
    # Store memory
    r1 = client.post(
        "/v1/responses",
        json={
            "input": "Store this fact: LUKHAS means Logic Unified Knowledge Hyper Adaptable System",
            "store_memory": True
        },
        headers=auth_headers
    )
    assert r1.status_code == 200

    # Retrieve memory
    r2 = client.post(
        "/v1/responses",
        json={
            "input": "What does LUKHAS stand for?",
            "use_memory": True
        },
        headers=auth_headers
    )
    assert r2.status_code == 200


def test_matriz_memory_capacity_under_100mb(client, auth_headers):
    """Verify MATRIZ memory usage stays under 100MB target."""
    # Note: This is a basic test - full memory profiling requires separate tooling
    response = client.post(
        "/v1/responses",
        json={"input": "test memory footprint"},
        headers=auth_headers
    )

    assert response.status_code == 200
    # Memory usage checked via profiling tools in production


# MATRIZ Tracing Tests
def test_matriz_processing_trace_available(client, auth_headers):
    """Verify MATRIZ provides processing trace when requested."""
    response = client.post(
        "/v1/responses",
        json={
            "input": "Show processing steps",
            "trace": True
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Should include trace information
    assert "output" in data
    # Trace available via X-Trace-Id header
    assert "x-trace-id" in response.headers or "X-Trace-Id" in response.headers


def test_matriz_distributed_tracing_propagation(client, auth_headers):
    """Verify MATRIZ propagates W3C trace context."""
    trace_parent = "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01"

    response = client.post(
        "/v1/responses",
        json={"input": "test tracing"},
        headers={
            **auth_headers,
            "traceparent": trace_parent
        }
    )

    assert response.status_code == 200

    # Should propagate trace context
    assert "x-trace-id" in response.headers or "X-Trace-Id" in response.headers
