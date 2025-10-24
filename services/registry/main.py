"""LUKHAS Hybrid Registry Prototype (TG-002).

Minimal FastAPI service that validates NodeSpec v1 and manages a hybrid
static/dynamic registry with signed checkpoints (HMAC placeholder → PQC migration).

Features:
- POST /api/v1/registry/register - Register node with GLYMPH validation
- POST /api/v1/registry/validate - Validate NodeSpec without registration
- GET /api/v1/registry/query - Query by signal or capability
- DELETE /api/v1/registry/{id} - Deregister node
- HMAC checkpoint signing (TODO: migrate to Dilithium2)
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
import time
import hmac
import hashlib
from typing import Optional
from pathlib import Path
import jsonschema

REGISTRY_FILE = Path("services/registry/registry_store.json")
SCHEMA_PATH = Path("docs/schemas/nodespec_schema.json")
HMAC_KEY = os.environ.get("REGISTRY_HMAC_KEY", "test-key-please-rotate")

app = FastAPI(title="LUKHAS Hybrid Registry (Prototype)")

# Load NodeSpec schema
with open(SCHEMA_PATH, "r") as f:
    NODE_SCHEMA = json.load(f)

# In-memory store (TODO: persist to file with checkpoints)
store = {}
checkpoint_version = 0


def save_checkpoint():
    """Save registry state with HMAC signature.

    TODO: Replace HMAC with Dilithium2 post-quantum signatures.
    """
    global checkpoint_version
    checkpoint_version += 1
    payload = {"version": checkpoint_version, "ts": time.time(), "entries": store}
    REGISTRY_FILE.write_text(json.dumps(payload, indent=2))
    sig = hmac.new(HMAC_KEY.encode(), REGISTRY_FILE.read_bytes(), hashlib.sha256).hexdigest()
    (REGISTRY_FILE.parent / "checkpoint.sig").write_text(sig)
    return sig


@app.post("/api/v1/registry/register")
async def register_node(payload: dict):
    """Register a node after validating NodeSpec and checking GLYMPH provenance.

    Args:
        payload: {"node_spec": <NodeSpec v1>, "mode": "static|dynamic"}

    Returns:
        {"status": "accepted", "registry_id": "...", "checkpoint_sig": "..."}

    Raises:
        HTTPException: 400 if schema validation fails, 403 if no GLYMPH provenance
    """
    try:
        ns = payload.get("node_spec", {})
        jsonschema.validate(ns, NODE_SCHEMA)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Schema validation failed: {e}")

    # Require GLYMPH provenance
    if not ns.get("provenance_manifest", {}).get("glymph_enabled", False):
        raise HTTPException(status_code=403, detail="Provenance GLYMPH required")

    node_id = f"{ns['metadata']['name']}::{int(time.time())}"
    store[node_id] = {"node_spec": ns, "registered_at": time.time(), "mode": payload.get("mode", "dynamic")}
    sig = save_checkpoint()
    return {"status": "accepted", "registry_id": node_id, "checkpoint_sig": sig}


@app.post("/api/v1/registry/validate")
async def validate_node(payload: dict):
    """Validate a NodeSpec without registering it.

    Args:
        payload: {"node_spec": <NodeSpec v1>}

    Returns:
        {"valid": True} or {"valid": False, "error": "..."}
    """
    try:
        jsonschema.validate(payload.get("node_spec", {}), NODE_SCHEMA)
        return {"valid": True}
    except Exception as e:
        return {"valid": False, "error": str(e)}


@app.get("/api/v1/registry/query")
async def query_registry(signal: Optional[str] = None, capability: Optional[str] = None):
    """Query registry by emitted signal or capability.

    Args:
        signal: Signal name to match (emits or subscribes)
        capability: Capability pattern to match (allow list)

    Returns:
        {"results": [{"registry_id": "...", "node_type": "...", "metadata": {...}}, ...]}
    """
    results = []
    for nid, entry in store.items():
        spec = entry["node_spec"]
        signals = spec.get("interfaces", {}).get("signals", {})
        emits = [s.get("name") for s in signals.get("emits", [])] if signals else []
        subs = [s.get("signal") for s in signals.get("subscribes", [])] if signals else []
        caps = spec.get("identity", {}).get("capabilities_policy", {}).get("allow", [])

        if (not signal or signal in emits or signal in subs) and \
           (not capability or any(capability in c for c in caps)):
            results.append({
                "registry_id": nid,
                "node_type": spec.get("node_type"),
                "metadata": spec.get("metadata")
            })
    return {"results": results}


@app.delete("/api/v1/registry/{registry_id}")
async def deregister(registry_id: str):
    """Deregister a node and save checkpoint.

    Args:
        registry_id: Node ID to deregister

    Returns:
        {"status": "deregistered"}

    Raises:
        HTTPException: 404 if node not found
    """
    if registry_id not in store:
        raise HTTPException(status_code=404, detail="Not found")
    del store[registry_id]
    save_checkpoint()
    return {"status": "deregistered"}
