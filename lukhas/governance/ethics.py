"""Shim: lukhas.governance.ethics → governance.ethics or candidate.governance.ethics."""
try:
    from governance.ethics import *  # noqa: F401, F403
except ImportError:
    try:
        from candidate.governance.ethics import *  # noqa: F401, F403
    except ImportError:
        pass
