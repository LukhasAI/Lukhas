"""
Security headers middleware for LUKHAS API.

Implements defense-in-depth security headers:
- HSTS (Strict-Transport-Security)
- X-Content-Type-Options (nosniff)
- X-Frame-Options (DENY)
- Referrer-Policy (no-referrer)
- Content-Security-Policy (minimal for API)

Phase 3: Added as part of OpenAI surface polish.
"""
import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses.

    Args:
        hsts_max_age: Max age for HSTS in seconds (default 1 year)
        include_subdomains: Include subdomains in HSTS (default True)
    """

    def __init__(self, app, *, hsts_max_age: int = 31536000, include_subdomains: bool = True):
        super().__init__(app)
        self.hsts = f"max-age={hsts_max_age}"
        if include_subdomains:
            self.hsts += "; includeSubDomains"

    async def dispatch(self, request: Request, call_next) -> Response:
        resp = await call_next(request)

        # Transport security
        resp.headers.setdefault("Strict-Transport-Security", self.hsts)

        # MIME type sniffing protection
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")

        # Clickjacking protection
        resp.headers.setdefault("X-Frame-Options", "DENY")

        # Referrer policy
        resp.headers.setdefault("Referrer-Policy", "no-referrer")

        # Content Security Policy (minimal for API)
        # Blocks all resources, prevents framing, disables base tag
        resp.headers.setdefault(
            "Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
        )

        return resp


class VersionHeaderMiddleware(BaseHTTPMiddleware):
    """
    Add X-Service-Version header to all responses.

    Attaches git SHA or version string to responses for deployment tracking.
    Useful for correlating issues with specific deployments.

    Phase 3: Added for deployment observability.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        resp = await call_next(request)

        # Try GITHUB_SHA first (CI/CD), fall back to LUKHAS_VERSION, then "dev"
        version = (
            os.environ.get("GITHUB_SHA", "")[:7]
            or os.environ.get("LUKHAS_VERSION", "")
            or "dev"
        )

        resp.headers.setdefault("X-Service-Version", version)

        return resp
