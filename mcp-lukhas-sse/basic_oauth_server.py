#!/usr/bin/env python3
"""Basic OAuth test server without FastMCP dependency."""

import logging
import os
import time

from jose import JWTError, jwt
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleOAuthMiddleware(BaseHTTPMiddleware):
    """Simple OAuth middleware for testing."""

    def __init__(self, app, oauth_secret: str = None):
        super().__init__(app)
        self.oauth_secret = oauth_secret or "test-secret-key-for-local-development-only-do-not-use-in-production"

    async def dispatch(self, request: Request, call_next):
        # Allow health check
        if request.url.path == "/health":
            return await call_next(request)

        # Check for Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                {"error": "Missing Authorization header"},
                status_code=401
            )

        # Extract token
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                {"error": "Invalid Authorization header format"},
                status_code=401
            )

        token = auth_header[7:]  # Remove "Bearer "

        # Validate JWT (skip audience validation for testing)
        try:
            payload = jwt.decode(
                token,
                self.oauth_secret,
                algorithms=['HS256'],
                options={"verify_aud": False}  # Skip audience validation for testing
            )
            logger.info(f"✅ Valid token for user: {payload.get('sub', 'unknown')}")
            # Add user info to request
            request.state.user = payload
        except JWTError as e:
            logger.warning(f"❌ Invalid token: {e}")
            return JSONResponse(
                {"error": "Invalid token"},
                status_code=403
            )

        return await call_next(request)

# Route handlers
async def health_check(request):
    """Health check endpoint (no auth required)."""
    return JSONResponse({
        "status": "healthy",
        "timestamp": time.time(),
        "service": "LUKHAS OAuth Test Server"
    })

async def sse_endpoint(request):
    """SSE endpoint (requires auth)."""
    user = getattr(request.state, 'user', {})
    return JSONResponse({
        "message": "SSE endpoint",
        "authenticated": True,
        "user": user.get('sub', 'unknown'),
        "timestamp": time.time()
    })

async def protected_endpoint(request):
    """Protected endpoint (requires auth)."""
    user = getattr(request.state, 'user', {})
    return JSONResponse({
        "message": "You are authenticated!",
        "user_id": user.get('sub'),
        "email": user.get('email'),
        "scopes": user.get('scope', '').split() if user.get('scope') else []
    })

# Create app with middleware
middleware = [
    Middleware(SimpleOAuthMiddleware)
]

routes = [
    Route("/health", health_check),
    Route("/sse/", sse_endpoint, methods=["GET", "POST"]),
    Route("/protected", protected_endpoint),
]

app = Starlette(
    debug=True,
    routes=routes,
    middleware=middleware
)

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8080))
    logger.info("=" * 50)
    logger.info("🚀 LUKHAS OAuth Test Server Starting")
    logger.info("=" * 50)
    logger.info(f"📍 Port: {port}")
    logger.info(f"📁 Allowed roots: {os.getenv('ALLOWED_ROOTS', '/tmp')}")
    logger.info(f"🔗 Health check: http://localhost:{port}/health")
    logger.info(f"🔗 SSE endpoint: http://localhost:{port}/sse/")
    logger.info(f"🔒 Protected endpoint: http://localhost:{port}/protected")
    logger.info("=" * 50)

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
