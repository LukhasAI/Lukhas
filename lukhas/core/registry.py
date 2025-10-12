"""Shim: lukhas.core.registry → core.registry or candidate.core.registry."""
try:
    from core.registry import *  # noqa: F401, F403
except ImportError:
    try:
        from labs.core.registry import *  # noqa: F401, F403
    except ImportError:
        pass
