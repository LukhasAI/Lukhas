"""Integration tests for full security middleware stack.

Tests the complete middleware chain:
    SecurityHeaders → CORS → Auth → NIAS → Business Logic

Validates:
    1. All middlewares working together without conflicts
    2. Security headers applied to all responses
    3. NIAS audit events written with correct metadata
    4. Authentication flow (success and failure)
    5. Trace ID propagation through stack
    6. Performance overhead with full stack
    7. Error handling (4xx, 5xx still audited)
    8. End-to-end request lifecycle

This is an INTEGRATION test - it uses a real FastAPI app with all
middlewares registered, unlike unit tests that test components in isolation.
"""

import json
import time
from pathlib import Path
from typing import Dict, List

import pytest
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient

from lukhas.middleware import SecurityHeaders
from lukhas.guardian.nias import NIASMiddleware


@pytest.fixture
def temp_log_path(tmp_path):
    """Create temporary NIAS log path for testing."""
    return str(tmp_path / "nias_integration.jsonl")


@pytest.fixture
def full_stack_app(temp_log_path):
    """Create FastAPI app with full security middleware stack.

    Middleware Order (same as serve/main.py):
        1. SecurityHeaders - OWASP headers
        2. CORS - Cross-origin (simulated with custom middleware)
        3. Auth - Authentication (simulated with custom middleware)
        4. NIAS - Audit logging
        5. Business Logic - Route handlers
    """
    app = FastAPI(title="Integration Test App")

    # 1. Security Headers (first - applies to all responses)
    app.add_middleware(SecurityHeaders)

    # 2. CORS (simulated - just adds header)
    @app.middleware("http")
    async def simulated_cors(request: Request, call_next):
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    # 3. Auth (simulated - checks Authorization header)
    @app.middleware("http")
    async def simulated_auth(request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        if request.url.path.startswith("/protected"):
            if not auth_header or not auth_header.startswith("Bearer valid-"):
                return Response(
                    content='{"error": "Unauthorized"}',
                    status_code=401,
                    media_type="application/json",
                )
        # Set caller identity for NIAS
        if auth_header and auth_header.startswith("Bearer valid-"):
            request.state.caller = "authenticated-user"
        response = await call_next(request)
        return response

    # 4. NIAS Middleware
    app.add_middleware(NIASMiddleware, log_path=temp_log_path)

    # 5. Business Logic Routes
    @app.get("/healthz")
    def health_check():
        return {"status": "healthy"}

    @app.get("/public")
    def public_route():
        return {"message": "Public data"}

    @app.get("/protected")
    def protected_route():
        return {"message": "Protected data"}

    @app.post("/echo")
    def echo_route(data: dict):
        return data

    @app.get("/slow")
    def slow_route():
        time.sleep(0.1)  # 100ms delay
        return {"message": "Slow response"}

    @app.get("/error")
    def error_route():
        raise ValueError("Intentional error for testing")

    return app


@pytest.fixture
def client(full_stack_app):
    """Create TestClient for the full stack app."""
    return TestClient(full_stack_app)


def read_audit_events(log_path: str) -> List[Dict]:
    """Read all audit events from NIAS log file."""
    if not Path(log_path).exists():
        return []

    with open(log_path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def test_full_stack_health_check(client, temp_log_path):
    """Test basic health check with full middleware stack."""
    response = client.get("/healthz", headers={"X-Trace-Id": "test-trace-001"})

    # Verify response
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

    # Verify security headers present
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert "Content-Security-Policy" in response.headers

    # Verify CORS header present (from simulated CORS middleware)
    assert response.headers.get("Access-Control-Allow-Origin") == "*"

    # Verify NIAS audit event written
    time.sleep(0.05)  # Allow I/O
    events = read_audit_events(temp_log_path)
    assert len(events) == 1

    event = events[0]
    assert event["route"] == "/healthz"
    assert event["method"] == "GET"
    assert event["status_code"] == 200
    assert event["trace_id"] == "test-trace-001"
    assert event["duration_ms"] > 0


def test_full_stack_public_route(client, temp_log_path):
    """Test public route (no auth required)."""
    response = client.get("/public")

    assert response.status_code == 200
    assert response.json() == {"message": "Public data"}

    # Security headers present
    assert response.headers.get("X-Frame-Options") == "DENY"

    # NIAS event written
    time.sleep(0.05)
    events = read_audit_events(temp_log_path)
    assert len(events) == 1
    assert events[0]["route"] == "/public"
    assert events[0]["caller"] is None  # No auth, so no caller


def test_full_stack_protected_route_unauthorized(client, temp_log_path):
    """Test protected route WITHOUT valid auth token (401 expected)."""
    response = client.get("/protected")

    # Auth middleware rejects
    assert response.status_code == 401
    assert response.json() == {"error": "Unauthorized"}

    # Security headers STILL applied (SecurityHeaders is first)
    assert response.headers.get("X-Frame-Options") == "DENY"

    # NIAS STILL logs event (failure-safe design)
    time.sleep(0.05)
    events = read_audit_events(temp_log_path)
    assert len(events) == 1

    event = events[0]
    assert event["route"] == "/protected"
    assert event["status_code"] == 401
    assert event["caller"] is None  # No auth token


def test_full_stack_protected_route_authorized(client, temp_log_path):
    """Test protected route WITH valid auth token (200 expected)."""
    response = client.get(
        "/protected",
        headers={
            "Authorization": "Bearer valid-token-123",
            "X-Trace-Id": "test-trace-002",
        },
    )

    # Auth middleware allows
    assert response.status_code == 200
    assert response.json() == {"message": "Protected data"}

    # Security headers present
    assert response.headers.get("X-Frame-Options") == "DENY"

    # NIAS logs with caller identity
    time.sleep(0.05)
    events = read_audit_events(temp_log_path)
    assert len(events) == 1

    event = events[0]
    assert event["route"] == "/protected"
    assert event["status_code"] == 200
    assert event["trace_id"] == "test-trace-002"
    # Note: Our simulated auth doesn't set request headers, so NIAS won't see OpenAI-Organization
    # In production, auth middleware would set headers that NIAS reads


def test_full_stack_post_request(client, temp_log_path):
    """Test POST request with JSON body."""
    payload = {"test": "data", "count": 42}
    response = client.post("/echo", json=payload)

    assert response.status_code == 200
    assert response.json() == payload

    # Security headers on POST responses
    assert response.headers.get("X-Content-Type-Options") == "nosniff"

    # NIAS logs POST requests
    time.sleep(0.05)
    events = read_audit_events(temp_log_path)
    assert len(events) == 1

    event = events[0]
    assert event["route"] == "/echo"
    assert event["method"] == "POST"
    assert event["status_code"] == 200
    # Note: NIAS does NOT log request body (privacy-by-design)


def test_full_stack_error_handling(client, temp_log_path):
    """Test that 500 errors are still audited and have security headers."""
    response = client.get("/error")

    # FastAPI returns 500 for unhandled exceptions
    assert response.status_code == 500

    # Security headers STILL applied (even on errors)
    assert response.headers.get("X-Frame-Options") == "DENY"

    # NIAS STILL logs event (finally block ensures always executed)
    time.sleep(0.05)
    events = read_audit_events(temp_log_path)
    assert len(events) == 1

    event = events[0]
    assert event["route"] == "/error"
    assert event["status_code"] == 500
    assert event["duration_ms"] > 0


def test_full_stack_trace_id_propagation(client, temp_log_path):
    """Test that trace IDs propagate through entire middleware stack."""
    trace_id = "integration-test-trace-12345"

    response = client.get("/healthz", headers={"X-Trace-Id": trace_id})
    assert response.status_code == 200

    # NIAS captures trace ID
    time.sleep(0.05)
    events = read_audit_events(temp_log_path)
    assert len(events) == 1
    assert events[0]["trace_id"] == trace_id


def test_full_stack_multiple_requests(client, temp_log_path):
    """Test multiple requests generate multiple audit events."""
    # Make 5 requests
    for i in range(5):
        response = client.get(f"/healthz", headers={"X-Trace-Id": f"trace-{i}"})
        assert response.status_code == 200

    time.sleep(0.1)  # Allow I/O
    events = read_audit_events(temp_log_path)

    # All 5 requests logged
    assert len(events) == 5

    # Trace IDs match
    for i, event in enumerate(events):
        assert event["trace_id"] == f"trace-{i}"
        assert event["route"] == "/healthz"
        assert event["status_code"] == 200


def test_full_stack_performance_overhead(client, temp_log_path):
    """Test total performance overhead of full middleware stack."""
    # Make 50 requests to get stable measurements
    durations = []

    for _ in range(50):
        response = client.get("/healthz")
        assert response.status_code == 200

    time.sleep(0.2)  # Allow I/O
    events = read_audit_events(temp_log_path)

    # Should have 50 events
    assert len(events) == 50

    # Extract durations
    durations = [event["duration_ms"] for event in events]

    # Calculate percentiles
    durations.sort()
    p50 = durations[len(durations) // 2]
    p95 = durations[int(len(durations) * 0.95)]
    p99 = durations[int(len(durations) * 0.99)]

    print(f"\nFull Stack Performance: p50={p50:.2f}ms, p95={p95:.2f}ms, p99={p99:.2f}ms")

    # With ALL middlewares, overhead should still be reasonable
    # SecurityHeaders: ~0.1ms
    # CORS: ~0.1ms
    # Auth: ~0.2ms
    # NIAS: ~2ms
    # Total: <5ms expected

    # Allow some variance for CI environments
    assert p50 < 10.0, f"p50 duration {p50}ms exceeds 10ms threshold"
    assert p95 < 15.0, f"p95 duration {p95}ms exceeds 15ms threshold"
    assert p99 < 20.0, f"p99 duration {p99}ms exceeds 20ms threshold"


def test_full_stack_slow_route(client, temp_log_path):
    """Test that slow business logic doesn't break auditing."""
    response = client.get("/slow")
    assert response.status_code == 200

    time.sleep(0.05)
    events = read_audit_events(temp_log_path)
    assert len(events) == 1

    event = events[0]
    assert event["route"] == "/slow"
    # Duration should be ~100ms (sleep time) + middleware overhead
    assert event["duration_ms"] >= 95  # At least 95ms
    assert event["duration_ms"] < 200  # Less than 200ms (allow some variance)


def test_full_stack_request_metadata_capture(client, temp_log_path):
    """Test that NIAS captures request metadata from real requests."""
    response = client.get(
        "/public",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "IntegrationTestClient/1.0",
        },
    )
    assert response.status_code == 200

    time.sleep(0.05)
    events = read_audit_events(temp_log_path)
    assert len(events) == 1

    event = events[0]
    assert event["request_meta"]["accept"] == "application/json"
    # Note: TestClient may set different User-Agent, so just check it exists
    assert "user_agent" in event["request_meta"]


def test_full_stack_concurrent_requests(client, temp_log_path):
    """Test that concurrent requests don't interfere with each other."""
    import concurrent.futures

    def make_request(i: int):
        response = client.get("/healthz", headers={"X-Trace-Id": f"concurrent-{i}"})
        return response.status_code

    # Make 20 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request, i) for i in range(20)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    # All should succeed
    assert all(status == 200 for status in results)

    time.sleep(0.2)  # Allow I/O
    events = read_audit_events(temp_log_path)

    # All 20 requests logged
    assert len(events) == 20

    # All have unique trace IDs
    trace_ids = {event["trace_id"] for event in events}
    assert len(trace_ids) == 20  # No duplicates


def test_full_stack_csp_header_parsing(client):
    """Test that CSP header from SecurityHeaders is valid."""
    response = client.get("/healthz")

    csp = response.headers.get("Content-Security-Policy", "")
    assert csp, "CSP header missing"

    # Parse directives
    directives = [d.strip() for d in csp.split(";") if d.strip()]
    directive_names = [d.split()[0] for d in directives]

    # Required directives
    assert "default-src" in directive_names
    assert "object-src" in directive_names
    assert "frame-ancestors" in directive_names

    # Verify values
    assert "default-src 'self'" in csp
    assert "object-src 'none'" in csp
    assert "frame-ancestors 'none'" in csp


def test_full_stack_security_headers_on_errors(client):
    """Test that security headers are applied even to error responses."""
    response = client.get("/nonexistent-route")

    # 404 from FastAPI
    assert response.status_code == 404

    # Security headers STILL present
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert "Content-Security-Policy" in response.headers


def test_full_stack_all_security_headers(client):
    """Comprehensive test that ALL security headers are present."""
    response = client.get("/healthz")

    # All OWASP headers
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("Referrer-Policy") in [
        "strict-origin-when-cross-origin",
        "no-referrer",  # Alternative secure value
    ]
    assert "Permissions-Policy" in response.headers
    assert "Content-Security-Policy" in response.headers

    # Permissions-Policy should restrict dangerous features
    permissions = response.headers.get("Permissions-Policy", "")
    assert "camera=()" in permissions
    assert "microphone=()" in permissions
    assert "geolocation=()" in permissions


def test_full_stack_nias_event_schema_validation(client, temp_log_path):
    """Test that NIAS events conform to schema (all required fields present)."""
    response = client.get("/healthz", headers={"X-Trace-Id": "schema-test"})
    assert response.status_code == 200

    time.sleep(0.05)
    events = read_audit_events(temp_log_path)
    assert len(events) == 1

    event = events[0]

    # Required fields
    assert "ts" in event and event["ts"]
    assert "route" in event and event["route"] == "/healthz"
    assert "method" in event and event["method"] == "GET"
    assert "status_code" in event and event["status_code"] == 200
    assert "duration_ms" in event and event["duration_ms"] > 0

    # Optional fields (may be None)
    assert "trace_id" in event  # Present but may be None
    assert "caller" in event  # Present but may be None
    assert "drift_score" in event  # Present but may be None
    assert "request_meta" in event and isinstance(event["request_meta"], dict)
    assert "response_meta" in event and isinstance(event["response_meta"], dict)
    assert "notes" in event  # Present but may be None


def test_full_stack_end_to_end_lifecycle(client, temp_log_path):
    """End-to-end test simulating real user request lifecycle.

    User Flow:
        1. User makes authenticated request to protected endpoint
        2. Request passes through all middlewares
        3. Response includes security headers
        4. NIAS logs audit event with all metadata
        5. User receives response
    """
    # Simulate real user request
    response = client.get(
        "/protected",
        headers={
            "Authorization": "Bearer valid-user-token",
            "X-Trace-Id": "user-request-12345",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Accept": "application/json",
        },
    )

    # User receives successful response
    assert response.status_code == 200
    assert response.json() == {"message": "Protected data"}

    # User's browser receives security headers
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Content-Security-Policy")

    # Backend logs audit event
    time.sleep(0.05)
    events = read_audit_events(temp_log_path)
    assert len(events) == 1

    event = events[0]
    assert event["route"] == "/protected"
    assert event["method"] == "GET"
    assert event["status_code"] == 200
    assert event["trace_id"] == "user-request-12345"
    assert event["duration_ms"] > 0
    assert "user_agent" in event["request_meta"]

    # Compliance: Audit event contains everything needed for GDPR/DSA reporting
    assert "ts" in event  # Timestamp for Art. 30 records
    assert event["request_meta"]  # Metadata for security analytics
    # No request body logged (privacy-by-design, GDPR Art. 25)


# Performance benchmark (optional - can be slow, marked for manual runs)
@pytest.mark.slow
def test_full_stack_stress_test(client, temp_log_path):
    """Stress test with 500 requests to validate stability."""
    print("\nRunning stress test with 500 requests...")

    errors = []
    start_time = time.time()

    for i in range(500):
        try:
            response = client.get(f"/healthz", headers={"X-Trace-Id": f"stress-{i}"})
            if response.status_code != 200:
                errors.append(f"Request {i}: status {response.status_code}")
        except Exception as e:
            errors.append(f"Request {i}: {e}")

    elapsed = time.time() - start_time

    # All requests should succeed
    assert len(errors) == 0, f"Errors: {errors}"

    # Performance should be acceptable
    avg_ms = (elapsed / 500) * 1000
    print(f"Stress test completed: {elapsed:.2f}s total, {avg_ms:.2f}ms avg per request")

    # Allow I/O to complete
    time.sleep(1.0)

    # All 500 events logged
    events = read_audit_events(temp_log_path)
    assert len(events) == 500, f"Expected 500 events, got {len(events)}"

    # Verify no duplicates
    trace_ids = [event["trace_id"] for event in events]
    assert len(set(trace_ids)) == 500, "Duplicate trace IDs detected"
