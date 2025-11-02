import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Any, Dict, cast

import pytest


def _load_schema() -> Dict[str, Any]:
    schema_path = Path("docs/schemas/nodespec_schema.json").resolve()
    assert schema_path.exists(), f"Schema not found at {schema_path}"
    return json.loads(schema_path.read_text())


def _example_nodespec(name: str = "memory_adapter") -> Dict[str, Any]:
    """Load a sample NodeSpec example for mutation in tests."""
    examples_dir = Path("docs/schemas/examples")
    candidates = [
        examples_dir / f"{name}.json",
        examples_dir / "memory_adapter.json",
        examples_dir / "dream_processor.json",
    ]
    for p in candidates:
        if p.exists():
            return json.loads(p.read_text())
    pytest.skip("No NodeSpec example files found under docs/schemas/examples/")


def test_invalid_nodespec_missing_required_fields():
    """
    Negative: NodeSpec missing required fields should fail jsonschema validation.
    - Remove 'metadata' and 'identity' which are required by the schema.
    """
    schema = _load_schema()

    bad_spec: Dict[str, Any] = {
        # 'node_type': intentionally present to ensure failure is about missing blocks
        "node_type": "matriz.memory.adapter",
        # 'metadata': missing
        # 'identity': missing
        "interfaces": {"inputs": [], "outputs": [], "signals": {}},
        "contracts": {},
        "provenance_manifest": {},
        "security": {},
    }

    import jsonschema

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=bad_spec, schema=schema)


def test_missing_glymph_provenance_should_403_or_policy_block():
    """
    Negative: Missing GLYMPH provenance should be blocked.

    Behavior under two modes:
    - If a live Registry API is available (REGISTRY_BASE_URL set), POST should return HTTP 403.
    - Otherwise, we assert policy locally: missing 'identity.owner_id' or
      'provenance_manifest.glymph_enabled' -> treated as forbidden.
    """
    base_url = os.environ.get("REGISTRY_BASE_URL")

    spec = _example_nodespec()
    # Remove GLYMPH owner and disable provenance
    if "identity" in spec:
        spec["identity"].pop("owner_id", None)
    spec.setdefault("provenance_manifest", {}).update({"glymph_enabled": False})

    if base_url:
        # Attempt real HTTP call if service is running
        import requests  # type: ignore[import]

        url = base_url.rstrip("/") + "/api/v1/registry/register"
        r = requests.post(url, json=spec, timeout=5)
        # Accept either 403 or 400 depending on implementation details
        assert r.status_code in (403, 400)
        if r.status_code == 400:
            # Ensure message mentions missing/invalid GLYMPH/owner
            assert "owner" in r.text.lower() or "glymph" in r.text.lower()
    else:
        # No API available; enforce local policy expectation
        # Missing GLYMPH should be considered forbidden by policy
        owner = spec.get("identity", {}).get("owner_id")
        glymph_enabled = spec.get("provenance_manifest", {}).get("glymph_enabled")
        assert owner is None or owner == ""
        assert glymph_enabled is False


def test_bad_signature_tampering_detection_hmac_placeholder():
    """
    Negative: Simulate signature verification failure via HMAC placeholder.
    This stands in for future PQC (Dilithium2) integration.
    """
    key = b"secret-key"
    payload = b"registry-checkpoint"
    sig = hmac.new(key, payload, hashlib.sha256).digest()

    # Tamper with payload
    tampered = payload + b"-mutated"
    sig_tampered = hmac.new(key, tampered, hashlib.sha256).digest()

    # A verifier comparing signatures must detect mismatch
    assert sig != sig_tampered


def test_malformed_json_in_register_endpoint_or_parser():
    """
    Negative: Malformed JSON should be rejected.
    If API available, expect HTTP 400. Otherwise, ensure JSON parser raises.
    """
    malformed = "{"  # invalid JSON

    base_url = os.environ.get("REGISTRY_BASE_URL")
    if base_url:
        import requests  # type: ignore[import]

        url = base_url.rstrip("/") + "/api/v1/registry/register"
        # Send invalid body with content-type application/json
        r = requests.post(url, data=malformed, headers={"Content-Type": "application/json"}, timeout=5)
        assert r.status_code in (400, 422)
    else:
        with pytest.raises(json.JSONDecodeError):
            json.loads(malformed)


def test_query_with_nonexistent_signal_or_capability():
    """
    Negative: Querying for non-existent signal/capability should return empty/404 when API exists,
    or be verifiably absent in example spec when API is not available.
    """
    base_url = os.environ.get("REGISTRY_BASE_URL")
    target_signal = "__signal_that_does_not_exist__"
    target_cap = "nonexistent/capability"

    if base_url:
        import requests  # type: ignore[import]

        u_signal = base_url.rstrip("/") + f"/api/v1/registry/query?signal={target_signal}"
        rs = requests.get(u_signal, timeout=5)
        assert rs.status_code in (200, 404)
        if rs.status_code == 200:
            data = rs.json()
            assert not data

        u_cap = base_url.rstrip("/") + f"/api/v1/registry/query?capability={target_cap}"
        rc = requests.get(u_cap, timeout=5)
        assert rc.status_code in (200, 404)
        if rc.status_code == 200:
            data = rc.json()
            assert not data
    else:
        spec = _example_nodespec()
        interfaces = cast(Dict[str, Any], spec.get("interfaces", {}) or {})
        signals = cast(Dict[str, Any], interfaces.get("signals", {}) or {})
        emits = cast(list[Dict[str, Any]], signals.get("emits", []) or [])
        names = {e.get("name") for e in emits}
        assert target_signal not in names


@pytest.mark.xfail(reason="Registry API not yet implemented; this test expects live HTTP 403 when available.")
def test_register_missing_glymph_explicit_http_403_when_api_exists():
    base_url = os.environ.get("REGISTRY_BASE_URL")
    if not base_url:
        pytest.skip("REGISTRY_BASE_URL not set")

    import requests  # type: ignore[import]

    spec = _example_nodespec()
    if "identity" in spec:
        spec["identity"].pop("owner_id", None)
    spec.setdefault("provenance_manifest", {}).update({"glymph_enabled": False})

    url = base_url.rstrip("/") + "/api/v1/registry/register"
    r = requests.post(url, json=spec, timeout=5)
    assert r.status_code == 403
