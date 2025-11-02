#!/usr/bin/env python3
"""
LUKHAS Advanced API Optimization System

Enterprise-grade API performance optimization with intelligent rate limiting,
analytics, request optimization, and adaptive response caching.

# ΛTAG: api_optimization, performance_enhancement, rate_limiting, api_analytics
"""

import asyncio
import hashlib
import json
import logging
import statistics
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

# Optional dependencies
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from prometheus_client import Counter, Gauge, Histogram
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


class APITier(Enum):
    """API access tiers with different performance guarantees."""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    INTERNAL = "internal"


class OptimizationStrategy(Enum):
    """API optimization strategies."""
    AGGRESSIVE_CACHE = "aggressive_cache"
    BALANCED = "balanced"
    LOW_LATENCY = "low_latency"
    HIGH_THROUGHPUT = "high_throughput"
    RESOURCE_CONSERVATION = "resource_conservation"


class RequestPriority(Enum):
    """Request priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BACKGROUND = "background"


@dataclass
class APIQuota:
    """API usage quota configuration."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    concurrent_requests: int = 10
    max_request_size_mb: float = 10.0
    max_response_size_mb: float = 50.0
    allowed_endpoints: Optional[Set[str]] = None
    tier: APITier = APITier.FREE


@dataclass
class OptimizationConfig:
    """API optimization configuration."""
    strategy: OptimizationStrategy = OptimizationStrategy.BALANCED
    enable_request_compression: bool = True
    enable_response_compression: bool = True
    enable_adaptive_caching: bool = True
    enable_request_batching: bool = True
    enable_connection_pooling: bool = True
    enable_prefetching: bool = False
    cache_ttl_seconds: int = 300
    compression_threshold_bytes: int = 1024
    batch_window_ms: int = 100
    max_batch_size: int = 10
    connection_pool_size: int = 20
    request_timeout_seconds: float = 30.0
    enable_metrics: bool = True


