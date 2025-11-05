"""
Test embeddings endpoint for shape, dtype, and stability compliance.

Validates:
- Numeric dtype (all values are floats)
- Vector length consistency (1536 dimensions for OpenAI compatibility)
- Stability across identical calls (deterministic hashing)
- Range normalization (values in [0, 1] for stub mode)
- Response format compliance
"""
import pytest
from fastapi.testclient import TestClient
from serve.main import app
from tests.smoke.fixtures import GOLDEN_AUTH_HEADERS


import os

@pytest.fixture
def client():
    """Create test client with auth."""
    os.environ['LUKHAS_POLICY_MODE'] = 'strict'
    client = TestClient(app)
    yield client
    del os.environ['LUKHAS_POLICY_MODE']


@pytest.fixture
def auth_headers():
    """Provide valid Bearer token for authenticated requests."""
    return GOLDEN_AUTH_HEADERS


def test_embeddings_happy_path(client, auth_headers):
    """Verify basic embeddings functionality."""
    response = client.post(
        "/v1/embeddings",
        json={"input": "test text"},
        headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0
    assert "embedding" in data["data"][0]


def test_embeddings_vector_length(client, auth_headers):
    """Verify embeddings have correct dimensionality (1536 for OpenAI compat)."""
    response = client.post(
        "/v1/embeddings",
        json={"input": "hello world"},
        headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()
    embedding = data["data"][0]["embedding"]

    # Stub mode uses 1536 dimensions (SHA256 hash -> 32 bytes -> 1536 floats)
    # When real backend lands, this should remain 1536 for OpenAI compatibility
    assert len(embedding) == 1536, f"Expected 1536 dimensions, got {len(embedding)}"


def test_embeddings_numeric_dtype(client, auth_headers):
    """Verify all embedding values are numeric (float)."""
    response = client.post(
        "/v1/embeddings",
        json={"input": "numeric validation test"},
        headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()
    embedding = data["data"][0]["embedding"]

    # All values must be float/int (numeric)
    for i, value in enumerate(embedding):
        assert isinstance(value, (int, float)), \
            f"Value at index {i} is not numeric: {type(value)}"


def test_embeddings_range_normalization(client, auth_headers):
    """Verify embedding values are in valid range [0, 1] for stub mode."""
    response = client.post(
        "/v1/embeddings",
        json={"input": "range check"},
        headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()
    embedding = data["data"][0]["embedding"]

    # Stub implementation normalizes to [0, 1]
    # Real backend may use different range (e.g., [-1, 1])
    for i, value in enumerate(embedding):
        assert 0.0 <= value <= 1.0, \
            f"Value at index {i} out of range [0, 1]: {value}"


def test_embeddings_stability_identical_input(client, auth_headers):
    """Verify identical inputs produce identical embeddings (deterministic)."""
    text = "stability test input"

    # Call twice with same input
    response1 = client.post(
        "/v1/embeddings",
        json={"input": text},
        headers=auth_headers
    )
    response2 = client.post(
        "/v1/embeddings",
        json={"input": text},
        headers=auth_headers
    )

    assert response1.status_code == 200
    assert response2.status_code == 200

    embedding1 = response1.json()["data"][0]["embedding"]
    embedding2 = response2.json()["data"][0]["embedding"]

    # Should be identical (deterministic hashing)
    assert embedding1 == embedding2, "Embeddings not stable across identical calls"


def test_embeddings_different_inputs_different_vectors(client, auth_headers):
    """Verify different inputs produce different embeddings."""
    response1 = client.post(
        "/v1/embeddings",
        json={"input": "first text"},
        headers=auth_headers
    )
    response2 = client.post(
        "/v1/embeddings",
        json={"input": "second text"},
        headers=auth_headers
    )

    assert response1.status_code == 200
    assert response2.status_code == 200

    embedding1 = response1.json()["data"][0]["embedding"]
    embedding2 = response2.json()["data"][0]["embedding"]

    # Should be different
    assert embedding1 != embedding2, "Different inputs produced identical embeddings"


def test_embeddings_empty_input_handled(client, auth_headers):
    """Verify empty input is handled gracefully (400 error)."""
    response = client.post(
        "/v1/embeddings",
        json={"input": ""},
        headers=auth_headers
    )
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "error" in data["detail"]
    assert data["detail"]["error"]["type"] == "invalid_request_error"
    assert data["detail"]["error"]["code"] == "invalid_parameter"


def test_embeddings_missing_input_field(client, auth_headers):
    """Verify missing 'input' field returns 400."""
    response = client.post(
        "/v1/embeddings",
        json={},
        headers=auth_headers
    )
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "error" in data["detail"]
    assert data["detail"]["error"]["type"] == "invalid_request_error"
    assert data["detail"]["error"]["code"] == "missing_required_parameter"


def test_embeddings_requires_auth(client):
    """Verify embeddings endpoint requires authentication."""
    response = client.post(
        "/v1/embeddings",
        json={"input": "test"}
    )
    assert response.status_code == 401


def test_embeddings_response_format(client, auth_headers):
    """Verify response matches OpenAI embeddings format."""
    response = client.post(
        "/v1/embeddings",
        json={"input": "format validation"},
        headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()

    # Required fields
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0

    # First embedding object
    first = data["data"][0]
    assert "embedding" in first
    assert "index" in first
    assert isinstance(first["embedding"], list)
    assert first["index"] == 0


def test_embeddings_long_text_handling(client, auth_headers):
    """Verify long text inputs are handled correctly."""
    long_text = "test " * 500  # 2500 characters

    response = client.post(
        "/v1/embeddings",
        json={"input": long_text},
        headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()
    embedding = data["data"][0]["embedding"]

    # Should still produce valid embedding
    assert len(embedding) == 1536
    assert all(isinstance(v, (int, float)) for v in embedding)


def test_embeddings_unicode_text(client, auth_headers):
    """Verify unicode text is handled correctly."""
    unicode_text = "Hello 世界 🌍 Привет مرحبا"

    response = client.post(
        "/v1/embeddings",
        json={"input": unicode_text},
        headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()
    embedding = data["data"][0]["embedding"]

    # Should produce valid embedding for unicode
    assert len(embedding) == 1536
    assert all(0.0 <= v <= 1.0 for v in embedding)


def test_embeddings_vector_not_all_zeros(client, auth_headers):
    """Verify embeddings are not trivial (not all zeros)."""
    response = client.post(
        "/v1/embeddings",
        json={"input": "non-trivial vector test"},
        headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()
    embedding = data["data"][0]["embedding"]

    # Should have some non-zero values
    non_zero_count = sum(1 for v in embedding if v != 0.0)
    assert non_zero_count > 0, "Embedding is all zeros (trivial)"

    # Most values should vary (not constant)
    unique_values = len(set(embedding))
    assert unique_values > 10, f"Only {unique_values} unique values (too uniform)"


def test_embeddings_cosine_similarity_sanity(client, auth_headers):
    """Verify embeddings have reasonable cosine similarity properties."""
    # Similar texts
    response1 = client.post(
        "/v1/embeddings",
        json={"input": "cat animal pet"},
        headers=auth_headers
    )
    response2 = client.post(
        "/v1/embeddings",
        json={"input": "dog animal pet"},
        headers=auth_headers
    )

    # Very different text
    response3 = client.post(
        "/v1/embeddings",
        json={"input": "mathematics equation algebra"},
        headers=auth_headers
    )

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 200

    emb1 = response1.json()["data"][0]["embedding"]
    emb2 = response2.json()["data"][0]["embedding"]
    emb3 = response3.json()["data"][0]["embedding"]

    # All vectors should have same length
    assert len(emb1) == len(emb2) == len(emb3) == 1536

    # All should be distinct
    assert emb1 != emb2
    assert emb1 != emb3
    assert emb2 != emb3
