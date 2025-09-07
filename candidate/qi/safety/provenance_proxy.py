# path: qi/safety/provenance_proxy.py
from __future__ import annotations

import os
from typing import Optional

import streamlit as st
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse

from consciousness.qi import qi
from qi.safety.provenance_links import presign_for_record
from qi.safety.provenance_receipts import write_receipt
from qi.safety.provenance_uploader import load_record_by_sha

app = FastAPI(title="Lukhas Provenance Proxy", version="1.0.0")


def _get_client_ip(req: Request) -> str:
    # best-effort client IP extraction behind proxies
    xff = req.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return req.client.host if req.client else "unknown"


def _summary_record(sha: str, rec: dict) -> dict:
    return {
        "artifact_sha256": sha,
        "storage_url": rec.get("storage_url"),
        "mime_type": rec.get("mime_type"),
        "size_bytes": rec.get("size_bytes"),
        "created_at": rec.get("created_at"),
        "model_id": rec.get("model_id"),
    }


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.get("/provenance/{sha}/link")
def get_presigned_link(sha: str, request: Request, expires: int = 600, filename: str | None = None):
    try:
        rec = load_record_by_sha(sha)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Record not found for {sha}: {e}",
    )

    return {"record": _summary_record(sha, rec), "link": link}


@app.get("/provenance/{sha}/download")
def download(sha: str, request: Request, expires: int = 600, filename: str | None = None):
    try:
        rec = load_record_by_sha(sha)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Record not found for {sha}: {e}",
        )
        return FileResponse(
            path,
            filename=filename or os.path.basename(path),
            media_type=rec.get("mime_type") or "application/octet-stream",
        )

    # S3/GCS: redirect
    write_receipt(
        artifact_sha=sha,
        event="download_redirect",
        user_id=request.headers.get("x-user-id"),
        url=link.get("url"),
        client_ip=_get_client_ip(request),
        user_agent=request.headers.get("user-agent"),
        purpose=request.query_params.get("purpose"),
        extras={"backend": backend, "expires_in": link.get("expires_in")},
    )
    return RedirectResponse(link["url"], status_code=302)


@app.post("/provenance/{sha}/receipt")
async def ack_receipt(sha: str, request: Request):
    """
    Optional client-side acknowledgement, e.g., after a browser successfully opens a file.
    Body JSON (all optional): {"event":"view_ack","purpose":"...", "extras":{...}
    """
    try:
        body = await request.json()
    except Exception:
        body = {}
    event = body.get("event", "view_ack")
    purpose = body.get("purpose")
    extras = body.get("extras") or {}

    write_receipt(
        artifact_sha=sha,
        event=event,
        user_id=request.headers.get("x-user-id"),
        url=None,
        client_ip=_get_client_ip(request),
        user_agent=request.headers.get("user-agent"),
        purpose=purpose,
        extras=extras,
    )
    return {"ok": True, "sha": sha, "event": event}
