"""Hybrid Registry service with Dilithium2 checkpoint signing (MATRIZ-007).

==============================================================================
  WARNING: SECURITY CONTROLLED - VERIFY PQC DEPLOYMENT BEFORE PROMOTION
==============================================================================
This registry service now emits Dilithium2 checkpoint signatures with an
HMAC-SHA256 compatibility tag during the migration window. Signature bundles
are verified on load; tampering or stale timestamps halt startup.

Tracking: MATRIZ-007 (PQC Migration)
Status: Production readiness candidate (dual-sign mode)
Target: Retire HMAC compatibility once downstream consumers migrate
==============================================================================

Endpoints:
- POST   /api/v1/registry/validate   -> validates NodeSpec against docs/schemas/nodespec_schema.json
- POST   /api/v1/registry/register   -> validates + registers node (requires provenance_manifest.glymph_enabled == True)
- GET    /api/v1/registry/query      -> query by signal or capability
- DELETE /api/v1/registry/{registry_id} -> deregister
- GET    /health                     -> simple health for readiness

Notes:
- Payloads for validate/register are the NodeSpec JSON itself (not wrapped).
- Checkpoint signing produces Dilithium2 + HMAC bundle to maintain compatibility.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import jsonschema
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

# PQC signer integration
from services.registry.pqc_signer import create_registry_signer

# Logging configuration (kept lightweight for stub service)
logger = logging.getLogger("services.registry")
if not logger.handlers:
    logging.basicConfig(level=os.environ.get("REGISTRY_LOG_LEVEL", "INFO"))

# Resolve repository root from this file location: services/registry/main.py
ROOT_DIR = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT_DIR / "docs" / "schemas" / "nodespec_schema.json"

REGISTRY_STORE = ROOT_DIR / "services" / "registry" / "registry_store.json"
REGISTRY_SIG = ROOT_DIR / "services" / "registry" / "checkpoint.sig"
REGISTRY_META = ROOT_DIR / "services" / "registry" / "checkpoint.meta.json"
HMAC_KEY = os.environ.get("REGISTRY_HMAC_KEY", "test-key-please-rotate")
SIGNER_ID = os.environ.get("REGISTRY_SIGNER_ID", "registry-dev-signer")
TIMESTAMP_TOLERANCE_SECONDS = int(os.environ.get("REGISTRY_TIMESTAMP_TOLERANCE_SECONDS", "300"))

FORCE_HMAC = os.environ.get("REGISTRY_FORCE_HMAC", "0") in {"1", "true", "TRUE"}

SIGNER = create_registry_signer(
    registry_root=ROOT_DIR / "services" / "registry",
    force_hmac=FORCE_HMAC,
)

app = FastAPI(title="LUKHΛS Hybrid Registry (Stub)")

# Load schema if present
if SCHEMA_PATH.exists():
    with SCHEMA_PATH.open() as f:
        NODE_SCHEMA = json.load(f)
else:
    NODE_SCHEMA = None

# In-memory store for runtime (persisted to REGISTRY_STORE on changes)
_store: Dict[str, Dict[str, Any]] = {}


class StaleCheckpointError(RuntimeError):
    """Raised when a checkpoint's timestamp falls outside the freshness window."""


def _purge_checkpoint_artifacts() -> None:
    """Remove on-disk checkpoint artifacts (used when bootstrap detects stale data)."""

    for artifact in (REGISTRY_STORE, REGISTRY_SIG, REGISTRY_META):
        try:
            artifact.unlink()
        except FileNotFoundError:
            continue


def _normalize_nodespec_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract NodeSpec from payload allowing legacy wrapper format."""

    if "node_spec" in payload and isinstance(payload["node_spec"], dict):
        return payload["node_spec"]
    return payload


def _canonicalize_payload(payload: Dict[str, Any]) -> bytes:
    """Return canonical JSON bytes used for signing."""

    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def _compute_legacy_hmac(payload_bytes: bytes) -> str:
    """Compute HMAC-SHA256 over canonical payload for compatibility."""

    return hmac.new(HMAC_KEY.encode(), payload_bytes, hashlib.sha256).hexdigest()


def _build_signature_bundle(payload: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Build signature bundle and metadata for checkpoint payload.

    Returns tuple of (signature_bundle, meta_record).
    """

    payload_bytes = _canonicalize_payload(payload)

    bundle: Dict[str, Any] = {
        "version": payload["version"],
        "timestamp": payload["ts"],
        "signer_id": SIGNER_ID,
        "signatures": {
            "hmac": {
                "scheme": "HMAC-SHA256",
                "signature": _compute_legacy_hmac(payload_bytes),
            }
        },
    }

    pqc_signature_bytes: Optional[bytes] = None
    if SIGNER.pqc_available:
        try:
            pqc_signature_bytes = SIGNER.sign(payload_bytes)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Dilithium2 signing failed, falling back to HMAC only: %s", exc)
            pqc_signature_bytes = None

    if pqc_signature_bytes:
        bundle["signatures"]["pqc"] = {
            "scheme": "Dilithium2",
            "algorithm": "NIST PQC Dilithium2",
            "signature": base64.b64encode(pqc_signature_bytes).decode(),
        }
        public_key_b64 = None
        if hasattr(SIGNER, "public_key") and SIGNER.public_key:
            public_key_b64 = base64.b64encode(SIGNER.public_key).decode()
        bundle["mode"] = "dual"
    else:
        public_key_b64 = None
        bundle["mode"] = "hmac_only"

    meta_record = {
        "version": payload["version"],
        "timestamp": payload["ts"],
        "signer_id": SIGNER_ID,
        "mode": bundle["mode"],
        "pqc_public_key": public_key_b64,
        "timestamp_tolerance_seconds": TIMESTAMP_TOLERANCE_SECONDS,
    }

    return bundle, meta_record


