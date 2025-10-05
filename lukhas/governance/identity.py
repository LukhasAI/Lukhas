"""Shim: lukhas.governance.identity → governance.identity or candidate.governance.identity."""
try:
    from governance.identity import *  # noqa: F401, F403
except ImportError:
    try:
        from candidate.governance.identity import *  # noqa: F401, F403
    except ImportError:
        pass
