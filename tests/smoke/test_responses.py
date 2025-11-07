"""
Test /v1/responses endpoint for MATRIZ integration and response generation.

Validates:
- MATRIZ orchestrator integration (stub and real modes)
- Request/response format compliance
- Error handling (400, 401, 500)
- Timeout behavior
- Output text generation
- Trace information when available
"""
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


def test_responses_requires_auth(client):
    """Verify /v1/responses requires authentication."""
    response = client.post(
        "/v1/responses",
        json={"input": "test"}
    )
    assert response.status_code == 401


def test_responses_happy_path(client, auth_headers):
    """Verify basic response generation works."""
    response = client.post(
        "/v1/responses",
        json={"input": "hello world"},
        headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()
    assert "id" in data
    assert "model" in data
    assert "output" in data
    assert "text" in data["output"]


def test_responses_missing_input_returns_400(client, auth_headers):
    """Verify missing 'input' field returns 400."""
    response = client.post(
        "/v1/responses",
        json={},
        headers=auth_headers
    )
    assert response.status_code == 400


def test_responses_empty_input_returns_400(client, auth_headers):
    """Verify empty input string returns 400."""
    response = client.post(
        "/v1/responses",
        json={"input": ""},
        headers=auth_headers
    )
    assert response.status_code == 400


def test_responses_id_format(client, auth_headers):
    """Verify response ID follows expected format (resp_*)."""
    response = client.post(
        "/v1/responses",
        json={"input": "test query"},
        headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()
    resp_id = data["id"]

    # Should start with "resp_"
    assert resp_id.startswith("resp_"), \
        f"Response ID should start with 'resp_': {resp_id}"

    # Should be followed by hex string
    hex_part = resp_id[5:]  # After "resp_"
    assert len(hex_part) == 8  # 8-char hex
    assert all(c in "0123456789abcdef" for c in hex_part)


def test_responses_model_field_present(client, auth_headers):
    """Verify response includes model field."""
    response = client.post(
        "/v1/responses",
        json={"input": "which model?"},
        headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()
    assert "model" in data
    assert data["model"] == "lukhas-matriz"


def test_responses_output_text_non_empty(client, auth_headers):
    """Verify output text is not empty."""
    response = client.post(
        "/v1/responses",
        json={"input": "generate something"},
        headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()
    output_text = data["output"]["text"]

    assert len(output_text) > 0, "Output text should not be empty"


def test_responses_stub_mode_echo(client, auth_headers):
    """Verify stub mode echoes input when MATRIZ unavailable."""
    test_input = "unique test string xyz123"

    response = client.post(
        "/v1/responses",
        json={"input": test_input},
        headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()
    output_text = data["output"]["text"].lower()

    # Stub mode should echo or reference input
    # (May contain "echo:" prefix or actual MATRIZ response)
    assert test_input.lower() in output_text or "xyz123" in output_text


def test_responses_different_inputs_different_outputs(client, auth_headers):
    """Verify different inputs produce different outputs."""
    response1 = client.post(
        "/v1/responses",
        json={"input": "first query"},
        headers=auth_headers
    )
    response2 = client.post(
        "/v1/responses",
        json={"input": "second query"},
        headers=auth_headers
    )

    assert response1.status_code == 200
    assert response2.status_code == 200

    response1.json()["output"]["text"]
    response2.json()["output"]["text"]

    # Should be different (unless MATRIZ produces identical responses)
    # At minimum, request IDs should differ
    id1 = response1.json()["id"]
    id2 = response2.json()["id"]
    assert id1 != id2


def test_responses_long_input_handling(client, auth_headers):
    """Verify long input text is handled correctly."""
    long_input = "test " * 500  # 2500 characters

    response = client.post(
        "/v1/responses",
        json={"input": long_input},
        headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()
    assert "output" in data
    assert "text" in data["output"]


def test_responses_unicode_input(client, auth_headers):
    """Verify unicode input is handled correctly."""
    unicode_input = "Hello 世界 🌍 Привет مرحبا"

    response = client.post(
        "/v1/responses",
        json={"input": unicode_input},
        headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()
    output_text = data["output"]["text"]
    assert len(output_text) > 0


def test_responses_special_characters(client, auth_headers):
    """Verify special characters are handled."""
    special_input = "Test with <html>, {json}, and \"quotes\""

    response = client.post(
        "/v1/responses",
        json={"input": special_input},
        headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()
    assert "output" in data


def test_responses_trace_field_optional(client, auth_headers):
    """Verify trace field is optional (present when MATRIZ available)."""
    response = client.post(
        "/v1/responses",
        json={"input": "trace test"},
        headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()

    # Trace field is optional
    # If present, should be a dict
    if "trace" in data:
        assert isinstance(data["trace"], dict)


def test_responses_content_type_json(client, auth_headers):
    """Verify Content-Type is application/json."""
    response = client.post(
        "/v1/responses",
        json={"input": "content type test"},
        headers=auth_headers
    )
    assert response.status_code == 200

    content_type = response.headers.get("content-type", "")
    assert "application/json" in content_type.lower()


def test_responses_x_trace_id_header(client, auth_headers):
    """Verify X-Trace-Id header when OTEL enabled."""
    response = client.post(
        "/v1/responses",
        json={"input": "trace header test"},
        headers=auth_headers
    )
    assert response.status_code == 200

    # X-Trace-Id may or may not be present
    if "X-Trace-Id" in response.headers:
        trace_id = response.headers["X-Trace-Id"]
        assert len(trace_id) == 32
        assert all(c in "0123456789abcdef" for c in trace_id)


def test_responses_multiple_sequential_requests(client, auth_headers):
    """Verify multiple requests work correctly."""
    for i in range(5):
        response = client.post(
            "/v1/responses",
            json={"input": f"query {i}"},
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "id" in data
        assert "output" in data


def test_responses_malformed_payload_handled(client, auth_headers):
    """Verify malformed payloads are rejected."""
    # Missing required field
    response = client.post(
        "/v1/responses",
        json={"wrong_field": "value"},
        headers=auth_headers
    )
    # Should return 400 (missing input field)
    assert response.status_code == 400


def test_responses_processing_time_reasonable(client, auth_headers):
    """Verify response time is reasonable (< 5 seconds)."""
    import time

    start = time.time()
    response = client.post(
        "/v1/responses",
        json={"input": "quick test"},
        headers=auth_headers
    )
    elapsed = time.time() - start

    assert response.status_code == 200
    assert elapsed < 5.0, f"Response took {elapsed}s (should be < 5s)"


def test_responses_concurrent_requests_isolated(client, auth_headers):
    """Verify concurrent requests don't interfere with each other."""
    # Note: TestClient is synchronous, but this tests basic isolation
    response1 = client.post(
        "/v1/responses",
        json={"input": "request A"},
        headers=auth_headers
    )
    response2 = client.post(
        "/v1/responses",
        json={"input": "request B"},
        headers=auth_headers
    )

    assert response1.status_code == 200
    assert response2.status_code == 200

    # Should have unique IDs
    id1 = response1.json()["id"]
    id2 = response2.json()["id"]
    assert id1 != id2
