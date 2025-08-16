# path: qi/provenance/receipts_api.py
from __future__ import annotations
import os, json, glob, hashlib, time
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import JSONResponse

# NEW: optional CORS (uncomment if you want browser embedding from other origins)
try:
    from fastapi.middleware.cors import CORSMiddleware  # pip install fastapi
    _HAS_CORS = True
except Exception:
    _HAS_CORS = False

# Use original open to avoid sandbox recursion
import builtins
_ORIG_OPEN = builtins.open

STATE = os.path.expanduser(os.environ.get("LUKHAS_STATE", "~/.lukhas/state"))
RECDIR = os.path.join(STATE, "provenance", "exec_receipts")

# NEW: helpers imported from trace & replay modules
from qi.trace.trace_graph import build_dot
from qi.safety.teq_replay import replay_from_receipt

app = FastAPI(title="Lukhas Receipts API", version="1.1.0")

# Optional CORS: allow your UI origin(s)
if _HAS_CORS and os.environ.get("RECEIPTS_API_CORS"):
    origins = [o.strip() for o in os.environ["RECEIPTS_API_CORS"].split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_credentials=True,
        allow_methods=["GET", "OPTIONS"],
        allow_headers=["*"],
    )

def _read_json(path: str):
    with _ORIG_OPEN(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _receipt_path(rid: str) -> str:
    p = os.path.join(RECDIR, f"{rid}.json")
    if not os.path.exists(p):
        raise HTTPException(404, "receipt not found")
    return p

def _policy_fingerprint(policy_root: str, overlays_dir: Optional[str]) -> str:
    h = hashlib.sha256()
    def add_file(fp: str):
        h.update(fp.encode()); 
        try:
            with _ORIG_OPEN(fp, "rb") as f: h.update(f.read())
        except Exception:
            pass
    for root, _, files in os.walk(policy_root):
        for fn in sorted(files):
            if fn.endswith((".yaml",".yml",".json")):
                add_file(os.path.join(root, fn))
    if overlays_dir:
        ov = os.path.join(overlays_dir, "overlays.yaml")
        if os.path.exists(ov): add_file(ov)
    return h.hexdigest()

@app.get("/healthz")
def healthz(): 
    return {"ok": True}

@app.get("/receipts/{rid}")
def get_receipt(rid: str):
    p = _receipt_path(rid)
    return _read_json(p)

@app.get("/receipts")
def list_receipts(limit: int = Query(20, ge=1, le=200)):
    paths = sorted(glob.glob(os.path.join(RECDIR, "*.json")), reverse=True)[:limit]
    out = []
    for p in paths:
        try:
            r = _read_json(p)
            out.append({"id": r.get("id"), "task": r.get("activity", {}).get("type"),
                        "created_at": r.get("created_at"), "artifact_sha": r.get("entity", {}).get("digest_sha256"),
                        "risk_flags": r.get("risk_flags", [])})
        except Exception:
            continue
    return {"items": out, "count": len(out)}

# NEW: return a fresh TEQ replay for this receipt (JSON)
@app.get("/receipts/{rid}/replay.json")
def replay_receipt(
    rid: str,
    policy_root: str = Query(..., description="Path to policy_packs root"),
    overlays: Optional[str] = Query(None, description="Path to overlays dir with overlays.yaml")
):
    p = _receipt_path(rid)
    receipt = _read_json(p)
    rep = replay_from_receipt(receipt=receipt, policy_root=policy_root, overlays_dir=overlays,
                              verify_receipt_attestation=False, verify_provenance_attestation=False)
    # weak ETag (receipt mtime + policy fingerprint)
    mtime = os.path.getmtime(p)
    etag = hashlib.sha256(f"{rid}:{mtime}:{_policy_fingerprint(policy_root, overlays)}".encode()).hexdigest()[:16]
    return JSONResponse(rep, headers={"ETag": etag})

# NEW: render clickable trace SVG (DOT export baked-in)
@app.get("/receipts/{rid}/trace.svg")
def receipt_trace_svg(
    rid: str,
    policy_root: str = Query(..., description="Path to policy_packs root"),
    overlays: Optional[str] = Query(None, description="Path to overlays dir with overlays.yaml"),
    link_base: Optional[str] = Query(None, description="Receipts API base (click target for Activity)"),
    prov_base: Optional[str] = Query(None, description="Provenance Proxy base (click target for Artifact)")
):
    # load receipt + optional provenance, build DOT, render to SVG bytes (in-memory)
    p = _receipt_path(rid)
    receipt = _read_json(p)

    # lazy provenance load (optional)
    prov = None
    try:
        from qi.safety.provenance_uploader import load_record_by_sha
        sha = (receipt.get("entity") or {}).get("digest_sha256")
        if sha:
            prov = load_record_by_sha(sha)
    except Exception:
        prov = None

    # Replay for verdict text
    rep = replay_from_receipt(receipt=receipt, policy_root=policy_root, overlays_dir=overlays,
                              verify_receipt_attestation=False, verify_provenance_attestation=False)

    dot = build_dot(receipt=receipt, prov=prov, replay=rep, link_base=link_base, prov_base=prov_base)

    # Render to SVG bytes (no temp file)
    try:
        from graphviz import Source
        svg_bytes = Source(dot).pipe(format="svg")
    except ImportError as e:
        raise HTTPException(500, f"graphviz Python package not installed: {e}")
    except Exception as e:
        if "ExecutableNotFound" in str(type(e).__name__) or "dot" in str(e):
            raise HTTPException(500, "OS graphviz not installed. Install with: brew install graphviz (macOS) or apt-get install graphviz (Linux)")
        raise HTTPException(500, f"Error rendering SVG: {e}")

    # ETag for cache (receipt mtime + policy fingerprint)
    mtime = os.path.getmtime(p)
    etag = hashlib.sha256(f"{rid}:{mtime}:{_policy_fingerprint(policy_root, overlays)}".encode()).hexdigest()[:16]
    return Response(content=svg_bytes, media_type="image/svg+xml",
                    headers={"ETag": etag, "Cache-Control": "public, max-age=60"})

# NEW: Policy fingerprint endpoint for cache/diff operations
@app.get("/policy/fingerprint")
def policy_fp(policy_root: str = Query(...), overlays: Optional[str] = Query(None)):
    return {"fingerprint": _policy_fingerprint(policy_root, overlays)}