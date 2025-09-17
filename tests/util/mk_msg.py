#!/usr/bin/env python3
"""
MatrizMessage Constructor Utilities
T4-Approved helper for creating test messages from JSON

Usage:
    from tests.util.mk_msg import mk_msg_from_json

    msg = mk_msg_from_json({
        "lane": "experimental",
        "topic": "contradiction",
        "glyph": {"id": "uuid-string", "kind": "intent"},
        "payload": {"data": "value"}
    })
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from matriz.node_contract import GLYPH, MatrizMessage
from matriz.node_contract import CONTRACT_VERSION, ALLOWED_TOPICS, Topic


def _parse_ts(value: str) -> datetime:
    """Parse ISO-8601 timestamps; accept trailing 'Z' as UTC."""
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


def mk_msg_from_json(d: dict) -> MatrizMessage:
    """
    Construct MatrizMessage from JSON dictionary

    Args:
        d: Dictionary with message fields

    Returns:
        Properly constructed MatrizMessage

    Required fields:
        - lane: str
        - topic: str
        - glyph: dict with id, kind
        - payload: dict

    Optional fields:
        - msg_id: str (UUID) - generates if missing
        - ts: str (ISO format) - uses current time if missing
        - guardian_token: str - empty if missing
    """
    if d["topic"] not in ALLOWED_TOPICS:
        raise ValueError(f"Invalid topic '{d['topic']}'. Allowed: {sorted(ALLOWED_TOPICS)}")
    if "version" in d["glyph"] and d["glyph"]["version"] != CONTRACT_VERSION:
        raise ValueError(f"Incompatible glyph.version '{d['glyph'].get('version')}', expected {CONTRACT_VERSION}")
    return MatrizMessage(
        msg_id=UUID(d["msg_id"]) if "msg_id" in d else uuid4(),
        ts=_parse_ts(d["ts"]) if "ts" in d else datetime.utcnow(),
        lane=d["lane"],
        topic=d["topic"],
        glyph=GLYPH(
            id=UUID(d["glyph"]["id"]),
            kind=d["glyph"]["kind"],
            version=d["glyph"].get("version", CONTRACT_VERSION),
            tags=d["glyph"].get("tags", {})
        ),
        payload=d["payload"],
        guardian_token=d.get("guardian_token", "")
    )


def mk_test_glyph(kind: str = "test", tags: dict = None, id_override: UUID | None = None) -> GLYPH:
    """Create a test GLYPH"""
    return GLYPH(
        id=id_override or uuid4(),
        kind=kind,
        version=CONTRACT_VERSION,
        tags=tags or {}
    )


def mk_test_message(
    topic: str = Topic.CONTRADICTION.value,
    lane: str = "experimental",
    payload: dict = None,
    glyph_kind: str = "intent"
) -> MatrizMessage:
    """Create a test MatrizMessage with sensible defaults"""
    return MatrizMessage(
        msg_id=uuid4(),
        ts=datetime.utcnow(),
        lane=lane,
        topic=topic,
        glyph=mk_test_glyph(glyph_kind),
        payload=payload or {},
        guardian_token=""
    )


# Example usage for tests
def example_message() -> MatrizMessage:
    """Example message for documentation and testing"""
    return mk_msg_from_json({
        "lane": "experimental",
        "topic": "contradiction",
        "glyph": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "kind": "intent",
            "tags": {"priority": "high"}
        },
        "payload": {
            "parameter_A": "value1",
            "parameter_B": "value2",
            "target_improve": 0.8
        }
    })


__all__ = [
    "mk_msg_from_json",
    "mk_test_glyph",
    "mk_test_message",
    "example_message",
    "Topic",
    "ALLOWED_TOPICS"
]