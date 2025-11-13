# [H4] Security Headers Advanced Configuration & Per-Route Policies

**Labels**: `enhancement`, `security-headers`, `configuration`
**Priority**: Low
**Milestone**: Q3 2026
**Estimated Effort**: 2-3 days
**Depends On**: #H3 (CSP reporting must be deployed first)

---

## Problem Statement

The current SecurityHeaders middleware applies the same headers to ALL routes:
1. **No Per-Route Customization**: Swagger UI needs different CSP than API endpoints
2. **No Header Overrides**: Cannot disable headers for specific routes (e.g., `/metrics`)
3. **Static Configuration**: All headers hardcoded in middleware (no config file)
4. **No Environment-Specific Policies**: Production uses same headers as development
5. **Manual Management**: Updating headers requires code changes + deployment

**Current Implementation** (`lukhas/middleware/security_headers.py`):
```python
response.headers.setdefault("X-Frame-Options", "DENY")  # Applied to ALL routes
response.headers.setdefault("Content-Security-Policy", "...")  # Same CSP everywhere
```

**Issues**:
- Swagger UI (`/docs`) needs `X-Frame-Options: SAMEORIGIN` (not DENY)
- Prometheus metrics (`/metrics`) don't need CSP
- OpenAPI spec (`/openapi.json`) is public data, doesn't need strict headers

## Proposed Solution

Implement **per-route security header policies** with **external configuration**:

### Architecture

```
Request → SecurityHeaders Middleware
            ↓
    Match route against policy config
            ↓
    ┌─────────────────────────────────┐
    │ Route: /docs → swagger_policy   │
    │ Route: /metrics → metrics_policy│
    │ Route: /v1/* → api_policy       │
    │ Default → strict_policy         │
    └─────────────────────────────────┘
            ↓
    Apply matched policy headers
            ↓
    Response with route-specific headers
```

### 1. Configuration File

**YAML Config** (`config/security_headers.yml`):
```yaml
# Security Headers Configuration
# Reference: https://owasp.org/www-project-secure-headers/

# Default policy (applied to all routes unless overridden)
default:
  x-frame-options: DENY
  x-content-type-options: nosniff
  referrer-policy: strict-origin-when-cross-origin
  permissions-policy: camera=(), microphone=(), geolocation=()
  content-security-policy: "default-src 'self'; object-src 'none'; frame-ancestors 'none'"
  strict-transport-security: max-age=31536000; includeSubDomains; preload
  x-xss-protection: "0"  # Disabled (CSP is better)

# Swagger UI policy (allows embedding, inline scripts)
swagger:
  x-frame-options: SAMEORIGIN  # Allow iframe in same origin
  content-security-policy: |
    default-src 'self';
    script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;
    style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;
    img-src 'self' data: https:;
    font-src 'self' data:
  # Inherit other headers from default

# Metrics policy (minimal headers for Prometheus scraping)
metrics:
  # Only essential headers, no CSP
  x-content-type-options: nosniff
  # Override: remove other headers

# Public content policy (OpenAPI spec, health checks)
public:
  x-frame-options: SAMEORIGIN
  referrer-policy: no-referrer
  # No CSP (static JSON data)

# Route mappings (regex patterns)
routes:
  - pattern: "^/docs.*"
    policy: swagger
  - pattern: "^/redoc.*"
    policy: swagger
  - pattern: "^/openapi.json$"
    policy: public
  - pattern: "^/healthz$"
    policy: public
  - pattern: "^/metrics$"
    policy: metrics
  - pattern: "^/v1/.*"
    policy: default  # Strict API headers
  - pattern: ".*"  # Catch-all
    policy: default
```

### 2. Policy Matcher

