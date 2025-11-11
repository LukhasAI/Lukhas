import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from redis.asyncio import Redis

class CacheMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.redis = Redis(host="localhost", port=6379, decode_responses=True)
        self.default_ttl = 300  # 5 minutes

    async def dispatch(self, request: Request, call_next):
        user_id = getattr(request.state, "user_id", None)
        cache_key = f"cache:{user_id}:{request.url.path}?{request.query_params}"

        if request.method == "GET":
            cached_response = await self.get_cached(cache_key)
            if cached_response:
                return JSONResponse(content=cached_response, status_code=200)

        response = await call_next(request)

        if request.method == "GET" and response.status_code == 200:
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk

            # Decode bytes to string before JSON parsing
            try:
                body_json = json.loads(response_body.decode())
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Not a valid JSON response, don't cache
                return response

            ttl_header = request.headers.get("X-Test-Cache-TTL")
            ttl = int(ttl_header) if ttl_header else None

            await self.set_cached(cache_key, body_json, ttl=ttl)

            # Return a new response as the body_iterator has been consumed
            return JSONResponse(content=body_json, status_code=response.status_code, headers=dict(response.headers))

        if request.method in ["POST", "PUT", "DELETE"]:
            # Invalidate caches for this user
            await self.invalidate(f"{user_id}:{request.url.path}")

        return response

    async def get_cached(self, key: str):
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None

    async def set_cached(self, key: str, value: dict, ttl: int = None):
        await self.redis.setex(key, ttl or self.default_ttl, json.dumps(value))

    async def invalidate(self, pattern: str):
        keys = [key async for key in self.redis.scan_iter(f"cache:*{pattern}*")]
        if keys:
            await self.redis.delete(*keys)
