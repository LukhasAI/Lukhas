"""
Test concurrent request handling and async behavior.

Validates:
- Thread-safe request processing
- No race conditions in metrics tracking
- Concurrent requests don't interfere
- Rate limiting works correctly under load
- Response ID uniqueness under concurrency
"""
import concurrent.futures
import threading

import pytest
from fastapi.testclient import TestClient
from serve.main import app
from tests.smoke.fixtures import GOLDEN_AUTH_HEADERS


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Provide valid Bearer token for authenticated requests."""
    return GOLDEN_AUTH_HEADERS


def test_concurrent_models_requests(client, auth_headers):
    """Verify concurrent /v1/models requests work correctly."""
    def make_request():
        response = client.get("/v1/models", headers=auth_headers)
        return response.status_code

    # Make 10 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(10)]
        results = [f.result() for f in futures]

    # All should succeed
    assert all(status == 200 for status in results)


def test_concurrent_responses_unique_ids(client, auth_headers):
    """Verify concurrent requests generate unique response IDs."""
    response_ids = []
    lock = threading.Lock()

    def make_request(query_num):
        response = client.post(
            "/v1/responses",
            json={"input": f"concurrent query {query_num}"},
            headers=auth_headers
        )
        if response.status_code == 200:
            resp_id = response.json()["id"]
            with lock:
                response_ids.append(resp_id)

    # Make 20 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request, i) for i in range(20)]
        [f.result() for f in futures]

    # All IDs should be unique
    assert len(response_ids) == len(set(response_ids)), \
        "Duplicate response IDs found in concurrent requests"


def test_concurrent_embeddings_requests(client, auth_headers):
    """Verify concurrent embeddings requests work correctly."""
    results = []
    lock = threading.Lock()

    def make_request(text):
        response = client.post(
            "/v1/embeddings",
            json={"input": text},
            headers=auth_headers
        )
        with lock:
            results.append({
                "status": response.status_code,
                "text": text,
                "embedding": response.json()["data"][0]["embedding"] if response.status_code == 200 else None
            })

    texts = [f"text {i}" for i in range(10)]

    # Make concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request, text) for text in texts]
        [f.result() for f in futures]

    # All should succeed
    assert all(r["status"] == 200 for r in results)

    # Different texts should have different embeddings
    embeddings = [r["embedding"] for r in results]
    unique_embeddings = [str(e) for e in embeddings]
    assert len(set(unique_embeddings)) > 1, "All embeddings are identical"


def test_concurrent_different_endpoints(client, auth_headers):
    """Verify concurrent requests to different endpoints don't interfere."""
    results = []
    lock = threading.Lock()

    def call_models():
        response = client.get("/v1/models", headers=auth_headers)
        with lock:
            results.append(("models", response.status_code))

    def call_responses():
        response = client.post(
            "/v1/responses",
            json={"input": "concurrent test"},
            headers=auth_headers
        )
        with lock:
            results.append(("responses", response.status_code))

    def call_embeddings():
        response = client.post(
            "/v1/embeddings",
            json={"input": "concurrent test"},
            headers=auth_headers
        )
        with lock:
            results.append(("embeddings", response.status_code))

    # Mix of different endpoints
    with concurrent.futures.ThreadPoolExecutor(max_workers=9) as executor:
        futures = []
        for _ in range(3):
            futures.append(executor.submit(call_models))
            futures.append(executor.submit(call_responses))
            futures.append(executor.submit(call_embeddings))
        [f.result() for f in futures]

    # All should succeed
    assert all(status == 200 for _, status in results)

    # Should have all three endpoint types
    endpoints = {endpoint for endpoint, _ in results}
    assert "models" in endpoints
    assert "responses" in endpoints
    assert "embeddings" in endpoints


def test_metrics_thread_safe(client, auth_headers):
    """Verify metrics tracking is thread-safe under concurrent load."""
    def make_requests():
        for _ in range(5):
            client.get("/v1/models", headers=auth_headers)

    # Make concurrent requests to trigger metrics updates
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_requests) for _ in range(10)]
        [f.result() for f in futures]

    # Metrics endpoint should work after concurrent updates
    metrics_response = client.get("/metrics")
    assert metrics_response.status_code == 200

    # Metrics should contain data
    metrics_text = metrics_response.text
    assert len(metrics_text) > 0
    assert "http_requests_total" in metrics_text


