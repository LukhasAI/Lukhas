import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse
from starlette.types import ASGIApp
import redis
import logging

logger = logging.getLogger(__name__)

class CacheClient:
    def __init__(self):
        try:
            self.redis = redis.Redis(host="localhost", port=6379, decode_responses=True)
            self.redis.ping()
            logger.info("CacheClient connected to Redis.")
        except redis.exceptions.ConnectionError as e:
            self.redis = None
            logger.warning(f"CacheClient could not connect to Redis: {e}")
        self.default_ttl = 300  # 5 minutes

    def get_cached(self, key: str):
        if not self.redis:
            return None
        cached = self.redis.get(key)
        if cached:
            logger.debug(f"Cache HIT for key: {key}")
            return json.loads(cached)
        logger.debug(f"Cache MISS for key: {key}")
        return None

    def set_cached(self, key: str, value: dict, ttl: int = None):
        if not self.redis:
            return
        self.redis.setex(key, ttl or self.default_ttl, json.dumps(value))
        logger.debug(f"Cache SET for key: {key}")

    def invalidate(self, pattern: str):
        if not self.redis:
            return
        keys = self.redis.keys(f"cache:*{pattern}*")
        if keys:
            self.redis.delete(*keys)
            logger.info(f"Cache INVALIDATED for pattern: {pattern}, keys: {keys}")

class CacheMiddleware(BaseHTTPMiddleware):

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.cache_client = CacheClient()

    async def dispatch(self, request: Request, call_next):
        # Only cache GET requests
        if request.method != "GET":
            # Invalidate cache on any data-modifying request
            if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
                 # Invalidate based on the request's path.
                 # e.g., a POST to /v1/items/1 invalidates cache for /v1/items
                 base_path = "/".join(request.url.path.split('/')[:-1])
                 self.cache_client.invalidate(base_path)
            return await call_next(request)

        cache_key = f"cache:{request.url.path}?{request.url.query}"

        cached_response = self.cache_client.get_cached(cache_key)
        if cached_response:
            return JSONResponse(content=cached_response)

        response = await call_next(request)

        if response.status_code == 200:
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk

            try:
                # Attempt to parse body as JSON before caching
                data_to_cache = json.loads(response_body)
                self.cache_client.set_cached(cache_key, data_to_cache)
            except json.JSONDecodeError:
                # Not a JSON response, so we don't cache it.
                pass

            # Return a new response with the consumed body
            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        return response
