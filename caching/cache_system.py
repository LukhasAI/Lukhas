#!/usr/bin/env python3
"""
LUKHAS Advanced Caching System

Enterprise-grade distributed caching with Redis support, intelligent cache warming,
hierarchical cache layers, and performance optimization.

# ΛTAG: caching_system, redis_integration, cache_warming, distributed_cache, performance_optimization
"""

import asyncio
import hashlib
import json
import logging
import pickle
import statistics
import time
import zlib
from abc import ABC, abstractmethod
from collections import OrderedDict, defaultdict
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

# Optional Redis integration
try:
    import aioredis
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available - using in-memory caching only")


class CacheLevel(Enum):
    """Cache hierarchy levels."""
    L1_MEMORY = "l1_memory"      # In-process memory cache
    L2_REDIS = "l2_redis"        # Redis distributed cache
    L3_PERSISTENT = "l3_persistent"  # Persistent storage cache


class CacheStrategy(Enum):
    """Cache replacement strategies."""
    LRU = "lru"                  # Least Recently Used
    LFU = "lfu"                  # Least Frequently Used
    FIFO = "fifo"                # First In, First Out
    TTL = "ttl"                  # Time To Live based
    ADAPTIVE = "adaptive"         # Adaptive based on access patterns


class CacheEventType(Enum):
    """Cache event types for monitoring."""
    HIT = "hit"
    MISS = "miss"
    SET = "set"
    DELETE = "delete"
    EXPIRE = "expire"
    EVICT = "evict"
    WARM = "warm"


@dataclass
class CacheConfig:
    """Configuration for caching system."""

    # Memory cache settings
    l1_max_size: int = 1000
    l1_ttl_seconds: int = 300  # 5 minutes
    l1_strategy: CacheStrategy = CacheStrategy.LRU

    # Redis cache settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_ssl: bool = False
    redis_max_connections: int = 10
    l2_ttl_seconds: int = 3600  # 1 hour

    # Persistent cache settings
    l3_ttl_seconds: int = 86400  # 24 hours
    persistent_storage_path: str = "/tmp/lukhas_cache"

    # Performance settings
    compression_enabled: bool = True
    compression_threshold: int = 1024  # Compress data > 1KB
    serialization_format: str = "pickle"  # pickle, json, msgpack

    # Cache warming settings
    warming_enabled: bool = True
    warming_batch_size: int = 100
    warming_interval_seconds: int = 300  # 5 minutes

    # Monitoring settings
    metrics_enabled: bool = True
    statistics_window_minutes: int = 60

    # Advanced features
    hierarchical_caching: bool = True
    write_through: bool = False
    write_behind: bool = True
    invalidation_patterns: List[str] = field(default_factory=list)


@dataclass
class CacheEntry:
    """Cache entry with metadata."""

    key: str
    value: Any
    created_at: float
    last_accessed: float
    access_count: int
    ttl_seconds: Optional[int]
    size_bytes: int
    compression_used: bool = False

    def is_expired(self, current_time: Optional[float] = None) -> bool:
        """Check if entry is expired."""
        if self.ttl_seconds is None:
            return False

        if current_time is None:
            current_time = time.time()

        return (current_time - self.created_at) > self.ttl_seconds

    def age_seconds(self, current_time: Optional[float] = None) -> float:
        """Get age of entry in seconds."""
        if current_time is None:
            current_time = time.time()
        return current_time - self.created_at

    def update_access(self, current_time: Optional[float] = None) -> None:
        """Update access statistics."""
        if current_time is None:
            current_time = time.time()
        self.last_accessed = current_time
        self.access_count += 1


