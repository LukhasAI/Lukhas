# [N3] NIAS PII Detection Integration (with ABAS)

**Labels**: `enhancement`, `nias`, `abas`, `privacy`, `gdpr`
**Priority**: High
**Milestone**: Q2 2026
**Estimated Effort**: 3-4 days
**Depends On**: #A4 (ABAS middleware must be deployed first)

---

## Problem Statement

NIAS currently logs audit events without PII awareness:
1. **GDPR Art. 32 Gap**: Cannot demonstrate PII detection measures
2. **No PII Flagging**: Audit logs don't indicate which requests contained PII
3. **Compliance Blind Spot**: Cannot generate reports on PII processing volumes
4. **Manual Review**: Security team cannot filter for PII-related incidents

**Current Behavior**: NIAS logs all requests equally, no PII detection.

## Proposed Solution

Integrate NIAS with ABAS PII detection to flag PII-containing requests:

### Architecture

```
Request → ABAS Middleware → OPA PII Detection → NIAS Middleware
                                    ↓
                            request.state.pii_detected = True
                            request.state.pii_categories = ["email", "ssn"]
                                    ↓
                            NIAS reads state, adds to event:
                            {
                              "pii_detected": true,
                              "pii_categories": ["email", "ssn"],
                              "notes": "PII detected: email, ssn"
                            }
```

### Implementation

**ABAS OPA Policy** (`enforcement/abas/pii_detection.rego`):
```rego
package pii

# Detect PII patterns in request body
pii_detected := {
    "email": count(email_matches) > 0,
    "ssn": count(ssn_matches) > 0,
    "phone": count(phone_matches) > 0,
    "credit_card": count(cc_matches) > 0
}

# Email regex
email_matches := [m | regex.find_n(`\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b`, input.body_text, -1)[_] = m]

# SSN regex (US)
ssn_matches := [m | regex.find_n(`\b\d{3}-\d{2}-\d{4}\b`, input.body_text, -1)[_] = m]

# Phone regex (international)
phone_matches := [m | regex.find_n(`\b(\+\d{1,3}[-\s]?)?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}\b`, input.body_text, -1)[_] = m]

# Credit card regex (basic Luhn check)
cc_matches := [m | regex.find_n(`\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b`, input.body_text, -1)[_] = m]
```

**ABAS Middleware** (`enforcement/abas/middleware.py`):
```python
class ABasMiddleware:
    async def dispatch(self, request: Request, call_next):
        # ... existing ABAS logic ...

        # Check PII detection policy
        opa_response = await self.query_opa({
            "input": {
                "body_text": await request.body().decode("utf-8"),
                "route": str(request.url.path),
            }
        })

        # Set request state for NIAS
        if opa_response.get("result", {}).get("pii_detected"):
            request.state.pii_detected = True
            request.state.pii_categories = [
                k for k, v in opa_response["result"]["pii_detected"].items() if v
            ]

        response = await call_next(request)
        return response
```

**NIAS Middleware Enhancement** (`lukhas/guardian/nias/middleware.py:204-232`):
```python
# Extract PII detection results from ABAS
pii_detected = getattr(request.state, 'pii_detected', False)
pii_categories = getattr(request.state, 'pii_categories', [])

# Build audit event with PII flagging
event = NIASAuditEvent(
    route=str(request.url.path),
    method=request.method,
    status_code=status_code,
    duration_ms=duration_ms,
    caller=caller,
    trace_id=trace_id,
    drift_score=_estimate_drift(request),
    request_meta={
        "content_type": request.headers.get("content-type"),
        "accept": request.headers.get("accept"),
        "user_agent": request.headers.get("user-agent"),
        "pii_detected": pii_detected,  # NEW FIELD
        "pii_categories": pii_categories if pii_detected else [],  # NEW FIELD
    },
    response_meta={...},
    notes=f"PII detected: {', '.join(pii_categories)}" if pii_detected else None
)
```

**NIAS Event Schema Update** (`lukhas/guardian/nias/models.py`):
```python
class NIASAuditEvent(BaseModel):
    # ... existing fields ...

    # New PII detection fields (backward-compatible with extra="allow")
    pii_detected: Optional[bool] = Field(default=False, description="PII detected in request")
    pii_categories: List[str] = Field(default_factory=list, description="PII types: email, ssn, phone, etc.")
```

### Example Audit Event (with PII)

