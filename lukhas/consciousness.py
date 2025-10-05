"""Shim: lukhas.consciousness → consciousness or candidate.consciousness."""
try:
    from consciousness import *  # noqa: F401, F403
except ImportError:
    try:
        from candidate.consciousness import *  # noqa: F401, F403
    except ImportError:
        pass
