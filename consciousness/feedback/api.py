#!/usr/bin/env python3
"""
LUKHΛS Feedback API (v1)
- Validates UI feedback against JSON schema
- Links to audit node_id
- Stores append-only JSONL for analytics and follow-ups
- Safe-by-default (consent enforced; redaction happens in audit layer)
"""

from __future__ import annotations

import json
import pathlib
import time
from typing import Any

from jsonschema import Draft202012Validator

SCHEMAS_DIR = pathlib.Path("schemas")
AUDIT_DIR = pathlib.Path("audit_logs")
FEEDBACK_FILE = AUDIT_DIR / "feedback.jsonl"

# Load schema once
_FEEDBACK_SCHEMA = json.loads((SCHEMAS_DIR / "feedback_event_v1.json").read_text())
_VALIDATOR = Draft202012Validator(_FEEDBACK_SCHEMA)


def validate_event(evt: dict[str, Any]) -> None:
    errors = sorted(_VALIDATOR.iter_errors(evt), key=lambda e: e.path)
    if errors:
        raise ValueError("Invalid feedback event: " + "; ".join([e.message for e in errors]))


def record_feedback(evt: dict[str, Any]) -> dict[str, Any]:
    """
    Persist a validated feedback event. Returns a minimal receipt.
    - append-only, one JSON object per line
    - safe to call from UI or server components
    """
    validate_event(evt)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    line = json.dumps(evt, sort_keys=True)

    if FEEDBACK_FILE.exists():
        FEEDBACK_FILE.write_text(FEEDBACK_FILE.read_text() + line + "\n")
    else:
        FEEDBACK_FILE.write_text(line + "\n")

    return {
        "ok": True,
        "stored_at": time.time(),
        "node_id": evt["node_id"],
        "rating": evt["rating"]
    }


def quick_card(node_id: str, scale: int = 5) -> dict[str, Any]:
    """
    Convenience: generate a default card spec (matches feedback_card_v1)
    """
    return {
        "node_id": node_id,
        "layout": {
            "rating_scale": scale,
            "fields": [
                {
                    "name": "comment",
                    "label": "Tell us more",
                    "type": "textarea",
                    "maxLength": 2000
                },
                {
                    "name": "tags",
                    "label": "Tags",
                    "type": "chips",
                    "options": ["hallucination", "typo", "slow", "unsafe", "great"]
                }
            ]
        }
    }
