# path: qi/provenance/receipts_api.py
from __future__ import annotations

import glob
import hashlib
import json
import os
import random

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import HTMLResponse, JSONResponse

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
from qi.safety.teq_replay import replay_from_receipt
from qi.trace.trace_graph import build_dot

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


def _policy_fingerprint(policy_root: str, overlays_dir: str | None) -> str:
    h = hashlib.sha256()

    def add_file(fp: str):
        h.update(fp.encode())
        try:
            with _ORIG_OPEN(fp, "rb") as f:
                h.update(f.read())
        except Exception:
            pass

    for root, _, files in os.walk(policy_root):
        for fn in sorted(files):
            if fn.endswith((".yaml", ".yml", ".json")):
                add_file(os.path.join(root, fn))
    if overlays_dir:
        ov = os.path.join(overlays_dir, "overlays.yaml")
        if os.path.exists(ov):
            add_file(ov)
    return h.hexdigest()


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.get("/receipts/sample")
def receipt_sample(
    task: str | None = Query(None, description="Optional task filter"),
    window: int = Query(500, ge=1, le=5000, description="Sample among N newest receipts"),
):
    items = _load_all_receipts_meta()
    if task:
        items = [x for x in items if (x.get("task") == task)]
    items = items[:window]
    if not items:
        raise HTTPException(404, "no receipts available")
    pick = random.choice(items)
    return {"id": pick["id"], "task": pick["task"], "created_at": pick["created_at"]}


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
            out.append(
                {
                    "id": r.get("id"),
                    "task": r.get("activity", {}).get("type"),
                    "created_at": r.get("created_at"),
                    "artifact_sha": r.get("entity", {}).get("digest_sha256"),
                    "risk_flags": r.get("risk_flags", []),
                }
            )
        except Exception:
            continue
    return {"items": out, "count": len(out)}


# NEW: return a fresh TEQ replay for this receipt (JSON)
@app.get("/receipts/{rid}/replay.json")
def replay_receipt(
    rid: str,
    policy_root: str = Query(..., description="Path to policy_packs root"),
    overlays: str | None = Query(None, description="Path to overlays dir with overlays.yaml"),
):
    p = _receipt_path(rid)
    receipt = _read_json(p)
    rep = replay_from_receipt(
        receipt=receipt,
        policy_root=policy_root,
        overlays_dir=overlays,
        verify_receipt_attestation=False,
        verify_provenance_attestation=False,
    )
    # weak ETag (receipt mtime + policy fingerprint)
    mtime = os.path.getmtime(p)
    etag = hashlib.sha256(
        f"{rid}:{mtime}:{_policy_fingerprint(policy_root, overlays)}".encode()
    ).hexdigest()[:16]
    return JSONResponse(rep, headers={"ETag": etag})


