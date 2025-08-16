# path: qi/provenance/receipts_api.py
from __future__ import annotations
import os, json, glob
from typing import Optional
from fastapi import FastAPI, HTTPException, Query

STATE = os.path.expanduser(os.environ.get("LUKHAS_STATE", "~/.lukhas/state"))
RECDIR = os.path.join(STATE, "provenance", "exec_receipts")

app = FastAPI(title="Lukhas Receipts API", version="1.0.0")

@app.get("/healthz")
def healthz(): return {"ok": True}

@app.get("/receipts/{rid}")
def get_receipt(rid: str):
    p = os.path.join(RECDIR, f"{rid}.json")
    if not os.path.exists(p):
        raise HTTPException(404, "not found")
    return json.load(open(p, "r", encoding="utf-8"))

@app.get("/receipts")
def list_receipts(limit: int = Query(20, ge=1, le=200)):
    paths = sorted(glob.glob(os.path.join(RECDIR, "*.json")), reverse=True)[:limit]
    out = []
    for p in paths:
        try:
            r = json.load(open(p, "r", encoding="utf-8"))
            out.append({"id": r.get("id"), "task": r.get("activity", {}).get("type"),
                        "created_at": r.get("created_at"), "artifact_sha": r.get("entity", {}).get("digest_sha256"),
                        "risk_flags": r.get("risk_flags", [])})
        except Exception:
            continue
    return {"items": out, "count": len(out)}