"""
Compatibility shim for the historic `lukhas` package path.

This repository has promoted modules into top-level packages like `core/` and
`serve/`. Several CI jobs and external docs still import via the
`lukhas.*` namespace. To preserve backwards compatibility without duplicating
code, we provide a minimal alias layer:

  - `lukhas.core`      → `core`
  - `lukhas.governance`→ `core.governance`

For the OpenAI-compatible API entrypoint used by tooling and CI
(`lukhas.adapters.openai.api:get_app`), see files under
`lukhas/adapters/openai/` in this shim.

Note: This file intentionally avoids heavy imports and does not re-export all
symbols. It sets up module aliases on demand so that imports like
`from lukhas.core import common` resolve to `core.common`.
"""

from __future__ import annotations

import importlib
import sys


def _alias_module(shim_name: str, target: str) -> None:
    """Register a module alias in sys.modules if not already present.

    Example: _alias_module("lukhas.core", "core")
    """
    if shim_name in sys.modules:
        return
    mod = importlib.import_module(target)
    # Expose the target module under the shimmed name
    sys.modules[shim_name] = mod


# Set up common aliases eagerly so basic imports succeed in light environments
try:
    _alias_module("lukhas.core", "core")
except Exception:
    # Core may not be importable in ultra-minimal envs; defer to runtime
    pass

try:
    _alias_module("lukhas.governance", "core.governance")
except Exception:
    pass


__all__ = []
