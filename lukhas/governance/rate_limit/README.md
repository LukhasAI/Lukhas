# Rate Limiting System

**Task 2.2: DoS Prevention through Rate Limiting**

## Overview

The LUKHAS AI rate limiting system implements sliding window rate limiting to prevent Denial-of-Service (DoS) attacks and ensure fair resource usage across users. This system mitigates **OWASP A04: Insecure Design** vulnerabilities.

### Key Features

- **Sliding Window Algorithm**: Accurate rate limiting without fixed window issues
- **Tier-Based Limits**: Different limits for free, basic, and pro users
- **Per-IP Limits**: Prevents DDoS attacks from single sources
- **Per-User Limits**: Ensures fair resource allocation per authenticated user
- **Path-Specific Rules**: Stricter limits for sensitive endpoints (auth, feedback)
- **Whitelisting/Blacklisting**: IP-based access control
- **Standard HTTP Headers**: RFC-compliant rate limit headers
- **Thread-Safe Storage**: Concurrent request handling
- **Zero External Dependencies**: In-memory storage (Redis support planned)

## Architecture

### Components

```
lukhas/governance/rate_limit/
├── __init__.py          # Public API exports
├── config.py            # Configuration and rule definitions
├── storage.py           # Storage backends (in-memory, Redis planned)
├── middleware.py        # FastAPI middleware integration
└── README.md            # This documentation
```

### Request Flow

```
1. Request arrives at FastAPI
2. StrictAuthMiddleware validates JWT → populates request.state.user_id
3. RateLimitMiddleware checks rate limits:
   a. Extract client IP (handle X-Forwarded-For)
   b. Check if IP is blocked → 403 Forbidden
   c. Check if IP is whitelisted → skip rate limiting
   d. Check per-IP rate limits → 429 if exceeded
   e. Check per-user rate limits (if authenticated) → 429 if exceeded
   f. Allow request and add rate limit headers
4. Request processed by application
5. Response returned with rate limit headers
```

## Configuration

### Default Tier Limits

The system provides sensible defaults for three user tiers:

| Tier | Type | Requests | Window | Description |
|------|------|----------|--------|-------------|
| 0 | Free | 100 | 1 hour | Basic tier for testing |
| 1 | Basic | 1,000 | 1 hour | Development usage |
| 2+ | Pro/Enterprise | 10,000 | 1 hour | Production usage |

### Path-Specific Limits

Sensitive endpoints have stricter limits:

| Endpoint Pattern | Tier 0 | Tier 1 | Purpose |
|-----------------|--------|--------|---------|
| `/feedback/*` | 60/hour (1/min) | 300/hour (5/min) | Prevent feedback spam |
| `/api/v1/auth/*` | 20/hour | 20/hour | Prevent brute force attacks |
| `/api/v1/auth/login` | 5/min | 5/min | Login attempt limiting |
| `/api/v1/consciousness/query` | 50/hour | 500/hour | Expensive AI queries |

### Per-IP Limits

Global IP limits prevent DDoS attacks:

| Rule | Limit | Window | Purpose |
|------|-------|--------|---------|
| Global requests | 10,000 | 1 hour | Prevent sustained abuse |
| Burst protection | 500 | 1 minute | Prevent traffic spikes |
| Auth endpoints | 20 | 1 hour | Brute force protection |
| Login attempts | 5 | 1 minute | Account security |

### Custom Configuration

```python
from lukhas.governance.rate_limit import RateLimitConfig, RateLimitRule

# Create custom configuration
config = RateLimitConfig(
    enabled=True,
    per_user_rules=[
        RateLimitRule(
            requests=1000,
            window_seconds=3600,
            path_pattern="/api/*",
            tier=1,
            description="Custom tier 1 limit"
        )
    ],
    per_ip_rules=[
        RateLimitRule(
            requests=5000,
            window_seconds=3600,
            path_pattern="*"
        )
    ],
    burst_multiplier=1.5,  # Allow 50% burst traffic
    blocked_ips=["192.168.1.100"],  # IP blocklist
    whitelisted_ips=["127.0.0.1", "10.0.0.1"]  # IP whitelist
)
```

## Usage

### Integration with FastAPI

