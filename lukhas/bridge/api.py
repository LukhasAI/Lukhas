"""Shim: lukhas.bridge.api → bridge.api or candidate.bridge.api."""
try:
    from bridge.api import *  # noqa: F401, F403
except ImportError:
    try:
        from labs.bridge.api import *  # noqa: F401, F403
    except ImportError:
        pass
