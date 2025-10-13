"""Shim: lukhas.bridge.llm_wrappers.base_wrapper → candidate.bridge.llm_wrappers.base_wrapper."""
try:
    from labs.bridge.llm_wrappers.base_wrapper import *  # noqa: F403
except ImportError:
    try:
        from bridge.llm_wrappers.base_wrapper import *  # noqa: F403
    except ImportError:
        pass
