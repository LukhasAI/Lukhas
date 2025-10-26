"""
Smoke test: /v1/responses endpoint stub behavior.

Validates that the /v1/responses endpoint returns proper OpenAI-compatible responses:
- Accepts both "input" and "messages" format
- Returns deterministic stub response
- Proper response envelope with id, object, choices, usage

Phase 4: P0 audit-ready implementation (Engineer Brief 2025-10-22).
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from serve.main import app

from tests.smoke.fixtures import GOLDEN_AUTH_HEADERS


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_responses_stub_with_messages(client: TestClient) -> None:
    """Verify /v1/responses accepts messages array and returns stub."""
    r = client.post(
        "/v1/responses",
        json={
            "model": "lukhas-mini",
            "messages": [{"role": "user", "content": "ping"}]
        },
        headers=GOLDEN_AUTH_HEADERS
    )
    assert r.status_code == 200

    j = r.json()
    assert j["object"] in ("chat.completion", "response"), f"Unexpected object type: {j.get('object')}"
    assert "choices" in j, "Missing 'choices' field"
    assert len(j["choices"]) > 0, "Expected at least one choice"
    assert j["choices"][0]["message"]["content"].startswith("[stub]"), \
        f"Expected [stub] prefix in response: {j['choices'][0]['message']['content']}"


def test_responses_stub_with_input(client: TestClient) -> None:
    """Verify /v1/responses accepts input field and returns stub."""
    r = client.post(
        "/v1/responses",
        json={
            "model": "lukhas-mini",
            "input": "test input"
        },
        headers=GOLDEN_AUTH_HEADERS
    )
    assert r.status_code == 200

    j = r.json()
    assert j["object"] in ("chat.completion", "response")
    assert j["choices"][0]["message"]["content"].startswith("[stub]")


def test_responses_deterministic_id(client: TestClient) -> None:
    """Verify response IDs are deterministic based on request."""
    payload = {
        "model": "lukhas-mini",
        "input": "deterministic test"
    }

    r1 = client.post("/v1/responses", json=payload, headers=GOLDEN_AUTH_HEADERS)
    r2 = client.post("/v1/responses", json=payload, headers=GOLDEN_AUTH_HEADERS)

    assert r1.status_code == 200
    assert r2.status_code == 200

    id1 = r1.json()["id"]
    id2 = r2.json()["id"]

    assert id1 == id2, f"Expected deterministic IDs, got {id1} != {id2}"
    assert id1.startswith("resp_"), f"Expected 'resp_' prefix, got {id1}"


def test_responses_usage_field_present(client: TestClient) -> None:
    """Verify response includes usage field (OpenAI parity)."""
    r = client.post(
        "/v1/responses",
        json={
            "model": "lukhas-mini",
            "input": "test"
        },
        headers=GOLDEN_AUTH_HEADERS
    )
    assert r.status_code == 200

    j = r.json()
    assert "usage" in j, "Missing 'usage' field"
    assert "prompt_tokens" in j["usage"]
    assert "completion_tokens" in j["usage"]
    assert "total_tokens" in j["usage"]


def test_responses_empty_input_handled(client: TestClient) -> None:
    """Verify empty input is handled gracefully."""
    r = client.post(
        "/v1/responses",
        json={
            "model": "lukhas-mini",
            "input": ""
        },
        headers=GOLDEN_AUTH_HEADERS
    )
    assert r.status_code == 200

    j = r.json()
    # Should return some response even for empty input
    assert "choices" in j
    assert len(j["choices"]) > 0
