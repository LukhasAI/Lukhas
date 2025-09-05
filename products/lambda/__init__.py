"""Compatibility shim for `lambda_products` after consolidation.

This package re-exports the moved package under `products.lambda_products` so older
imports keep working during the migration.
"""

import sys
from importlib import import_module

try:
    mod = import_module("products.lambda_products")
    sys.modules[__name__] = mod
except Exception:
    __all__ = []
