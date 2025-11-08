
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class HeadersMiddleware(BaseHTTPMiddleware):
    """Add OpenAI-compatible headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        trace_id = str(uuid.uuid4()).replace('-', '')
        response.headers['X-Trace-Id'] = trace_id
        response.headers['X-Request-Id'] = trace_id
        response.headers['X-RateLimit-Limit'] = '60'
        response.headers['X-RateLimit-Remaining'] = '59'
        response.headers['X-RateLimit-Reset'] = str(int(time.time()) + 60)
        response.headers['x-ratelimit-limit-requests'] = '60'
        response.headers['x-ratelimit-remaining-requests'] = '59'
        response.headers['x-ratelimit-reset-requests'] = str(int(time.time()) + 60)
        return response
