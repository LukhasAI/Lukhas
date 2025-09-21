"""
Compatibility package providing lowercase access to MATRIZ modules.

This module provides lowercase access to MATRIZ functionality for compatibility
with existing imports that expect matriz.* instead of MATRIZ.*.
"""

# ΛTAG: matriz_lowercase_shim
import importlib
import sys

# Import the actual MATRIZ package
try:
    _upper = importlib.import_module("MATRIZ")
    core_module = importlib.import_module("MATRIZ.core")

    # Import node_contract directly
    node_contract_module = importlib.import_module("matriz.node_contract")

    # Set up module aliases in sys.modules
    sys.modules[__name__ + ".core"] = core_module
    sys.modules[__name__ + ".node_contract"] = node_contract_module

    __all__ = ["core", "node_contract"]

except ImportError as e:
    # Fallback if MATRIZ package is not available
    import warnings
    warnings.warn(f"Could not import MATRIZ package: {e}", ImportWarning)
    __all__ = []