"""Shim: lukhas.core.ethics → core.ethics or candidate.core.ethics."""
try:
    from core.ethics import *  # noqa: F401, F403
except ImportError:
    try:
        from candidate.core.ethics import *  # noqa: F401, F403
    except ImportError:
        pass
