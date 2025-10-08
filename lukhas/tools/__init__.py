"""
LUKHAS Tools Package.

Provides utility tools and simulators for the LUKHAS platform.
"""

from __future__ import annotations

import sys

try:
    from . import todo as _todo  # type: ignore

    sys.modules.setdefault("TODO", _todo)
    sys.modules.setdefault("todo", _todo)
except Exception:
    pass
