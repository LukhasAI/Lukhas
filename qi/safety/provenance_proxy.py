# path: qi/safety/provenance_proxy.py
from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
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

# T4: code=F821 | ticket=SKELETON-487CA9DC | owner=lukhas-platform | status=skeleton
# reason: Undefined link in development skeleton - awaiting implementation
# estimate: 4h | priority=low | dependencies=production-implementation
    return {"record": _summary_record(sha, rec), "link": link}  # TODO: link


@app.get("/provenance/{sha}/download")
def download(sha: str, request: Request, expires: int = 600, filename: str | None = None):
    try:
        rec = load_record_by_sha(sha)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Record not found for {sha}: {e}",
        )
        return FileResponse(
# T4: code=F821 | ticket=SKELETON-9732BBF2 | owner=lukhas-platform | status=skeleton
# reason: Undefined path in development skeleton - awaiting implementation
# estimate: 4h | priority=low | dependencies=production-implementation
            path,  # TODO: path
# T4: code=F821 | ticket=SKELETON-9732BBF2 | owner=lukhas-platform | status=skeleton
# reason: Undefined path in development skeleton - awaiting implementation
# estimate: 4h | priority=low | dependencies=production-implementation
            filename=filename or os.path.basename(path),  # TODO: path
            media_type=rec.get("mime_type") or "application/octet-stream",
        )

    # S3/GCS: redirect
    write_receipt(
        artifact_sha=sha,
        event="download_redirect",
        user_id=request.headers.get("x-user-id"),
# T4: code=F821 | ticket=SKELETON-487CA9DC | owner=lukhas-platform | status=skeleton
# reason: Undefined link in development skeleton - awaiting implementation
# estimate: 4h | priority=low | dependencies=production-implementation
        url=link.get("url"),  # TODO: link
        client_ip=_get_client_ip(request),
        user_agent=request.headers.get("user-agent"),
        purpose=request.query_params.get("purpose"),
# T4: code=F821 | ticket=SKELETON-487CA9DC | owner=lukhas-platform | status=skeleton
# reason: Undefined link in development skeleton - awaiting implementation
# estimate: 4h | priority=low | dependencies=production-implementation
# T4: code=F821 | ticket=SKELETON-1A76683B | owner=lukhas-platform | status=skeleton
# reason: Undefined backend in development skeleton - awaiting implementation
# estimate: 4h | priority=low | dependencies=production-implementation
        extras={"backend": backend, "expires_in": link.get("expires_in")},  # TODO: backend
    )
# T4: code=F821 | ticket=SKELETON-487CA9DC | owner=lukhas-platform | status=skeleton
# reason: Undefined link in development skeleton - awaiting implementation
# estimate: 4h | priority=low | dependencies=production-implementation
    return RedirectResponse(link["url"], status_code=302)  # TODO: link


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
