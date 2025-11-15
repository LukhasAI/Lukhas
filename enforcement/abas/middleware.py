"""
enforcement.abas.middleware

General ABAS middleware (policy enforcement point) with optional JSON body excerpting.

Notes:
- Only includes a short, sanitized excerpt of JSON body (up to 1024 chars) when content-type indicates JSON.
- After reading body, the middleware re-attaches a receive() implementation so downstream handlers can read body normally.
- Conservative defaults: fail-closed when PDP unreachable (configurable).
"""

from __future__ import annotations
import os
import time
import asyncio
import hashlib
import json
from typing import Any, Dict, Optional, List
import httpx
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

OPA_URL = os.getenv("OPA_URL", "http://127.0.0.1:8181/v1/data/abas/authz/allow")
OPA_REASON_URL = os.getenv("OPA_REASON_URL", "http://127.0.0.1:8181/v1/data/abas/authz/reason")
CACHE_TTL = float(os.getenv("ABAS_CACHE_TTL", "5"))
OPA_TIMEOUT = float(os.getenv("ABAS_TIMEOUT", "2.0"))
FAIL_CLOSED = os.getenv("ABAS_FAILCLOSED", "true").lower() == "true"
SENSITIVE_PREFIXES = [p.strip() for p in os.getenv("ABAS_SENSITIVE_PREFIXES", "/admin,/v1/responses,/nias").split(",") if p.strip()]

class AsyncTTLCache:
    def __init__(self, ttl: float = CACHE_TTL):
        self.ttl = ttl
        self._store: Dict[str, Any] = {}
        self._exp: Dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            exp = self._exp.get(key)
            if exp is None or time.time() > exp:
                if key in self._store:
                    del self._store[key]
                    del self._exp[key]
                return None
            return self._store.get(key)

    async def set(self, key: str, value: Any):
        async with self._lock:
            self._store[key] = value
            self._exp[key] = time.time() + self.ttl

_cache = AsyncTTLCache()

def _cache_key(payload: Dict[str, Any]) -> str:
    j = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(j.encode("utf-8")).hexdigest()

def _is_sensitive_path(path: str) -> bool:
    if not SENSITIVE_PREFIXES:
        return True
    for p in SENSITIVE_PREFIXES:
        if path.startswith(p):
            return True
    return False

class ABASMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = str(request.url.path)
        if not _is_sensitive_path(path):
            return await call_next(request)

        caller = request.headers.get("OpenAI-Organization") or request.headers.get("X-Caller")
        caller_role = request.headers.get("X-Caller-Role") or "unknown"
        caller_verified = (request.headers.get("X-Caller-Verified") or "").lower() == "true"
        region = (request.headers.get("X-Region") or "EU").upper()

        # Safe body excerpt (JSON only). We try to read it and then restore request._receive
        body_excerpt = ""
        body_bytes = b""
        content_type = (request.headers.get("content-type") or "").lower()
        if content_type.startswith("application/json"):
            try:
                body_bytes = await request.body()
                if body_bytes:
                    # Keep only a modest excerpt to avoid leaking large content
                    btext = body_bytes.decode("utf-8", errors="ignore")
                    if len(btext) > 1024:
                        body_excerpt = btext[:1024]
                    else:
                        body_excerpt = btext
                # Reattach receive so downstream can read body as normal
                async def receive():
                    return {"type": "http.request", "body": body_bytes}
                request._receive = receive  # type: ignore
            except Exception:
                body_excerpt = ""

        payload = {
            "input": {
                "request": {"path": path, "method": request.method, "body": body_excerpt},
                "caller": caller,
                "caller_role": caller_role,
                "caller_verified": caller_verified,
                "region": region,
            }
        }

        ckey = _cache_key(payload)
        cached = await _cache.get(ckey)
        if cached is not None:
            allow = bool(cached.get("allow", False))
            reason = cached.get("reason")
            if not allow:
                return JSONResponse({"error": {"message": reason or "policy_denied", "type": "policy_denied"}}, status_code=403)
            return await call_next(request)

        try:
            async with httpx.AsyncClient(timeout=OPA_TIMEOUT) as client:
                resp = await client.post(OPA_URL, json=payload)
                resp.raise_for_status()
                result = resp.json().get("result", False)
                allow = bool(result)
                await _cache.set(ckey, {"allow": allow})
                if not allow:
                    reason = "policy_denied"
                    try:
                        r2 = await client.post(OPA_REASON_URL, json=payload, timeout=1.0)
                        if r2.status_code == 200:
                            reason = r2.json().get("result", reason)
                    except Exception:
                        pass
                    await _cache.set(ckey, {"allow": allow, "reason": reason})
                    return JSONResponse({"error": {"message": reason, "type": "policy_denied"}}, status_code=403)
        except Exception:
            if FAIL_CLOSED:
                return JSONResponse({"error": {"message": "policy unavailable", "type": "policy_error"}}, status_code=503)
            else:
                return await call_next(request)

        return await call_next(request)
