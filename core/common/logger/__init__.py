"""Bridge: core.common.logger -> candidate or stdlib fallback."""
from __future__ import annotations

try:
    from candidate.core.common.logger import *  # noqa: F401, F403
    __all__ = [n for n in locals().keys() if not n.startswith("_")]
except Exception:
    # Fallback to standard logging
    import logging as _logging

    getLogger = _logging.getLogger
    __all__ = ["getLogger"]
