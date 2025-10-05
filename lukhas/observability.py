"""Shim: lukhas.observability → observability or candidate.observability."""
try:
    from observability import *  # noqa: F401, F403
except ImportError:
    try:
        from candidate.observability import *  # noqa: F401, F403
    except ImportError:
        pass
