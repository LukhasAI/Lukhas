"""
LUKHAS - Legacy Compatibility Module
Redirects to the real ``lukhas`` package.

This module exists for backwards compatibility.
All new code should use ``import lukhas`` instead.
"""

from __future__ import annotations

import importlib.util
import sys
import warnings
from pathlib import Path

# ΛTAG: legacy_bridge - dynamically load actual lukhas package
_PACKAGE_DIR = Path(__file__).with_name(" lukhas")
_spec = importlib.util.spec_from_file_location("lukhas", _PACKAGE_DIR / "__init__.py")
_module = importlib.util.module_from_spec(_spec)
_module.__path__ = [str(_PACKAGE_DIR)]
sys.modules["lukhas"] = _module
_spec.loader.exec_module(_module)  # type: ignore[union-attr]

warnings.warn(
    "The 'lukhas' namespace is deprecated. Please use 'import lukhas' instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Expose package attributes through compatibility module
sys.modules[__name__] = _module
