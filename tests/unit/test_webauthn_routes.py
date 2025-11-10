"""Tests for the minimal WebAuthn FastAPI routes."""

from __future__ import annotations

import importlib
import sys
from collections.abc import Callable
from typing import Any, Optional

import pytest
from fastapi.testclient import TestClient

# ΛTAG: webauthn_tests


@pytest.fixture(name="load_app")
def fixture_load_app(monkeypatch: pytest.MonkeyPatch) -> Callable[[Optional[str]], Any]:
    """Reload ``serve.main`` with the provided WebAuthn environment toggle."""

    def _loader(flag_value: Optional[str]) -> Any:
        if flag_value is None:
            monkeypatch.delenv("LUKHAS_WEBAUTHN", raising=False)
        else:
            monkeypatch.setenv("LUKHAS_WEBAUTHN", flag_value)

        module = sys.modules.get("serve.main")
        if module is None:
            module = importlib.import_module("serve.main")
        else:
            module = importlib.reload(module)
        return module.app

    return _loader


def test_webauthn_roundtrip(load_app: Callable[[Optional[str]], Any]) -> None:
    """Happy-path challenge creation and verification."""

    app = load_app("1")
    with TestClient(app) as client:
        challenge_payload = {
            "user_id": "user-123",
            "rp_id": "lukhas.ai",
            "origin": "https://lukhas.ai",
        }
        challenge_response = client.post("/id/webauthn/challenge", json=challenge_payload)
        assert challenge_response.status_code == 200
        options = challenge_response.json()
        assert options["challenge"]
        assert options["rpId"] == "lukhas.ai"

        verification_response = client.post(
            "/id/webauthn/verify",
            json={
                "response": {
                    "challenge": options["challenge"],
                    "user_verified": True,
                },
                "expected_challenge": options["challenge"],
            },
        )
        assert verification_response.status_code == 200
        assert verification_response.json() == {
            "ok": True,
            "user_verified": True,
        }


def test_webauthn_routes_disabled(load_app: Callable[[Optional[str]], Any]) -> None:
    """Routes should be unavailable when the feature flag is not enabled."""

    app = load_app(None)
    with TestClient(app) as client:
        response = client.post(
            "/id/webauthn/challenge",
            json={"user_id": "u", "rp_id": "r", "origin": "o"},
        )
        assert response.status_code == 404
