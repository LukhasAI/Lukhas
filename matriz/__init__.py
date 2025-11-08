"""
MATRIZ - Memory-Attention-Thought-Action-Decision-Awareness Cognitive Engine

Canonical package name: MATRIZ (uppercase)

IMPORTANT: On case-insensitive filesystems (macOS), Python imports this as 'matriz'
(lowercase) because that's how the directory appears to the import system. This
__init__.py handles making it available under both names via sys.modules aliasing.

On case-sensitive filesystems (Linux/CI), git tracks this as 'MATRIZ/' (uppercase).

DEPRECATION NOTICE:
Always use 'from MATRIZ import X' or 'import MATRIZ' in new code. The package will
work with both cases due to aliasing, but uppercase is canonical. Migration window: Q2 2026.
"""

from __future__ import annotations

import importlib
import os
import sys
import warnings
from types import ModuleType

__version__ = "1.0.0"
__all__: list[str] = []

# Detect how we were imported and set up aliasing
_this_module = sys.modules[__name__]
_canonical_name = "MATRIZ"
_compat_name = "matriz"

# If imported as 'matriz', alias to 'MATRIZ' and emit warning
_suppress_warning = os.getenv("LUKHAS_SUPPRESS_MATRIZ_COMPAT_WARNING", "").lower() in {
    "1",
    "true",
    "yes",
}

if __name__ == _compat_name:
    if not _suppress_warning:
        warnings.warn(
            f"Importing '{_compat_name}' (lowercase) is deprecated. Use 'from {_canonical_name} import X' instead. "
            "This compatibility will be removed in Q2 2026.",
            DeprecationWarning,
            stacklevel=2,
        )
    # Make available as uppercase too
    sys.modules[_canonical_name] = _this_module

# If imported as 'MATRIZ', also register lowercase for compatibility
elif __name__ == _canonical_name:
    sys.modules[_compat_name] = _this_module


def _alias(subpkg: str) -> ModuleType | None:
    """Map both matriz.<subpkg> and MATRIZ.<subpkg> to the same module."""
    # Determine source based on how we were loaded
    if __name__ == _compat_name:
        src_name = f"{_compat_name}.{subpkg}"
    else:
        src_name = f"{_canonical_name}.{subpkg}"

    try:
        mod = importlib.import_module(src_name)
    except Exception:
        return None

    # Register under both names
    sys.modules[f"{_canonical_name}.{subpkg}"] = mod
    sys.modules[f"{_compat_name}.{subpkg}"] = mod

    if subpkg not in __all__:
        __all__.append(subpkg)
    return mod


# Load and alias common subpackages
for _name in (
    "core",
    "adapters",
    "runtime",
    "nodes",
    "utils",
    "visualization",
    "consciousness",
    "orchestration",
    "memory",
    "interfaces",
    "docs",
    "tests",
):
    _alias(_name)

# Handle node_contract module specially (it's a file, not a package)
try:
    _nc_src = f"{__name__}.node_contract"
    node_contract = importlib.import_module(_nc_src)
    sys.modules[f"{_canonical_name}.node_contract"] = node_contract
    sys.modules[f"{_compat_name}.node_contract"] = node_contract
    __all__.append("node_contract")
except Exception:
    pass
