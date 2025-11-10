"""
LUKHAS Glyphs Wrapper Module

Provides production-safe interface to GLYPH token system with feature flag control.
Wraps existing glyph utilities from core.common.glyph for modular access.

Constellation Framework: Spark Star (⚡) - Inter-module communication
"""

import os
from typing import Any, Dict, List, Optional, Union

# Feature flag
GLYPHS_ENABLED = os.environ.get("GLYPHS_ENABLED", "false").lower() in ("true", "1", "yes", "on")

# Lazy-loaded module references
_glyph_module: Optional[Any] = None
_glyph_token_class: Optional[type] = None
_glyph_router_class: Optional[type] = None


def _ensure_glyphs_loaded() -> None:
    """
    Ensure GLYPH module is loaded.

    Raises:
        RuntimeError: If glyphs not enabled or not available
    """
    global _glyph_module, _glyph_token_class, _glyph_router_class

    if not GLYPHS_ENABLED:
        raise RuntimeError("Glyphs subsystem not enabled (set GLYPHS_ENABLED=true)")

    if _glyph_module is None:
        try:
            from lukhas_website.lukhas.core.common import glyph as glyph_module
            _glyph_module = glyph_module
            _glyph_token_class = glyph_module.GLYPHToken
            _glyph_router_class = glyph_module.GLYPHRouter
        except ImportError as e:
            raise RuntimeError(f"Glyphs module not available: {e}") from e


def get_glyph_token_class() -> type:
    """
    Get GLYPHToken class.

    Returns:
        GLYPHToken class

    Raises:
        RuntimeError: If glyphs not enabled
    """
    _ensure_glyphs_loaded()
    return _glyph_token_class  # type: ignore[return-value]


def get_glyph_router_class() -> type:
    """
    Get GLYPHRouter class.

    Returns:
        GLYPHRouter class

    Raises:
        RuntimeError: If glyphs not enabled
    """
    _ensure_glyphs_loaded()
    return _glyph_router_class  # type: ignore[return-value]


def create_glyph(
    symbol: Union[str, Any],
    source: str,
    target: str,
    payload: Optional[Dict[str, Any]] = None,
    context: Optional[Union[Dict[str, Any], Any]] = None,
    priority: Union[str, Any] = "NORMAL",
    **metadata: Any,
) -> Any:
    """
    Create a new GLYPH token.

    Args:
        symbol: GLYPH symbol
        source: Source module name
        target: Target module name
        payload: Data payload
        context: Context information
        priority: Message priority
        **metadata: Additional metadata

    Returns:
        New GLYPH token

    Raises:
        RuntimeError: If glyphs not enabled
    """
    _ensure_glyphs_loaded()
    return _glyph_module.create_glyph(  # type: ignore[union-attr]
        symbol=symbol,
        source=source,
        target=target,
        payload=payload,
        context=context,
        priority=priority,
        **metadata,
    )


def parse_glyph(data: Union[str, Dict[str, Any]]) -> Any:
    """
    Parse GLYPH token from JSON string or dictionary.

    Args:
        data: JSON string or dictionary

    Returns:
        Parsed GLYPH token

    Raises:
        RuntimeError: If glyphs not enabled
    """
    _ensure_glyphs_loaded()
    return _glyph_module.parse_glyph(data)  # type: ignore[union-attr]


def validate_glyph(token: Any) -> bool:
    """
    Validate GLYPH token structure.

    Args:
        token: GLYPH token to validate

    Returns:
        True if valid

    Raises:
        RuntimeError: If glyphs not enabled
    """
    _ensure_glyphs_loaded()
    return _glyph_module.validate_glyph(token)  # type: ignore[union-attr]


def create_response_glyph(
    request: Any,
    symbol: Union[str, Any],
    payload: Optional[Dict[str, Any]] = None,
    **metadata: Any,
) -> Any:
    """
    Create a response GLYPH token from a request.

    Args:
        request: Original request token
        symbol: Response symbol
        payload: Response payload
        **metadata: Additional metadata

    Returns:
        Response GLYPH token

    Raises:
        RuntimeError: If glyphs not enabled
    """
    _ensure_glyphs_loaded()
    return _glyph_module.create_response_glyph(  # type: ignore[union-attr]
        request=request,
        symbol=symbol,
        payload=payload,
        **metadata,
    )


def create_error_glyph(
    request: Any,
    error_message: str,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Create an error GLYPH token.

    Args:
        request: Original request token
        error_message: Error message
        error_code: Error code
        details: Error details

    Returns:
        Error GLYPH token

    Raises:
        RuntimeError: If glyphs not enabled
    """
    _ensure_glyphs_loaded()
    return _glyph_module.create_error_glyph(  # type: ignore[union-attr]
        request=request,
        error_message=error_message,
        error_code=error_code,
        details=details,
    )


def create_router() -> Any:
    """
    Create a new GLYPH router instance.

    Returns:
        GLYPHRouter instance

    Raises:
        RuntimeError: If glyphs not enabled
    """
    _ensure_glyphs_loaded()
    return _glyph_router_class()  # type: ignore[misc]


# Re-export common types for convenience (when enabled)
def _get_glyph_symbols() -> Optional[type]:
    """Get GLYPHSymbol enum if available."""
    if GLYPHS_ENABLED:
        try:
            from lukhas_website.lukhas.core.common.glyph import GLYPHSymbol
            return GLYPHSymbol
        except ImportError:
            return None
    return None


def _get_glyph_priority() -> Optional[type]:
    """Get GLYPHPriority enum if available."""
    if GLYPHS_ENABLED:
        try:
            from lukhas_website.lukhas.core.common.glyph import GLYPHPriority
            return GLYPHPriority
        except ImportError:
            return None
    return None


# Module-level convenience exports (only when enabled)
GLYPHSymbol = _get_glyph_symbols()
GLYPHPriority = _get_glyph_priority()

# Lazy-loaded classes (accessed via getters when enabled)
GLYPHToken = property(lambda self: get_glyph_token_class())  # type: ignore[assignment]
GLYPHRouter = property(lambda self: get_glyph_router_class())  # type: ignore[assignment]

# Version information
__version__ = "1.0.0"
__framework__ = "Constellation Framework - Spark Star (⚡)"

# Public exports
__all__ = [
    "GLYPHS_ENABLED",
    "get_glyph_token_class",
    "get_glyph_router_class",
    "create_glyph",
    "parse_glyph",
    "validate_glyph",
    "create_response_glyph",
    "create_error_glyph",
    "create_router",
    "GLYPHSymbol",
    "GLYPHPriority",
    "__version__",
    "__framework__",
]
