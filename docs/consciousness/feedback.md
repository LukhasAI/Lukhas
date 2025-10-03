# Feedback + Audit Integration

- **Why**: Hyper-adaptability needs tight, per-decision feedback.
- **How**: Each output has an `audit node_id`. The UI binds feedback to that id. Back end validates & stores append-only JSONL.

## Quickstart

```python
from consciousness.feedback.api import quick_card, record_feedback

card = quick_card(node_id="abc123", scale=10)
receipt = record_feedback({
  "node_id": "abc123",
  "rating": 7.5,
  "comment": "Good answer but missed an edge case",
  "tags": ["edge-case"],
  "consent": {"feedback.store": True, "pii.read": False},
  "created_at": "2025-10-03T10:00:00Z"
})
```

## Artifacts

- File: `audit_logs/feedback.jsonl` (append-only)
- Validated against: `schemas/feedback_event_v1.json`
