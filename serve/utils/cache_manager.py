import json
import logging
from typing import Any, Optional

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


class CacheManager:
    """A Redis-based cache manager with connection pooling and graceful fallbacks."""

    def __init__(self, redis_url: str, default_ttl: int = 300):
        self.default_ttl = default_ttl
        self.pool = ConnectionPool.from_url(redis_url, decode_responses=True)

    @property
    def client(self) -> redis.Redis:
        """Get a Redis client from the connection pool."""
        return redis.Redis(connection_pool=self.pool)

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache.

        Args:
            key: The cache key.

        Returns:
            The cached value, or None if the key is not found or Redis is unavailable.
        """
        try:
            cached_value = await self.client.get(key)
            if cached_value:
                return json.loads(cached_value)
        except RedisError as e:
            logger.error(f"Redis GET failed for key '{key}': {e}")
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set a value in the cache.

        Args:
            key: The cache key.
            value: The value to cache.
            ttl: The time-to-live for the cache entry in seconds.
        """
        try:
            await self.client.setex(
                key, ttl or self.default_ttl, json.dumps(value)
            )
        except RedisError as e:
            logger.error(f"Redis SET failed for key '{key}': {e}")

    async def invalidate(self, pattern: str):
        """Invalidate cache entries matching a pattern.

        Args:
            pattern: The pattern to match against cache keys.
        """
        try:
            keys = [key async for key in self.client.scan_iter(f"cache:*{pattern}*")]
            if keys:
                await self.client.delete(*keys)
        except RedisError as e:
            logger.error(f"Redis invalidate failed for pattern '{pattern}': {e}")

    async def clear_user_cache(self, user_id: str):
        """Clear all cache entries for a specific user.

        Args:
            user_id: The ID of the user whose cache should be cleared.
        """
        await self.invalidate(f"user:{user_id}:*")
