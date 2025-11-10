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

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from matriz.node_contract import GLYPH, MatrizMessage


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
    """
    glyph_data = d.get('glyph', {})
    if 'id' not in glyph_data:
        glyph_data['id'] = '550e8400-e29b-41d4-a716-446655440000'
    if 'kind' not in glyph_data:
        glyph_data['kind'] = 'intent'
    if 'version' not in glyph_data:
        glyph_data['version'] = '1.0.0'
    if 'tags' not in glyph_data:
        glyph_data['tags'] = {}
    return MatrizMessage(
        msg_id=UUID(d['msg_id']) if 'msg_id' in d else uuid4(),
    ts=datetime.fromisoformat(d['ts']) if 'ts' in d else datetime.now(timezone.utc),
        lane=d['lane'],
        topic=d['topic'],
        glyph=GLYPH(
            id=UUID(glyph_data['id']),
            kind=glyph_data['kind'],
            version=glyph_data['version'],
            tags=glyph_data['tags']
        ),
        payload=d.get('payload', {})
    )

def mk_test_glyph(kind: str='intent', tags: Optional[dict]=None, id_override: Optional[UUID]=None) -> GLYPH:
    """Create a test GLYPH with stable defaults"""
    return GLYPH(
        id=id_override or UUID('550e8400-e29b-41d4-a716-446655440000'),
        kind=kind,
        version='1.0.0',
        tags=tags or {}
    )

def mk_test_message(topic: str='contradiction', lane: str='experimental', payload: Optional[dict]=None, glyph_kind: str='intent') -> MatrizMessage:
    """Create a test MatrizMessage with sensible defaults"""
    return MatrizMessage(
        msg_id=uuid4(),
    ts=datetime.now(timezone.utc),
        lane=lane,
        topic=topic,
        glyph=mk_test_glyph(glyph_kind),
        payload=payload or {}
    )
__all__ = ['mk_msg_from_json', 'mk_test_glyph', 'mk_test_message']
