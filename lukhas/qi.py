"""Shim: lukhas.qi → qi or candidate.qi."""
try:
    from qi import *  # noqa: F401, F403
except ImportError:
    try:
        from candidate.qi import *  # noqa: F401, F403
    except ImportError:
        pass
