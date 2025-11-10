"""
Glyph Binder
"""
import hashlib
import time
from typing import Any, Dict

# Import the shared in-memory store from the retriever
from .glyph_retriever import _bindings


class GlyphBinder:
    async def bind(self, glyph_id: str, context: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Binds the glyph to a context for a user and stores it in the shared
        in-memory dictionary.
        """
        if not all([glyph_id, isinstance(context, dict), user_id]):
            return {"success": False, "error": "Invalid input"}

        # Create a unique binding ID
        binding_id = hashlib.sha256(
            f"{glyph_id}{user_id}{time.time()}{context.get('nonce', '')}".encode()
        ).hexdigest()

        # Create the binding record
        binding_record = {
            "binding_id": binding_id,
            "glyph_id": glyph_id,
            "user_id": user_id,
            "context": context,
            "timestamp": time.time(),
        }

        # Store the binding in the shared dictionary
        _bindings[binding_id] = binding_record

        return {
            "success": True,
            "binding_id": binding_id,
        }