# NEW: render clickable trace SVG (DOT export baked-in)
@app.get("/receipts/{rid}/trace.svg")
def receipt_trace_svg(
    rid: str,
    policy_root: str = Query(..., description="Path to policy_packs root"),
    overlays: str | None = Query(None, description="Path to overlays dir with overlays.yaml"),
    link_base: str | None = Query(
        None, description="Receipts API base (click target for Activity)"
    ),
    prov_base: str | None = Query(
        None, description="Provenance Proxy base (click target for Artifact)"
    ),
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
    rep = replay_from_receipt(
        receipt=receipt,
        policy_root=policy_root,
        overlays_dir=overlays,
        verify_receipt_attestation=False,
        verify_provenance_attestation=False,
    )

    dot = build_dot(
        receipt=receipt, prov=prov, replay=rep, link_base=link_base, prov_base=prov_base
    )

    # Render to SVG bytes (no temp file)
    try:
        from graphviz import Source

        svg_bytes = Source(dot).pipe(format="svg")
    except ImportError as e:
        raise HTTPException(500, f"graphviz Python package not installed: {e}")
    except Exception as e:
        if "ExecutableNotFound" in str(type(e).__name__) or "dot" in str(e):
            raise HTTPException(
                500,
                "OS graphviz not installed. Install with: brew install graphviz (macOS) or apt-get install graphviz (Linux)",
            )
        raise HTTPException(500, f"Error rendering SVG: {e}")

    # ETag for cache (receipt mtime + policy fingerprint)
    mtime = os.path.getmtime(p)
    etag = hashlib.sha256(
        f"{rid}:{mtime}:{_policy_fingerprint(policy_root, overlays)}".encode()
    ).hexdigest()[:16]
    return Response(
        content=svg_bytes,
        media_type="image/svg+xml",
        headers={"ETag": etag, "Cache-Control": "public, max-age=60"},
    )


# NEW: Policy fingerprint endpoint for cache/diff operations
@app.get("/policy/fingerprint")
def policy_fp(policy_root: str = Query(...), overlays: str | None = Query(None)):
    return {"fingerprint": _policy_fingerprint(policy_root, overlays)}


def _load_all_receipts_meta() -> list[dict]:
    items = []
    for p in glob.glob(os.path.join(RECDIR, "*.json")):
        try:
            r = _read_json(p)
            items.append(
                {
                    "id": r.get("id"),
                    "created_at": float(r.get("created_at", os.path.getmtime(p))),
                    "task": (r.get("activity") or {}).get("type"),
                }
            )
        except Exception:
            continue
    # newest first
    items.sort(key=lambda x: x["created_at"], reverse=True)
    return items


@app.get("/receipts/{rid}/neighbors")
def receipt_neighbors(
    rid: str, task: str | None = Query(None, description="If set, restrict prev/next to this task")
):
    items = _load_all_receipts_meta()
    if task:
        items = [x for x in items if (x.get("task") == task)]
    ids = [x["id"] for x in items if x.get("id")]
    try:
        idx = ids.index(rid)
    except ValueError:
        raise HTTPException(404, "receipt not found in current slice")
    prev_id = ids[idx - 1] if idx - 1 >= 0 else None
    next_id = ids[idx + 1] if idx + 1 < len(ids) else None
    return {"prev": prev_id, "next": next_id, "count": len(ids), "index": idx, "task": task or None}


# --- UI: single-file drilldown served by the API ---
_UI_DEFAULT = {
    "api_base": os.environ.get("RECEIPTS_API_BASE", "http://127.0.0.1:8095"),
    "policy_root": os.environ.get("RECEIPTS_POLICY_ROOT", "qi/safety/policy_packs"),
    "overlays": os.environ.get("RECEIPTS_OVERLAYS", "qi/risk"),
}

# Optional: serve from a file if you prefer (set RECEIPTS_UI_PATH to /absolute/path/to/trace_drilldown.html)
_UI_PATH = os.environ.get("RECEIPTS_UI_PATH")


@app.get("/ui/trace", response_class=HTMLResponse)
def ui_trace(
    rid: str | None = Query(None),
    api_base: str = Query(_UI_DEFAULT["api_base"]),
    policy_root: str = Query(_UI_DEFAULT["policy_root"]),
    overlays: str = Query(_UI_DEFAULT["overlays"]),
    public: bool = Query(False),
):
    # load HTML from file or fallback to embedded minimal loader that pulls the full page from disk
    if _UI_PATH and os.path.exists(_UI_PATH):
        html = _ORIG_OPEN(_UI_PATH, "r", encoding="utf-8").read()
    else:
        # Minimal bootstrap if file not provided: instructs user where to place the HTML
        html = f"""<!doctype html><html><head><meta charset='utf-8'><title>LUKHΛS • Trace Drill-down</title></head>
<body style="font-family: system-ui, sans-serif; padding: 24px; color:#e7eaf0; background:#0f1115">
  <h2>Trace Drill-down</h2>
  <p>Static UI file not found. Put your <code>web/trace_drilldown.html</code> on disk and set
     <code>RECEIPTS_UI_PATH</code> to its absolute path, or keep using the file directly.</p>
  <p>Query defaults are still passed to the page:</p>
  <pre>rid={rid or ""}\napi_base={api_base}\npolicy_root={policy_root}\noverlays={overlays}\npublic={public}</pre>
</body></html>"""
    # Inject defaults via a tiny script so the page picks them up
    inject = f"""
<script>
  window.LUKHAS_TRACE_DEFAULTS = {{
    rid: {json.dumps(rid)},
    apiBase: {json.dumps(api_base)},
    policyRoot: {json.dumps(policy_root)},
    overlays: {json.dumps(overlays)},
    publicRedact: {str(public).lower()}
  }};
</script>
"""
    # If the HTML already has </body>, inject before; else append
    if "</body>" in html:
        html = html.replace("</body>", inject + "</body>")
    else:
        html += inject
    return HTMLResponse(content=html)
