"""
LUKHAS GLYPH Wrapper Module
============================

Production-safe wrapper for core GLYPH (symbolic communication) functionality.
All features are gated behind LUKHAS_GLYPHS_ENABLED flag (default: OFF).

GLYPHs provide symbolic communication and encoding across the LUKHAS ecosystem.

Usage:
    from lukhas.glyphs import is_enabled, encode_concept, bind_glyph

    if is_enabled():
        symbol = encode_concept("morning_reflection")
"""
import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Feature flag - default OFF for safety
_GLYPHS_ENABLED = (os.getenv("LUKHAS_GLYPHS_ENABLED", "0") or "0").strip() == "1"

# Import core modules safely
_GLYPHS_AVAILABLE = False
_glyph_engine = None
_glyph_factory = None

if _GLYPHS_ENABLED:
    try:
        from labs.core.glyph import (
            GlyphEngine,
            GlyphProcessor,
            emit_glyph,
            process_glyph,
        )
        from labs.core.glyph.glyph_engine import EnhancedGlyphEngine

        # Initialize the glyph engine
        _glyph_engine = EnhancedGlyphEngine()
        _GLYPHS_AVAILABLE = True
        logger.info("GLYPH subsystem initialized successfully")
    except ImportError as e:
        logger.warning(f"GLYPH subsystem unavailable: {e}")
    except Exception as e:
        logger.error(f"Error initializing GLYPH subsystem: {e}")


def is_enabled() -> bool:
    """Check if GLYPH subsystem is enabled and available."""
    return _GLYPHS_ENABLED and _GLYPHS_AVAILABLE


def get_glyph_engine() -> Optional[Any]:
    """
    Get the GLYPH engine instance.

    Returns:
        EnhancedGlyphEngine if available, None otherwise
    """
    if not is_enabled():
        logger.debug("GLYPH subsystem not enabled")
        return None
    return _glyph_engine


def encode_concept(
    concept: str,
    emotion: Optional[dict[str, float]] = None,
    modalities: Optional[set[str]] = None,
    domains: Optional[set[str]] = None,
    source_module: Optional[str] = None
) -> Optional[dict[str, Any]]:
    """
    Encode a concept into a Universal Symbol with GLYPH core.

    Args:
        concept: The concept to encode
        emotion: Optional emotional context
        modalities: Symbol modalities (defaults to TEXT)
        domains: Symbol domains (defaults to UNIVERSAL)
        source_module: Module creating the symbol (for tracking)

    Returns:
        Universal Symbol dictionary if successful, None otherwise
    """
    if not is_enabled():
        logger.debug("GLYPH subsystem not enabled")
        return None

    try:
        if _glyph_engine:
            symbol = _glyph_engine.encode_concept(
                concept=concept,
                emotion=emotion,
                modalities=modalities,
                domains=domains,
                source_module=source_module
            )
            # Convert to serializable dict
            return {
                "concept": concept,
                "symbol_id": getattr(symbol, "symbol_id", None),
                "modalities": list(modalities) if modalities else ["TEXT"],
                "domains": list(domains) if domains else ["UNIVERSAL"],
                "emotion": emotion,
                "source_module": source_module,
            }
    except Exception as e:
        logger.error(f"Error encoding concept: {e}")
    return None


def decode_symbol(symbol_data: dict) -> Optional[str]:
    """
    Decode a symbol back to human-readable concept.

    Args:
        symbol_data: Symbol dictionary

    Returns:
        Decoded concept string if successful, None otherwise
    """
    if not is_enabled():
        logger.debug("GLYPH subsystem not enabled")
        return None

    try:
        # Placeholder implementation
        return symbol_data.get("concept", "")
    except Exception as e:
        logger.error(f"Error decoding symbol: {e}")
    return None


