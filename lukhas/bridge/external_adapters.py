"""Shim: lukhas.bridge.external_adapters → bridge.external_adapters or candidate.bridge.external_adapters."""
try:
    from bridge.external_adapters import *  # noqa: F401, F403
except ImportError:
    try:
        from labs.bridge.external_adapters import *  # noqa: F401, F403
    except ImportError:
        pass
