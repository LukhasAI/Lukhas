"""Shim: lukhas.cognitive_core → cognitive_core or candidate.cognitive_core."""
try:
    from cognitive_core import *  # noqa: F401, F403
except ImportError:
    try:
        from candidate.cognitive_core import *  # noqa: F401, F403
    except ImportError:
        pass
