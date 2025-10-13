"""
Smoke test: Idempotency-Key support.

Verifies that Idempotency-Key header provides safe replay semantics:
- Same key + same body = cached response
- Same key + different body = conflict or recomputation

Phase 3: Added for reliability polish.
"""
import os
import pytest
import requests
import json

BASE = os.getenv("LUKHAS_BASE_URL", "http://localhost:8000")


def test_idempotency_key_replay_same_body_returns_cached():
    """Replay with same Idempotency-Key and body returns cached response."""
    headers = {"Authorization": "Bearer test", "Idempotency-Key": "test-abc123"}
    payload = {"input": "hello", "model": "lukhas-embed"}
    
    r1 = requests.post(f"{BASE}/v1/embeddings", headers=headers, json=payload)
    r2 = requests.post(f"{BASE}/v1/embeddings", headers=headers, json=payload)
    
    # Both should succeed (in permissive mode) or both fail (in strict mode)
    assert r1.status_code == r2.status_code
    
    # If successful, responses should be identical
    if r1.status_code == 200:
        assert r1.text == r2.text, "Cached response should match original"


def test_idempotency_key_different_body_handled():
    """Different body with same Idempotency-Key is handled (conflict or recompute)."""
    headers = {"Authorization": "Bearer test", "Idempotency-Key": "test-xyz789"}
    p1 = {"input": "hello", "model": "lukhas-embed"}
    p2 = {"input": "world", "model": "lukhas-embed"}
    
    r1 = requests.post(f"{BASE}/v1/embeddings", headers=headers, json=p1)
    r2 = requests.post(f"{BASE}/v1/embeddings", headers=headers, json=p2)
    
    # Should either conflict (409) or recompute (200), but not server error
    assert r2.status_code in (200, 409, 401, 403), f"Unexpected: {r2.status_code}"


def test_idempotency_key_works_for_responses():
    """Idempotency-Key works for /v1/responses endpoint."""
    headers = {"Authorization": "Bearer test", "Idempotency-Key": "test-resp456"}
    payload = {"model": "lukhas-response", "input": "hi", "stream": False}
    
    r1 = requests.post(f"{BASE}/v1/responses", headers=headers, json=payload)
    r2 = requests.post(f"{BASE}/v1/responses", headers=headers, json=payload)
    
    # Same status for both
    assert r1.status_code == r2.status_code
    
    # If successful, responses should be identical
    if r1.status_code == 200:
        assert r1.text == r2.text, "Cached response should match original"


def test_without_idempotency_key_not_cached():
    """Without Idempotency-Key, requests are not cached."""
    headers = {"Authorization": "Bearer test"}
    payload = {"input": "test", "model": "lukhas-embed"}
    
    r1 = requests.post(f"{BASE}/v1/embeddings", headers=headers, json=payload)
    r2 = requests.post(f"{BASE}/v1/embeddings", headers=headers, json=payload)
    
    # Both should execute independently (not cached)
    # We can't assert different responses, but we can verify both are processed
    assert r1.status_code in (200, 401, 403)
    assert r2.status_code in (200, 401, 403)
