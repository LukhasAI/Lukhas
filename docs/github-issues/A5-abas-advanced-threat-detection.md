# [A5] ABAS Advanced Threat Detection & Response

**Labels**: `enhancement`, `abas`, `security`, `threat-detection`
**Priority**: High
**Milestone**: Q3 2026
**Estimated Effort**: 5-7 days
**Depends On**: #A4 (ABAS performance optimization), #N2 (NIAS drift detection)

---

## Problem Statement

ABAS currently provides basic policy enforcement (PII detection, consent validation) but lacks advanced threat detection:
1. **No Attack Pattern Recognition**: Cannot detect SQL injection, XSS, SSRF attempts
2. **No Rate Limiting Intelligence**: Fixed rate limits, no adaptive throttling
3. **No Behavioral Analysis**: Cannot detect credential stuffing, brute force attacks
4. **No Automated Response**: Security team must manually block malicious IPs
5. **No Threat Intelligence Integration**: Doesn't use external threat feeds (e.g., known bad IPs)

**Current Capabilities**: Static policy rules only (regex-based PII detection).

## Proposed Solution

Enhance ABAS with **ML-based threat detection** and **automated response**:

### Architecture

```
Request → ABAS Middleware
            ↓
    [Threat Detection Pipeline]
            ↓
    ┌─────────────────────────────┐
    │ 1. Static Rules (OPA)       │ ← SQL injection, XSS patterns
    │ 2. Drift Detection (ML)     │ ← NIAS drift score >0.8
    │ 3. Behavioral Analysis      │ ← Brute force, credential stuffing
    │ 4. Threat Intel Lookup      │ ← IP reputation, domain blacklists
    │ 5. Adaptive Rate Limiting   │ ← Dynamic throttling based on risk
    └─────────────────────────────┘
            ↓
    [Risk Scoring: 0-100]
            ↓
    ┌─────────────────────────────┐
    │ Risk < 30: Allow            │
    │ Risk 30-60: Flag + Allow    │
    │ Risk 60-80: Throttle        │
    │ Risk > 80: Block + Alert    │
    └─────────────────────────────┘
```

### 1. Attack Pattern Detection (Static Rules)

**OPA Policy** (`enforcement/abas/attack_patterns.rego`):
```rego
package attacks

# SQL Injection patterns
sql_injection_detected := count(sql_patterns) > 0

sql_patterns := [p |
    p := input.body_text
    regex.match(`(?i)(union|select|insert|update|delete|drop|--|;|'|"|\bor\b.*=.*\bor\b)`, p)
]

# XSS patterns
xss_detected := count(xss_patterns) > 0

xss_patterns := [p |
    p := input.body_text
    regex.match(`(?i)(<script|javascript:|onerror=|onload=|<iframe|eval\()`, p)
]

# SSRF patterns (internal IP addresses, localhost)
ssrf_detected := count(ssrf_patterns) > 0

ssrf_patterns := [p |
    p := input.body_text
    regex.match(`(127\.0\.0\.1|localhost|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|169\.254\.\d+\.\d+)`, p)
]

# Path traversal
path_traversal_detected := count(path_patterns) > 0

path_patterns := [p |
    p := input.request_path
    regex.match(`(\.\./|\.\.\\|%2e%2e|%252e)`, p)
]

# Aggregate risk score from attack patterns
attack_risk_score := (sql_injection_detected * 30) + (xss_detected * 25) + (ssrf_detected * 20) + (path_traversal_detected * 15)
```

### 2. Behavioral Analysis (Brute Force Detection)

**Implementation** (`enforcement/abas/behavioral.py`):
```python
"""Behavioral analysis for ABAS threat detection."""
import time
from collections import defaultdict, deque
from typing import Dict, Tuple

class BehavioralAnalyzer:
    """Detect brute force, credential stuffing, and other behavioral attacks."""

    def __init__(self):
        # Track failed auth attempts: IP -> deque of timestamps
        self._failed_auth: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10))
        # Track unique user attempts: IP -> set of usernames
        self._username_attempts: Dict[str, set] = defaultdict(set)

    def analyze_auth_failure(self, ip: str, username: str) -> Tuple[bool, str]:
        """Analyze authentication failure for brute force patterns.

        Returns:
            (is_attack, reason)
        """
        now = time.time()

        # Record failure
        self._failed_auth[ip].append(now)
        self._username_attempts[ip].add(username)

        # Check 1: >5 failures in 60 seconds = brute force
        recent_failures = [t for t in self._failed_auth[ip] if now - t < 60]
        if len(recent_failures) >= 5:
            return True, f"Brute force: {len(recent_failures)} failures in 60s"

        # Check 2: >10 unique usernames from same IP = credential stuffing
        if len(self._username_attempts[ip]) >= 10:
            return True, f"Credential stuffing: {len(self._username_attempts[ip])} unique usernames"

        return False, "Normal"

    def clear_old_data(self):
        """Periodically clear data >1 hour old (prevent memory leak)."""
        now = time.time()
        for ip in list(self._failed_auth.keys()):
            # Remove failures >1 hour old
            self._failed_auth[ip] = deque(
                (t for t in self._failed_auth[ip] if now - t < 3600),
                maxlen=10
            )
            if not self._failed_auth[ip]:
                del self._failed_auth[ip]


