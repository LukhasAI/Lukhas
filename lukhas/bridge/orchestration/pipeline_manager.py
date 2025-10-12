"""Shim: lukhas.bridge.orchestration.pipeline_manager → candidate.bridge.orchestration.pipeline_manager."""
try:
    from labs.bridge.orchestration.pipeline_manager import *  # noqa: F401, F403
except ImportError:
    try:
        from bridge.orchestration.pipeline_manager import *  # noqa: F401, F403
    except ImportError:
        pass
