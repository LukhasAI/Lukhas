"""Bridge: adapters.openai.api - OpenAI adapter API."""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates, safe_guard

_CANDIDATES = (
    "lukhas_website.adapters.openai.api",
    "candidate.adapters.openai.api",
    "labs.adapters.openai.api",
    "lukhas.adapters.openai.api",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)

# Ensure get_app is available
if "get_app" not in globals():
    def get_app():
        """Stub get_app function."""
        from typing import Any
        class StubApp:
            """Stub FastAPI app."""
            pass
        return StubApp()
    globals()["get_app"] = get_app
    if "get_app" not in __all__:
        __all__.append("get_app")

# Ensure OpenAIAdapter is available
if "OpenAIAdapter" not in globals():
    class OpenAIAdapter:
        """Stub OpenAI adapter."""
        pass
    globals()["OpenAIAdapter"] = OpenAIAdapter
    if "OpenAIAdapter" not in __all__:
        __all__.append("OpenAIAdapter")

safe_guard(__name__, __all__)
