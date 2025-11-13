"""
OpenAI Adapter API Bridge
Bridge to adapter openai implementations

OpenAI API adapter for LUKHAS.
"""
try:
    from candidate.adapters.openai.api import *  # noqa: F401, F403
except (ModuleNotFoundError, ImportError):
    try:
        from labs.adapters.openai.api import *  # noqa: F401, F403
    except (ModuleNotFoundError, ImportError):
        # Minimal stub
        class OpenAIAdapter:
            """Placeholder for OpenAI adapter."""
            pass

__all__ = ["OpenAIAdapter"]
