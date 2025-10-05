"""Shim: lukhas.identity → identity or candidate.identity."""
try:
    from identity import *  # noqa: F401, F403
except ImportError:
    try:
        from candidate.identity import *  # noqa: F401, F403
    except ImportError:
        pass
