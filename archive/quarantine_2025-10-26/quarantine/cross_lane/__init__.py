"""
LUKHAS Accepted Bio Package
Re-exports bio engine, symbolic, awareness, and adapters under the
`accepted.bio` namespace so older imports continue to work.

This package prefers the internal `bio` top-level package, then falls back
to `candidate.bio` implementations when available.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Try to wire up preferred implementations in order
try:
    # Prefer the top-level `bio` package if present
    import bio.adapters as _adapters_mod
    import bio.awareness as _awareness_mod
    import bio.engine as _engine_mod
    import bio.symbolic as _symbolic_mod

    logger.info("accepted.bio: using top-level bio package")
except Exception:
    try:
        # Fall back to candidate implementations
        import bio.adapters as _adapters_mod
        import bio.awareness as _awareness_mod
        import bio.core as _engine_mod
        import bio.symbolic as _symbolic_mod

        logger.info("accepted.bio: using candidate.bio implementations")
    except Exception as e:
        logger.warning(f"accepted.bio: could not wire bio implementations: {e}")
        _engine_mod = None
        _symbolic_mod = None
        _awareness_mod = None
        _adapters_mod = None

# Export common symbols with safe defaults
if _engine_mod is not None and hasattr(_engine_mod, "BioEngine"):
    BioEngine = _engine_mod.BioEngine
else:

    class BioEngine:
        def __init__(self):
            self.status = "fallback"


if _symbolic_mod is not None and hasattr(_symbolic_mod, "get_symbolic_processor"):
    get_symbolic_processor = _symbolic_mod.get_symbolic_processor
else:

    def get_symbolic_processor(*args, **kwargs):
        return None


if _awareness_mod is not None and hasattr(_awareness_mod, "BioAwareness"):
    BioAwareness = _awareness_mod.BioAwareness
else:

    class BioAwareness:
        def __init__(self):
            self.level = 0.5


# Expose a minimal API
__all__ = ["BioEngine", "get_symbolic_processor", "BioAwareness"]
