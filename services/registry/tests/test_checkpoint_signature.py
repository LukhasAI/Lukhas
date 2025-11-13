"""Integration tests for Dilithium2 checkpoint signing."""

from __future__ import annotations

import base64
import contextlib
import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from services.registry import main as registry_main
from services.registry.main import app


def _load_sample_nodespec() -> dict[str, Any]:
    spec_path = Path("docs/schemas/examples/memory_adapter.json")
    if not spec_path.exists():
        pytest.skip("memory_adapter.json example not available")
    return json.loads(spec_path.read_text())


@pytest.fixture(autouse=True)
def reset_registry_state():
    """Ensure checkpoint artifacts are isolated per test."""

    registry_main._store.clear()
    for artifact in (
        registry_main.REGISTRY_STORE,
        registry_main.REGISTRY_SIG,
        registry_main.REGISTRY_META,
    ):
        with contextlib.suppress(FileNotFoundError):
            artifact.unlink()

    yield

    registry_main._store.clear()
    for artifact in (
        registry_main.REGISTRY_STORE,
        registry_main.REGISTRY_SIG,
        registry_main.REGISTRY_META,
    ):
        with contextlib.suppress(FileNotFoundError):
            artifact.unlink()


def test_checkpoint_signature_bundle_integrity():
    """Registry emits Dilithium2 + HMAC bundle and stores metadata."""

    client = TestClient(app)
    response = client.post("/api/v1/registry/register", json=_load_sample_nodespec())
    assert response.status_code == 200

    body = response.json()
    bundle = body["checkpoint_signature"]
    assert Path(registry_main.REGISTRY_SIG).exists()
    assert Path(registry_main.REGISTRY_META).exists()
    assert bundle["signatures"]["hmac"]["scheme"] == "HMAC-SHA256"

    payload = json.loads(registry_main.REGISTRY_STORE.read_text())
    canonical = registry_main._canonicalize_payload(payload)
    expected_hmac = registry_main._compute_legacy_hmac(canonical)
    assert bundle["signatures"]["hmac"]["signature"] == expected_hmac

    pqc_info = bundle["signatures"].get("pqc")
    if registry_main.SIGNER.pqc_available and pqc_info and pqc_info.get("signature"):
        pqc_sig = base64.b64decode(pqc_info["signature"])
        assert registry_main.SIGNER.verify(canonical, pqc_sig)
        assert bundle["mode"] == "dual"
    else:
        assert bundle["mode"] in {"dual", "hmac_only"}


def test_checkpoint_signature_tamper_detection():
    """Tampering with checkpoint data triggers verification failure on load."""

    client = TestClient(app)
    response = client.post("/api/v1/registry/register", json=_load_sample_nodespec())
    assert response.status_code == 200

    payload = json.loads(registry_main.REGISTRY_STORE.read_text())
    payload.setdefault("entries", {})["tampered::0000"] = {"node_spec": {"foo": "bar"}}
    registry_main.REGISTRY_STORE.write_text(json.dumps(payload, indent=2))

    with pytest.raises(RuntimeError, match="verification"):
        registry_main.load_checkpoint()
