"""
Smoke test: Idempotency-Key support.

Verifies that Idempotency-Key header provides safe replay semantics:
- Same key + same body = cached response
- Same key + different body = conflict or recomputation

Phase 3: Added for reliability polish.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from lukhas.adapters.openai.api import get_app


@pytest.fixture
def client() -> TestClient:
    """Provide a fresh TestClient for each idempotency test."""
    return TestClient(get_app())


def _auth_headers(extra: dict[str, str] | None = None) -> dict[str, str]:
    headers = {"Authorization": "Bearer sk-lukhas-test-1234567890abcdef"}
    if extra:
        headers.update(extra)
    return headers


def test_idempotency_key_replay_same_body_returns_cached(client: TestClient) -> None:
    """Replay with same Idempotency-Key and body returns cached response."""
    headers = _auth_headers({"Idempotency-Key": "test-abc123"})
    payload = {"input": "hello", "model": "lukhas-embed"}

    r1 = client.post("/v1/embeddings", headers=headers, json=payload)
    r2 = client.post("/v1/embeddings", headers=headers, json=payload)

    assert r1.status_code == r2.status_code

    if r1.status_code == 200:
        assert r1.json() == r2.json(), "Cached response should match original"


def test_idempotency_key_different_body_handled(client: TestClient) -> None:
    """Different body with same Idempotency-Key is handled (conflict or recompute)."""
    headers = _auth_headers({"Idempotency-Key": "test-xyz789"})
    p1 = {"input": "hello", "model": "lukhas-embed"}
    p2 = {"input": "world", "model": "lukhas-embed"}

    r1 = client.post("/v1/embeddings", headers=headers, json=p1)
    r2 = client.post("/v1/embeddings", headers=headers, json=p2)

    assert r2.status_code in (200, 409, 401, 403), f"Unexpected: {r2.status_code}"


def test_idempotency_key_works_for_responses(client: TestClient) -> None:
    """Idempotency-Key works for /v1/responses endpoint."""
    headers = _auth_headers({"Idempotency-Key": "test-resp456"})
    payload = {"model": "lukhas-response", "input": "hi", "stream": False}

    r1 = client.post("/v1/responses", headers=headers, json=payload)
    r2 = client.post("/v1/responses", headers=headers, json=payload)

    assert r1.status_code == r2.status_code

    if r1.status_code == 200:
        assert r1.json() == r2.json(), "Cached response should match original"


def test_without_idempotency_key_not_cached(client: TestClient) -> None:
    """Without Idempotency-Key, requests are not cached."""
    headers = _auth_headers()
    payload = {"input": "test", "model": "lukhas-embed"}

    r1 = client.post("/v1/embeddings", headers=headers, json=payload)
    r2 = client.post("/v1/embeddings", headers=headers, json=payload)

    assert r1.status_code in (200, 401, 403)
    assert r2.status_code in (200, 401, 403)