def bind_glyph(
    glyph_data: dict,
    memory_id: str,
    user_id: Optional[str] = None,
    token: Optional[str] = None
) -> dict[str, Any]:
    """
    Bind a GLYPH to a memory with safety checks.

    Args:
        glyph_data: GLYPH data to bind
        memory_id: Target memory identifier
        user_id: User identifier for authorization
        token: Authorization token

    Returns:
        Dictionary with binding result:
        {
            "success": bool,
            "binding_id": str,
            "error": str (if failed)
        }
    """
    if not is_enabled():
        return {
            "success": False,
            "error": "GLYPH subsystem not enabled"
        }

    try:
        # Validate inputs
        if not glyph_data or not isinstance(glyph_data, dict):
            return {
                "success": False,
                "error": "Invalid glyph_data: must be non-empty dictionary"
            }

        if not memory_id or not isinstance(memory_id, str):
            return {
                "success": False,
                "error": "Invalid memory_id: must be non-empty string"
            }

        # TODO: Implement actual token verification
        # if token:
        #     verify_token(token, user_id)

        # TODO: Implement actual binding logic
        import hashlib
        import time

        binding_id = hashlib.sha256(
            f"{memory_id}{time.time()}".encode()
        ).hexdigest()[:16]

        result = {
            "success": True,
            "binding_id": binding_id,
            "glyph_data": glyph_data,
            "memory_id": memory_id,
            "user_id": user_id,
            "timestamp": time.time()
        }

        logger.info(f"GLYPH bound successfully: {binding_id}")
        return result

    except Exception as e:
        logger.error(f"Error binding GLYPH: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_binding(binding_id: str) -> Optional[dict]:
    """
    Retrieve a GLYPH binding by its ID.

    Args:
        binding_id: Binding identifier

    Returns:
        Binding data if found, None otherwise
    """
    if not is_enabled():
        logger.debug("GLYPH subsystem not enabled")
        return None

    try:
        # TODO: Implement actual retrieval logic
        logger.debug(f"Retrieving binding: {binding_id}")
        return None
    except Exception as e:
        logger.error(f"Error retrieving binding: {e}")
    return None


def validate_glyph(glyph_data: dict) -> tuple[bool, Optional[str]]:
    """
    Validate GLYPH data structure and content.

    Args:
        glyph_data: GLYPH data to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(glyph_data, dict):
        return False, "GLYPH data must be a dictionary"

    # Check required fields
    required_fields = ["concept"]
    for field in required_fields:
        if field not in glyph_data:
            return False, f"Missing required field: {field}"

    # Validate concept
    concept = glyph_data.get("concept", "")
    if not concept or not isinstance(concept, str):
        return False, "Concept must be a non-empty string"

    if len(concept) > 1000:
        return False, "Concept exceeds maximum length (1000 characters)"

    # Validate emotion if present
    if "emotion" in glyph_data:
        emotion = glyph_data["emotion"]
        if not isinstance(emotion, dict):
            return False, "Emotion must be a dictionary"

        # Check emotion values are floats between 0 and 1
        for key, value in emotion.items():
            if not isinstance(value, (int, float)):
                return False, f"Emotion value '{key}' must be numeric"
            if not (0.0 <= value <= 1.0):
                return False, f"Emotion value '{key}' must be between 0.0 and 1.0"

    return True, None


def get_glyph_stats() -> dict[str, Any]:
    """
    Get GLYPH subsystem statistics.

    Returns:
        Dictionary with stats
    """
    if not is_enabled():
        return {
            "enabled": False,
            "available": False
        }

    try:
        if _glyph_engine and hasattr(_glyph_engine, "stats"):
            return {
                "enabled": True,
                "available": True,
                "stats": _glyph_engine.stats
            }
    except Exception as e:
        logger.error(f"Error getting GLYPH stats: {e}")

    return {
        "enabled": True,
        "available": True,
        "stats": {}
    }


# Public API
__all__ = [
    "is_enabled",
    "get_glyph_engine",
    "encode_concept",
    "decode_symbol",
    "bind_glyph",
    "get_binding",
    "validate_glyph",
    "get_glyph_stats",
]

# Expose feature flag status for testing
GLYPHS_ENABLED = _GLYPHS_ENABLED
