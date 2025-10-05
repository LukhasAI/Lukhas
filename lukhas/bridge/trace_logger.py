"""Shim: lukhas.bridge.trace_logger → candidate.bridge.trace_logger or bridge.trace_logger."""
try:
    from candidate.bridge.trace_logger import *  # noqa: F401, F403
except ImportError:
    try:
        from bridge.trace_logger import *  # noqa: F401, F403
    except ImportError:
        pass
