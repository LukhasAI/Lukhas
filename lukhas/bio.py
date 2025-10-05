"""Shim: lukhas.bio → bio or candidate.bio."""
try:
    from bio import *  # noqa: F401, F403
except ImportError:
    try:
        from candidate.bio import *  # noqa: F401, F403
    except ImportError:
        pass
