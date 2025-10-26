"""Shim: governance.identity → governance.identity or candidate.governance.identity."""
try:
    from governance.identity import *  # noqa: F403
except ImportError:
    try:
        from labs.governance.identity import *  # noqa: F403
    except ImportError:
        pass