@dataclass
class APIMetrics:
    """API performance metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    cache_hit_rate: float = 0.0
    compression_ratio: float = 0.0
    throughput_requests_per_second: float = 0.0
    concurrent_requests: int = 0
    quota_violations: int = 0
    error_rate: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class RequestContext:
    """Context for API request optimization."""
    request_id: str
    endpoint: str
    method: str
    user_id: Optional[str] = None
    api_key: Optional[str] = None
    tier: APITier = APITier.FREE
    priority: RequestPriority = RequestPriority.NORMAL
    start_time: float = field(default_factory=time.time)
    size_bytes: int = 0
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class RateLimiter:
    """Advanced rate limiter with multiple algorithms and tier support."""

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.local_buckets = defaultdict(lambda: deque())
        self.local_quotas = defaultdict(lambda: defaultdict(int))
        self.tier_configs = {
            APITier.FREE: APIQuota(
                requests_per_minute=60,
                requests_per_hour=1000,
                requests_per_day=10000,
                concurrent_requests=5
            ),
            APITier.BASIC: APIQuota(
                requests_per_minute=300,
                requests_per_hour=10000,
                requests_per_day=100000,
                concurrent_requests=20
            ),
            APITier.PREMIUM: APIQuota(
                requests_per_minute=1000,
                requests_per_hour=50000,
                requests_per_day=1000000,
                concurrent_requests=50
            ),
            APITier.ENTERPRISE: APIQuota(
                requests_per_minute=10000,
                requests_per_hour=500000,
                requests_per_day=10000000,
                concurrent_requests=200
            ),
            APITier.INTERNAL: APIQuota(
                requests_per_minute=100000,
                requests_per_hour=1000000,
                requests_per_day=100000000,
                concurrent_requests=1000
            )
        }

    async def is_allowed(self, context: RequestContext) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is allowed under rate limits."""
        quota = self.tier_configs.get(context.tier, self.tier_configs[APITier.FREE])

        # Get rate limit status
        current_counts = await self._get_current_counts(context.user_id or context.api_key, context.tier)

        # Check all limits
        checks = {
            "requests_per_minute": current_counts.get("minute", 0) < quota.requests_per_minute,
            "requests_per_hour": current_counts.get("hour", 0) < quota.requests_per_hour,
            "requests_per_day": current_counts.get("day", 0) < quota.requests_per_day,
            "concurrent_requests": current_counts.get("concurrent", 0) < quota.concurrent_requests,
            "request_size": context.size_bytes <= (quota.max_request_size_mb * 1024 * 1024)
        }

        # Check endpoint restrictions
        if quota.allowed_endpoints and context.endpoint not in quota.allowed_endpoints:
            checks["endpoint_allowed"] = False

        allowed = all(checks.values())

        if allowed:
            await self._increment_counts(context.user_id or context.api_key, context.tier)

        return allowed, {
            "quota": quota,
            "current_counts": current_counts,
            "checks": checks,
            "retry_after_seconds": await self._calculate_retry_after(context.tier, current_counts)
        }

    async def _get_current_counts(self, identifier: str, tier: APITier) -> Dict[str, int]:
        """Get current usage counts for rate limiting."""
        if self.redis_client:
            return await self._get_redis_counts(identifier, tier)
        else:
            return await self._get_local_counts(identifier, tier)

    async def _get_redis_counts(self, identifier: str, tier: APITier) -> Dict[str, int]:
        """Get counts from Redis."""
        try:
            pipe = self.redis_client.pipeline()

            now = datetime.now()
            minute_key = f"rate_limit:{identifier}:{tier.value}:minute:{now.strftime('%Y%m%d%H%M')}"
            hour_key = f"rate_limit:{identifier}:{tier.value}:hour:{now.strftime('%Y%m%d%H')}"
            day_key = f"rate_limit:{identifier}:{tier.value}:day:{now.strftime('%Y%m%d')}"
            concurrent_key = f"rate_limit:{identifier}:{tier.value}:concurrent"

            pipe.get(minute_key)
            pipe.get(hour_key)
            pipe.get(day_key)
            pipe.get(concurrent_key)

            results = await pipe.execute()

            return {
                "minute": int(results[0] or 0),
                "hour": int(results[1] or 0),
                "day": int(results[2] or 0),
                "concurrent": int(results[3] or 0)
            }
        except Exception as e:
            logger.warning(f"Redis rate limit check failed: {e}")
            return await self._get_local_counts(identifier, tier)

    async def _get_local_counts(self, identifier: str, tier: APITier) -> Dict[str, int]:
        """Get counts from local memory."""
        now = time.time()
        bucket_key = f"{identifier}:{tier.value}"

        # Clean old entries
        bucket = self.local_buckets[bucket_key]
        while bucket and bucket[0] < now - 86400:  # Remove entries older than 1 day
            bucket.popleft()

        # Count entries in different time windows
        minute_count = sum(1 for ts in bucket if ts > now - 60)
        hour_count = sum(1 for ts in bucket if ts > now - 3600)
        day_count = len(bucket)

        return {
            "minute": minute_count,
            "hour": hour_count,
            "day": day_count,
            "concurrent": self.local_quotas[bucket_key]["concurrent"]
        }

    async def _increment_counts(self, identifier: str, tier: APITier):
        """Increment usage counts."""
        if self.redis_client:
            await self._increment_redis_counts(identifier, tier)
        else:
            await self._increment_local_counts(identifier, tier)

    async def _increment_redis_counts(self, identifier: str, tier: APITier):
        """Increment Redis counts."""
        try:
            pipe = self.redis_client.pipeline()
            now = datetime.now()

            minute_key = f"rate_limit:{identifier}:{tier.value}:minute:{now.strftime('%Y%m%d%H%M')}"
            hour_key = f"rate_limit:{identifier}:{tier.value}:hour:{now.strftime('%Y%m%d%H')}"
            day_key = f"rate_limit:{identifier}:{tier.value}:day:{now.strftime('%Y%m%d')}"
            concurrent_key = f"rate_limit:{identifier}:{tier.value}:concurrent"

            pipe.incr(minute_key)
            pipe.expire(minute_key, 120)  # 2 minutes TTL
            pipe.incr(hour_key)
            pipe.expire(hour_key, 7200)  # 2 hours TTL
            pipe.incr(day_key)
            pipe.expire(day_key, 172800)  # 2 days TTL
            pipe.incr(concurrent_key)

            await pipe.execute()
        except Exception as e:
            logger.warning(f"Redis rate limit increment failed: {e}")
            await self._increment_local_counts(identifier, tier)

    async def _increment_local_counts(self, identifier: str, tier: APITier):
        """Increment local memory counts."""
        bucket_key = f"{identifier}:{tier.value}"
        self.local_buckets[bucket_key].append(time.time())
        self.local_quotas[bucket_key]["concurrent"] += 1

    async def _calculate_retry_after(self, tier: APITier, current_counts: Dict[str, int]) -> int:
        """Calculate retry-after seconds for rate limited requests."""
        quota = self.tier_configs[tier]

        # Calculate when each limit will reset
        retry_times = []

        if current_counts.get("minute", 0) >= quota.requests_per_minute:
            retry_times.append(60)

        if current_counts.get("hour", 0) >= quota.requests_per_hour:
            retry_times.append(3600)

        if current_counts.get("concurrent", 0) >= quota.concurrent_requests:
            retry_times.append(10)  # Assume concurrent requests resolve quickly

        return min(retry_times) if retry_times else 0

    async def decrement_concurrent(self, identifier: str, tier: APITier):
        """Decrement concurrent request count."""
        if self.redis_client:
            try:
                concurrent_key = f"rate_limit:{identifier}:{tier.value}:concurrent"
                await self.redis_client.decr(concurrent_key)
            except Exception as e:
                logger.warning(f"Redis concurrent decrement failed: {e}")
        else:
            bucket_key = f"{identifier}:{tier.value}"
            self.local_quotas[bucket_key]["concurrent"] = max(0,
                self.local_quotas[bucket_key]["concurrent"] - 1)


