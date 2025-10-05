"""Shim: lukhas.tools → tools or candidate.tools."""
try:
    from tools import *  # noqa: F401, F403
except ImportError:
    try:
        from candidate.tools import *  # noqa: F401, F403
    except ImportError:
        pass
