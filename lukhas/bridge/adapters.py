"""Shim: lukhas.bridge.adapters → bridge.adapters or candidate.bridge.adapters."""
try:
    from bridge.adapters import *  # noqa: F401, F403
except ImportError:
    try:
        from candidate.bridge.adapters import *  # noqa: F401, F403
    except ImportError:
        pass
