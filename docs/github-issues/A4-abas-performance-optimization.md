# [A4] ABAS Performance Optimization & Caching

**Labels**: `enhancement`, `abas`, `performance`, `optimization`
**Priority**: Medium
**Milestone**: Q2 2026
**Estimated Effort**: 2-3 days
**Depends On**: Phase 4 ABAS deployment (in progress via Claude Code Web)

---

## Problem Statement

ABAS (Adaptive Behavior/Access Shield) middleware makes synchronous OPA HTTP calls for every request, causing:
1. **High Latency**: Each OPA call adds 5-15ms (p50), up to 50ms (p99)
2. **OPA Overload**: At 1000 req/s, OPA server receives 1000 policy queries/s
3. **Single Point of Failure**: If OPA server down, all requests blocked (fail-closed)
4. **No Caching**: Same caller/route combinations re-evaluated every time
5. **Network Overhead**: HTTP roundtrip for every request

**Current Performance** (from SYSTEMS_2.md spec):
- Target: <5ms p50 overhead
- Actual: ~10-15ms p50 (OPA call dominates)

## Proposed Solution

Implement **multi-layer caching** and **async OPA calls** to reduce latency:

### Architecture

```
Request → ABAS Middleware
            ↓
       [L1 Cache: AsyncTTLCache]
       (in-memory, 60s TTL)
            ↓ (cache miss)
       [OPA HTTP Call]
       (httpx.AsyncClient)
            ↓
       [L2 Cache: Redis]
       (distributed, 300s TTL)
            ↓
       Policy Decision (allow/deny)
```

### 1. L1 Cache (In-Memory AsyncTTLCache)

**Benefits**:
- Sub-millisecond cache hits
- No network overhead
- Shared across worker processes (if using shared memory)

**Implementation**:
```python
# enforcement/abas/cache.py
import asyncio
import time
from typing import Dict, Optional, Tuple

class AsyncTTLCache:
    """Async-safe TTL cache with LRU eviction."""

    def __init__(self, max_size: int = 10000, ttl_seconds: int = 60):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Tuple[any, float]] = {}  # key -> (value, expiry)
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[any]:
        """Get value from cache, return None if expired/missing."""
        async with self._lock:
            if key not in self._cache:
                return None

            value, expiry = self._cache[key]
            if time.time() > expiry:
                del self._cache[key]  # Expired
                return None

            return value

    async def set(self, key: str, value: any):
        """Set value in cache with TTL."""
        async with self._lock:
            # LRU eviction if full
            if len(self._cache) >= self.max_size:
                oldest_key = min(self._cache, key=lambda k: self._cache[k][1])
                del self._cache[oldest_key]

            expiry = time.time() + self.ttl_seconds
            self._cache[key] = (value, expiry)

    async def clear(self):
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()


# Global cache instance
_pdp_cache = AsyncTTLCache(max_size=10000, ttl_seconds=60)


async def get_cached_decision(cache_key: str) -> Optional[dict]:
    """Get cached PDP decision."""
    return await _pdp_cache.get(cache_key)


async def cache_decision(cache_key: str, decision: dict):
    """Cache PDP decision for TTL period."""
    await _pdp_cache.set(cache_key, decision)
```

**Integration** (`enforcement/abas/middleware.py`):
```python
from enforcement.abas.cache import get_cached_decision, cache_decision

class ABasMiddleware:
    async def dispatch(self, request: Request, call_next):
        # Build cache key (route + method + caller + body hash)
        body = await request.body()
        body_hash = hashlib.sha256(body).hexdigest()[:16]
        caller = request.headers.get("OpenAI-Organization", "anonymous")
        cache_key = f"{request.method}:{request.url.path}:{caller}:{body_hash}"

        # Check L1 cache
        cached_decision = await get_cached_decision(cache_key)
        if cached_decision:
            logger.debug(f"ABAS cache HIT: {cache_key}")
            if not cached_decision["allow"]:
                return Response(content=cached_decision["message"], status_code=403)
            return await call_next(request)

        # Cache MISS: Query OPA
        logger.debug(f"ABAS cache MISS: {cache_key}")
        decision = await self._query_opa(request, body)

        # Cache decision
        await cache_decision(cache_key, decision)

        # Enforce decision
        if not decision["allow"]:
            return Response(content=decision["message"], status_code=403)

        return await call_next(request)
```

### 2. Async OPA Calls (httpx)

**Before** (blocking):
```python
import requests
response = requests.post(OPA_URL, json=input_data, timeout=5.0)
# Blocks event loop for 5-15ms
```

**After** (async):
```python
import httpx
async with httpx.AsyncClient() as client:
    response = await client.post(OPA_URL, json=input_data, timeout=5.0)
    # Non-blocking, other requests can process
```

### 3. L2 Cache (Redis - Optional)

**Benefits**:
- Distributed cache (shared across API servers)
- Persistent across restarts
- Higher capacity (GB-scale)

**Implementation**:
```python
# enforcement/abas/cache.py (addition)
import aioredis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

async def get_redis_cached_decision(cache_key: str) -> Optional[dict]:
    """Get cached decision from Redis."""
    redis = await aioredis.from_url(REDIS_URL)
    value = await redis.get(f"abas:{cache_key}")
    if value:
        return json.loads(value)
    return None

async def cache_redis_decision(cache_key: str, decision: dict, ttl: int = 300):
    """Cache decision in Redis with TTL."""
    redis = await aioredis.from_url(REDIS_URL)
    await redis.setex(f"abas:{cache_key}", ttl, json.dumps(decision))
```

