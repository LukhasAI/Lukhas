import json

from fastapi import Request
from serve.utils.cache_manager import CacheManager
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class CacheMiddleware(BaseHTTPMiddleware):
    """A caching middleware that uses a CacheManager to cache responses."""

    def __init__(self, app, cache_manager: CacheManager, default_ttl: int = 300):
        super().__init__(app)
        self.cache_manager = cache_manager
        self.default_ttl = default_ttl

    async def dispatch(self, request: Request, call_next):
        """Cache GET requests and invalidate cache for other methods."""
        if request.method != "GET":
            # Invalidate cache for mutating methods
            if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
                await self.invalidate_related_caches(request)
            return await call_next(request)

        # Skip caching for authenticated users unless explicitly enabled
        if hasattr(request.state, "user_id") and not request.headers.get(
            "X-Cache-Authenticated"
        ):
            return await call_next(request)

        cache_key = self.generate_cache_key(request)
        cached_response = await self.cache_manager.get(cache_key)
        if cached_response:
            return JSONResponse(content=cached_response)

        response = await call_next(request)

        if response.status_code == 200:
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            try:
                body_json = json.loads(response_body.decode())
                ttl = self.get_ttl_for_endpoint(request)
                if ttl > 0:
                    await self.cache_manager.set(cache_key, body_json, ttl=ttl)
                return JSONResponse(content=body_json, headers=dict(response.headers))
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass  # Don't cache non-JSON responses

        return response

    def generate_cache_key(self, request: Request) -> str:
        """Generate a cache key from the request path, query params, and headers."""
        user_id = getattr(request.state, "user_id", "anonymous")
        headers = sorted(request.headers.items())
        header_str = "&".join([f"{k}={v}" for k, v in headers])
        return f"cache:user:{user_id}:{request.url.path}?{request.query_params}&headers={header_str}"

    def get_ttl_for_endpoint(self, request: Request) -> int:
        """Get the cache TTL for a specific endpoint."""
        path = request.url.path
        if path in ["/health", "/healthz"]:
            return 60
        if path == "/metrics":
            return 30
        if path.startswith("/feedback/report/"):
            return 300
        if path == "/memory-dump/":
            return 300
        return self.default_ttl

    async def invalidate_related_caches(self, request: Request):
        """Invalidate caches related to a mutating request."""
        path = request.url.path
        if path == "/feedback/capture":
            user_id = getattr(request.state, "user_id", None)
            if user_id:
                await self.cache_manager.invalidate(f"/feedback/report/{user_id}")
        else:
            await self.cache_manager.invalidate(path)