@dataclass
class CacheStatistics:
    """Cache performance statistics."""

    total_requests: int = 0
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0

    # Performance metrics
    average_response_time_ms: float = 0.0
    hit_ratio: float = 0.0
    memory_usage_bytes: int = 0
    entry_count: int = 0

    # Recent activity
    recent_requests: List[float] = field(default_factory=list)
    recent_response_times: List[float] = field(default_factory=list)

    def update_hit(self, response_time_ms: float) -> None:
        """Update hit statistics."""
        self.hits += 1
        self.total_requests += 1
        self._update_performance_metrics(response_time_ms)

    def update_miss(self, response_time_ms: float) -> None:
        """Update miss statistics."""
        self.misses += 1
        self.total_requests += 1
        self._update_performance_metrics(response_time_ms)

    def _update_performance_metrics(self, response_time_ms: float) -> None:
        """Update performance metrics."""
        current_time = time.time()

        # Update response times
        self.recent_response_times.append(response_time_ms)
        if len(self.recent_response_times) > 1000:
            self.recent_response_times = self.recent_response_times[-500:]

        # Update recent requests
        self.recent_requests.append(current_time)
        if len(self.recent_requests) > 1000:
            self.recent_requests = self.recent_requests[-500:]

        # Calculate averages
        if self.recent_response_times:
            self.average_response_time_ms = statistics.mean(self.recent_response_times)

        if self.total_requests > 0:
            self.hit_ratio = self.hits / self.total_requests

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total_requests": self.total_requests,
            "hits": self.hits,
            "misses": self.misses,
            "sets": self.sets,
            "deletes": self.deletes,
            "evictions": self.evictions,
            "average_response_time_ms": self.average_response_time_ms,
            "hit_ratio": self.hit_ratio,
            "memory_usage_bytes": self.memory_usage_bytes,
            "entry_count": self.entry_count,
            "requests_per_second": len([
                t for t in self.recent_requests
                if time.time() - t < 1.0
            ])
        }


