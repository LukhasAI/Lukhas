# [H3] Security Headers CSP Reporting & Monitoring

**Labels**: `enhancement`, `security-headers`, `monitoring`, `csp`
**Priority**: Medium
**Milestone**: Q2 2026
**Estimated Effort**: 2-3 days

---

## Problem Statement

The current SecurityHeaders middleware applies a Content Security Policy (CSP) but lacks:
1. **No Violation Reporting**: Cannot detect CSP violations (blocked resources)
2. **No Report-Only Mode**: Must deploy strict CSP immediately (risky)
3. **No Monitoring**: Cannot track which directives are being violated
4. **No Analytics**: Don't know if CSP is too strict or too permissive
5. **Manual Tuning**: CSP refinement requires manual log review

**Current CSP** (`lukhas/middleware/security_headers.py:37-38`):
```python
response.headers.setdefault("Content-Security-Policy",
    "default-src 'self'; object-src 'none'; frame-ancestors 'none'")
```

**Issues**:
- No reporting endpoint configured (`report-uri` or `report-to` directive)
- Deployed in enforcement mode (blocks immediately, no testing phase)
- Generic policy (doesn't account for Swagger UI, Grafana, etc.)

## Proposed Solution

Implement **CSP violation reporting** with **report-only mode** for safe deployment:

### Architecture

```
Browser → FastAPI App (with CSP header)
            ↓
    User loads page with CSP
            ↓
    Browser detects CSP violation
    (e.g., inline script blocked)
            ↓
    POST /csp-report
    {
      "csp-report": {
        "document-uri": "https://api.lukhas.ai/docs",
        "violated-directive": "script-src",
        "blocked-uri": "inline",
        "source-file": "https://api.lukhas.ai/docs"
      }
    }
            ↓
    CSPReportHandler logs violation
            ↓
    Prometheus metric: csp_violations_total
            ↓
    Grafana alert: CSP violation spike
```

### 1. CSP Reporting Endpoint

**Implementation** (`lukhas/middleware/csp_reporting.py`):
```python
"""CSP violation reporting endpoint."""
import logging
from typing import Dict

from fastapi import APIRouter, Request
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


class CSPReport(BaseModel):
    """CSP violation report (browser-generated)."""
    document_uri: str
    violated_directive: str
    blocked_uri: str
    source_file: str
    line_number: int = 0
    column_number: int = 0
    status_code: int = 0


class CSPReportWrapper(BaseModel):
    """Wrapper for CSP report (browser sends as {"csp-report": {...}})."""
    csp_report: CSPReport


@router.post("/csp-report")
async def handle_csp_report(report: CSPReportWrapper):
    """Handle CSP violation reports from browsers."""
    violation = report.csp_report

    # Log violation
    logger.warning(
        f"CSP violation: {violation.violated_directive} blocked {violation.blocked_uri} "
        f"on {violation.document_uri} (line {violation.line_number})"
    )

    # Increment Prometheus counter
    from prometheus_client import Counter
    csp_violations_total.labels(
        directive=violation.violated_directive,
        blocked_uri=violation.blocked_uri[:100],  # Truncate long URIs
    ).inc()

    return {"status": "reported"}


# Prometheus metric
from prometheus_client import Counter
csp_violations_total = Counter(
    "csp_violations_total",
    "Total CSP violations reported by browsers",
    ["directive", "blocked_uri"]
)
```

**Integration** (`serve/main.py`):
```python
from lukhas.middleware.csp_reporting import router as csp_router

app.include_router(csp_router, tags=["security"])
```

### 2. CSP Report-Only Mode

**Strategy**: Deploy in report-only mode first, monitor violations, then enforce.

**Report-Only Header**:
```python
# lukhas/middleware/security_headers.py (enhancement)
CSP_REPORT_ONLY = os.getenv("CSP_REPORT_ONLY", "true").lower() == "true"
CSP_REPORT_URI = os.getenv("CSP_REPORT_URI", "https://api.lukhas.ai/csp-report")

if CSP_REPORT_ONLY:
    # Report-only: log violations but don't block
    response.headers.setdefault("Content-Security-Policy-Report-Only",
        f"default-src 'self'; object-src 'none'; frame-ancestors 'none'; report-uri {CSP_REPORT_URI}")
else:
    # Enforce mode: block violations
    response.headers.setdefault("Content-Security-Policy",
        f"default-src 'self'; object-src 'none'; frame-ancestors 'none'; report-uri {CSP_REPORT_URI}")
```

**Deployment Phases**:
1. **Week 1-2**: Deploy with `CSP_REPORT_ONLY=true`, collect violation data
2. **Week 3**: Analyze violations, refine CSP (allowlist Swagger UI, etc.)
3. **Week 4**: Deploy with `CSP_REPORT_ONLY=false` (enforcement mode)

### 3. Enhanced CSP Policy

**Current Policy** (too strict for Swagger UI):
```
default-src 'self'; object-src 'none'; frame-ancestors 'none'
```

**Enhanced Policy** (allows Swagger UI, Grafana):
```
default-src 'self';
script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;
style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;
img-src 'self' data: https:;
font-src 'self' data:;
connect-src 'self' https://api.lukhas.ai;
object-src 'none';
frame-ancestors 'none';
base-uri 'self';
form-action 'self';
report-uri https://api.lukhas.ai/csp-report
```

**Explanation**:
- `script-src 'unsafe-inline'`: Required for Swagger UI (inline scripts)
- `style-src 'unsafe-inline'`: Required for Swagger UI (inline styles)
- `img-src data: https:`: Allow data URIs and HTTPS images
- `connect-src`: Allow API calls to self
- `report-uri`: Send violations to /csp-report

**Implementation**:
```python
# lukhas/middleware/security_headers.py (enhancement)
CSP_POLICY = os.getenv("CSP_POLICY", "default")

CSP_POLICIES = {
    "default": "default-src 'self'; object-src 'none'; frame-ancestors 'none'",
    "swagger": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self'; "
        "object-src 'none'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    ),
}

csp_value = CSP_POLICIES.get(CSP_POLICY, CSP_POLICIES["default"])
if CSP_REPORT_URI:
    csp_value += f"; report-uri {CSP_REPORT_URI}"
```

### 4. CSP Violation Dashboard

**Grafana Panel**:
```json
{
  "title": "CSP Violations (Last 24h)",
  "targets": [
    {
      "expr": "sum by (directive) (rate(csp_violations_total[24h]))",
      "legendFormat": "{{directive}}"
    }
  ],
  "type": "graph"
}
```

**Top Blocked URIs**:
```json
{
  "title": "Top 10 Blocked URIs",
  "targets": [
    {
      "expr": "topk(10, sum by (blocked_uri) (csp_violations_total))",
      "legendFormat": "{{blocked_uri}}"
    }
  ],
  "type": "table"
}
```

### 5. CSP Nonce Generation (Future)

**Problem**: `'unsafe-inline'` weakens CSP (allows all inline scripts).

**Solution**: Use nonces for inline scripts:
```html
<!-- Backend generates nonce per request -->
<script nonce="abc123xyz">
  console.log('This script is allowed');
</script>
```

**CSP Header**:
```
script-src 'self' 'nonce-abc123xyz'; style-src 'self' 'nonce-abc123xyz'
```

**Implementation** (future):
```python
import secrets

def generate_csp_nonce(request: Request) -> str:
    """Generate CSP nonce for inline scripts/styles."""
    nonce = secrets.token_urlsafe(16)
    request.state.csp_nonce = nonce
    return nonce

# In middleware
nonce = generate_csp_nonce(request)
csp_value = f"script-src 'self' 'nonce-{nonce}'; style-src 'self' 'nonce-{nonce}'"
```

## Acceptance Criteria

- [ ] `/csp-report` endpoint implemented and handles browser violation reports
- [ ] CSP deployed in report-only mode (`Content-Security-Policy-Report-Only` header)
- [ ] Prometheus metric `csp_violations_total{directive,blocked_uri}` exported
- [ ] Grafana dashboard with 2 panels (violations over time, top blocked URIs)
- [ ] Enhanced CSP policy supports Swagger UI without violations
- [ ] CSP enforcement mode tested (after 2 weeks of report-only)
- [ ] Documentation: `docs/security/CSP_GUIDE.md`
- [ ] Alert configured: CSP violation spike >10/min

## Implementation Plan

**Phase 1**: Reporting Endpoint (1 day)
1. Implement `lukhas/middleware/csp_reporting.py`
2. Add `/csp-report` route to `serve/main.py`
3. Test with manual CSP violation (inline script in test page)

**Phase 2**: Report-Only Deployment (0.5 days)
1. Add `CSP_REPORT_ONLY` env var support
2. Deploy with `CSP_REPORT_ONLY=true`
3. Monitor for 2 weeks

**Phase 3**: Policy Refinement (0.5 days)
1. Analyze top 10 violated directives
2. Refine CSP to allowlist necessary resources (Swagger UI, etc.)
3. Test with updated policy

**Phase 4**: Enforcement Mode (1 day)
1. Deploy with `CSP_REPORT_ONLY=false`
2. Monitor for broken functionality
3. Rollback if critical issues

## Testing Strategy

```bash
# Unit tests
pytest tests/middleware/test_csp_reporting.py

# Integration tests
pytest tests/integration/test_csp_violations.py

# Manual testing (trigger CSP violation)
# 1. Add inline script to test page
echo '<html><body><script>alert("XSS")</script></body></html>' > /tmp/test.html
# 2. Serve with CSP header
python3 -m http.server 8080
# 3. Open in browser, check console for CSP violation
# 4. Verify /csp-report receives POST

# Load test (with CSP header)
locust -f tests/load/locustfile_csp.py --users 100
```

## Monitoring & Alerting

**Metrics**:
- `csp_violations_total{directive,blocked_uri}` (counter)
- `csp_reports_received_total` (counter, /csp-report endpoint hits)
- `csp_report_errors_total` (counter, invalid reports)

**Alerts**:
```yaml
- alert: CSPViolationSpike
  expr: rate(csp_violations_total[5m]) > 10
  annotations:
    summary: "CSP violations spiking: >10/min (broken functionality or attack)"

- alert: CSPReportEndpointDown
  expr: up{job="lukhas-api", endpoint="/csp-report"} == 0
  annotations:
    summary: "CSP report endpoint down (violations not being logged)"
```

## Benefits

1. **Safe Deployment**: Report-only mode allows testing without breaking functionality
2. **Visibility**: Know exactly what CSP is blocking
3. **Data-Driven**: Refine policy based on real violation data
4. **Attack Detection**: Spike in violations may indicate XSS attack attempts
5. **Compliance**: Demonstrate proactive XSS protection (OWASP A7)

## Related Issues

- #H4: Security Headers Advanced Configuration (nonce generation, per-route CSP)
- #D4: ZAP CI/CD Enhancements (validate CSP in DAST scans)
- #XXX: Swagger UI CSP compatibility (allowlist cdn.jsdelivr.net)

## References

- [CSP MDN Docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [CSP Evaluator (Google)](https://csp-evaluator.withgoogle.com/)
- [CSP Reporting Spec](https://www.w3.org/TR/CSP3/#reporting)
- [OWASP CSP Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)
- Gonzo Spec: `docs/gonzo/DAST + NIAS + ABAS + Security Headers .yml` (H3 section)

---

**Created**: 2025-11-13
**Author**: Security Enhancement Team
**Reviewers**: @security-team, @frontend-team
