"""Strict Authentication Middleware - Stub Implementation"""


class StrictAuthMiddleware:
    """Strict authentication middleware."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, request, call_next):
        # Stub: pass-through
        return await call_next(request)


__all__ = ["StrictAuthMiddleware"]
