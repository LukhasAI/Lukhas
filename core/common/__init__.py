"""Bridge: core.common -> canonical implementations (GLYPHToken + get_logger)."""
from __future__ import annotations

# First get local logger
try:
    from .logger import (
        get_logger as _get_logger,  # noqa: TID252 (relative imports in __init__.py are idiomatic)
    )
except ImportError:
    import logging
    _get_logger = logging.getLogger

# Then bridge to get GLYPHToken and other symbols
from lukhas._bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "labs.core.common",
    "lukhas_website.lukhas.core.common",
)

__all__, _exports = bridge_from_candidates(*_CANDIDATES)

# Ensure get_logger is always available
_exports["get_logger"] = _get_logger
if "get_logger" not in __all__:
    __all__.append("get_logger")

globals().update(_exports)
