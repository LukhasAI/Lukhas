"""Security Headers Middleware - Stub Implementation"""


class SecurityHeadersMiddleware:
    """Security headers middleware."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, request, call_next):
        response = await call_next(request)
        try:
            response.headers["X-LUKHAS-Stub"] = "true"
        except Exception:
            pass
        return response


__all__ = ["SecurityHeadersMiddleware"]
