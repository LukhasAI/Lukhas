"""
LUKHAS - Legacy Compatibility Module
Redirects to new ``lukhas`` namespace.

This shim loads the real package located in the directory named
" lukhas" (note the leading space) so that ``import lukhas`` behaves as
expected. All new code should import ``lukhas`` directly.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import warnings

# ΛTAG: import_bridge
_pkg_path = Path(__file__).with_name(" lukhas")
_spec = importlib.util.spec_from_file_location(
    "lukhas",
    _pkg_path / "__init__.py",
    submodule_search_locations=[str(_pkg_path)],
)
if _spec is None or _spec.loader is None:  # TODO: support alternate package paths
    raise ModuleNotFoundError("Unable to load lukhas package")

_lukhas_pkg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_lukhas_pkg)

# Issue deprecation warning
warnings.warn(
    "The 'lukhas' namespace is deprecated. Please use 'import lukhas' instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Make all lukhas attributes available through lukhas
sys.modules[__name__] = _lukhas_pkg

