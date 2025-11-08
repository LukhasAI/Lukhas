"""
Redis-based rate limiting backend for distributed deployments.

Implements token bucket rate limiting using Redis for state persistence
across multiple API instances. Integrates with QuotaResolver for dynamic
per-principal rate limits with fallback to environment variables.

Phase 3: Guardian enhancements for production scalability.
"""

import logging
import math
import os
import time
from typing import Optional

from core.reliability.quota_resolver import QuotaResolver

logger = logging.getLogger(__name__)

# Check if Redis is available
try:
    import redis
    from redis import Redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, RedisRateLimitBackend will be disabled")
    Redis = None  # type: ignore


class RedisRateLimitBackend:
    """
    Redis-based distributed rate limiter with quota resolver integration.

    Features:
    - Token bucket algorithm with distributed state in Redis
    - Per-principal quotas from configs/quotas.yaml
    - Fallback to env vars (LUKHAS_DEFAULT_RPS, LUKHAS_DEFAULT_BURST)
    - Atomic operations via Lua scripting for consistency
    """

    LUA_CONSUME_SCRIPT = """
    local key = KEYS[1]
    local capacity = tonumber(ARGV[1])
    local rate = tonumber(ARGV[2])
    local tokens_requested = tonumber(ARGV[3])
    local now = tonumber(ARGV[4])
    local ttl = tonumber(ARGV[5])

    -- Get current bucket state
    local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
    local tokens = tonumber(bucket[1]) or capacity
    local last_refill = tonumber(bucket[2]) or now

    -- Refill tokens based on elapsed time
    local elapsed = math.max(0, now - last_refill)
    tokens = math.min(capacity, tokens + (elapsed * rate))

    -- Try to consume tokens
    local allowed = 0
    local retry_after = 0

    if tokens >= tokens_requested then
        tokens = tokens - tokens_requested
        allowed = 1
    else
        -- Calculate retry time
        local needed = tokens_requested - tokens
        retry_after = needed / rate
    end

    -- Update bucket state
    redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
    redis.call('EXPIRE', key, ttl)

    return {allowed, retry_after, tokens, capacity}
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        quota_resolver: Optional[QuotaResolver] = None,
        key_prefix: str = "lukhas:ratelimit:",
        ttl_seconds: int = 300,
    ):
        """
        Initialize Redis rate limit backend.

        Args:
            redis_url: Redis connection URL (default: env REDIS_URL or localhost)
            quota_resolver: QuotaResolver for dynamic quotas (optional)
            key_prefix: Redis key prefix for rate limit keys
            ttl_seconds: TTL for rate limit keys in Redis
        """
        if not REDIS_AVAILABLE:
            raise RuntimeError("Redis is not installed, cannot use RedisRateLimitBackend")

        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.key_prefix = key_prefix
        self.ttl_seconds = ttl_seconds

        # Initialize Redis client
        try:
            self.redis: Redis = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self.redis.ping()
            logger.info(f"Redis connection established: {self.redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis at {self.redis_url}: {e}")
            raise

        # Initialize quota resolver (or create default)
        self.quota_resolver = quota_resolver or QuotaResolver()

        # Load Lua script
        try:
            self.consume_script = self.redis.register_script(self.LUA_CONSUME_SCRIPT)
            logger.info("Redis Lua consume script registered")
        except Exception as e:
            logger.error(f"Failed to register Lua script: {e}")
            raise

    def check_limit(self, key: str, tokens: int = 1) -> tuple[bool, float]:
        """
        Check rate limit and consume tokens if allowed.

        Args:
            key: Rate limit key (format: "route:principal")
            tokens: Number of tokens to consume (default: 1)

        Returns:
            (allowed, retry_after_seconds) tuple
        """
        # Resolve quota for this key
        rps, burst = self.quota_resolver.get_quota_for_key(key)

        # Build Redis key
        redis_key = f"{self.key_prefix}{key}"
        now = time.time()

        try:
            # Execute Lua script atomically
            result = self.consume_script(
                keys=[redis_key], args=[burst, rps, tokens, now, self.ttl_seconds]
            )

            allowed = bool(result[0])
            retry_after = float(result[1])

            return allowed, retry_after

        except Exception as e:
            logger.error(f"Redis rate limit check failed for {key}: {e}", exc_info=True)
            # Fail open on Redis errors (allow request but log)
            return True, 0.0

    def current_window(self, key: str) -> dict:
        """
        Get current token bucket state for a key.

        Args:
            key: Rate limit key

        Returns:
            Dictionary with limit, remaining, and reset_seconds
        """
        rps, burst = self.quota_resolver.get_quota_for_key(key)
        redis_key = f"{self.key_prefix}{key}"

        try:
            bucket = self.redis.hmget(redis_key, "tokens", "last_refill")
            tokens = float(bucket[0]) if bucket[0] else float(burst)
            last_refill = float(bucket[1]) if bucket[1] else time.time()

            # Apply passive refill
            now = time.time()
            elapsed = max(0.0, now - last_refill)
            tokens = min(burst, tokens + (elapsed * rps))

            # Calculate reset time
            reset_seconds = 0.0 if tokens >= burst or rps <= 0 else (burst - tokens) / rps

            return {
                "limit": float(burst),
                "remaining": float(math.floor(tokens)),
                "reset_seconds": float(round(reset_seconds, 3)),
            }

        except Exception as e:
            logger.error(f"Failed to get window for {key}: {e}")
            # Return safe defaults
            return {
                "limit": float(burst),
                "remaining": float(burst),
                "reset_seconds": 0.0,
            }

    def is_healthy(self) -> bool:
        """
        Check if Redis backend is healthy and available.

        Returns:
            True if Redis is reachable, False otherwise
        """
        try:
            self.redis.ping()
            return True
        except Exception as e:
            logger.debug(f"Redis health check failed: {e}")
            return False

    def get_stats(self) -> dict:
        """
        Get Redis backend statistics for monitoring.

        Returns:
            Dictionary with connection status and key count
        """
        try:
            info = self.redis.info("stats")
            key_pattern = f"{self.key_prefix}*"
            key_count = len(self.redis.keys(key_pattern))

            return {
                "connected": True,
                "url": self.redis_url,
                "total_keys": key_count,
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
            }
        except Exception as e:
            logger.error(f"Failed to get Redis stats: {e}")
            return {
                "connected": False,
                "error": str(e),
            }