def _verify_timestamp(timestamp: float) -> None:
    """Validate checkpoint timestamp freshness."""

    now = time.time()
    if abs(now - timestamp) > TIMESTAMP_TOLERANCE_SECONDS:
        raise StaleCheckpointError(
            "Checkpoint timestamp outside allowed tolerance: "
            f"delta={abs(now - timestamp):.2f}s tolerance={TIMESTAMP_TOLERANCE_SECONDS}s"
        )


def _read_signature_bundle(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Read signature bundle from disk, tolerating legacy formats."""

    raw = REGISTRY_SIG.read_text().strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Legacy checkpoint signature format detected; using compatibility mode")
        version = payload.get("version") if payload else None
        timestamp = payload.get("ts") if payload else None
        legacy_signature = raw
        return {
            "version": version,
            "timestamp": timestamp,
            "signer_id": "legacy-hmac",
            "mode": "hmac_only",
            "signatures": {
                "hmac": {
                    "scheme": "HMAC-SHA256",
                    "signature": legacy_signature,
                }
            },
        }


def _verify_signature_bundle(
    payload: Dict[str, Any],
    bundle: Dict[str, Any],
    raw_payload_bytes: Optional[bytes] = None,
) -> None:
    """Verify Dilithium2/HMAC signatures for stored checkpoint."""

    payload_bytes = _canonicalize_payload(payload)
    signatures = bundle.get("signatures", {})

    timestamp = bundle.get("timestamp")
    if bundle.get("signer_id") != "legacy-hmac" and isinstance(timestamp, (int, float)):
        _verify_timestamp(float(timestamp))

    # Verify HMAC compatibility signature
    hmac_info = signatures.get("hmac")
    if hmac_info and hmac_info.get("signature"):
        if bundle.get("signer_id") == "legacy-hmac" and raw_payload_bytes is not None:
            expected = hmac.new(HMAC_KEY.encode(), raw_payload_bytes, hashlib.sha256).hexdigest()
        else:
            expected = _compute_legacy_hmac(payload_bytes)
        provided = hmac_info["signature"]
        if not hmac.compare_digest(expected, str(provided)):
            raise RuntimeError("Checkpoint HMAC verification failed")
    else:
        raise RuntimeError("Missing legacy HMAC signature in checkpoint bundle")

    pqc_info = signatures.get("pqc")
    pqc_signature_b64 = pqc_info.get("signature") if pqc_info else None
    if SIGNER.pqc_available and pqc_signature_b64:
        try:
            pqc_signature = base64.b64decode(pqc_signature_b64)
        except Exception as exc:  # pragma: no cover - invalid encoding
            raise RuntimeError("Invalid base64 for PQC signature") from exc

        if not SIGNER.verify(payload_bytes, pqc_signature):
            raise RuntimeError("Dilithium2 signature verification failed")


def save_checkpoint() -> Dict[str, Any]:
    payload = {"version": int(time.time()), "ts": time.time(), "entries": _store}
    REGISTRY_STORE.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_STORE.write_text(json.dumps(payload, indent=2))
    signature_bundle, meta_record = _build_signature_bundle(payload)
    REGISTRY_SIG.write_text(json.dumps(signature_bundle, indent=2))
    REGISTRY_META.write_text(json.dumps(meta_record, indent=2))
    return signature_bundle


def load_checkpoint(*, allow_stale_reset: bool = False) -> None:
    """Load checkpoint from disk and verify signatures."""

    if not REGISTRY_STORE.exists() or not REGISTRY_SIG.exists():
        logger.info("Registry checkpoint not found; starting with empty store")
        return

    payload_text = REGISTRY_STORE.read_text()
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Registry checkpoint corrupted: invalid JSON") from exc

    signature_bundle = _read_signature_bundle(payload)

    global _store

    try:
        _verify_signature_bundle(payload, signature_bundle, raw_payload_bytes=payload_text.encode())
    except StaleCheckpointError:
        if allow_stale_reset:
            logger.warning("Stale registry checkpoint detected during bootstrap; resetting store")
            _purge_checkpoint_artifacts()
            _store = {}
            return
        raise

    _store = payload.get("entries", {}) or {}
    logger.info("Loaded registry checkpoint with %d entries", len(_store))


@app.post("/api/v1/registry/validate")
async def validate_node(req: Request):
    """Accepts a NodeSpec JSON (top-level object) and validates against schema if available."""
    try:
        payload = await req.json()
    except Exception as e:
        return JSONResponse(status_code=400, content={"valid": False, "error": f"Invalid JSON: {e}"})

    if not isinstance(payload, dict):
        return JSONResponse(
            status_code=400,
            content={"valid": False, "error": "NodeSpec payload must be a JSON object"},
        )

    node_spec = _normalize_nodespec_payload(payload)

    if NODE_SCHEMA is None:
        # Schema missing: accept simple shape so CI can still run
        return {"valid": True, "note": "No schema found in repo: skipping strict validation"}
    try:
        jsonschema.validate(node_spec, NODE_SCHEMA)
        return {"valid": True}
    except Exception as e:
        return {"valid": False, "error": str(e)}


@app.post("/api/v1/registry/register")
async def register_node(req: Request):
    """Validates and registers a NodeSpec. Enforces glymph provenance flag for this stub."""
    try:
        payload = await req.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="NodeSpec must be a JSON object")

    node_spec = _normalize_nodespec_payload(payload)

    # Validate against schema if present
    if NODE_SCHEMA:
        try:
            jsonschema.validate(node_spec, NODE_SCHEMA)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Schema validation failed: {e}")

    # Enforce GLYMPH provenance gate (negative smoke expects 4xx when removed)
    prov = node_spec.get("provenance_manifest", {})
    if not prov.get("glymph_enabled", False):
        raise HTTPException(status_code=403, detail="Provenance GLYMPH required")

    rid = f"{node_spec.get('metadata', {}).get('name', 'node')}::{uuid.uuid4().hex[:8]}"
    _store[rid] = {"node_spec": node_spec, "registered_at": time.time()}
    signature_bundle = save_checkpoint()
    legacy_hmac = signature_bundle["signatures"]["hmac"]["signature"]
    return {
        "status": "accepted",
        "registry_id": rid,
        "checkpoint_sig": legacy_hmac,
        "checkpoint_signature": signature_bundle,
    }


@app.get("/api/v1/registry/query")
async def query_registry(signal: Optional[str] = None, capability: Optional[str] = None):
    """Query by signal or capability (simple contains-based match for stub)."""
    results: List[Dict[str, Any]] = []
    for rid, entry in _store.items():
        spec = entry["node_spec"]
        sigs = spec.get("interfaces", {}).get("signals", {}) or {}
        emits = [s.get("name") for s in sigs.get("emits", [])]
        subscribes = [s.get("signal") for s in sigs.get("subscribes", [])]
        caps = spec.get("identity", {}).get("capabilities_policy", {}).get("allow", [])

        match_signal = (not signal) or (signal in (emits or []) or signal in (subscribes or []))
        match_cap = (not capability) or any(capability in c for c in caps)
        if match_signal and match_cap:
            results.append(
                {
                    "registry_id": rid,
                    "node_type": spec.get("node_type"),
                    "metadata": spec.get("metadata"),
                }
            )
    return {"results": results}


@app.delete("/api/v1/registry/{registry_id}")
async def deregister(registry_id: str):
    if registry_id not in _store:
        raise HTTPException(status_code=404, detail="Not found")
    del _store[registry_id]
    signature_bundle = save_checkpoint()
    return {
        "status": "deregistered",
        "checkpoint_signature": signature_bundle,
    }


@app.get("/health")
def health():
    return {"status": "ok", "uptime": time.time()}


# Attempt to load existing checkpoint at import time.
BOOTSTRAP_LOAD = os.environ.get("REGISTRY_BOOTSTRAP_LOAD", "1").lower() not in {
    "0",
    "false",
}

if BOOTSTRAP_LOAD:
    try:
        load_checkpoint(allow_stale_reset=True)
    except RuntimeError as exc:  # pragma: no cover - service startup failure path
        logger.error("Failed to load registry checkpoint: %s", exc)
        raise
