"""
LUKHAS Tools Package.

Provides utility tools and simulators for the LUKHAS platform.
"""

from __future__ import annotations

import sys

try:
    from . import todo as _todo  # type: ignore  # noqa: TID252 (relative imports in __init__.py are idiomatic)

    sys.modules.setdefault("TODO", _todo)
    sys.modules.setdefault("todo", _todo)
except Exception:
    pass