class APICache:
    """Advanced API response caching with intelligent invalidation."""

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.local_cache = {}
        self.cache_stats = defaultdict(int)

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached response."""
        try:
            if self.redis_client:
                cached = await self.redis_client.get(f"api_cache:{key}")
                if cached:
                    self.cache_stats["hits"] += 1
                    return json.loads(cached)
            else:
                if key in self.local_cache:
                    entry = self.local_cache[key]
                    if entry["expires_at"] > time.time():
                        self.cache_stats["hits"] += 1
                        return entry["data"]
                    else:
                        del self.local_cache[key]

            self.cache_stats["misses"] += 1
            return None
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
            self.cache_stats["errors"] += 1
            return None

    async def set(self, key: str, data: Dict[str, Any], ttl_seconds: int = 300):
        """Set cached response."""
        try:
            if self.redis_client:
                await self.redis_client.setex(
                    f"api_cache:{key}",
                    ttl_seconds,
                    json.dumps(data)
                )
            else:
                self.local_cache[key] = {
                    "data": data,
                    "expires_at": time.time() + ttl_seconds
                }

                # Simple cleanup for local cache
                if len(self.local_cache) > 10000:
                    # Remove expired entries
                    now = time.time()
                    expired_keys = [k for k, v in self.local_cache.items()
                                  if v["expires_at"] <= now]
                    for k in expired_keys:
                        del self.local_cache[k]

            self.cache_stats["sets"] += 1
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
            self.cache_stats["errors"] += 1

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern."""
        try:
            count = 0
            if self.redis_client:
                keys = await self.redis_client.keys(f"api_cache:{pattern}")
                if keys:
                    count = await self.redis_client.delete(*keys)
            else:
                # Simple pattern matching for local cache
                import fnmatch
                matching_keys = [k for k in self.local_cache.keys()
                               if fnmatch.fnmatch(k, pattern)]
                for k in matching_keys:
                    del self.local_cache[k]
                count = len(matching_keys)

            self.cache_stats["invalidations"] += count
            return count
        except Exception as e:
            logger.warning(f"Cache invalidation failed: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_operations = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_operations * 100) if total_operations > 0 else 0

        return {
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "sets": self.cache_stats["sets"],
            "invalidations": self.cache_stats["invalidations"],
            "errors": self.cache_stats["errors"],
            "hit_rate_percent": hit_rate,
            "local_cache_size": len(self.local_cache)
        }


class APIAnalytics:
    """Advanced API analytics and intelligence."""

    def __init__(self):
        self.request_history = deque(maxlen=10000)
        self.endpoint_stats = defaultdict(lambda: defaultdict(list))
        self.user_patterns = defaultdict(lambda: defaultdict(list))
        self.error_patterns = defaultdict(list)

    async def record_request(self, context: RequestContext,
                           response_time_ms: float,
                           status_code: int,
                           response_size_bytes: int):
        """Record API request for analytics."""
        timestamp = time.time()

        request_record = {
            "timestamp": timestamp,
            "request_id": context.request_id,
            "endpoint": context.endpoint,
            "method": context.method,
            "user_id": context.user_id,
            "tier": context.tier.value,
            "priority": context.priority.value,
            "request_size": context.size_bytes,
            "response_size": response_size_bytes,
            "response_time_ms": response_time_ms,
            "status_code": status_code,
            "headers": dict(context.headers),
            "metadata": dict(context.metadata)
        }

        self.request_history.append(request_record)

        # Update endpoint statistics
        endpoint_key = f"{context.method}:{context.endpoint}"
        self.endpoint_stats[endpoint_key]["response_times"].append(response_time_ms)
        self.endpoint_stats[endpoint_key]["request_sizes"].append(context.size_bytes)
        self.endpoint_stats[endpoint_key]["response_sizes"].append(response_size_bytes)
        self.endpoint_stats[endpoint_key]["status_codes"].append(status_code)

        # Update user patterns
        if context.user_id:
            self.user_patterns[context.user_id]["endpoints"].append(endpoint_key)
            self.user_patterns[context.user_id]["response_times"].append(response_time_ms)
            self.user_patterns[context.user_id]["timestamps"].append(timestamp)

        # Record errors
        if status_code >= 400:
            self.error_patterns[endpoint_key].append({
                "timestamp": timestamp,
                "status_code": status_code,
                "user_id": context.user_id,
                "response_time_ms": response_time_ms
            })

    async def get_endpoint_analytics(self, endpoint: str, method: str = "GET") -> Dict[str, Any]:
        """Get analytics for specific endpoint."""
        endpoint_key = f"{method}:{endpoint}"
        stats = self.endpoint_stats[endpoint_key]

        if not stats.get("response_times"):
            return {"error": "No data available for endpoint"}

        response_times = stats["response_times"][-1000:]  # Last 1000 requests
        request_sizes = stats["request_sizes"][-1000:]
        response_sizes = stats["response_sizes"][-1000:]
        status_codes = stats["status_codes"][-1000:]

        return {
            "endpoint": endpoint,
            "method": method,
            "total_requests": len(response_times),
            "avg_response_time_ms": statistics.mean(response_times),
            "p50_response_time_ms": statistics.median(response_times),
            "p95_response_time_ms": self._percentile(response_times, 95),
            "p99_response_time_ms": self._percentile(response_times, 99),
            "min_response_time_ms": min(response_times),
            "max_response_time_ms": max(response_times),
            "avg_request_size": statistics.mean(request_sizes),
            "avg_response_size": statistics.mean(response_sizes),
            "error_rate": len([s for s in status_codes if s >= 400]) / len(status_codes) * 100,
            "status_code_distribution": self._count_distribution(status_codes)
        }

    async def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get analytics for specific user."""
        user_data = self.user_patterns[user_id]

        if not user_data.get("endpoints"):
            return {"error": "No data available for user"}

        endpoints = user_data["endpoints"][-1000:]  # Last 1000 requests
        response_times = user_data["response_times"][-1000:]
        timestamps = user_data["timestamps"][-1000:]

        # Calculate request frequency
        recent_requests = [ts for ts in timestamps if ts > time.time() - 3600]  # Last hour
        requests_per_hour = len(recent_requests)

        return {
            "user_id": user_id,
            "total_requests": len(endpoints),
            "unique_endpoints": len(set(endpoints)),
            "most_used_endpoints": self._count_distribution(endpoints),
            "avg_response_time_ms": statistics.mean(response_times),
            "requests_per_hour": requests_per_hour,
            "request_pattern": self._analyze_request_pattern(timestamps)
        }

    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics."""
        recent_requests = [r for r in self.request_history
                          if r["timestamp"] > time.time() - 3600]  # Last hour

        if not recent_requests:
            return {"error": "No recent data available"}

        response_times = [r["response_time_ms"] for r in recent_requests]
        status_codes = [r["status_code"] for r in recent_requests]

        return {
            "total_requests_last_hour": len(recent_requests),
            "avg_response_time_ms": statistics.mean(response_times),
            "p95_response_time_ms": self._percentile(response_times, 95),
            "error_rate_percent": len([s for s in status_codes if s >= 400]) / len(status_codes) * 100,
            "requests_per_second": len(recent_requests) / 3600,
            "unique_users_last_hour": len(set(r["user_id"] for r in recent_requests if r["user_id"])),
            "top_endpoints": self._get_top_endpoints(recent_requests),
            "health_score": self._calculate_health_score(response_times, status_codes)
        }

    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]

    def _count_distribution(self, data: List[Any]) -> Dict[Any, int]:
        """Get count distribution of data."""
        counts = defaultdict(int)
        for item in data:
            counts[item] += 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

    def _analyze_request_pattern(self, timestamps: List[float]) -> str:
        """Analyze user request patterns."""
        if len(timestamps) < 10:
            return "insufficient_data"

        # Calculate intervals between requests
        intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
        avg_interval = statistics.mean(intervals)

        if avg_interval < 1:
            return "burst"
        elif avg_interval < 60:
            return "frequent"
        elif avg_interval < 3600:
            return "regular"
        else:
            return "sporadic"

    def _get_top_endpoints(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get top endpoints by request count."""
        endpoint_counts = defaultdict(int)
        for req in requests:
            endpoint_key = f"{req['method']}:{req['endpoint']}"
            endpoint_counts[endpoint_key] += 1

        return [
            {"endpoint": endpoint, "requests": count}
            for endpoint, count in sorted(endpoint_counts.items(),
                                        key=lambda x: x[1], reverse=True)[:10]
        ]

    def _calculate_health_score(self, response_times: List[float],
                               status_codes: List[int]) -> float:
        """Calculate overall system health score (0-100)."""
        if not response_times or not status_codes:
            return 0.0

        # Response time score (0-40 points)
        avg_response_time = statistics.mean(response_times)
        time_score = max(0, 40 - (avg_response_time / 100))  # Deduct points for slow responses

        # Error rate score (0-40 points)
        error_rate = len([s for s in status_codes if s >= 400]) / len(status_codes)
        error_score = max(0, 40 - (error_rate * 100))

        # Consistency score (0-20 points)
        response_time_std = statistics.stdev(response_times) if len(response_times) > 1 else 0
        consistency_score = max(0, 20 - (response_time_std / 100))

        return min(100, time_score + error_score + consistency_score)


class LUKHASAPIOptimizer:
    """Main API optimization coordinator."""

    def __init__(self, config: OptimizationConfig, redis_client: Optional[redis.Redis] = None):
        self.config = config
        self.rate_limiter = RateLimiter(redis_client)
        self.cache = APICache(redis_client)
        self.analytics = APIAnalytics()
        self.active_requests = {}
        self.metrics = APIMetrics()

        # Prometheus metrics (if available)
        if PROMETHEUS_AVAILABLE and config.enable_metrics:
            self.request_counter = Counter('lukhas_api_requests_total',
                                         'Total API requests', ['endpoint', 'method', 'status'])
            self.response_time_histogram = Histogram('lukhas_api_response_time_seconds',
                                                   'API response times', ['endpoint', 'method'])
            self.active_requests_gauge = Gauge('lukhas_api_active_requests',
                                             'Currently active API requests')

    async def process_request(self, context: RequestContext) -> Tuple[bool, Dict[str, Any]]:
        """Process API request with optimization."""
        start_time = time.time()

        # Check rate limits
        allowed, rate_limit_info = await self.rate_limiter.is_allowed(context)
        if not allowed:
            await self.analytics.record_request(context, 0, 429, 0)
            return False, {
                "error": "Rate limit exceeded",
                "rate_limit_info": rate_limit_info
            }

        # Check cache
        cache_key = self._generate_cache_key(context)
        if self.config.enable_adaptive_caching:
            cached_response = await self.cache.get(cache_key)
            if cached_response:
                response_time = (time.time() - start_time) * 1000
                await self.analytics.record_request(context, response_time, 200,
                                                  len(json.dumps(cached_response)))
                return True, {
                    "cached": True,
                    "data": cached_response,
                    "cache_key": cache_key
                }

        # Track active request
        self.active_requests[context.request_id] = context

        return True, {
            "cache_key": cache_key,
            "rate_limit_info": rate_limit_info
        }

    async def complete_request(self, context: RequestContext,
                             response_data: Dict[str, Any],
                             status_code: int):
        """Complete request processing with caching and analytics."""
        response_time = (time.time() - context.start_time) * 1000
        response_size = len(json.dumps(response_data))

        # Remove from active requests
        self.active_requests.pop(context.request_id, None)

        # Cache successful responses
        if (status_code == 200 and
            self.config.enable_adaptive_caching and
            self._should_cache_response(context, response_data)):

            cache_key = self._generate_cache_key(context)
            await self.cache.set(cache_key, response_data, self.config.cache_ttl_seconds)

        # Record analytics
        await self.analytics.record_request(context, response_time, status_code, response_size)

        # Update metrics
        await self._update_metrics(context, response_time, status_code)

        # Decrement concurrent request count
        await self.rate_limiter.decrement_concurrent(
            context.user_id or context.api_key, context.tier)

    async def get_optimization_stats(self) -> Dict[str, Any]:
        """Get comprehensive optimization statistics."""
        cache_stats = self.cache.get_stats()
        system_health = await self.analytics.get_system_health()

        return {
            "cache": cache_stats,
            "system_health": system_health,
            "active_requests": len(self.active_requests),
            "metrics": {
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "avg_response_time_ms": self.metrics.avg_response_time_ms,
                "error_rate": self.metrics.error_rate,
                "cache_hit_rate": cache_stats.get("hit_rate_percent", 0)
            },
            "config": {
                "strategy": self.config.strategy.value,
                "caching_enabled": self.config.enable_adaptive_caching,
                "compression_enabled": self.config.enable_response_compression,
                "batching_enabled": self.config.enable_request_batching
            }
        }

    def _generate_cache_key(self, context: RequestContext) -> str:
        """Generate cache key for request."""
        key_parts = [
            context.method,
            context.endpoint,
            hashlib.md5(json.dumps(context.params, sort_keys=True).encode()).hexdigest()[:16]
        ]

        # Include user-specific data for personalized responses
        if context.user_id:
            key_parts.append(f"user:{context.user_id}")

        return ":".join(key_parts)

    def _should_cache_response(self, context: RequestContext, response_data: Dict[str, Any]) -> bool:
        """Determine if response should be cached."""
        # Don't cache large responses
        response_size = len(json.dumps(response_data))
        if response_size > 1024 * 1024:  # 1MB
            return False

        # Don't cache POST/PUT/DELETE requests
        if context.method in ["POST", "PUT", "DELETE", "PATCH"]:
            return False

        # Don't cache personalized responses (unless explicitly marked as cacheable)
        if context.user_id and not context.metadata.get("cacheable", False):
            return False

        return True

    async def _update_metrics(self, context: RequestContext,
                            response_time_ms: float, status_code: int):
        """Update performance metrics."""
        self.metrics.total_requests += 1

        if status_code < 400:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1

        # Update response time statistics
        if self.metrics.total_requests == 1:
            self.metrics.avg_response_time_ms = response_time_ms
        else:
            self.metrics.avg_response_time_ms = (
                (self.metrics.avg_response_time_ms * (self.metrics.total_requests - 1) + response_time_ms) /
                self.metrics.total_requests
            )

        # Update error rate
        self.metrics.error_rate = (self.metrics.failed_requests / self.metrics.total_requests) * 100

        # Update Prometheus metrics
        if PROMETHEUS_AVAILABLE and self.config.enable_metrics:
            self.request_counter.labels(
                endpoint=context.endpoint,
                method=context.method,
                status=str(status_code)
            ).inc()

            self.response_time_histogram.labels(
                endpoint=context.endpoint,
                method=context.method
            ).observe(response_time_ms / 1000)

            self.active_requests_gauge.set(len(self.active_requests))


# Example usage and factory functions
async def create_api_optimizer(
    strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
    redis_url: Optional[str] = None
) -> LUKHASAPIOptimizer:
    """Create API optimizer with optional Redis backend."""

    config = OptimizationConfig(strategy=strategy)

    redis_client = None
    if redis_url and REDIS_AVAILABLE:
        try:
            redis_client = redis.from_url(redis_url)
            await redis_client.ping()
            logger.info("Connected to Redis for API optimization")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}")
            redis_client = None

    return LUKHASAPIOptimizer(config, redis_client)


# Context manager for request processing
@asynccontextmanager
async def optimized_api_request(optimizer: LUKHASAPIOptimizer,
                               context: RequestContext):
    """Context manager for optimized API request processing."""

    # Pre-processing
    allowed, info = await optimizer.process_request(context)
    if not allowed:
        yield False, info
        return

    try:
        yield True, info
    finally:
        # Post-processing will be handled by complete_request call
        pass


if __name__ == "__main__":
    async def test_api_optimizer():
        """Test the API optimizer."""
        optimizer = await create_api_optimizer()

        # Create test request
        context = RequestContext(
            request_id="test_123",
            endpoint="/api/v1/test",
            method="GET",
            user_id="test_user",
            tier=APITier.BASIC,
            size_bytes=1024
        )

        # Process request
        async with optimized_api_request(optimizer, context) as (allowed, info):
            if allowed:
                print("✅ Request allowed")

                # Simulate API processing
                await asyncio.sleep(0.1)

                # Complete request
                await optimizer.complete_request(
                    context,
                    {"result": "success", "data": "test response"},
                    200
                )

                # Get stats
                stats = await optimizer.get_optimization_stats()
                print(f"📊 Stats: {stats}")
            else:
                print(f"❌ Request denied: {info}")

    asyncio.run(test_api_optimizer())
