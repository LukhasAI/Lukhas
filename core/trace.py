"""
core/trace.py

GLYPH-aware trace crumb generation for auditability.

Usage:
  from core.trace import mk_crumb
  trace = {"enter": mk_crumb("adapter_enter", msg.glyph, topic=msg.topic)}
"""
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, Optional

# Avoid runtime dependency on MATRIZ in core by importing types only for typing.
if TYPE_CHECKING:  # pragma: no cover
    from MATRIZ.node_contract import GLYPH  # type: ignore


def mk_crumb(event: str, glyph: Optional["GLYPH"] = None, **kv: Any) -> dict[str, Any]:
    """
    Minimal, deterministic trace crumb.
    """
    out = {'ts': datetime.now(timezone.utc).isoformat(), 'event': event}
    if glyph is not None:
        # Access attributes defensively to avoid hard dependency on type
        gid = getattr(glyph, 'id', None)
        kind = getattr(glyph, 'kind', None)
        ver = getattr(glyph, 'version', None)
        out['glyph'] = {
            'id': str(gid) if gid is not None else None,
            'kind': kind,
            'v': ver,
        }
    if kv:
        out['data'] = kv
    return out
