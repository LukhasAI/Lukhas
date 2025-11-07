"""Bridge utilities - canonical location at bridge/_bridgeutils.py"""
# This is a compatibility shim for imports that use `from _bridgeutils import ...`
# The actual implementation is in bridge/_bridgeutils.py
from bridge._bridgeutils import (
    bridge,
    bridge_from_candidates,
    deprecate,
    export_from,
    resolve_first,
    safe_guard,
)

__all__ = [
    "bridge",
    "bridge_from_candidates",
    "deprecate",
    "export_from",
    "resolve_first",
    "safe_guard",
]