# Global analyzer instance
_analyzer = BehavioralAnalyzer()


def analyze_request_behavior(request, response) -> int:
    """Analyze request/response for behavioral attacks.

    Returns:
        Risk score (0-30)
    """
    risk_score = 0

    # Check authentication failures
    if response.status_code == 401:
        ip = request.client.host
        username = request.headers.get("X-Username", "unknown")
        is_attack, reason = _analyzer.analyze_auth_failure(ip, username)

        if is_attack:
            logger.warning(f"Behavioral attack detected: {reason} from {ip}")
            risk_score += 30  # High risk

    return risk_score
```

### 3. Threat Intelligence Integration

**Integration with IPQualityScore / AbuseIPDB**:
```python
# enforcement/abas/threat_intel.py
import httpx

IPQS_API_KEY = os.getenv("IPQS_API_KEY")

async def check_ip_reputation(ip: str) -> int:
    """Check IP reputation using IPQualityScore.

    Returns:
        Risk score (0-50): 0 = clean, 50 = known attacker
    """
    if not IPQS_API_KEY:
        return 0  # No threat intel configured

    url = f"https://www.ipqualityscore.com/api/json/ip/{IPQS_API_KEY}/{ip}"

    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(url)
            data = response.json()

            # IPQualityScore fraud score (0-100)
            fraud_score = data.get("fraud_score", 0)

            # Normalize to 0-50 range
            return min(50, fraud_score // 2)

    except Exception as e:
        logger.warning(f"Threat intel lookup failed for {ip}: {e}")
        return 0  # Fail-open on threat intel errors
```

### 4. Adaptive Rate Limiting

**Risk-Based Throttling**:
```python
# enforcement/abas/rate_limiting.py
from typing import Dict

# Rate limits per risk level
RATE_LIMITS = {
    "low": 1000,    # req/hour (risk < 30)
    "medium": 100,  # req/hour (risk 30-60)
    "high": 10,     # req/hour (risk 60-80)
    "critical": 0,  # req/hour (risk > 80) - blocked
}

class AdaptiveRateLimiter:
    """Risk-based rate limiting."""

    def __init__(self):
        self._request_counts: Dict[str, int] = {}  # caller -> count
        self._last_reset: float = time.time()

    def check_rate_limit(self, caller: str, risk_score: int) -> Tuple[bool, str]:
        """Check if request should be rate limited.

        Returns:
            (allow, reason)
        """
        # Reset counts every hour
        if time.time() - self._last_reset > 3600:
            self._request_counts.clear()
            self._last_reset = time.time()

        # Determine rate limit based on risk
        if risk_score >= 80:
            limit = RATE_LIMITS["critical"]
        elif risk_score >= 60:
            limit = RATE_LIMITS["high"]
        elif risk_score >= 30:
            limit = RATE_LIMITS["medium"]
        else:
            limit = RATE_LIMITS["low"]

        # Check current count
        count = self._request_counts.get(caller, 0)
        if count >= limit:
            return False, f"Rate limit exceeded: {count}/{limit} req/hour (risk={risk_score})"

        # Increment count
        self._request_counts[caller] = count + 1
        return True, "OK"
```

### 5. Automated Response & Alerting

**Integration** (`enforcement/abas/middleware.py`):
```python
class ABasMiddleware:
    async def dispatch(self, request: Request, call_next):
        # ... existing ABAS logic ...

        # Calculate composite risk score
        risk_score = 0

        # 1. Static attack patterns (OPA)
        opa_response = await self._query_opa(request)
        risk_score += opa_response.get("result", {}).get("attack_risk_score", 0)

        # 2. Drift detection (NIAS)
        drift_score = getattr(request.state, "drift_score", 0.0)
        risk_score += int(drift_score * 50)  # Convert 0.0-1.0 to 0-50

        # 3. Threat intelligence (IP reputation)
        ip_risk = await check_ip_reputation(request.client.host)
        risk_score += ip_risk

        # 4. Behavioral analysis
        response = await call_next(request)
        behavior_risk = analyze_request_behavior(request, response)
        risk_score += behavior_risk

        # 5. Adaptive rate limiting
        caller = request.headers.get("OpenAI-Organization", request.client.host)
        allow, reason = rate_limiter.check_rate_limit(caller, risk_score)

        # Risk-based decision
        if risk_score >= 80:
            # BLOCK + ALERT
            logger.error(f"🚨 HIGH RISK REQUEST BLOCKED: {risk_score} from {caller}")
            await send_slack_alert(f"High risk request blocked: {risk_score} from {caller}")
            return Response(content='{"error": "Request blocked: security risk"}', status_code=403)

        elif risk_score >= 60:
            # THROTTLE
            if not allow:
                logger.warning(f"⚠️ Rate limit applied: {reason}")
                return Response(content=f'{{"error": "{reason}"}}', status_code=429)

        elif risk_score >= 30:
            # FLAG (allow but log warning)
            logger.warning(f"⚠️ Medium risk request: {risk_score} from {caller}")

        # Low risk: allow
        return response
```

## Acceptance Criteria

- [ ] Attack pattern detection (SQL injection, XSS, SSRF, path traversal) implemented in OPA
- [ ] Behavioral analysis (brute force, credential stuffing) detects 10+ attacks/day
- [ ] Threat intelligence integration (IPQualityScore or AbuseIPDB) enabled
- [ ] Adaptive rate limiting: high-risk IPs limited to 10 req/hour
- [ ] Automated blocking: risk >80 requests blocked + Slack alert sent
- [ ] Composite risk scoring: combines 4 sources (static, drift, threat intel, behavioral)
- [ ] Dashboard: Grafana panels for risk score distribution, blocked requests, threat intel hits
- [ ] Documentation: `docs/abas/THREAT_DETECTION.md`
- [ ] Load test: 1000 req/s with threat detection enabled (<10ms overhead)

## Implementation Plan

**Phase 1**: Static Attack Patterns (2 days)
1. Implement `attack_patterns.rego` with 4 attack types
2. Write unit tests: `enforcement/abas/attack_patterns_test.rego`
3. Test with known attack payloads

**Phase 2**: Behavioral Analysis (2 days)
1. Implement `behavioral.py` with brute force detection
2. Track failed auth attempts per IP
3. Test with simulated brute force attacks

**Phase 3**: Threat Intel Integration (1 day)
1. Sign up for IPQualityScore API (free tier: 5000 lookups/month)
2. Implement `threat_intel.py` async lookup
3. Cache results (1 hour TTL) to reduce API calls

**Phase 4**: Adaptive Rate Limiting (1 day)
1. Implement `rate_limiting.py` with risk-based limits
2. Integrate with composite risk scoring
3. Test with high-risk requests

**Phase 5**: Automated Response (1 day)
1. Integrate all components into ABAS middleware
2. Implement Slack alerting for high-risk blocks
3. Test end-to-end with simulated attacks

## Testing Strategy

```bash
# Attack pattern tests
opa test enforcement/abas/attack_patterns.rego enforcement/abas/attack_patterns_test.rego

# Behavioral analysis tests
pytest tests/abas/test_behavioral.py

# Integration tests (full threat detection)
pytest tests/integration/test_abas_threat_detection.py

# Simulated attacks
python3 tests/security/simulate_sql_injection.py
python3 tests/security/simulate_brute_force.py
python3 tests/security/simulate_credential_stuffing.py
```

## Monitoring & Alerting

**Metrics**:
- `abas_risk_score{source="static|drift|threat_intel|behavioral"}` (histogram, 0-100)
- `abas_requests_blocked_total{reason="high_risk|rate_limit"}` (counter)
- `abas_threat_intel_hits_total{verdict="malicious|suspicious|clean"}` (counter)
- `abas_attack_patterns_detected_total{type="sql_injection|xss|ssrf|path_traversal"}` (counter)

**Alerts**:
```yaml
- alert: HighRiskRequestSpike
  expr: rate(abas_requests_blocked_total{reason="high_risk"}[5m]) > 5
  annotations:
    summary: "High risk requests spiking: >5 blocks/5min (potential attack)"

- alert: KnownMaliciousIP
  expr: abas_threat_intel_hits_total{verdict="malicious"} > 0
  annotations:
    summary: "Known malicious IP detected: {{$labels.ip}}"
```

## Benefits

1. **Proactive Defense**: Block attacks before they reach application logic
2. **Reduced Alert Fatigue**: Composite risk scoring reduces false positives
3. **Adaptive Security**: Rate limits adjust dynamically to threat level
4. **Intelligence-Driven**: External threat feeds enhance detection
5. **Automated Response**: Security team only alerted for critical threats

## Related Issues

- #N2: NIAS Drift Detection (prerequisite for drift-based risk scoring)
- #A4: ABAS Performance Optimization (caching reduces overhead)
- #XXX: SOC integration (forward ABAS alerts to SIEM)

## References

- [OWASP Attack Patterns](https://owasp.org/www-community/attacks/)
- [IPQualityScore API](https://www.ipqualityscore.com/documentation/overview)
- [AbuseIPDB API](https://www.abuseipdb.com/api)
- [NIST SP 800-94: Intrusion Detection](https://csrc.nist.gov/publications/detail/sp/800-94/final)
- Gonzo Spec: `docs/gonzo/SYSTEMS_2.md` (A5 section)

---

**Created**: 2025-11-13
**Author**: Security Enhancement Team
**Reviewers**: @security-team, @soc-team
