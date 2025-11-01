"""Compatibility shim for legacy :mod:`flags` imports.

This package forwards imports to the canonical implementation located in
``lukhas_website.lukhas.flags``. The shim keeps historical import paths working
for test suites and downstream tools while the codebase completes its module
renaming.
"""

from __future__ import annotations

from importlib import import_module
import sys
from typing import Any

_CANONICAL_PACKAGE = "lukhas_website.lukhas.flags"

_flags_pkg = import_module(_CANONICAL_PACKAGE)
_ff_module = import_module(f"{_CANONICAL_PACKAGE}.ff")

# Ensure ``from flags.ff import Flags`` keeps working by pre-registering the
# redirected module in ``sys.modules``.
sys.modules.setdefault(__name__ + ".ff", _ff_module)

Flags: Any = getattr(_ff_module, "Flags")

__all__ = getattr(_flags_pkg, "__all__", []).copy()
if "Flags" not in __all__:
    __all__.append("Flags")
