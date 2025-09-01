# path: qi/autonomy/approver_api.py
from __future__ import annotations

# Safe I/O (avoid sandbox recursion)
import builtins
import os

from fastapi import FastAPI, Header, HTTPException, Query

_ORIG_OPEN = builtins.open

from qi.autonomy.self_healer import (
    apply as _apply,
    approve as _approve,
    list_proposals,
    observe_signals,
    plan_proposals,
    reject as _reject,
)

API = FastAPI(title="Lukhas • Approver UI", version="1.0.0")
TOKEN = os.environ.get("AUTONOMY_API_TOKEN")  # optional bearer/token


def _auth(x_auth_token: str | None):
    if TOKEN and (x_auth_token or "") != TOKEN:
        raise HTTPException(401, "unauthorized")


@API.get("/healthz")
def healthz():
    return {"ok": True}


@API.get("/proposals")
def api_list_proposals(x_auth_token: str | None = Header(None)):
    _auth(x_auth_token)
    return {"items": list_proposals()}


@API.post("/proposals/plan")
def api_plan(
    targets: str | None = Query(None, description="comma-separated target config files"),
    x_auth_token: str | None = Header(None),
):
    _auth(x_auth_token)
    sig = observe_signals()
    props = plan_proposals(sig, config_targets=(targets.split(",") if targets else []))
    return {"planned": [p.id for p in props]}


@API.post("/proposals/{proposal_id}/approve")
def api_approve(
    proposal_id: str,
    by: str = Query(...),
    reason: str = Query(""),
    x_auth_token: str | None = Header(None),
):
    _auth(x_auth_token)
    try:
        return _approve(proposal_id, approver=by, reason=reason)
    except FileNotFoundError:
        raise HTTPException(404, "proposal not found")


@API.post("/proposals/{proposal_id}/reject")
def api_reject(
    proposal_id: str,
    by: str = Query(...),
    reason: str = Query(""),
    x_auth_token: str | None = Header(None),
):
    _auth(x_auth_token)
    try:
        return _reject(proposal_id, approver=by, reason=reason)
    except FileNotFoundError:
        raise HTTPException(404, "proposal not found")


@API.post("/proposals/{proposal_id}/apply")
def api_apply(proposal_id: str, as_user: str = Query("ops"), x_auth_token: str | None = Header(None)):
    _auth(x_auth_token)
    try:
        return _apply(proposal_id, subject_user=as_user)
    except Exception as e:
        raise HTTPException(400, str(e))
