"""Shim: lukhas.bridge.llm_wrappers.openai_wrapper → candidate.bridge.llm_wrappers.openai_wrapper."""
try:
    from labs.bridge.llm_wrappers.openai_wrapper import *  # noqa: F401, F403
except ImportError:
    try:
        from bridge.llm_wrappers.openai_wrapper import *  # noqa: F401, F403
    except ImportError:
        pass
