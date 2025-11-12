"""
Glyph Retriever
"""
from typing import Any, Optional

# In-memory store for bindings.
# This is shared with the GlyphBinder to make the feature functional.
_bindings: dict[str, dict[str, Any]] = {}

class GlyphRetriever:
    async def retrieve(self, binding_id: str) -> Optional[dict[str, Any]]:
        """
        Retrieves a glyph binding from the in-memory store.
        """
        return _bindings.get(binding_id)

    @staticmethod
    async def _add_binding_for_testing(binding_id: str, data: dict[str, Any]):
        """Helper to add a binding for testing purposes."""
        _bindings[binding_id] = data

    @staticmethod
    async def _clear_bindings_for_testing():
        """Helper to clear all bindings for testing purposes."""
        _bindings.clear()
