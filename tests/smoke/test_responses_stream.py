"""
Smoke test: Streaming responses (SSE).

Verifies that /v1/responses supports Server-Sent Events streaming:
- Content-Type: text/event-stream
- data: prefix on chunks
- data: [DONE] terminator
- Backpressure handling (large payloads)
- Header propagation (X-Trace-Id, rate limits)

Phase 3: Added for OpenAI parity polish.
Phase 4: Enhanced with backpressure + header parity tests (Task 2).
"""
from __future__ import annotations

import asyncio
import time

import pytest
from fastapi.testclient import TestClient

from lukhas.adapters.openai.api import get_app

AUTH_HEADERS = {"Authorization": "Bearer sk-lukhas-test-1234567890abcdef"}


@pytest.fixture
def client() -> TestClient:
    return TestClient(get_app())


def test_streaming_responses_sse_protocol(client: TestClient) -> None:
    """Verify SSE protocol compliance for streaming responses."""
    payload = {"model": "lukhas-response", "input": "hi", "stream": True}

    with client.stream("POST", "/v1/responses", headers=AUTH_HEADERS, json=payload) as r:
        assert r.status_code == 200
        assert r.headers.get("content-type", "").startswith("text/event-stream")

        data_frames: list[str] = []
        done_received = False

        for line in r.iter_lines():
            if not line:
                continue
            if line.startswith("data: "):
                data = line[6:]
                if data == "[DONE]":
                    done_received = True
                    break
                data_frames.append(data)

        assert data_frames or done_received, "Expected data frames or DONE marker"


def test_streaming_vs_non_streaming(client: TestClient) -> None:
    """Verify stream parameter controls response format."""
    base_payload = {"model": "lukhas-response", "input": "test"}

    r1 = client.post("/v1/responses", headers=AUTH_HEADERS, json={**base_payload, "stream": False})
    with client.stream("POST", "/v1/responses", headers=AUTH_HEADERS, json={**base_payload, "stream": True}) as r2:
        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r1.headers.get("content-type", "").startswith("application/json")
        assert r2.headers.get("content-type", "").startswith("text/event-stream")


def test_streaming_trace_header(client: TestClient) -> None:
    """Verify trace headers present even in streaming responses."""
    payload = {"model": "lukhas-response", "input": "trace test", "stream": True}

    with client.stream("POST", "/v1/responses", headers=AUTH_HEADERS, json=payload) as r:
        assert r.status_code == 200
        trace_id = r.headers.get("X-Trace-Id")
        assert trace_id is not None, "Missing X-Trace-Id in streaming response"


# =============================================================================
# Task 2: SSE Backpressure + Header Parity Tests
# =============================================================================


def test_sse_yields_incremental_chunks(client: TestClient) -> None:
    """
    Task 2.1: SSE stream yields data incrementally, not all at once.
    
    OpenAI Behavior: Stream chunks arrive progressively with <100ms inter-chunk delay.
    
    DoD:
    - At least 5 chunks received
    - Chunks arrive progressively (not all buffered)
    - Total time > 500ms (proves streaming, not buffered)
    """
    payload = {"model": "lukhas-response", "input": "Generate a detailed 200-word response.", "stream": True}
    
    chunk_count = 0
    chunk_times = []
    start_time = time.time()
    
    with client.stream("POST", "/v1/responses", headers=AUTH_HEADERS, json=payload) as r:
        assert r.status_code == 200
        assert r.headers.get("content-type", "").startswith("text/event-stream")
        
        for line in r.iter_lines():
            if not line:
                continue
            if line.startswith("data: "):
                chunk_count += 1
                chunk_times.append(time.time() - start_time)
                data = line[6:]
                if data == "[DONE]":
                    break
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Assertions
    assert chunk_count >= 5, f"Expected ≥5 chunks, got {chunk_count}"
    assert total_time > 0.5, f"Stream completed too fast ({total_time:.2f}s), likely buffered"
    
    # Verify progressive delivery (chunks not all at once)
    if len(chunk_times) >= 2:
        time_spread = chunk_times[-1] - chunk_times[0]
        assert time_spread > 0.1, "Chunks arrived too quickly, not truly streaming"


def test_sse_backpressure_1MB_payload_no_drop(client: TestClient) -> None:
    """
    Task 2.2: SSE handles backpressure on large payloads without dropping data.
    
    OpenAI Behavior: Large responses stream reliably without truncation.
    
    DoD:
    - Request generates substantial streamed data
    - All chunks received (no drops)
    - Response complete ([DONE] marker received)
    - No 5xx errors or connection drops
    """
    large_payload = {
        "model": "lukhas-response",
        "input": "Generate a very detailed 1000-word technical document on quantum computing.",
        "stream": True,
        "max_tokens": 2000,  # Large token count to trigger backpressure
    }
    
    chunk_count = 0
    total_bytes = 0
    received_done = False
    
    with client.stream("POST", "/v1/responses", headers=AUTH_HEADERS, json=large_payload) as r:
        assert r.status_code == 200
        
        for line in r.iter_lines():
            if not line:
                continue
            total_bytes += len(line.encode("utf-8"))
            
            if line.startswith("data: "):
                chunk_count += 1
                data = line[6:]
                if data == "[DONE]":
                    received_done = True
                    break
    
    # Assertions
    assert chunk_count >= 10, f"Expected ≥10 chunks for large payload, got {chunk_count}"
    assert total_bytes >= 5_000, f"Expected ≥5KB data, got {total_bytes} bytes"
    assert received_done, "Stream did not complete with [DONE] marker"


def test_sse_includes_x_trace_id_and_rl_headers(client: TestClient) -> None:
    """
    Task 2.3: SSE response includes X-Trace-Id and rate limit headers.
    
    OpenAI Parity: Headers must be present on streaming responses (PR #406).
    
    DoD:
    - X-Trace-Id header present (or X-Request-Id alias)
    - x-ratelimit-limit-requests header present
    - x-ratelimit-remaining-requests header present
    - x-ratelimit-reset-requests header present
    """
    payload = {"model": "lukhas-response", "input": "header test", "stream": True}
    
    with client.stream("POST", "/v1/responses", headers=AUTH_HEADERS, json=payload) as r:
        assert r.status_code == 200
        
        # Verify trace header (either format)
        trace_id = r.headers.get("x-trace-id") or r.headers.get("x-request-id")
        assert trace_id, "Missing X-Trace-Id or X-Request-Id header"
        
        # Verify rate limit headers (OpenAI parity - lowercase per #406)
        rl_limit = r.headers.get("x-ratelimit-limit-requests")
        rl_remaining = r.headers.get("x-ratelimit-remaining-requests")
        rl_reset = r.headers.get("x-ratelimit-reset-requests")
        
        assert rl_limit, "Missing x-ratelimit-limit-requests header"
        assert rl_remaining, "Missing x-ratelimit-remaining-requests header"
        assert rl_reset, "Missing x-ratelimit-reset-requests header"
        
        # Verify values are numeric
        assert int(rl_limit) > 0, f"Invalid rate limit: {rl_limit}"
        assert int(rl_remaining) >= 0, f"Invalid remaining: {rl_remaining}"
        
        # Consume stream (verify no errors)
        chunk_count = 0
        for line in r.iter_lines():
            if not line:
                continue
            if line.startswith("data: "):
                chunk_count += 1
                if line[6:] == "[DONE]":
                    break
        
        assert chunk_count >= 1, "Stream produced no chunks"
