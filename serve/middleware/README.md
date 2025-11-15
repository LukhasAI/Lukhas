# LUKHAS Serve Middleware

Middleware components for the LUKHAS production API.

## StrictAuthMiddleware

Comprehensive authentication middleware for production API with ΛiD token validation, JWT verification, rate limiting, and audit logging.

### Features

- **JWT Token Validation**: Validates ΛiD tokens using signature verification
- **Path-based Protection**: Only enforces auth on `/v1/*` paths
- **Rate Limiting**: 100 requests/minute per user (configurable)
- **Audit Logging**: Comprehensive authentication event logging
- **OpenAI-Compatible Errors**: Returns standardized error responses
- **HTTPS Enforcement**: Optional HTTPS requirement for production

### Usage

#### Basic Setup

```python
from fastapi import FastAPI
from serve.middleware.strict_auth import StrictAuthMiddleware

app = FastAPI()

# Add middleware with default settings
app.add_middleware(StrictAuthMiddleware)
```

#### Advanced Configuration

```python
app.add_middleware(
    StrictAuthMiddleware,
    exempted_paths=["/health", "/docs", "/metrics"],  # Paths that bypass auth
    require_https=True,  # Enforce HTTPS in production
    protected_path_prefix="/v1",  # Only /v1/* requires auth
    rate_limit_enabled=True,  # Enable rate limiting
    max_requests_per_minute=100,  # Rate limit threshold
)
```

### Protected Paths

By default, only paths starting with `/v1` require authentication:

- ✅ `/v1/models` - **Requires Auth**
- ✅ `/v1/chat/completions` - **Requires Auth**
- ❌ `/health` - No auth (exempted)
- ❌ `/docs` - No auth (exempted)
- ❌ `/v2/experimental` - No auth (different prefix)

### Authentication Flow

1. **Extract Token**: Get Bearer token from `Authorization` header
2. **Validate JWT**: Verify signature, expiry, and claims using ΛiD auth system
3. **Rate Limit**: Check user hasn't exceeded request threshold
4. **Attach Context**: Add `UserContext` to `request.state.user`
5. **Audit Log**: Record authentication event
6. **Process Request**: Forward to endpoint handler

### Error Responses

All errors follow OpenAI-compatible format:

```json
{
  "error": {
    "type": "invalid_api_key",
    "code": "invalid_api_key",
    "message": "Missing Authorization header"
  }
}
```

**Common Errors:**

| Status | Message | Cause |
|--------|---------|-------|
| 401 | Missing Authorization header | No `Authorization` header provided |
| 401 | Authorization header must use Bearer scheme | Wrong auth scheme (e.g., `Basic`) |
| 401 | Bearer token is empty | Empty token after `Bearer ` |
| 401 | Invalid authentication credentials | JWT verification failed |
| 401 | Token expired | Token past expiry time |
| 401 | Token missing user_id claim | Invalid token structure |
| 429 | Rate limit exceeded | User exceeded 100 req/min |
| 403 | HTTPS required | Non-HTTPS request when enforcement enabled |

### Accessing User Context

After successful authentication, user context is available in the request:

```python
@app.get("/v1/protected")
async def protected_endpoint(request: Request):
    user = request.state.user  # UserContext object

    print(f"User ID: {user.user_id}")
    print(f"Scopes: {user.scopes}")
    print(f"Claims: {user.token_claims}")
    print(f"Auth Time: {user.authenticated_at}")

    return {"user_id": user.user_id}
```

### Rate Limiting

**Algorithm**: Sliding window

**Default**: 100 requests per minute per user

**Implementation**: In-memory for development, should use Redis for production

**Response Headers**:
- `X-RateLimit-Remaining`: Number of requests remaining

**Production Recommendation**:
```python
# For production, replace in-memory rate limiter with Redis
# See: lukhas.governance.rate_limit for Redis-based implementation
```

### Audit Logging

All authentication events are logged to `lukhas.audit.auth` logger:

