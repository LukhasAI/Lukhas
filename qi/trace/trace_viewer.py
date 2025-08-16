# path: qi/trace/trace_viewer.py
from __future__ import annotations
import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response

from qi.trace.trace_graph import _load_receipt, _load_prov, _teq_replay, build_dot, render_svg, STATE

app = FastAPI(title="Lukhas Trace Viewer", version="1.0.0")

@app.get("/healthz")
def healthz(): return {"ok": True}

@app.get("/trace/{receipt_id}.svg")
def trace_svg(receipt_id: str,
              policy_root: str = Query(default="qi/safety/policy_packs"),
              overlays: Optional[str] = Query(default=None),
              link_base: Optional[str] = Query(default=None),
              prov_base: Optional[str] = Query(default=None)):
    try:
        r = _load_receipt(receipt_id, None)
        prov = _load_prov((r.get("entity") or {}).get("digest_sha256"))
        rep = _teq_replay(r, policy_root, overlays)
        dot = build_dot(receipt=r, prov=prov, replay=rep, link_base=link_base, prov_base=prov_base)
        svg_path = os.path.join(STATE, "provenance", "exec_receipts", f"{receipt_id}.svg")
        render_svg(dot, svg_path)
        data = open(svg_path, "rb").read()
        return Response(content=data, media_type="image/svg+xml")
    except FileNotFoundError:
        raise HTTPException(404, f"Receipt {receipt_id} not found")
    except Exception as e:
        raise HTTPException(500, f"Error generating trace: {str(e)}")