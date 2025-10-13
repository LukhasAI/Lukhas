"""Shim: lukhas.bridge.orchestration.context_bus → candidate.bridge.orchestration.context_bus."""
try:
    from labs.bridge.orchestration.context_bus import *  # noqa: F403
except ImportError:
    try:
        from bridge.orchestration.context_bus import *  # noqa: F403
    except ImportError:
        pass
