"""Bridge: core.common -> canonical implementations."""
from __future__ import annotations

# Re-export get_logger from logger submodule
try:
    from .logger import get_logger
    __all__ = ["get_logger"]
except ImportError:
    # Fallback to standard logging
    import logging
    get_logger = logging.getLogger
    __all__ = ["get_logger"]