**Success Events** (INFO):
```json
{
  "timestamp": "2025-11-15T10:30:00Z",
  "path": "/v1/models",
  "method": "GET",
  "success": true,
  "user_id": "user_123",
  "client_ip": "192.168.1.100",
  "user_agent": "curl/7.68.0"
}
```

**Failure Events** (WARNING):
```json
{
  "timestamp": "2025-11-15T10:30:00Z",
  "path": "/v1/models",
  "method": "GET",
  "success": false,
  "user_id": null,
  "error": "Missing Authorization header",
  "client_ip": "192.168.1.100",
  "user_agent": "curl/7.68.0"
}
```

### Integration Points

#### ΛiD Authentication System
- **Module**: `labs.core.security.auth`
- **Function**: `get_auth_system()`
- **Method**: `verify_jwt(token: str) -> Optional[dict]`

#### Rate Limiting (Future)
- **Module**: `lukhas.governance.rate_limit`
- **Status**: Currently using in-memory implementation
- **Production**: Should migrate to Redis-based limiter

#### Audit System (Future)
- **Module**: `lukhas.governance.audit`
- **Status**: Currently using Python logging
- **Production**: Should integrate with compliance audit system

### Testing

Comprehensive test suite in `tests/unit/serve/middleware/test_strict_auth.py`:

```bash
pytest tests/unit/serve/middleware/test_strict_auth.py -v
```

**Test Coverage**:
- ✅ Authorization header validation
- ✅ Bearer token format validation
- ✅ JWT verification via auth system
- ✅ 401 error responses on auth failure
- ✅ OpenAI-compatible error format
- ✅ /v1/* path enforcement
- ✅ Exempted paths bypass
- ✅ All HTTP methods (GET, POST, PUT, DELETE)
- ✅ Concurrent request handling
- ✅ Token extraction edge cases

### Security Considerations

1. **JWT Secret**: Ensure `JWT_PRIVATE_KEY` env var is set in production
2. **HTTPS**: Enable `require_https=True` in production
3. **Rate Limiting**: Monitor and adjust thresholds based on usage patterns
4. **Audit Logs**: Ensure audit logs are sent to secure, tamper-proof storage
5. **Token Revocation**: Auth system checks token revocation list
6. **Scope Validation**: Future enhancement for fine-grained permissions

### Performance

- **Overhead**: ~1-2ms per request for JWT validation
- **Rate Limiter**: O(1) check with periodic cleanup
- **Memory**: ~100 bytes per active user in rate limiter
- **Cleanup**: Automatic cleanup of old rate limit entries every 5 minutes

### Production Deployment Checklist

- [ ] Set `JWT_PRIVATE_KEY` environment variable
- [ ] Enable `require_https=True`
- [ ] Configure appropriate `max_requests_per_minute`
- [ ] Set up Redis for rate limiting (replace in-memory limiter)
- [ ] Configure audit log destination (e.g., CloudWatch, Elasticsearch)
- [ ] Set up monitoring for 401/429 error rates
- [ ] Configure exempted paths for health checks, metrics
- [ ] Test with production traffic patterns
- [ ] Set up alerts for authentication failures

### Future Enhancements

1. **Scope-based Access Control**: Fine-grained permissions per endpoint
2. **Redis Rate Limiting**: Distributed rate limiting across instances
3. **Token Refresh**: Support for refresh token flow
4. **Multi-factor Authentication**: Additional verification for sensitive operations
5. **IP Allowlisting**: Restrict access by IP ranges
6. **Custom Claims Validation**: Validate custom JWT claims
7. **Metrics Integration**: Prometheus metrics for auth events
8. **Circuit Breaker**: Fail-open on auth system outages

## Other Middleware

- **CacheMiddleware**: Response caching with cache invalidation
- **PrometheusMiddleware**: Metrics collection for monitoring
- **SecurityHeadersMiddleware**: Security headers (X-Frame-Options, CSP, etc.)

## License

Copyright (c) 2025 LUKHAS AI. All rights reserved.
