# path: qi/autonomy/approver_api.py
from __future__ import annotations
import os, json
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.responses import JSONResponse

# Safe I/O (avoid sandbox recursion)
import builtins
_ORIG_OPEN = builtins.open

from qi.autonomy.self_healer import (
    list_proposals, approve as _approve, reject as _reject, apply as _apply,
    observe_signals, plan_proposals
)

API = FastAPI(title="Lukhas • Approver UI", version="1.0.0")
TOKEN = os.environ.get("AUTONOMY_API_TOKEN")  # optional bearer/token

def _auth(x_auth_token: Optional[str]):
    if TOKEN and (x_auth_token or "") != TOKEN:
        raise HTTPException(401, "unauthorized")

@API.get("/healthz")
def healthz(): return {"ok": True}

@API.get("/proposals")
def api_list_proposals(x_auth_token: Optional[str] = Header(None)):
    _auth(x_auth_token); 
    return {"items": list_proposals()}

@API.post("/proposals/plan")
def api_plan(
    targets: Optional[str] = Query(None, description="comma-separated target config files"),
    x_auth_token: Optional[str] = Header(None),
):
    _auth(x_auth_token)
    sig = observe_signals()
    props = plan_proposals(sig, config_targets=(targets.split(",") if targets else []))
    return {"planned": [p.id for p in props]}

@API.post("/proposals/{proposal_id}/approve")
def api_approve(proposal_id: str, by: str = Query(...), reason: str = Query(""), x_auth_token: Optional[str] = Header(None)):
    _auth(x_auth_token)
    try:
        return _approve(proposal_id, approver=by, reason=reason)
    except FileNotFoundError:
        raise HTTPException(404, "proposal not found")

@API.post("/proposals/{proposal_id}/reject")
def api_reject(proposal_id: str, by: str = Query(...), reason: str = Query(""), x_auth_token: Optional[str] = Header(None)):
    _auth(x_auth_token)
    try:
        return _reject(proposal_id, approver=by, reason=reason)
    except FileNotFoundError:
        raise HTTPException(404, "proposal not found")

@API.post("/proposals/{proposal_id}/apply")
def api_apply(proposal_id: str, as_user: str = Query("ops"), x_auth_token: Optional[str] = Header(None)):
    _auth(x_auth_token)
    try:
        return _apply(proposal_id, subject_user=as_user)
    except Exception as e:
        raise HTTPException(400, str(e))