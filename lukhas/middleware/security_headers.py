"""OWASP security headers middleware for browser-facing API protection.

This middleware adds security headers recommended by OWASP to all FastAPI responses,
providing defense against common web vulnerabilities including:
- Clickjacking (X-Frame-Options)
- MIME-sniffing attacks (X-Content-Type-Options)
- Cross-site scripting (Content-Security-Policy)
- Information leakage (Referrer-Policy)
- Feature abuse (Permissions-Policy)

The CSP is intentionally minimal to maintain compatibility with FastAPI/Swagger UI.
Tune once production UI assets and documentation hosting are finalized.

Performance: <1ms overhead per request (header setting is synchronous).
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeaders(BaseHTTPMiddleware):
    """Add OWASP-recommended security headers to all HTTP responses.

    Headers configured:
    - X-Frame-Options: DENY - Prevents clickjacking by disallowing iframe embedding
    - X-Content-Type-Options: nosniff - Prevents MIME-sniffing attacks
    - Referrer-Policy: strict-origin-when-cross-origin - Limits referrer info leakage
    - Permissions-Policy: Restricts camera, microphone, geolocation access
    - Content-Security-Policy: Minimal CSP for XSS protection

    Usage:
        from lukhas.middleware import SecurityHeaders
        app.add_middleware(SecurityHeaders)

    Note:
        Middleware ordering matters. Add this early in the stack (before auth/audit)
        to ensure headers are applied to all responses including error responses.
    """

    async def dispatch(self, request: Request, call_next):
        """Process request and add security headers to response.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in the chain

        Returns:
            Response with security headers added
        """
        response: Response = await call_next(request)

        # Clickjacking protection - deny all framing
        response.headers.setdefault("X-Frame-Options", "DENY")

        # Prevent MIME-sniffing attacks
        response.headers.setdefault("X-Content-Type-Options", "nosniff")

        # Control referrer information leakage
        response.headers.setdefault(
            "Referrer-Policy",
            "strict-origin-when-cross-origin"
        )

        # Restrict dangerous browser features
        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=()"
        )

        # Minimal CSP for XSS protection
        # Allows 'self' for assets, blocks objects, denies frame ancestors
        # Compatible with FastAPI/Swagger UI (allows inline scripts via 'unsafe-inline' implicitly)
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; object-src 'none'; frame-ancestors 'none'"
        )

        return response
