# Observability Module

Complete observability stack for LUKHAS with OpenTelemetry tracing, audit trails, and adaptive feedback.

## Features

✅ **OpenTelemetry Integration** - Trace MATRIZ pipeline stages with automatic exception recording
✅ **Audit Trails** - Append-only JSONL ledgers with optional Postgres backend
✅ **Signed Permalinks** - HMAC-SHA256 signed links with TTL for secure sharing
✅ **Consent-Aware Redaction** - Automatic PII masking based on viewer scopes
✅ **Evidence Tracking** - Link decisions to source data with consent metadata
✅ **Governance Events** - Log policy decisions (ALLOW/DENY/REDACT/WARN)
✅ **Adaptive Feedback** - Collect user ratings and follow-ups linked to traces

## Quick Start

```python
from observability.tracing import matriz_stage
from observability.audit.models import DecisionTrace
from observability.audit.storage import write_json

# 1. Trace MATRIZ stages
with matriz_stage("Memory", trace_id=trace_id):
    memories = retrieve_memories()

# 2. Store decision trace
trace = DecisionTrace(
    trace_id=trace_id,
    input_hash=hash_input(user_input),
    started_at=start_time,
    finished_at=end_time,
    latency_ms=latency,
    final_outcome={"text": answer},
    confidence=0.85
)
await write_json("decision_trace", {"id": trace_id, **trace.model_dump()})

# 3. Generate signed permalink
from observability.audit.links import mint_signed_query
query = mint_signed_query(trace_id, viewer_id, ttl_seconds=300)
```

## Structure

```
observability/
├── tracing.py              # OpenTelemetry span wrappers
├── audit/
│   ├── models.py           # Pydantic data models
│   ├── storage.py          # JSONL/Postgres storage
│   ├── api.py              # FastAPI endpoints
│   ├── links.py            # Signed permalink system
│   ├── redaction.py        # PII masking & consent
│   ├── schema.sql          # Postgres schema
│   └── system.py           # Legacy audit trail (Phase 1)
└── feedback/
    └── api.py              # Feedback submission endpoints
```

## Documentation

See [docs/observability/AUDIT_TRAILS.md](../docs/observability/AUDIT_TRAILS.md) for complete documentation.

## Demo

```bash
# Run complete observability demo
python3 demos/demo_audit_observability.py

# Validate audit ledgers
make audit-validate-ledger
make feedback-validate
```

## API

### Audit Endpoints (`/audit/*`)

- `POST /audit/trace` - Submit decision trace
- `POST /audit/span` - Submit trace span
- `POST /audit/evidence` - Submit evidence link
- `POST /audit/governance` - Submit governance event
- `POST /audit/link` - Generate signed permalink
- `GET /audit/trace/{id}` - Retrieve complete trace (requires signature)

### Feedback Endpoints (`/feedback/*`)

- `POST /feedback/` - Submit user feedback
- `POST /feedback/followup` - Submit follow-up answers
- `GET /feedback/card/{trace_id}` - Get adaptive feedback card

## Security

🔒 **Signed Links**: HMAC-SHA256 with TTL
🔒 **Consent Scopes**: `default`, `pii`, `tenant`, `allow`
🔒 **PII Redaction**: Automatic email, phone, SSN, credit card masking
🔒 **Rate Limiting**: Apply to `/audit/link` and `/audit/trace` (TODO)

## Configuration

```bash
# Required in production
export AUDIT_LINK_SECRET=your-secret-key-here
export AUDIT_REQUIRE_SIGNED=true

# Optional
export AUDIT_DEFAULT_SCOPE=default
```

## Integration with Existing Systems

This module **extends** the Phase 1 governance systems:

- **Phase 1** (`observability/audit/system.py`): Local audit trail with consent-aware redaction
- **Phase 2** (this module): OpenTelemetry + FastAPI + signed links + multi-table storage

Both systems work together:
- Phase 1 for local/offline auditing
- Phase 2 for distributed tracing & API access

## Performance

- OTel span overhead: <5%
- Audit write: <10ms p95
- Signed link gen: <1ms
- Redaction: <5ms per item
- Trace retrieval: <100ms p95

## Roadmap

- [ ] Async Postgres adapter with SQLAlchemy
- [ ] Frontend audit trail viewer (React)
- [ ] Frontend feedback cards
- [ ] Adaptive follow-up questions
- [ ] Auto-improvement proposals
- [ ] Real-time trace updates (WebSocket)
- [ ] Differential privacy for analytics
