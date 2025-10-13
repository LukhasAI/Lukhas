"""Shim: lukhas.bridge.trace_logger → candidate.bridge.trace_logger or bridge.trace_logger."""
try:
    from labs.bridge.trace_logger import *  # noqa: F403
except ImportError:
    try:
        from bridge.trace_logger import *  # noqa: F403
    except ImportError:
        pass