class CacheBackend(ABC):
    """Abstract cache backend interface."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value by key."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set key-value pair."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete key."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache entries."""
        pass

    @abstractmethod
    async def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern."""
        pass

    @abstractmethod
    async def size(self) -> int:
        """Get number of entries."""
        pass


class MemoryCacheBackend(CacheBackend):
    """In-memory cache backend with configurable eviction strategies."""

    def __init__(self,
                 max_size: int = 1000,
                 default_ttl: int = 300,
                 strategy: CacheStrategy = CacheStrategy.LRU):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.strategy = strategy

        # Storage
        self.entries: Dict[str, CacheEntry] = {}
        self.access_order: OrderedDict = OrderedDict()  # For LRU
        self.access_frequency: Dict[str, int] = defaultdict(int)  # For LFU

        # Statistics
        self.statistics = CacheStatistics()

    async def get(self, key: str) -> Optional[Any]:
        """Get value by key."""
        start_time = time.time()

        if key not in self.entries:
            self.statistics.update_miss((time.time() - start_time) * 1000)
            return None

        entry = self.entries[key]

        # Check expiration
        if entry.is_expired():
            await self.delete(key)
            self.statistics.update_miss((time.time() - start_time) * 1000)
            return None

        # Update access statistics
        entry.update_access()
        self._update_access_tracking(key)

        self.statistics.update_hit((time.time() - start_time) * 1000)
        return entry.value

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set key-value pair."""

        if ttl_seconds is None:
            ttl_seconds = self.default_ttl

        # Calculate size
        try:
            size_bytes = len(pickle.dumps(value))
        except Exception:
            size_bytes = len(str(value).encode())

        current_time = time.time()

        # Create cache entry
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=current_time,
            last_accessed=current_time,
            access_count=1,
            ttl_seconds=ttl_seconds,
            size_bytes=size_bytes
        )

        # Check if we need to evict
        if key not in self.entries and len(self.entries) >= self.max_size:
            await self._evict_entries(1)

        # Store entry
        self.entries[key] = entry
        self._update_access_tracking(key)

        self.statistics.sets += 1
        self._update_statistics()

        return True

    async def delete(self, key: str) -> bool:
        """Delete key."""

        if key in self.entries:
            del self.entries[key]

            if key in self.access_order:
                del self.access_order[key]

            if key in self.access_frequency:
                del self.access_frequency[key]

            self.statistics.deletes += 1
            self._update_statistics()
            return True

        return False

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if key not in self.entries:
            return False

        entry = self.entries[key]
        if entry.is_expired():
            await self.delete(key)
            return False

        return True

    async def clear(self) -> bool:
        """Clear all cache entries."""
        self.entries.clear()
        self.access_order.clear()
        self.access_frequency.clear()
        self._update_statistics()
        return True

    async def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern."""
        import fnmatch

        # Clean expired entries first
        await self._clean_expired()

        if pattern == "*":
            return list(self.entries.keys())

        return [key for key in self.entries if fnmatch.fnmatch(key, pattern)]

    async def size(self) -> int:
        """Get number of entries."""
        await self._clean_expired()
        return len(self.entries)

    def _update_access_tracking(self, key: str) -> None:
        """Update access tracking for eviction strategies."""

        if self.strategy == CacheStrategy.LRU:
            # Move to end (most recently used)
            if key in self.access_order:
                del self.access_order[key]
            self.access_order[key] = time.time()

        elif self.strategy == CacheStrategy.LFU:
            self.access_frequency[key] += 1

    async def _evict_entries(self, count: int) -> None:
        """Evict entries based on strategy."""

        evicted = 0

        if self.strategy == CacheStrategy.LRU:
            # Evict least recently used
            while evicted < count and self.access_order:
                oldest_key = next(iter(self.access_order))
                await self.delete(oldest_key)
                evicted += 1

        elif self.strategy == CacheStrategy.LFU:
            # Evict least frequently used
            if self.access_frequency:
                sorted_keys = sorted(self.access_frequency.items(), key=lambda x: x[1])
                for key, _ in sorted_keys[:count]:
                    await self.delete(key)
                    evicted += 1

        elif self.strategy == CacheStrategy.FIFO:
            # Evict oldest entries
            sorted_entries = sorted(
                self.entries.items(),
                key=lambda x: x[1].created_at
            )
            for key, _ in sorted_entries[:count]:
                await self.delete(key)
                evicted += 1

        elif self.strategy == CacheStrategy.TTL:
            # Evict entries closest to expiration
            time.time()
            sorted_entries = sorted(
                self.entries.items(),
                key=lambda x: (x[1].created_at + (x[1].ttl_seconds or 0)) if x[1].ttl_seconds else float('inf')
            )
            for key, _ in sorted_entries[:count]:
                await self.delete(key)
                evicted += 1

        self.statistics.evictions += evicted

    async def _clean_expired(self) -> None:
        """Clean expired entries."""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.entries.items()
            if entry.is_expired(current_time)
        ]

        for key in expired_keys:
            await self.delete(key)

    def _update_statistics(self) -> None:
        """Update cache statistics."""
        self.statistics.entry_count = len(self.entries)
        self.statistics.memory_usage_bytes = sum(
            entry.size_bytes for entry in self.entries.values()
        )


class RedisCacheBackend(CacheBackend):
    """Redis distributed cache backend."""

    def __init__(self, config: CacheConfig):
        self.config = config
        self.redis_client: Optional[redis.Redis] = None
        self.statistics = CacheStatistics()
        self.serializer = self._get_serializer()

    async def connect(self) -> bool:
        """Connect to Redis server."""
        if not REDIS_AVAILABLE:
            logger.error("Redis not available")
            return False

        try:
            self.redis_client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                password=self.config.redis_password,
                ssl=self.config.redis_ssl,
                max_connections=self.config.redis_max_connections,
                decode_responses=False  # We handle serialization ourselves
            )

            # Test connection
            await self.redis_client.ping()
            logger.info("Connected to Redis cache backend")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
            return False

    async def get(self, key: str) -> Optional[Any]:
        """Get value by key."""
        if not self.redis_client:
            return None

        start_time = time.time()

        try:
            data = await self.redis_client.get(key)

            if data is None:
                self.statistics.update_miss((time.time() - start_time) * 1000)
                return None

            # Deserialize
            value = self._deserialize(data)
            self.statistics.update_hit((time.time() - start_time) * 1000)
            return value

        except Exception as e:
            logger.error(f"Redis get error: {e}")
            self.statistics.update_miss((time.time() - start_time) * 1000)
            return None

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set key-value pair."""
        if not self.redis_client:
            return False

        if ttl_seconds is None:
            ttl_seconds = self.config.l2_ttl_seconds

        try:
            # Serialize
            data = self._serialize(value)

            # Set with TTL
            result = await self.redis_client.setex(key, ttl_seconds, data)

            if result:
                self.statistics.sets += 1

            return bool(result)

        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key."""
        if not self.redis_client:
            return False

        try:
            result = await self.redis_client.delete(key)

            if result > 0:
                self.statistics.deletes += 1

            return result > 0

        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self.redis_client:
            return False

        try:
            result = await self.redis_client.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False

    async def clear(self) -> bool:
        """Clear all cache entries."""
        if not self.redis_client:
            return False

        try:
            await self.redis_client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            return False

    async def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern."""
        if not self.redis_client:
            return []

        try:
            keys = await self.redis_client.keys(pattern)
            return [key.decode() if isinstance(key, bytes) else key for key in keys]
        except Exception as e:
            logger.error(f"Redis keys error: {e}")
            return []

    async def size(self) -> int:
        """Get number of entries."""
        if not self.redis_client:
            return 0

        try:
            return await self.redis_client.dbsize()
        except Exception as e:
            logger.error(f"Redis size error: {e}")
            return 0

    def _get_serializer(self) -> Tuple[Callable, Callable]:
        """Get serialization functions."""

        if self.config.serialization_format == "json":
            return json.dumps, json.loads
        elif self.config.serialization_format == "pickle":
            return pickle.dumps, pickle.loads
        else:
            # Default to pickle
            return pickle.dumps, pickle.loads

    def _serialize(self, value: Any) -> bytes:
        """Serialize value."""

        serializer, _ = self.serializer
        data = serializer(value)

        # Compress if enabled and data is large enough
        if (self.config.compression_enabled and
            len(data) > self.config.compression_threshold):
            data = zlib.compress(data)
            # Add compression marker
            data = b"COMPRESSED:" + data

        return data

    def _deserialize(self, data: bytes) -> Any:
        """Deserialize value."""

        _, deserializer = self.serializer

        # Check for compression marker
        if data.startswith(b"COMPRESSED:"):
            data = zlib.decompress(data[11:])  # Remove "COMPRESSED:" prefix

        return deserializer(data)


