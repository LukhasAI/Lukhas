"""
Legacy core compatibility layer - DEPRECATED

This module provides temporary aliasing from 'core' to 'lukhas.core' for
compatibility during migration. It is disabled by default in production
and will be removed in 1-2 releases.

Set LUKHAS_CORE_COMPAT=1 to enable legacy imports during transition.
"""

import os
import sys
import importlib
import types
import warnings

if os.getenv("LUKHAS_CORE_COMPAT", "0") != "1":
    warnings.warn(
        "Legacy 'core' imports are disabled. Set LUKHAS_CORE_COMPAT=1 to enable temporary aliasing.",
        DeprecationWarning,
        stacklevel=2,
    )
    # Fail early & loud to flush stragglers in CI/dev; prod will never set the flag.
    raise ImportError("Legacy 'core' alias disabled; use 'lukhas.core'")

class _Proxy(types.ModuleType):
    """Proxy module that dynamically imports from lukhas.core."""

    def __getattr__(self, name):
        mod = importlib.import_module(f"lukhas.core.{name}")
        setattr(self, name, mod)
        return mod

# Expose lukhas.core at legacy name when explicitly enabled
_lukhas_core = importlib.import_module("lukhas.core")
m = _Proxy("core")
m.__dict__.update({"__doc__": _lukhas_core.__doc__})
sys.modules[__name__] = m