**Implementation** (`lukhas/middleware/security_headers.py`):
```python
"""Enhanced security headers middleware with per-route policies."""
import re
from pathlib import Path
from typing import Dict, Optional

import yaml
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Load config
CONFIG_PATH = Path(__file__).parent.parent.parent / "config/security_headers.yml"

with open(CONFIG_PATH) as f:
    CONFIG = yaml.safe_load(f)

# Compile route patterns
ROUTE_PATTERNS = [
    (re.compile(route["pattern"]), route["policy"])
    for route in CONFIG["routes"]
]


def get_policy_for_route(route_path: str) -> Dict[str, str]:
    """Get security header policy for given route.

    Args:
        route_path: Request path (e.g., /v1/chat/completions)

    Returns:
        Dict of header name -> value
    """
    # Match against route patterns
    for pattern, policy_name in ROUTE_PATTERNS:
        if pattern.match(route_path):
            policy = CONFIG.get(policy_name, CONFIG["default"])

            # Merge with default (if policy doesn't override)
            merged = CONFIG["default"].copy()
            merged.update(policy)

            return merged

    # Fallback to default
    return CONFIG["default"]


class SecurityHeaders(BaseHTTPMiddleware):
    """Apply security headers based on route-specific policies."""

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        # Get policy for this route
        policy = get_policy_for_route(str(request.url.path))

        # Apply headers from policy
        for header_name, header_value in policy.items():
            if header_value is not None:  # Skip if explicitly set to null (remove header)
                # Convert header_name to HTTP header format
                http_header = header_name.replace("_", "-").title()
                response.headers.setdefault(http_header, str(header_value))

        return response
```

### 3. Environment-Specific Policies

**Development** (`config/security_headers.dev.yml`):
```yaml
# Development environment (relaxed CSP, verbose errors)
default:
  content-security-policy: "default-src 'self' 'unsafe-inline' 'unsafe-eval'; report-uri http://localhost:8000/csp-report"
  x-frame-options: SAMEORIGIN  # Allow iframe for debugging
  # No HSTS (allow HTTP)
```

**Production** (`config/security_headers.prod.yml`):
```yaml
# Production environment (strict CSP, HSTS enabled)
default:
  content-security-policy: "default-src 'self'; object-src 'none'; frame-ancestors 'none'; report-uri https://api.lukhas.ai/csp-report"
  x-frame-options: DENY
  strict-transport-security: max-age=31536000; includeSubDomains; preload
```

**Loading** (via env var):
```python
import os

ENV = os.getenv("APP_ENV", "development")
CONFIG_PATH = Path(__file__).parent.parent.parent / f"config/security_headers.{ENV}.yml"
```

### 4. Dynamic Header Generation (Nonces)

**CSP Nonces** (per-request unique values):
```python
import secrets

class SecurityHeaders(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate nonce for this request
        nonce = secrets.token_urlsafe(16)
        request.state.csp_nonce = nonce

        # Get policy
        policy = get_policy_for_route(str(request.url.path))

        # Replace {{nonce}} placeholder in CSP
        csp = policy.get("content-security-policy", "")
        if "{{nonce}}" in csp:
            csp = csp.replace("{{nonce}}", nonce)

        # Apply headers
        response = await call_next(request)
        response.headers.setdefault("Content-Security-Policy", csp)

        return response
```

**Template Usage** (in HTML):
```html
<!-- Backend renders nonce in template -->
<script nonce="{{ request.state.csp_nonce }}">
  console.log('This script is allowed');
</script>
```

### 5. Header Validation & Testing

**Validation Script** (`scripts/validate_security_headers.py`):
```python
"""Validate security headers configuration."""
import yaml
from pathlib import Path

CONFIG_PATH = Path("config/security_headers.yml")

with open(CONFIG_PATH) as f:
    config = yaml.safe_load(f)

# Required headers
REQUIRED_HEADERS = [
    "x-frame-options",
    "x-content-type-options",
    "referrer-policy",
    "content-security-policy"
]

# Validate default policy
for header in REQUIRED_HEADERS:
    if header not in config["default"]:
        print(f"❌ Missing required header in default policy: {header}")
        exit(1)

# Validate route patterns
for route in config["routes"]:
    if "pattern" not in route or "policy" not in route:
        print(f"❌ Invalid route config: {route}")
        exit(1)

    # Check policy exists
    policy_name = route["policy"]
    if policy_name not in config:
        print(f"❌ Unknown policy: {policy_name} in route {route['pattern']}")
        exit(1)

print("✅ Security headers config valid")
```

**CI Integration** (`.github/workflows/validate-security-headers.yml`):
```yaml
name: Validate Security Headers Config

on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate config
        run: python3 scripts/validate_security_headers.py

      - name: Check for common CSP mistakes
        run: |
          # Fail if 'unsafe-eval' in production config
          if grep -q "unsafe-eval" config/security_headers.prod.yml; then
            echo "❌ Production CSP contains 'unsafe-eval' (insecure)"
            exit 1
          fi
```

