"""Compatibility shim for legacy `lambd_id_routes` module.

⚠️ DEPRECATION WARNING: This module provides backward compatibility only.
Λ = LUKHAS, not Lambda! New code should use lukhas_id_routes.py directly.

Migration path:
- OLD: from .lambd_id_routes import lambd_id_bp
- NEW: from .lukhas_id_routes import lukhas_id_bp
"""

import warnings

# Issue deprecation warning
warnings.warn(
    "lambd_id_routes.py is deprecated. Λ = LUKHAS, not Lambda! Use lukhas_id_routes.py instead.",
    DeprecationWarning,
    stacklevel=2
)

try:
    # Try to import from the correct module first
    from .lukhas_id_routes import lukhas_id_bp as _lukhas_bp
    
    # Provide backward-compatible aliases
    lambda_id_bp = _lukhas_bp
    lambd_id_bp = _lukhas_bp
    
    __all__ = ["lambda_id_bp", "lambd_id_bp", "lukhas_id_bp"]
    
except ImportError:
    # Fallback to legacy module if new one isn't available
    from .lambda_id_routes import lambda_id_bp
    
    # Backwards-compatible alias expected by older code
    lambd_id_bp = lambda_id_bp
    
    __all__ = ["lambda_id_bp", "lambd_id_bp"]