class HierarchicalCacheManager:
    """Manages hierarchical cache with multiple levels."""

    def __init__(self, config: CacheConfig):
        self.config = config

        # Initialize cache levels
        self.l1_cache = MemoryCacheBackend(
            max_size=config.l1_max_size,
            default_ttl=config.l1_ttl_seconds,
            strategy=config.l1_strategy
        )

        self.l2_cache: Optional[RedisCacheBackend] = None
        if REDIS_AVAILABLE and config.hierarchical_caching:
            self.l2_cache = RedisCacheBackend(config)

        # Cache warming
        self.warming_enabled = config.warming_enabled
        self.warming_task: Optional[asyncio.Task] = None
        self.warming_candidates: Set[str] = set()

        # Statistics
        self.global_statistics = CacheStatistics()

        # Telemetry integration
        try:
            from observability.telemetry_system import get_telemetry
            self.telemetry = get_telemetry()
        except ImportError:
            self.telemetry = None

    async def initialize(self) -> bool:
        """Initialize cache manager."""

        # Connect to Redis if configured
        if self.l2_cache:
            redis_connected = await self.l2_cache.connect()
            if not redis_connected:
                logger.warning("Redis connection failed - using L1 cache only")
                self.l2_cache = None

        # Start cache warming if enabled
        if self.warming_enabled:
            self.warming_task = asyncio.create_task(self._cache_warming_loop())

        logger.info("Hierarchical cache manager initialized")
        return True

    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache hierarchy."""

        start_time = time.time()

        # Try L1 cache first
        value = await self.l1_cache.get(key)
        if value is not None:
            self._emit_cache_event(CacheEventType.HIT, key, CacheLevel.L1_MEMORY)
            return value

        # Try L2 cache (Redis)
        if self.l2_cache:
            value = await self.l2_cache.get(key)
            if value is not None:
                # Store in L1 for faster future access
                await self.l1_cache.set(key, value, self.config.l1_ttl_seconds)
                self._emit_cache_event(CacheEventType.HIT, key, CacheLevel.L2_REDIS)
                return value

        # Cache miss
        self._emit_cache_event(CacheEventType.MISS, key)
        self.global_statistics.update_miss((time.time() - start_time) * 1000)

        # Add to warming candidates if enabled
        if self.warming_enabled:
            self.warming_candidates.add(key)

        return default

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set value in cache hierarchy."""

        success = True

        # Set in L1 cache
        l1_ttl = min(ttl_seconds or self.config.l1_ttl_seconds, self.config.l1_ttl_seconds)
        l1_success = await self.l1_cache.set(key, value, l1_ttl)

        # Set in L2 cache (Redis) if available
        if self.l2_cache:
            l2_success = await self.l2_cache.set(key, value, ttl_seconds)
            success = l1_success and l2_success
        else:
            success = l1_success

        if success:
            self._emit_cache_event(CacheEventType.SET, key)
            self.global_statistics.sets += 1

        return success

    async def delete(self, key: str) -> bool:
        """Delete key from all cache levels."""

        l1_success = await self.l1_cache.delete(key)
        l2_success = True

        if self.l2_cache:
            l2_success = await self.l2_cache.delete(key)

        success = l1_success or l2_success

        if success:
            self._emit_cache_event(CacheEventType.DELETE, key)
            self.global_statistics.deletes += 1

        return success

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern."""

        invalidated = 0

        # Get matching keys from all levels
        l1_keys = await self.l1_cache.keys(pattern)
        l2_keys = []

        if self.l2_cache:
            l2_keys = await self.l2_cache.keys(pattern)

        # Combine and deduplicate keys
        all_keys = set(l1_keys + l2_keys)

        # Delete each key
        for key in all_keys:
            if await self.delete(key):
                invalidated += 1

        logger.info(f"Invalidated {invalidated} keys matching pattern: {pattern}")
        return invalidated

    @asynccontextmanager
    async def cached_operation(self,
                              cache_key: str,
                              operation: Callable,
                              ttl_seconds: Optional[int] = None,
                              force_refresh: bool = False):
        """Context manager for cached operations."""

        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_value = await self.get(cache_key)
            if cached_value is not None:
                yield cached_value
                return

        # Execute operation and cache result
        try:
            if asyncio.iscoroutinefunction(operation):
                result = await operation()
            else:
                result = operation()

            # Cache the result
            await self.set(cache_key, result, ttl_seconds)
            yield result

        except Exception as e:
            logger.error(f"Cached operation failed for key {cache_key}: {e}")
            raise

    async def warm_cache(self, keys: List[str], operation: Callable) -> int:
        """Warm cache with computed values for given keys."""

        warmed = 0

        for key in keys:
            try:
                # Check if key already exists
                if await self.l1_cache.exists(key):
                    continue

                # Compute value
                if asyncio.iscoroutinefunction(operation):
                    value = await operation(key)
                else:
                    value = operation(key)

                # Cache the value
                if await self.set(key, value):
                    warmed += 1
                    self._emit_cache_event(CacheEventType.WARM, key)

            except Exception as e:
                logger.error(f"Cache warming failed for key {key}: {e}")

        logger.info(f"Warmed {warmed} cache entries")
        return warmed

    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""

        stats = {
            "global": self.global_statistics.to_dict(),
            "l1_memory": self.l1_cache.statistics.to_dict(),
        }

        if self.l2_cache:
            stats["l2_redis"] = self.l2_cache.statistics.to_dict()
            stats["l2_redis"]["redis_info"] = await self._get_redis_info()

        # Calculate hit ratios across levels
        total_hits = self.l1_cache.statistics.hits
        total_misses = self.l1_cache.statistics.misses

        if self.l2_cache:
            total_hits += self.l2_cache.statistics.hits
            total_misses += self.l2_cache.statistics.misses

        if total_hits + total_misses > 0:
            stats["overall_hit_ratio"] = total_hits / (total_hits + total_misses)
        else:
            stats["overall_hit_ratio"] = 0.0

        # Cache warming statistics
        stats["warming"] = {
            "enabled": self.warming_enabled,
            "candidates": len(self.warming_candidates),
            "task_active": self.warming_task is not None and not self.warming_task.done()
        }

        return stats

    async def _get_redis_info(self) -> Dict[str, Any]:
        """Get Redis server information."""

        if not self.l2_cache or not self.l2_cache.redis_client:
            return {}

        try:
            info = await self.l2_cache.redis_client.info()
            return {
                "redis_version": info.get("redis_version", "unknown"),
                "used_memory": info.get("used_memory", 0),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0)
            }
        except Exception as e:
            logger.error(f"Failed to get Redis info: {e}")
            return {"error": str(e)}

    def _emit_cache_event(self,
                         event_type: CacheEventType,
                         key: str,
                         level: Optional[CacheLevel] = None) -> None:
        """Emit cache event for monitoring."""

        if self.telemetry:
            self.telemetry.emit_event(
                component="cache_manager",
                event_type=f"cache_{event_type.value}",
                message=f"Cache {event_type.value} for key: {key}",
                data={
                    "key": key,
                    "cache_level": level.value if level else None,
                    "event_type": event_type.value
                }
            )

            # Emit metrics
            self.telemetry.emit_metric(
                component="cache_manager",
                metric_name=f"cache_{event_type.value}_total",
                value=1.0
            )

    async def _cache_warming_loop(self) -> None:
        """Background cache warming loop."""

        while True:
            try:
                await asyncio.sleep(self.config.warming_interval_seconds)

                if not self.warming_candidates:
                    continue

                # Process warming candidates in batches
                candidates = list(self.warming_candidates)[:self.config.warming_batch_size]
                self.warming_candidates -= set(candidates)

                logger.info(f"Processing {len(candidates)} cache warming candidates")

                # This would typically be customized based on application needs
                # For now, we'll just log the warming candidates
                for candidate in candidates:
                    logger.debug(f"Cache warming candidate: {candidate}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cache warming loop error: {e}")
                await asyncio.sleep(60)  # Back off on error

    async def shutdown(self) -> None:
        """Shutdown cache manager."""

        if self.warming_task:
            self.warming_task.cancel()
            try:
                await self.warming_task
            except asyncio.CancelledError:
                pass

        if self.l2_cache and self.l2_cache.redis_client:
            await self.l2_cache.redis_client.close()

        logger.info("Cache manager shutdown complete")


# Global cache manager instance
_global_cache_manager: Optional[HierarchicalCacheManager] = None


def get_cache_manager() -> HierarchicalCacheManager:
    """Get global cache manager instance."""
    global _global_cache_manager

    if _global_cache_manager is None:
        config = CacheConfig()
        _global_cache_manager = HierarchicalCacheManager(config)

    return _global_cache_manager


# Convenience functions
async def cache_get(key: str, default: Any = None) -> Any:
    """Convenience function for cache get."""
    return await get_cache_manager().get(key, default)


async def cache_set(key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
    """Convenience function for cache set."""
    return await get_cache_manager().set(key, value, ttl_seconds)


async def cache_delete(key: str) -> bool:
    """Convenience function for cache delete."""
    return await get_cache_manager().delete(key)


def cache_operation(cache_key: str, ttl_seconds: Optional[int] = None):
    """Decorator for caching function results."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            cache_manager = get_cache_manager()

            # Generate cache key based on function name and arguments
            key_data = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            full_key = f"{cache_key}:{hashlib.md5(key_data.encode()).hexdigest()}"

            async with cache_manager.cached_operation(full_key, lambda: func(*args, **kwargs), ttl_seconds):
                pass

        return wrapper

    return decorator


if __name__ == "__main__":
    # Example usage
    async def demo_caching():

        # Create cache manager
        config = CacheConfig(
            l1_max_size=100,
            l1_ttl_seconds=300,
            warming_enabled=True
        )

        cache_manager = HierarchicalCacheManager(config)
        await cache_manager.initialize()

        # Basic cache operations
        await cache_manager.set("user:123", {"name": "John", "email": "john@example.com"})
        user_data = await cache_manager.get("user:123")
        print(f"✅ Cached user: {user_data}")

        # Cached operation
        async def expensive_computation(x):
            await asyncio.sleep(0.1)  # Simulate expensive operation
            return x ** 2

        async with cache_manager.cached_operation("compute:5", lambda: expensive_computation(5)):
            pass

        # Get statistics
        stats = await cache_manager.get_statistics()
        print(f"✅ Cache statistics: {stats['overall_hit_ratio']:.2f} hit ratio")

        await cache_manager.shutdown()

    asyncio.run(demo_caching())