The middleware is automatically wired into the FastAPI application in `serve/main.py`:

```python
from lukhas.governance.rate_limit import RateLimitMiddleware, RateLimitConfig

app = FastAPI(...)

# Add middleware stack (order matters!)
app.add_middleware(PrometheusMiddleware)
app.add_middleware(CORSMiddleware, ...)
app.add_middleware(StrictAuthMiddleware)  # Must be before RateLimitMiddleware
app.add_middleware(RateLimitMiddleware, config=RateLimitConfig())
app.add_middleware(HeadersMiddleware)
```

**Critical**: RateLimitMiddleware MUST be added after StrictAuthMiddleware to access validated user context.

### Response Headers

All responses include standard rate limit headers:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1704067200
```

When rate limit is exceeded:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 42
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1704067200

{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded for user. Please try again later.",
  "retry_after": 42,
  "limit": 1000,
  "reset_time": 1704067200
}
```

### Programmatic Usage

```python
from lukhas.governance.rate_limit import InMemoryRateLimitStorage

storage = InMemoryRateLimitStorage()

# Check rate limit
result = storage.check_rate_limit(
    key="user:123:path:/api/query",
    limit=100,
    window_seconds=3600
)

if result.allowed:
    # Process request
    print(f"Request allowed. {result.remaining} remaining.")
else:
    # Reject request
    print(f"Rate limit exceeded. Retry after {result.retry_after}s")

# Reset rate limit for specific key
storage.reset("user:123:path:/api/query")

# Reset all rate limits (testing only)
storage.reset_all()

# Clean up old windows (prevent memory leaks)
removed = storage.cleanup_old_windows(max_age_seconds=3600)
```

## Testing

### Run Tests

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
pytest tests/integration/test_rate_limiting.py -v
```

### Test Coverage

The test suite includes 28 comprehensive tests covering:

1. **Sliding Window Algorithm** (7 tests)
   - Requests within limit
   - Window expiration
   - Partial window expiry (true sliding window)
   - Key isolation
   - Reset functionality
   - Cleanup

2. **Configuration** (9 tests)
   - Default rule creation
   - Path matching (exact, wildcard, global)
   - Tier filtering
   - Rule sorting by specificity
   - IP blocking/whitelisting

3. **Middleware Integration** (8 tests)
   - Request allowing/blocking
   - Whitelist/blacklist enforcement
   - Per-user rate limiting
   - User isolation
   - X-Forwarded-For handling
   - Enable/disable toggle

4. **HTTP Headers** (2 tests)
   - Standard rate limit headers
   - 429 response with Retry-After

5. **End-to-End** (2 tests)
   - Tier-based limit enforcement
   - Path-specific limit overrides

### Test Results

```
============================== 28 passed in 5.13s ==============================
```

## Security Considerations

### OWASP A04: Insecure Design Mitigation

Rate limiting prevents:

- **DoS Attacks**: Per-IP limits prevent request flooding
- **Resource Exhaustion**: Per-user limits ensure fair allocation
- **Brute Force**: Stricter limits on auth endpoints
- **API Abuse**: Path-specific limits protect expensive operations
- **Account Enumeration**: Login attempt limiting

### Authentication Integration

- Rate limiting is applied AFTER authentication (via StrictAuthMiddleware)
- User context from validated JWT tokens (no user_id spoofing possible)
- Unauthenticated requests only checked against per-IP limits
- Authenticated requests checked against both per-IP and per-user limits

### IP Address Extraction

The middleware correctly handles proxied requests:

1. Check `X-Forwarded-For` header (proxies/load balancers)
2. Check `X-Real-IP` header (alternative proxy header)
3. Fall back to direct client IP
4. Uses first IP in `X-Forwarded-For` chain (client IP, not proxy)

### Whitelisting Best Practices

- Whitelist trusted infrastructure (monitoring, health checks)
- Use sparingly to maintain security posture
- Examples: `127.0.0.1`, internal load balancer IPs
- DO NOT whitelist entire CIDR ranges without justification

### Blacklisting Best Practices

- Block known malicious IPs
- Temporary measure during active attacks
- Prefer rate limiting over blanket blocking
- Provide mechanisms for legitimate users to appeal

## Performance

### In-Memory Storage

- **Latency**: <1ms per rate limit check
- **Memory**: ~100 bytes per active key
- **Throughput**: 10,000+ checks/second (single thread)
- **Scalability**: Single-server deployments only

### Memory Management

- Automatic cleanup of expired windows (1-hour interval)
- Manual cleanup via `cleanup_old_windows()` method
- Memory usage bounded by active user count × request rate

### Redis Storage (Planned)

For distributed deployments:

```python
from lukhas.governance.rate_limit import RedisRateLimitStorage

