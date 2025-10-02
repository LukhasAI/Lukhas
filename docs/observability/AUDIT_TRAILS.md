# LUKHAS Audit Trails & Observability

Complete observability stack for MATRIZ pipeline with OpenTelemetry tracing, audit trails, and adaptive feedback.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MATRIZ Pipeline                          │
│  Memory → Attention → Thought → Risk → Intent → Action      │
│            (each stage wrapped with OTel spans)             │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Audit Storage Layer                       │
│  • Decision Traces   • Spans   • Evidence   • Governance    │
│  • JSONL (dev) or Postgres (prod)                          │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Access Layer                             │
│  • Signed Permalinks  • Consent-Aware Redaction            │
│  • Scope-Based Access  • PII Masking                        │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  Feedback Loop                              │
│  • User Ratings  • Follow-ups  • Auto-Improvement          │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Instrument MATRIZ Stages

```python
from observability.tracing import matriz_stage

async def process_user_request(user_input: str, trace_id: str):
    # Memory stage
    with matriz_stage("Memory", trace_id=trace_id):
        memories = await retrieve_memories(user_input)

    # Thought stage
    with matriz_stage("Thought", trace_id=trace_id):
        answer = await generate_answer(memories)

    return answer
```

### 2. Store Audit Trails

```python
from observability.audit.models import DecisionTrace, TraceSpan
from observability.audit.storage import write_json

# Store decision trace
trace = DecisionTrace(
    trace_id=trace_id,
    input_hash=hash_input(user_input),
    started_at=start_time,
    finished_at=end_time,
    latency_ms=int((end_time - start_time) * 1000),
    final_outcome={"text": answer},
    confidence=0.85
)
await write_json("decision_trace", {"id": trace_id, **trace.model_dump()})
```

### 3. Generate Signed Permalink

```python
from observability.audit.links import mint_signed_query

# Generate short-lived (5min) signed link
query = mint_signed_query(trace_id, viewer_id="user@example.com", ttl_seconds=300)
url = f"/audit/trace/{trace_id}?{query}"
```

### 4. Collect Feedback

```python
# User submits feedback
POST /feedback/
{
  "trace_id": "trace-abc123",
  "rating_0_10": 8,
  "text": "Great answer!"
}
```

## Security Features

### Signed Permalinks

All audit trail links are signed with HMAC-SHA256:

- **Payload**: `trace={id}&viewer={id}&exp={timestamp}`
- **Signature**: `HMAC(secret, payload)`
- **TTL**: 5 minutes (configurable)
- **Verification**: Automatic on every request when `AUDIT_REQUIRE_SIGNED=true`

### Consent-Aware Redaction

Evidence is redacted based on viewer scopes:

```python
# Viewer with low scope sees redacted content
viewer_scopes = ["default"]
evidence_scope = "pii"

# PII automatically masked
"Email: user@example.com" → "Email: ██████"

# Viewer with high scope sees full content
viewer_scopes = ["default", "pii", "allow"]
# No redaction applied
```

### PII Patterns Detected

- Email addresses
- Phone numbers
- IBAN/account numbers
- SSN (US)
- Credit card numbers

## API Endpoints

### Audit Submission

```bash
# Submit decision trace
POST /audit/trace
{
  "trace_id": "trace-abc123",
  "input_hash": "sha256...",
  "started_at": 1234567890.123,
  "finished_at": 1234567890.456,
  "latency_ms": 333,
  "final_outcome": {...},
  "confidence": 0.85
}

# Submit span
POST /audit/span
{
  "span_id": "span-xyz",
  "trace_id": "trace-abc123",
  "module": "Memory",
  "operation": "retrieve",
  "ts_start": 1234567890.123,
  "ts_end": 1234567890.156,
  "status": "OK"
}

# Submit evidence
POST /audit/evidence
{
  "span_id": "span-xyz",
  "source_type": "memory",
  "uri_or_key": "memory://fold-850",
  "sha256": "abc123...",
  "excerpt": "Retrieved memory content...",
  "consent_scope": "default"
}
```

### Audit Retrieval

```bash
# Generate signed link
POST /audit/link
{
  "trace_id": "trace-abc123",
  "ttl_seconds": 300
}
→ { "url": "/audit/trace/trace-abc123?..." }

# Get complete trace (with signed query)
GET /audit/trace/trace-abc123?trace=...&viewer=...&exp=...&sig=...
→ {
  "trace": {...},
  "viewer": {"id": "...", "scopes": [...]},
  "spans": [...],
  "evidence_by_span": {...},
  "governance_events": [...],
  "feedback_events": [...]
}
```

### Feedback

```bash
# Submit feedback
POST /feedback/
{
  "trace_id": "trace-abc123",
  "rating_0_10": 8,
  "text": "Great answer!",
  "labels": {"helpful": 1.0}
}

# Get adaptive feedback card
GET /feedback/card/trace-abc123
→ {
  "trace_id": "trace-abc123",
  "questions": [...]
}
```

## Storage

### JSONL (Development)

Append-only JSONL files in `audit_logs/`:

```
audit_logs/
├── decision_trace.jsonl
├── trace_span.jsonl
├── evidence_link.jsonl
├── governance_event.jsonl
└── feedback_event.jsonl
```

### Postgres (Production)

Run schema migration:

```bash
psql $DATABASE_URL -f observability/audit/schema.sql
```

Switch to Postgres backend (TODO: add async SQLAlchemy adapter).

## Validation

```bash
# Validate audit ledgers against schema
make audit-validate-ledger

# Validate feedback events
make feedback-validate
```

## Environment Variables

```bash
# Signed link secret (REQUIRED in production)
AUDIT_LINK_SECRET=your-secret-key-here

# Require signed links (set to "true" in production)
AUDIT_REQUIRE_SIGNED=false

# Default viewer scope
AUDIT_DEFAULT_SCOPE=default
```

## Demo

```bash
# Run complete observability demo
python3 demos/demo_audit_observability.py
```

## Integration Checklist

- [ ] Add OTel SDK init in app startup
- [ ] Wrap all MATRIZ stages with `matriz_stage()`
- [ ] Submit decision traces after each request
- [ ] Submit evidence when fetching external data
- [ ] Generate signed links for audit trail viewers
- [ ] Configure `AUDIT_LINK_SECRET` in production
- [ ] Set `AUDIT_REQUIRE_SIGNED=true` in production
- [ ] Add viewer scope headers from ΛID system
- [ ] Rate-limit `/audit/link` endpoint
- [ ] Monitor audit trail latency and 5xx errors

## Performance Targets

- OTel span overhead: <5% of operation latency
- Audit write latency: <10ms p95
- Signed link generation: <1ms
- Redaction latency: <5ms per evidence item
- Complete trace retrieval: <100ms p95

## Phase 2 Features (TODO)

- [ ] Adaptive follow-up questions based on feedback
- [ ] Taxonomy classification for feedback labels
- [ ] Sentiment analysis on feedback text
- [ ] Auto-improvement proposals from feedback
- [ ] Canary testing for auto-changes
- [ ] Merkle logging for governance events
- [ ] Differential privacy for analytics
- [ ] Frontend audit trail viewer (React/Next.js)
- [ ] Frontend feedback cards
- [ ] Real-time trace updates (WebSocket)