## Acceptance Criteria

- [ ] `config/security_headers.yml` configuration file with 4 policies (default, swagger, metrics, public)
- [ ] Per-route policy matching (regex-based) implemented
- [ ] Environment-specific configs (dev, staging, prod) supported
- [ ] CSP nonce generation for inline scripts/styles
- [ ] Validation script ensures config correctness
- [ ] CI workflow validates security headers config on PRs
- [ ] Documentation: `docs/security/SECURITY_HEADERS_CONFIG.md`
- [ ] Test suite covers all route patterns

## Implementation Plan

**Phase 1**: Configuration File (1 day)
1. Create `config/security_headers.yml` with 4 policies
2. Define route patterns for Swagger, metrics, API
3. Test with different routes

**Phase 2**: Policy Matcher (1 day)
1. Implement `get_policy_for_route()` with regex matching
2. Merge policies with defaults
3. Apply headers in middleware

**Phase 3**: Environment-Specific Configs (0.5 days)
1. Create `security_headers.dev.yml` and `security_headers.prod.yml`
2. Load based on `APP_ENV` env var
3. Test in both environments

**Phase 4**: CSP Nonces (0.5 days)
1. Generate per-request nonces
2. Replace `{{nonce}}` placeholder in CSP
3. Test with inline scripts

**Phase 5**: Validation & CI (0.5 days)
1. Implement validation script
2. Add CI workflow
3. Test with invalid configs

## Testing Strategy

```bash
# Unit tests
pytest tests/middleware/test_security_headers_config.py

# Test route matching
curl -I http://localhost:8000/docs | grep X-Frame-Options
# Expected: X-Frame-Options: SAMEORIGIN

curl -I http://localhost:8000/v1/models | grep X-Frame-Options
# Expected: X-Frame-Options: DENY

curl -I http://localhost:8000/metrics | grep Content-Security-Policy
# Expected: (no CSP header)

# Test environment-specific config
APP_ENV=production pytest tests/integration/test_security_headers_prod.py
```

## Monitoring & Alerting

**Metrics**:
- `security_headers_policy_applied_total{route_pattern,policy}` (counter)
- `security_headers_config_errors_total` (counter, if config invalid)
- `security_headers_nonce_generated_total` (counter, CSP nonces)

**Alerts**:
```yaml
- alert: SecurityHeadersConfigInvalid
  expr: security_headers_config_errors_total > 0
  annotations:
    summary: "Security headers config has errors (failing to load)"
```

## Benefits

1. **Flexibility**: Different headers for different routes (Swagger, API, metrics)
2. **No Code Changes**: Update headers via config file, no deployment needed
3. **Environment-Aware**: Strict headers in production, relaxed in dev
4. **CSP Nonces**: Eliminate `'unsafe-inline'` (better security)
5. **Validation**: CI catches misconfigurations before deployment

## Migration Guide

**Before** (hardcoded in middleware):
```python
response.headers.setdefault("X-Frame-Options", "DENY")
```

**After** (config-driven):
```yaml
# config/security_headers.yml
default:
  x-frame-options: DENY
```

**Steps**:
1. Create `config/security_headers.yml` with current headers
2. Deploy new middleware with config support
3. Test that headers unchanged
4. Customize per-route policies as needed

## Related Issues

- #H3: CSP Reporting (CSP nonces require reporting for testing)
- #D4: ZAP CI/CD Enhancements (validate headers in DAST scans)
- #XXX: Swagger UI customization (may need additional CSP directives)

## References

- [OWASP Secure Headers Project](https://owasp.org/www-project-secure-headers/)
- [Mozilla Observatory](https://observatory.mozilla.org/) - Test headers
- [SecurityHeaders.com](https://securityheaders.com/) - Grade headers
- [CSP Nonces Best Practices](https://csp.withgoogle.com/docs/strict-csp.html)
- Gonzo Spec: `docs/gonzo/DAST + NIAS + ABAS + Security Headers .yml` (H4 section)

---

**Created**: 2025-11-13
**Author**: Security Enhancement Team
**Reviewers**: @security-team, @devops-team