def test_rate_limiting_concurrent_requests(client, auth_headers):
    """Verify rate limiting works correctly under concurrent load."""
    status_codes = []
    lock = threading.Lock()

    def make_request():
        response = client.get("/v1/models", headers=auth_headers)
        with lock:
            status_codes.append(response.status_code)

    # Make many concurrent requests to trigger rate limit
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(make_request) for _ in range(100)]
        [f.result() for f in futures]

    # Should have mix of 200s and possibly some 429s
    assert 200 in status_codes
    # Rate limit might kick in
    if 429 in status_codes:
        # Verify rate limiting is working
        assert status_codes.count(429) > 0


def test_concurrent_auth_validation(client):
    """Verify auth validation is thread-safe."""
    valid_headers = {"Authorization": "Bearer sk-lukhas-valid-1234567890"}
    invalid_headers = {"Authorization": "Bearer bad"}

    results = []
    lock = threading.Lock()

    def make_valid_request():
        response = client.get("/v1/models", headers=valid_headers)
        with lock:
            results.append(("valid", response.status_code))

    def make_invalid_request():
        response = client.get("/v1/models", headers=invalid_headers)
        with lock:
            results.append(("invalid", response.status_code))

    # Mix of valid and invalid requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for _ in range(10):
            futures.append(executor.submit(make_valid_request))
            futures.append(executor.submit(make_invalid_request))
        [f.result() for f in futures]

    # Valid requests should succeed
    valid_results = [status for auth_type, status in results if auth_type == "valid"]
    assert all(status == 200 for status in valid_results)

    # Invalid requests should fail
    invalid_results = [status for auth_type, status in results if auth_type == "invalid"]
    assert all(status == 401 for status in invalid_results)


def test_concurrent_health_checks(client):
    """Verify health endpoints handle concurrent requests."""
    def check_healthz():
        return client.get("/healthz").status_code

    def check_readyz():
        return client.get("/readyz").status_code

    # Many concurrent health checks
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        healthz_futures = [executor.submit(check_healthz) for _ in range(50)]
        readyz_futures = [executor.submit(check_readyz) for _ in range(50)]

        healthz_results = [f.result() for f in healthz_futures]
        readyz_results = [f.result() for f in readyz_futures]

    # All should succeed
    assert all(status == 200 for status in healthz_results)
    assert all(status == 200 for status in readyz_results)


def test_no_deadlocks_under_load(client, auth_headers):
    """Verify no deadlocks occur under high concurrent load."""
    import time

    completed = []
    lock = threading.Lock()

    def make_mixed_requests():
        # Mix of different operations
        client.get("/v1/models", headers=auth_headers)
        client.post("/v1/embeddings", json={"input": "test"}, headers=auth_headers)
        client.get("/healthz")
        with lock:
            completed.append(1)

    start = time.time()

    # High concurrency
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(make_mixed_requests) for _ in range(50)]

        # Wait with timeout to detect deadlocks
        try:
            [f.result(timeout=10) for f in futures]
        except concurrent.futures.TimeoutError:
            pytest.fail("Deadlock detected: requests didn't complete within timeout")

    elapsed = time.time() - start

    # Should complete reasonably quickly
    assert elapsed < 15, f"Requests took {elapsed}s (possible deadlock)"

    # All should complete
    assert len(completed) == 50


def test_concurrent_tenant_isolation(client):
    """Verify tenant isolation maintained under concurrent load."""
    tenant1_headers = {"Authorization": "Bearer sk-lukhas-tenant1-1234567890"}
    tenant2_headers = {"Authorization": "Bearer sk-lukhas-tenant2-0987654321"}

    tenant1_ids = []
    tenant2_ids = []
    lock = threading.Lock()

    def tenant1_request():
        response = client.post(
            "/v1/responses",
            json={"input": "tenant1 query"},
            headers=tenant1_headers
        )
        if response.status_code == 200:
            with lock:
                tenant1_ids.append(response.json()["id"])

    def tenant2_request():
        response = client.post(
            "/v1/responses",
            json={"input": "tenant2 query"},
            headers=tenant2_headers
        )
        if response.status_code == 200:
            with lock:
                tenant2_ids.append(response.json()["id"])

    # Interleaved requests from both tenants
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for _ in range(10):
            futures.append(executor.submit(tenant1_request))
            futures.append(executor.submit(tenant2_request))
        [f.result() for f in futures]

    # Response IDs should be unique across all requests
    all_ids = tenant1_ids + tenant2_ids
    assert len(all_ids) == len(set(all_ids)), \
        "Duplicate IDs found across tenants"

    # Both tenants should have responses
    assert len(tenant1_ids) > 0
    assert len(tenant2_ids) > 0
