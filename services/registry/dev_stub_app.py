#!/usr/bin/env python3
"""
Dev-only registry stub for CI smoke testing.

This is a minimal FastAPI app that mirrors the production registry endpoints
but operates in a fully mocked mode for CI testing. It does NOT share code
with the production registry to maintain clear separation.

Usage:
    REGISTRY_DEV_STUB=1 uvicorn services.registry.dev_stub_app:app

Environment:
    REGISTRY_DEV_STUB=1  Required to activate this stub

CI Integration:
    Only used when REGISTRY_DEV_STUB=1 is set in CI jobs
    Production code never imports or uses this module

Safety:
    - All responses marked with X-Dev-Stub: active header
    - Logs "DEV-STUB ACTIVE" on startup
    - No persistent state (in-memory only)
    - No production secrets or key material
"""

from __future__ import annotations

import json
import os
import time
import uuid
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse

# Verify we're in dev stub mode
if os.environ.get("REGISTRY_DEV_STUB") != "1":
    raise RuntimeError(
        "Dev stub app requires REGISTRY_DEV_STUB=1 environment variable. "
        "This is a safety check to prevent accidental use in production."
    )

print("=" * 80)
print("⚠️  DEV-STUB ACTIVE — Registry Development Stub Mode")
print("=" * 80)
print("This is a mock registry for CI testing only.")
print("All data is ephemeral and responses are simulated.")
print("Production registry code is NOT used.")
print("=" * 80)

app = FastAPI(
    title="LUKHAS Registry Dev Stub",
    description="Development-only mock registry for CI smoke tests",
    version="dev-stub-1.0.0",
)

# In-memory storage (ephemeral)
_registry: Dict[str, Dict[str, Any]] = {}

# Mock NodeSpec schema (simplified for dev stub)
MOCK_SCHEMA = {
    "type": "object",
    "required": ["node_id", "capabilities"],
    "properties": {
        "node_id": {"type": "string"},
        "capabilities": {"type": "array"},
        "provenance_manifest": {"type": "object", "properties": {"glymph_enabled": {"type": "boolean"}}},
    },
}


def add_dev_stub_header(response: Response) -> None:
    """Mark all responses as coming from dev stub."""
    response.headers["X-Dev-Stub"] = "active"
    response.headers["X-Dev-Stub-Version"] = "1.0.0"


@app.middleware("http")
async def dev_stub_middleware(request: Request, call_next):
    """Add dev stub markers to all responses."""
    response = await call_next(request)
    add_dev_stub_header(response)
    return response


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        {"status": "healthy", "mode": "dev-stub", "message": "Development stub is operational (CI testing only)"}
    )


@app.post("/api/v1/registry/validate")
async def validate_nodespec(request: Request):
    """
    Validate NodeSpec against schema (mocked).

    In dev stub mode, this performs minimal validation:
    - Checks for required fields (node_id, capabilities)
    - Returns success for well-formed JSON
    - Does NOT use production schema validation
    """
    try:
        nodespec = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Minimal validation (not production-grade)
    if "node_id" not in nodespec:
        raise HTTPException(status_code=400, detail="Missing required field: node_id")

    if "capabilities" not in nodespec:
        raise HTTPException(status_code=400, detail="Missing required field: capabilities")

    if not isinstance(nodespec.get("capabilities"), list):
        raise HTTPException(status_code=400, detail="capabilities must be an array")

    return JSONResponse(
        {
            "valid": True,
            "node_id": nodespec["node_id"],
            "dev_stub": True,
            "message": "NodeSpec validation passed (dev stub mode)",
        }
    )


@app.post("/api/v1/registry/register")
async def register_node(request: Request):
    """
    Register a node (mocked).

    In dev stub mode:
    - Validates basic structure
    - Generates mock registry_id
    - Stores in ephemeral memory
    - Does NOT persist to disk
    - Does NOT sign checkpoints with real crypto
    """
    try:
        nodespec = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Minimal validation
    if "node_id" not in nodespec:
        raise HTTPException(status_code=400, detail="Missing required field: node_id")

    # Check glymph_enabled (simplified check)
    provenance = nodespec.get("provenance_manifest", {})
    if not provenance.get("glymph_enabled"):
        raise HTTPException(status_code=400, detail="Registration requires provenance_manifest.glymph_enabled == true")

    # Generate mock registry_id
    registry_id = f"dev-stub-{uuid.uuid4().hex[:12]}"

    # Store in memory (ephemeral)
    _registry[registry_id] = {
        "registry_id": registry_id,
        "nodespec": nodespec,
        "registered_at": time.time(),
        "dev_stub": True,
    }

    # Mock checkpoint signature (NOT real crypto)
    mock_signature = f"MOCK-SIG-{uuid.uuid4().hex[:16]}"

    return JSONResponse(
        {
            "registry_id": registry_id,
            "node_id": nodespec["node_id"],
            "status": "registered",
            "checkpoint_signature": mock_signature,
            "dev_stub": True,
            "message": "Node registered in dev stub (ephemeral storage)",
        }
    )


@app.get("/api/v1/registry/query")
async def query_registry(signal: Optional[str] = None, capability: Optional[str] = None):
    """
    Query registered nodes (mocked).

    Returns all nodes in ephemeral storage that match query.
    In dev stub mode, this is a simple in-memory filter.
    """
    results = []

    for registry_id, entry in _registry.items():
        nodespec = entry["nodespec"]

        # Simple filtering (not production-grade)
        if capability:
            capabilities = nodespec.get("capabilities", [])
            if capability not in capabilities:
                continue

        results.append(
            {
                "registry_id": registry_id,
                "node_id": nodespec.get("node_id"),
                "capabilities": nodespec.get("capabilities", []),
                "registered_at": entry.get("registered_at"),
                "dev_stub": True,
            }
        )

    return JSONResponse(
        {
            "count": len(results),
            "results": results,
            "dev_stub": True,
            "message": f"Query returned {len(results)} nodes from dev stub",
        }
    )


@app.delete("/api/v1/registry/{registry_id}")
async def deregister_node(registry_id: str):
    """
    Deregister a node (mocked).

    Removes from ephemeral storage.
    In dev stub mode, no persistent cleanup needed.
    """
    if registry_id not in _registry:
        raise HTTPException(status_code=404, detail=f"Registry ID not found: {registry_id}")

    entry = _registry.pop(registry_id)

    return JSONResponse(
        {
            "registry_id": registry_id,
            "node_id": entry["nodespec"].get("node_id"),
            "status": "deregistered",
            "dev_stub": True,
            "message": "Node deregistered from dev stub",
        }
    )


@app.get("/api/v1/registry/stats")
async def registry_stats():
    """Dev stub statistics."""
    return JSONResponse(
        {
            "total_registered": len(_registry),
            "mode": "dev-stub",
            "storage": "ephemeral",
            "warning": "This is a development stub for CI testing only",
            "registry_ids": list(_registry.keys()),
        }
    )


if __name__ == "__main__":
    import uvicorn

    print("\n🚀 Starting Dev Stub Registry Server")
    print("⚠️  Development mode only — NOT for production use")
    print("📍 Listening on http://localhost:8000")
    print("\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
