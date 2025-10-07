---
status: wip
type: documentation
owner: unknown
module: ui
redirect: false
moved_to: null
---

# LUKHΛS Feedback Cards (v1)

The chat UI shows a small "brain" icon next to each output. Clicking it opens a **Feedback Card** bound to the exact `audit node_id`.

- Rating scale: 5 / 6 / 10 (configurable)
- Free-text comment (max 2k chars)
- Optional chips/tags
- Consent toggle ("store feedback") must be explicit

## UI Contract

- Schema: `schemas/feedback_card_v1.json`
- Submission payload: `schemas/feedback_event_v1.json`

## Example flow

1) Frontend calls `/feedback/card?node_id=...` → returns card spec (`quick_card()`).
2) User submits → frontend POSTs feedback event.
3) Backend calls `consciousness.feedback.api.record_feedback(evt)` → appends to `audit_logs/feedback.jsonl`.
4) Optional: trigger tailored follow-ups using the comment/tags (kept simple in v1).

## Tailored follow-up (v2 idea)

- If rating ≤ 2 (out of 5): ask one clarifying question
- If tag = "unsafe": immediately show audit trace + safe-mode explanation
