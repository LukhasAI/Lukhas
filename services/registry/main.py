"""
Minimal Hybrid Registry stub for CI smoke (TEMP-STUB, replace with PQC per MATRIZ-007).

Endpoints:
- POST   /api/v1/registry/validate   -> validates NodeSpec against docs/schemas/nodespec_schema.json
- POST   /api/v1/registry/register   -> validates + registers node (requires provenance_manifest.glymph_enabled == True)
- GET    /api/v1/registry/query      -> query by signal or capability
- DELETE /api/v1/registry/{registry_id} -> deregister
- GET    /health                     -> simple health for readiness

Notes:
- Payloads for validate/register are the NodeSpec JSON itself (not wrapped).
- Checkpoint signing uses HMAC as a visible placeholder for PQC migration.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import jsonschema
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

# Resolve repository root from this file location: services/registry/main.py
ROOT_DIR = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT_DIR / "docs" / "schemas" / "nodespec_schema.json"

REGISTRY_STORE = ROOT_DIR / "services" / "registry" / "registry_store.json"
REGISTRY_SIG = ROOT_DIR / "services" / "registry" / "checkpoint.sig"
HMAC_KEY = os.environ.get("REGISTRY_HMAC_KEY", "test-key-please-rotate")

app = FastAPI(title="LUKHΛS Hybrid Registry (Stub)")

# Load schema if present
if SCHEMA_PATH.exists():
    with SCHEMA_PATH.open() as f:
        NODE_SCHEMA = json.load(f)
else:
    NODE_SCHEMA = None

# In-memory store for runtime (persisted to REGISTRY_STORE on changes)
_store: Dict[str, Dict[str, Any]] = {}


def save_checkpoint() -> str:
    payload = {"version": int(time.time()), "ts": time.time(), "entries": _store}
    REGISTRY_STORE.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_STORE.write_text(json.dumps(payload, indent=2))
    sig = hmac.new(HMAC_KEY.encode(), REGISTRY_STORE.read_bytes(), hashlib.sha256).hexdigest()
    REGISTRY_SIG.write_text(sig)
    return sig


@app.post("/api/v1/registry/validate")
async def validate_node(req: Request):
    """Accepts a NodeSpec JSON (top-level object) and validates against schema if available."""
    try:
        node_spec = await req.json()
    except Exception as e:
        return JSONResponse(
            status_code=400, content={"valid": False, "error": f"Invalid JSON: {e}"}
        )

    if NODE_SCHEMA is None:
        # Schema missing: accept simple shape so CI can still run
        return {"valid": True, "note": "No schema found in repo: skipping strict validation"}
    try:
        jsonschema.validate(node_spec, NODE_SCHEMA)
        return {"valid": True}
    except Exception as e:
        return JSONResponse(status_code=400, content={"valid": False, "error": str(e)})


@app.post("/api/v1/registry/register")
async def register_node(req: Request):
    """Validates and registers a NodeSpec. Enforces glymph provenance flag for this stub."""
    try:
        node_spec = await req.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

    if not isinstance(node_spec, dict):
        raise HTTPException(status_code=400, detail="NodeSpec must be a JSON object")

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
    sig = save_checkpoint()
    return {"status": "accepted", "registry_id": rid, "checkpoint_sig": sig}


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
    save_checkpoint()
    return {"status": "deregistered"}


@app.get("/health")
def health():
    return {"status": "ok", "uptime": time.time()}
