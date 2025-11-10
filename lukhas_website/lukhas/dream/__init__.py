"""
LUKHAS Dreams Wrapper Module

Provides production-safe interface to dreams subsystem with feature flag control.
Integrates with consciousness DreamEngine for parallel dream processing.

Constellation Framework: Flow Star (🌊)
"""

import os
from typing import Any, Optional

# Feature flag
DREAMS_ENABLED = os.environ.get("DREAMS_ENABLED", "false").lower() in ("true", "1", "yes", "on")
PARALLEL_DREAMS_ENABLED = os.environ.get("PARALLEL_DREAMS_ENABLED", "false").lower() in ("true", "1", "yes", "on")

# Lazy-loaded engine reference
_dream_engine: Optional[Any] = None
_parallel_dreams_module: Optional[Any] = None


def get_dream_engine() -> Any:
    """
    Get dream engine if enabled.

    Returns:
        DreamEngine instance

    Raises:
        RuntimeError: If dreams not enabled or not available
    """
    global _dream_engine

    if not DREAMS_ENABLED:
        raise RuntimeError("Dreams subsystem not enabled (set DREAMS_ENABLED=true)")

    if _dream_engine is None:
        try:
            from lukhas_website.lukhas.consciousness.dream_engine import DreamEngine
            _dream_engine = DreamEngine()
        except ImportError as e:
            raise RuntimeError(f"Dreams module not available: {e}") from e

    return _dream_engine


def get_parallel_dreams():
    """
    Get parallel dreams processing module.

    Returns:
        Parallel dreams processor object

    Raises:
        RuntimeError: If parallel dreams not enabled
    """
    global _parallel_dreams_module

    if not DREAMS_ENABLED:
        raise RuntimeError("Dreams subsystem not enabled (set DREAMS_ENABLED=true)")

    if not PARALLEL_DREAMS_ENABLED:
        raise RuntimeError("Parallel dreams not enabled (set PARALLEL_DREAMS_ENABLED=true)")

    if _parallel_dreams_module is None:
        # For now, return the base dream engine
        # Future: implement actual parallel processing engine
        _parallel_dreams_module = get_dream_engine()

    return _parallel_dreams_module


# Module-level exports for backward compatibility with initialization.py
# initialization.py imports: from lukhas_website.lukhas.dream import parallel_dreams
class _ParallelDreamsModule:
    """
    Parallel dreams processing module wrapper.

    This provides the expected interface for initialization.py while
    maintaining feature flag control.
    """

    @staticmethod
    def is_enabled() -> bool:
        """Check if parallel dreams are enabled."""
        return DREAMS_ENABLED and PARALLEL_DREAMS_ENABLED

    @staticmethod
    def get_engine() -> Any:
        """Get the parallel dreams engine."""
        return get_parallel_dreams()


# Create module-level instance for import compatibility
# Note: This is evaluated at import time, so it checks the flag state at import
if DREAMS_ENABLED:
    parallel_dreams = _ParallelDreamsModule()
else:
    parallel_dreams = None  # type: ignore[assignment]

# Version information
__version__ = "1.0.0"
__framework__ = "Constellation Framework - Flow Star (🌊)"

# Public exports
__all__ = [
    "DREAMS_ENABLED",
    "PARALLEL_DREAMS_ENABLED",
    "get_dream_engine",
    "get_parallel_dreams",
    "parallel_dreams",
    "__version__",
    "__framework__",
]
