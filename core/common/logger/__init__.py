"""Bridge: core.common.logger"""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates, safe_guard
_CANDIDATES = (
    "lukhas_website.lukhas.core.common.logger",
    "candidate.core.common.logger",
)
__all__, _exp = bridge_from_candidates(*_CANDIDATES); globals().update(_exp)
safe_guard(__name__, __all__)

# compat: some tests call getLogger(name=None) or with extra kwargs
if "getLogger" in __all__:
    _orig = globals()["getLogger"]
    def _compat_getLogger(*args, **kwargs):
        return _orig(*args[:1]) if args else _orig()
    globals()["getLogger"] = _compat_getLogger
