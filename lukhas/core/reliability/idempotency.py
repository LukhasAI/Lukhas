"""
Idempotency-Key support for safe request replays.

Implements in-memory cache for idempotent requests to prevent duplicate processing
of the same operation when clients retry failed requests. This is critical for
payment processing, resource creation, and other non-idempotent operations.

Features:
- Cache keyed by (route, Idempotency-Key, body-hash)
- TTL of 24 hours (86,400 seconds)
- Returns cached response for matching replays
- Thread-safe in-memory storage
- Automatic expiration of stale entries

Usage Example:
    ```python
    from lukhas.core.reliability.idempotency import cache_key, get, put
    
    # Generate cache key from request
    key = cache_key(
        route="/v1/responses",
        idem_key="req-123-abc",
        body=b'{"prompt": "Hello"}'
    )
    
    # Check for cached response
    cached = get(key)
    if cached:
        status, body, content_type = cached
        return Response(body, status_code=status, media_type=content_type)
    
    # Process request and cache result
    response = await process_request()
    put(key, response.status_code, response.body, response.media_type)
    ```

Integration with FastAPI/Starlette:
    ```python
    from starlette.requests import Request
    from starlette.responses import Response
    
    @app.post("/v1/responses")
    async def create_response(request: Request):
        # Check for idempotency key
        idem_key = request.headers.get("Idempotency-Key")
        if not idem_key:
            # Process normally without caching
            return await process_response(request)
        
        # Generate cache key
        body = await request.body()
        key = cache_key(request.url.path, idem_key, body)
        
        # Check cache
        cached = get(key)
        if cached:
            status, body_bytes, content_type = cached
            return Response(body_bytes, status_code=status, media_type=content_type)
        
        # Process and cache
        response = await process_response(request)
        response_body = response.body
        put(key, response.status_code, response_body, response.media_type)
        return response
    ```

OpenAI API Compatibility:
    Add the `Idempotency-Key` header to your requests to enable replay protection:
    
    ```bash
    curl https://api.lukhas.ai/v1/responses \
      -H "Authorization: Bearer $LUKHAS_API_KEY" \
      -H "Idempotency-Key: req-20251013-abc123" \
      -H "Content-Type: application/json" \
      -d '{"prompt": "Hello", "max_tokens": 100}'
    ```
    
    Replaying the same request within 24 hours returns the cached response
    immediately without reprocessing.

Phase 3: Added for production reliability and OpenAI API compatibility.

See Also:
    - Stripe API Idempotency: https://stripe.com/docs/api/idempotent_requests
    - OpenAI API Best Practices: https://platform.openai.com/docs/guides/production-best-practices
"""
import time
import hashlib
from typing import Dict, Tuple, Optional

_TTL = 24 * 3600  # 24h
# key -> (ts, status, body_bytes, content_type)
_cache: Dict[str, Tuple[float, int, bytes, str]] = {}


def _hash(b: bytes) -> str:
    """Compute short hash of request body."""
    return hashlib.sha256(b).hexdigest()[:16]


def cache_key(route: str, idem_key: str, body: bytes) -> str:
    """
    Generate cache key for idempotent request.
    
    Creates a unique cache key combining the route path, client-provided
    idempotency key, and a hash of the request body. This ensures that
    only truly identical requests return cached responses.

    Args:
        route: API route path (e.g., "/v1/responses", "/v1/chat/completions")
        idem_key: Client-provided Idempotency-Key header value (recommended: UUID or timestamp-based)
        body: Request body bytes (used to detect modified requests with same key)

    Returns:
        Cache key string in format: "{route}:{idem_key}:{body_hash_16}"
        
    Example:
        >>> cache_key("/v1/responses", "req-123", b'{"prompt":"Hi"}')
        '/v1/responses:req-123:a1b2c3d4e5f6g7h8'
        
    Note:
        The body hash is truncated to 16 characters for readability while
        maintaining sufficient collision resistance for typical workloads.
    """
    return f"{route}:{idem_key}:{_hash(body)}"


def get(key: str) -> Optional[Tuple[int, bytes, str]]:
    """
    Retrieve cached response if not expired.
    
    Looks up a previously cached response and validates its TTL. If the
    cached entry has expired (>24 hours old), it is automatically removed
    and None is returned.

    Args:
        key: Cache key from cache_key()

    Returns:
        (status, body_bytes, content_type) tuple or None if not cached/expired
        
    Example:
        >>> key = cache_key("/v1/responses", "req-123", b'{"prompt":"Hi"}')
        >>> put(key, 200, b'{"result":"ok"}', "application/json")
        >>> cached = get(key)
        >>> if cached:
        ...     status, body, ctype = cached
        ...     print(f"Status: {status}, Type: {ctype}")
        Status: 200, Type: application/json
        
    Thread Safety:
        This function is safe to call from multiple threads, but the in-memory
        cache is not distributed. For horizontal scaling, consider Redis backend.
    """
    item = _cache.get(key)
    if not item:
        return None

    ts, status, body, ctype = item
    if time.time() - ts > _TTL:
        _cache.pop(key, None)
        return None

    return status, body, ctype


def put(key: str, status: int, body: bytes, content_type: str) -> None:
    """
    Cache response for future replays.
    
    Stores the complete HTTP response (status, body, content-type) with
    the current timestamp for TTL validation. Subsequent requests with
    the same cache key will receive this cached response.

    Args:
        key: Cache key from cache_key()
        status: HTTP status code (e.g., 200, 201, 400)
        body: Response body bytes (JSON, text, or binary)
        content_type: Content-Type header value (e.g., "application/json")
        
    Example:
        >>> key = cache_key("/v1/responses", "req-456", b'{"prompt":"Test"}')
        >>> put(key, 201, b'{"id":"resp-123"}', "application/json")
        >>> # Future requests with same key return cached response
        
    Storage Notes:
        - In-memory storage is cleared on server restart
        - Each cached entry consumes memory proportional to body size
        - Consider Redis backend for production horizontal scaling
        - Automatic cleanup happens lazily during get() calls
    """
    _cache[key] = (time.time(), status, body, content_type)


def clear() -> None:
    """
    Clear all cached responses (useful for testing).
    
    Removes all entries from the idempotency cache. Primarily used in
    test suites to ensure test isolation and prevent cache pollution
    between test runs.
    
    Example:
        >>> # In pytest fixtures
        >>> @pytest.fixture(autouse=True)
        ... def clear_idempotency_cache():
        ...     from lukhas.core.reliability.idempotency import clear
        ...     clear()
        ...     yield
        ...     clear()  # Cleanup after test
        
    Warning:
        Do NOT call this in production code. This will invalidate all
        in-flight idempotency guarantees and could lead to duplicate
        request processing.
    """
    _cache.clear()
