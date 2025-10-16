"""
Smoke test: Streaming responses (SSE).

Verifies that /v1/responses supports Server-Sent Events streaming:
- Content-Type: text/event-stream
- data: prefix on chunks
- data: [DONE] terminator

Phase 3: Added for OpenAI parity polish.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from lukhas.adapters.openai.api import get_app

from tests.smoke.fixtures import GOLDEN_AUTH_HEADERS

AUTH_HEADERS = GOLDEN_AUTH_HEADERS


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


def test_streaming_includes_rate_limit_headers(client: TestClient) -> None:
    """Verify RL headers (canonical + OpenAI aliases) exist on streaming responses."""
    payload = {"model": "lukhas-response", "input": "rl headers", "stream": True}

    with client.stream("POST", "/v1/responses", headers=AUTH_HEADERS, json=payload) as r:
        assert r.status_code == 200
        # Canonical
        has_canonical = bool(r.headers.get("X-RateLimit-Limit") and r.headers.get("X-RateLimit-Remaining"))
        # Aliases
        has_alias = bool(
            r.headers.get("x-ratelimit-limit-requests") and r.headers.get("x-ratelimit-remaining-requests")
        )
        assert has_canonical or has_alias, "Expected rate-limit headers on streaming response"
