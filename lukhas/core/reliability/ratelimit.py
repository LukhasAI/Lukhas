"""
Rate limiting for LUKHAS API endpoints.

Implements token bucket algorithm with per-endpoint and per-principal limits.
Keys by (route, bearer_token) or (route, ip) to prevent cross-tenant throttling.

RateLimiter keying strategy (Phase 3):
  Env LUKHAS_RL_KEYING:
  - 'route_principal' (default): key = f"{route}:{principal}"
  - 'route_only': key = route (fallback for testing or shared limits)

  Notes:
  - principal is 'tok:<sha256_16hex>' | 'ip:<addr>' | 'anonymous'
  - raw tokens are never stored (hash only, security)
"""
import hashlib
import os
import time
from collections import defaultdict
from threading import Lock
from typing import Dict, Optional, Tuple


class TokenBucket:
    """
    Token bucket rate limiter.

    Allows bursts up to capacity, refills at fixed rate.
    """

    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket.

        Args:
            capacity: Maximum tokens (burst size)
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill = time.time()
        self.lock = Lock()

    def consume(self, tokens: int = 1) -> Tuple[bool, float]:
        """
        Try to consume tokens.

        Returns:
            (success, retry_after_seconds)
        """
        with self.lock:
            now = time.time()
            elapsed = now - self.last_refill

            # Refill tokens based on elapsed time
            self.tokens = min(
                self.capacity,
                self.tokens + (elapsed * self.refill_rate)
            )
            self.last_refill = now

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True, 0.0
            else:
                # Calculate how long until enough tokens available
                needed = tokens - self.tokens
                retry_after = needed / self.refill_rate
                return False, retry_after


class RateLimiter:
    """
    Rate limiter with per-endpoint, per-principal token buckets.

    Keys by (route, bearer_token) or (route, client_ip) to isolate
    tenants and prevent cross-tenant throttling. Thread-safe for
    concurrent requests.
    """

    def __init__(self, default_rps: int = 20):
        """
        Initialize rate limiter.

        Args:
            default_rps: Default requests per second for endpoints
        """
        self.default_rps = default_rps
        self.buckets: Dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(capacity=default_rps * 2, refill_rate=default_rps)
        )
        self.lock = Lock()

    def _extract_principal(self, request) -> str:
        """
        Extract principal identifier from request.
        
        Prioritizes bearer token for tenant isolation, falls back to
        client IP address for anonymous requests.
        
        Args:
            request: FastAPI Request object
            
        Returns:
            Principal identifier (token or IP)
        """
        # Try to extract bearer token
        auth: Optional[str] = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1].strip()
            if token:
                # Hash token to avoid storing raw secrets in memory/logs/metrics
                digest = hashlib.sha256(token.encode()).hexdigest()[:16]
                return f"tok:{digest}"
        
        # Fallback to client IP (prefer X-Forwarded-For for proxies)
        xff = request.headers.get("x-forwarded-for")
        if xff:
            # Take first IP from comma-separated list
            ip = xff.split(",")[0].strip()
            if ip:
                return ip
        
        client = getattr(request, "client", None)
        if client:
            ip = getattr(client, "host", None)
            if ip:
                return ip
        
        # Last resort fallback
        return "anonymous"

    def _key_for_request(self, request) -> str:
        """
        Generate rate limit key for request.

        Key format depends on LUKHAS_RL_KEYING environment variable:
        - 'route_principal' (default): "{route}:{principal}"
        - 'route_only': "{route}" (shared limit across all users)

        The default ensures each (endpoint, tenant) pair has independent limits,
        preventing one tenant from exhausting another's quota.

        Args:
            request: FastAPI Request object

        Returns:
            Rate limit key string
        """
        strategy = os.environ.get("LUKHAS_RL_KEYING", "route_principal").lower()
        route = request.url.path

        if strategy == "route_only":
            return route

        # Default: route_principal
        principal = self._extract_principal(request)
        return f"{route}:{principal}"

    def configure_endpoint(self, endpoint: str, rps: int) -> None:
        """Configure custom rate limit for endpoint."""
        with self.lock:
            self.buckets[endpoint] = TokenBucket(
                capacity=rps * 2,  # Allow 2x burst
                refill_rate=rps
            )

    def check_limit(self, request) -> Tuple[bool, float]:
        """
        Check if request is within rate limit.
        
        Args:
            request: FastAPI Request object (used to derive key)

        Returns:
            (allowed, retry_after_seconds)
        """
        key = self._key_for_request(request)
        bucket = self.buckets[key]
        return bucket.consume(1)


def rate_limit_error(retry_after_s: float) -> dict:
    """
    Generate OpenAI-compatible rate limit error response.

    Args:
        retry_after_s: Seconds to wait before retry

    Returns:
        Error dict with headers
    """
    retry_after_int = max(1, int(retry_after_s))
    return {
        "error": {
            "type": "rate_limit_exceeded",
            "message": "Rate limit exceeded. Please retry after the specified time.",
            "retry_after": retry_after_int
        },
        "headers": {"Retry-After": str(retry_after_int)}
    }
