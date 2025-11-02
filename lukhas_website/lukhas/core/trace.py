"""
core/trace.py

GLYPH-aware trace crumb generation for auditability.

Usage:
  from core.trace import mk_crumb
  trace = {"enter": mk_crumb("adapter_enter", msg.glyph, topic=msg.topic)}
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from matriz.node_contract import GLYPH


def mk_crumb(event: str, glyph: Optional[GLYPH] = None, **kv: Any) -> Dict[str, Any]:
    """
    Minimal, deterministic trace crumb.
    """
    out = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
    }
    if glyph:
        out["glyph"] = {"id": str(glyph.id), "kind": glyph.kind, "v": glyph.version}
    if kv:
        out["data"] = kv
    return out