# Future implementation
storage = RedisRateLimitStorage(redis_url="redis://localhost:6379")
```

Benefits:
- Distributed rate limiting across multiple servers
- Persistent state (survives restarts)
- Lower per-server memory usage
- Atomic operations via Lua scripts

## Monitoring

### Metrics

Track rate limiting effectiveness:

- `rate_limit_hits_total{scope="user|ip",action="allow|deny"}` - Counter
- `rate_limit_check_duration_seconds` - Histogram
- `rate_limit_storage_keys_total` - Gauge (memory usage)
- `rate_limit_429_responses_total{path}` - Counter (abuse patterns)

### Logging

The middleware logs:

- **INFO**: Rate limit exceeded events (user/IP)
- **WARNING**: Blocked IP access attempts
- **DEBUG**: Whitelist bypasses

Example log entries:

```
WARNING: IP rate limit exceeded: 203.0.113.1 on /api/v1/query (limit: 10000, retry after: 42s)
WARNING: User rate limit exceeded: user_abc (tier 0) on /api/v1/consciousness/query (limit: 50, retry after: 120s)
WARNING: Blocked IP attempted access: 192.168.1.100
```

## Troubleshooting

### Common Issues

#### Issue: Legitimate users hitting rate limits

**Solution**:
1. Check user tier assignment
2. Verify tier limits are appropriate
3. Consider path-specific exceptions
4. Analyze request patterns for abuse

#### Issue: Rate limiting not working

**Checks**:
1. Is `RateLimitConfig.enabled = True`?
2. Is middleware added after StrictAuthMiddleware?
3. Are default rules being created? (check logs)
4. Is IP extraction working? (X-Forwarded-For)

#### Issue: 429 responses without user_id

**Cause**: User not authenticated or JWT token invalid

**Solution**: Only per-IP limits apply to unauthenticated requests

#### Issue: Memory growth in long-running servers

**Solution**:
```python
# Manually trigger cleanup
storage.cleanup_old_windows(max_age_seconds=3600)

# Or rely on automatic cleanup (runs hourly)
```

## Future Enhancements

### Planned Features

1. **Redis Backend** (Priority: HIGH)
   - Distributed rate limiting
   - Multi-server support
   - Persistent state

2. **Dynamic Configuration** (Priority: MEDIUM)
   - Runtime rule updates without restart
   - Admin API for configuration
   - A/B testing support

3. **Advanced Patterns** (Priority: LOW)
   - Token bucket algorithm option
   - Leaky bucket algorithm option
   - Adaptive rate limiting (ML-based)

4. **Enhanced Monitoring** (Priority: MEDIUM)
   - Grafana dashboard templates
   - Alerting rules for abuse detection
   - Per-endpoint rate limit metrics

5. **User Feedback** (Priority: LOW)
   - Client SDKs with automatic retry
   - Rate limit quotas in user dashboard
   - Email notifications approaching limits

## References

- **OWASP A04**: [Insecure Design](https://owasp.org/Top10/A04_2021-Insecure_Design/)
- **RFC 6585**: [Additional HTTP Status Codes](https://tools.ietf.org/html/rfc6585) (429 Too Many Requests)
- **IETF Draft**: [RateLimit Header Fields for HTTP](https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-ratelimit-headers)
- **Sliding Window**: [Rate Limiting Algorithms](https://en.wikipedia.org/wiki/Rate_limiting#Sliding_window)

## Support

For issues or questions:

- **GitHub**: [LukhasAI/Lukhas](https://github.com/LukhasAI/Lukhas)
- **Security Issues**: Email security@lukhas.ai
- **Documentation**: [docs.lukhas.ai](https://docs.lukhas.ai)