### 4. Cache Invalidation

**Problem**: Stale cache if OPA policies updated.

**Solution**: Cache versioning with policy hash:
```python
# Get OPA policy version
policy_version = await client.get(f"{OPA_URL}/v1/policies/abas").json()["result"]["version"]

# Include in cache key
cache_key = f"{request.method}:{request.url.path}:{caller}:{body_hash}:v{policy_version}"
```

**Alternative**: Expire cache on policy update (webhook from OPA).

## Acceptance Criteria

- [ ] `AsyncTTLCache` implemented with 60s TTL, 10k max entries
- [ ] L1 cache integrated into ABAS middleware
- [ ] Cache hit rate >80% after 10 minutes of traffic
- [ ] ABAS latency reduced from 10-15ms to <3ms (p50) for cache hits
- [ ] OPA load reduced by 80% (only 20% cache misses)
- [ ] Monitoring: `abas_cache_hit_rate`, `abas_cache_size`, `abas_opa_calls_total`
- [ ] Documentation: `docs/abas/PERFORMANCE_OPTIMIZATION.md`
- [ ] Load test: 1000 req/s with <5ms ABAS overhead

## Implementation Plan

**Phase 1**: AsyncTTLCache (1 day)
1. Implement `enforcement/abas/cache.py` with asyncio.Lock
2. Write unit tests: `tests/abas/test_cache.py`
3. Benchmark: measure cache hit/miss latency

**Phase 2**: ABAS Integration (1 day)
1. Build cache key (route + method + caller + body hash)
2. Check cache before OPA call
3. Cache decisions with 60s TTL
4. Test with integration tests

**Phase 3**: Monitoring & Tuning (0.5 days)
1. Add Prometheus metrics (hit rate, size)
2. Load test with Locust (1000 req/s)
3. Tune TTL and max_size for optimal performance

**Phase 4**: Redis L2 Cache (0.5 days, optional)
1. Implement Redis caching layer
2. Fallback to OPA if Redis unavailable
3. Test with distributed API servers

## Testing Strategy

```bash
# Unit tests
pytest tests/abas/test_cache.py -v

# Integration tests (with real OPA)
pytest tests/integration/test_abas_caching.py

# Load test (measure cache effectiveness)
locust -f tests/load/locustfile_abas.py --host http://localhost:8000 --users 100 --spawn-rate 10

# Cache hit rate test
python3 scripts/test_abas_cache_hit_rate.py
```

## Monitoring & Alerting

**Metrics**:
- `abas_cache_hits_total` (counter)
- `abas_cache_misses_total` (counter)
- `abas_cache_size` (gauge, current entries)
- `abas_cache_hit_rate` (gauge, hits / (hits + misses))
- `abas_opa_calls_total` (counter, should drop 80%)
- `abas_latency_seconds{cached="true|false"}` (histogram)

**Alerts**:
```yaml
- alert: ABAsCacheHitRateLow
  expr: abas_cache_hit_rate < 0.5
  for: 10m
  annotations:
    summary: "ABAS cache hit rate <50% (cache not effective)"

- alert: ABAsCacheFull
  expr: abas_cache_size > 9500
  annotations:
    summary: "ABAS cache near capacity (>9500/10000 entries)"
```

## Performance Benchmarks

**Before Caching**:
| Metric | Value |
|--------|-------|
| ABAS p50 latency | 12.5ms |
| ABAS p99 latency | 45ms |
| OPA calls/sec (1000 req/s) | 1000 |
| Total overhead | ~1.25% request time |

**After Caching** (projected):
| Metric | Value |
|--------|-------|
| ABAS p50 latency (cache hit) | <1ms |
| ABAS p50 latency (cache miss) | 12.5ms |
| ABAS p99 latency | 15ms (fewer OPA calls) |
| OPA calls/sec (1000 req/s) | 200 (80% reduction) |
| Total overhead | <0.3% request time |

## Trade-offs

**Pros**:
- ✅ 80%+ latency reduction for cached requests
- ✅ Reduced OPA server load
- ✅ Better scalability

**Cons**:
- ⚠️ Stale cache risk (mitigated with 60s TTL)
- ⚠️ Memory overhead (~10MB for 10k entries)
- ⚠️ Cache invalidation complexity if policies change frequently

**Recommendation**: Enable caching for production, disable for development (to catch policy bugs immediately).

## Related Issues

- #N2: NIAS Drift Detection (cache drift scores too)
- #XXX: ABAS fail-open mode (if OPA + cache both unavailable)
- #XXX: OPA policy versioning (for cache invalidation)

## References

- [AsyncIO Locking](https://docs.python.org/3/library/asyncio-sync.html#asyncio.Lock)
- [httpx Async Client](https://www.python-httpx.org/async/)
- [Redis TTL](https://redis.io/commands/expire/)
- [OPA Performance](https://www.openpolicyagent.org/docs/latest/performance/)
- Gonzo Spec: `docs/gonzo/SYSTEMS_2.md` (A4 section)

---

**Created**: 2025-11-13
**Author**: Security Enhancement Team
**Reviewers**: @security-team, @backend-team
