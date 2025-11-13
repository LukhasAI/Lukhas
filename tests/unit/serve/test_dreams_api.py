"""
Tests for Dreams API endpoint.

Tests:
- POST /v1/dreams with API key authentication
- API key validation via X-API-Key header
- Dream generation with seed and constraints
"""
import os
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from serve.dreams_api import router


@pytest.fixture
def app():
    """Create test FastAPI app with dreams router."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def valid_api_key(monkeypatch):
    """Set up valid API key in environment."""
    api_key = "test_api_key_12345"
    monkeypatch.setenv("LUKHAS_API_KEY", api_key)
    return api_key


@pytest.fixture
def no_api_key(monkeypatch):
    """Remove API key from environment."""
    monkeypatch.delenv("LUKHAS_API_KEY", raising=False)


class TestDreamsAuthentication:
    """Tests for API key authentication."""

    def test_dreams_requires_api_key(self, client, valid_api_key):
        """Test that dreams endpoint requires X-API-Key header."""
        response = client.post("/v1/dreams", json={"seed": "test"})

        # FastAPI returns 422 for missing required header parameter
        assert response.status_code == 422
        detail = response.json()["detail"]
        # Check that x-api-key is the missing field
        assert any(err["loc"] == ["header", "x-api-key"] for err in detail)

    def test_dreams_accepts_valid_api_key(self, client, valid_api_key):
        """Test that valid API key is accepted."""
        response = client.post(
            "/v1/dreams",
            json={},
            headers={"X-API-Key": valid_api_key}
        )

        assert response.status_code == 200

    def test_dreams_rejects_invalid_api_key(self, client, valid_api_key):
        """Test that invalid API key is rejected."""
        response = client.post(
            "/v1/dreams",
            json={},
            headers={"X-API-Key": "wrong_key"}
        )

        assert response.status_code == 401
        assert "Invalid API Key" in response.json()["detail"]

    def test_dreams_rejects_empty_api_key(self, client, valid_api_key):
        """Test that empty API key is rejected."""
        response = client.post(
            "/v1/dreams",
            json={},
            headers={"X-API-Key": ""}
        )

        assert response.status_code == 401

    def test_dreams_requires_header_name_case_insensitive(self, client, valid_api_key):
        """Test that X-API-Key header is case-insensitive."""
        # FastAPI/Starlette normalizes headers, so x-api-key should work
        response = client.post(
            "/v1/dreams",
            json={},
            headers={"x-api-key": valid_api_key}
        )

        assert response.status_code == 200


class TestDreamsGeneration:
    """Tests for dream generation functionality."""

    def test_dreams_basic_generation(self, client, valid_api_key):
        """Test basic dream generation without parameters."""
        response = client.post(
            "/v1/dreams",
            json={},
            headers={"X-API-Key": valid_api_key}
        )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "traces" in data
        assert "model" in data

    def test_dreams_with_seed(self, client, valid_api_key):
        """Test dream generation with a seed."""
        seed = "test_seed_123"
        response = client.post(
            "/v1/dreams",
            json={"seed": seed},
            headers={"X-API-Key": valid_api_key}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["seed"] == seed
        # Check that seed is used in traces
        assert any(seed in str(trace) for trace in data["traces"])

    def test_dreams_with_constraints(self, client, valid_api_key):
        """Test dream generation with constraints."""
        constraints = {"max_steps": 5, "theme": "ocean"}
        response = client.post(
            "/v1/dreams",
            json={"constraints": constraints},
            headers={"X-API-Key": valid_api_key}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["constraints"] == constraints

    def test_dreams_with_seed_and_constraints(self, client, valid_api_key):
        """Test dream generation with both seed and constraints."""
        seed = "creative_seed"
        constraints = {"max_steps": 3}
        response = client.post(
            "/v1/dreams",
            json={"seed": seed, "constraints": constraints},
            headers={"X-API-Key": valid_api_key}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["seed"] == seed
        assert data["constraints"] == constraints

    def test_dreams_none_seed(self, client, valid_api_key):
        """Test dream generation with explicit None seed."""
        response = client.post(
            "/v1/dreams",
            json={"seed": None},
            headers={"X-API-Key": valid_api_key}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["seed"] is None


class TestDreamsResponseStructure:
    """Tests for dream response structure."""

    def test_dreams_response_has_id(self, client, valid_api_key):
        """Test that response includes dream ID."""
        response = client.post(
            "/v1/dreams",
            json={},
            headers={"X-API-Key": valid_api_key}
        )

        data = response.json()
        assert "id" in data
        assert data["id"] == "dream_12345"

    def test_dreams_response_has_traces(self, client, valid_api_key):
        """Test that response includes traces array."""
        response = client.post(
            "/v1/dreams",
            json={},
            headers={"X-API-Key": valid_api_key}
        )

        data = response.json()
        assert "traces" in data
        assert isinstance(data["traces"], list)
        assert len(data["traces"]) > 0

    def test_dreams_traces_structure(self, client, valid_api_key):
        """Test that each trace has step and content."""
        response = client.post(
            "/v1/dreams",
            json={"seed": "test"},
            headers={"X-API-Key": valid_api_key}
        )

        data = response.json()
        for trace in data["traces"]:
            assert "step" in trace
            assert "content" in trace
            assert isinstance(trace["step"], int)
            assert isinstance(trace["content"], str)

    def test_dreams_response_has_model(self, client, valid_api_key):
        """Test that response includes model name."""
        response = client.post(
            "/v1/dreams",
            json={},
            headers={"X-API-Key": valid_api_key}
        )

        data = response.json()
        assert "model" in data
        assert data["model"] == "lukhas-consciousness"

    def test_dreams_response_complete_structure(self, client, valid_api_key):
        """Test complete response structure."""
        response = client.post(
            "/v1/dreams",
            json={"seed": "test", "constraints": {"max_steps": 3}},
            headers={"X-API-Key": valid_api_key}
        )

        data = response.json()
        expected_keys = {"id", "traces", "model", "seed", "constraints"}
        assert set(data.keys()) == expected_keys


class TestDreamsTraceContent:
    """Tests for dream trace content."""

    def test_dreams_includes_quantum_superposition(self, client, valid_api_key):
        """Test that first trace includes quantum superposition reference."""
        response = client.post(
            "/v1/dreams",
            json={"seed": "quantum_test"},
            headers={"X-API-Key": valid_api_key}
        )

        data = response.json()
        first_trace = data["traces"][0]
        assert "quantum superposition" in first_trace["content"]
        assert "quantum_test" in first_trace["content"]

    def test_dreams_trace_progression(self, client, valid_api_key):
        """Test that traces progress with increasing step numbers."""
        response = client.post(
            "/v1/dreams",
            json={},
            headers={"X-API-Key": valid_api_key}
        )

        data = response.json()
        steps = [trace["step"] for trace in data["traces"]]
        assert steps == sorted(steps)
        assert steps[0] == 1


class TestOpenAPISpec:
    """Tests for OpenAPI documentation."""

    def test_dreams_endpoint_has_openapi_metadata(self, app):
        """Test that dreams endpoint has OpenAPI metadata."""
        openapi = app.openapi()

        assert "/v1/dreams" in openapi["paths"]
        dreams_spec = openapi["paths"]["/v1/dreams"]["post"]
        assert "summary" in dreams_spec
        assert dreams_spec["summary"] == "Create a new dream"
        assert "200" in dreams_spec["responses"]
        assert "401" in dreams_spec["responses"]

    def test_dreams_request_schema(self, app):
        """Test that request schema is documented."""
        openapi = app.openapi()

        dreams_spec = openapi["paths"]["/v1/dreams"]["post"]
        assert "requestBody" in dreams_spec
        request_body = dreams_spec["requestBody"]
        assert "content" in request_body
        assert "application/json" in request_body["content"]


class TestErrorHandling:
    """Tests for error handling."""

    def test_dreams_invalid_json(self, client, valid_api_key):
        """Test handling of invalid JSON."""
        response = client.post(
            "/v1/dreams",
            content=b"invalid json",
            headers={
                "X-API-Key": valid_api_key,
                "Content-Type": "application/json"
            }
        )

        assert response.status_code == 422  # Unprocessable Entity

    def test_dreams_when_no_env_key_set(self, client, no_api_key):
        """Test behavior when LUKHAS_API_KEY is not set in environment."""
        response = client.post(
            "/v1/dreams",
            json={},
            headers={"X-API-Key": "any_key"}
        )

        # Should fail since env var is not set
        assert response.status_code == 401


class TestConcurrentRequests:
    """Tests for concurrent request handling."""

    def test_concurrent_dreams_generation(self, client, valid_api_key):
        """Test that multiple concurrent dream requests succeed."""
        import concurrent.futures

        def make_request(seed):
            return client.post(
                "/v1/dreams",
                json={"seed": seed},
                headers={"X-API-Key": valid_api_key}
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, f"seed_{i}") for i in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert len(results) == 10
        for response in results:
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert "traces" in data