```json
{
  "ts": "2025-11-13T15:30:00Z",
  "route": "/v1/chat/completions",
  "method": "POST",
  "status_code": 200,
  "duration_ms": 123.45,
  "caller": "org-acme-corp",
  "trace_id": "trace-abc123",
  "drift_score": 0.15,
  "pii_detected": true,
  "pii_categories": ["email", "phone"],
  "request_meta": {
    "content_type": "application/json",
    "pii_detected": true,
    "pii_categories": ["email", "phone"]
  },
  "notes": "PII detected: email, phone"
}
```

## Acceptance Criteria

- [ ] ABAS OPA policy `pii_detection.rego` detects 5 PII types (email, SSN, phone, CC, IBAN)
- [ ] ABAS sets `request.state.pii_detected` and `request.state.pii_categories`
- [ ] NIAS reads state and populates `pii_detected`, `pii_categories` fields
- [ ] NIAS events with PII flagged in JSONL logs
- [ ] Grafana dashboard: "PII-Containing Requests" panel (count by category)
- [ ] GDPR compliance report: "Requests with PII" generated from NIAS logs
- [ ] Documentation: `docs/nias/PII_DETECTION.md`
- [ ] At least 1000 PII-containing requests correctly flagged in first week

## Implementation Plan

**Phase 1**: OPA PII Detection (1 day)
1. Implement `pii_detection.rego` with regex patterns
2. Write unit tests: `enforcement/abas/pii_detection_test.rego`
3. Test with known PII samples

**Phase 2**: ABAS Integration (1 day)
1. Update `ABasMiddleware` to call PII detection policy
2. Set `request.state.pii_detected` and `request.state.pii_categories`
3. Test with integration tests

**Phase 3**: NIAS Integration (1 day)
1. Update `NIASAuditEvent` schema to add PII fields
2. Read ABAS state in NIAS middleware
3. Write PII-flagged events to JSONL
4. Verify with integration tests

**Phase 4**: Reporting & Monitoring (1 day)
1. Create Grafana dashboard panel for PII metrics
2. Implement GDPR compliance report generator
3. Test with production-like data

## Testing Strategy

```bash
# Unit tests (OPA policy)
opa test enforcement/abas/pii_detection.rego enforcement/abas/pii_detection_test.rego

# Integration tests (ABAS + NIAS)
pytest tests/integration/test_abas_nias_pii.py

# Test samples
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "My email is user@example.com and phone is 555-1234"}]}'

# Verify NIAS log
tail -n 1 audits/nias_events.jsonl | jq '.pii_detected'
# Expected: true
```

## Monitoring & Alerting

**Metrics**:
- `nias_pii_requests_total{category="email|ssn|phone|cc|iban"}` (counter)
- `nias_pii_categories_per_request` (histogram)
- `abas_pii_detection_errors_total` (counter, if regex fails)

**Alerts**:
```yaml
- alert: HighPIIVolume
  expr: rate(nias_pii_requests_total[1h]) > 100
  annotations:
    summary: "High PII volume: >100 PII-containing requests/hour"
    description: "May indicate data exfiltration or compliance issue"
```

## GDPR Compliance Benefits

**Art. 30 (Records of Processing)**:
- NIAS logs demonstrate PII processing activities
- Query: `cat audits/nias_events.jsonl | jq 'select(.pii_detected == true)' | wc -l`

**Art. 32 (Security of Processing)**:
- Automated PII detection proves "appropriate technical measures"
- Audit trail for DPA inspections

**Art. 35 (Data Protection Impact Assessment)**:
- NIAS provides data for DPIA: "We process X emails, Y SSNs per day"

## Privacy Considerations

**IMPORTANT**: NIAS logs the FLAG, NOT the actual PII content.

**What's Logged**:
- ✅ `pii_detected: true`
- ✅ `pii_categories: ["email"]`

**What's NOT Logged**:
- ❌ Actual email addresses
- ❌ Actual SSNs, phone numbers, etc.
- ❌ Request/response bodies

**Rationale**: Privacy by design (GDPR Art. 25) - audit logs must not become a PII repository.

## Related Issues

- #A4: ABAS FastAPI Middleware (prerequisite)
- #N2: NIAS Drift Detection (combine PII + drift scoring)
- #XXX: PII redaction in logs (future: replace detected PII with `[REDACTED]`)

## References

- [GDPR Art. 4(1) Definition of Personal Data](https://gdpr-info.eu/art-4-gdpr/)
- [NIST Privacy Framework](https://www.nist.gov/privacy-framework)
- [OPA Regex Functions](https://www.openpolicyagent.org/docs/latest/policy-reference/#regex)
- Gonzo Spec: `docs/gonzo/SYSTEMS_2.md` (N3 section)

---

**Created**: 2025-11-13
**Author**: Security Enhancement Team
**Reviewers**: @security-team, @legal-team, @dpo
