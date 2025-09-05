"""Compatibility shim for `lambda_products_pack` after consolidation.

This package re-exports the moved package under `products.lambda_pack` so older
imports keep working during the migration.
"""

import sys
from importlib import import_module

try:
    mod = import_module("products.lambda_pack")
    sys.modules[__name__] = mod
except Exception:
    # Best-effort: leave an empty package to avoid import errors on import time.
    __all__ = []
