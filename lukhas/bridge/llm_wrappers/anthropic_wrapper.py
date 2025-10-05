"""Shim: lukhas.bridge.llm_wrappers.anthropic_wrapper → candidate.bridge.llm_wrappers.anthropic_wrapper."""
try:
    from candidate.bridge.llm_wrappers.anthropic_wrapper import *  # noqa: F401, F403
except ImportError:
    try:
        from bridge.llm_wrappers.anthropic_wrapper import *  # noqa: F401, F403
    except ImportError:
        pass
