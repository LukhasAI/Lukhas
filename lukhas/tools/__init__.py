"""
LUKHAS Tools Package.

Provides utility tools and simulators for the LUKHAS platform.
"""

from __future__ import annotations

import sys
from importlib import import_module

try:
    from . import (
        todo as _todo,  # type: ignore  # (relative imports in __init__.py are idiomatic)
    )

    sys.modules.setdefault("TODO", _todo)
    sys.modules.setdefault("todo", _todo)
except Exception:
    pass

# Re-export legacy symbols needed by tests (temporary shims)

# collapse_simulator_main was historically imported from `tools`
try:
    _collapse = import_module("lukhas.tools.collapse")
    collapse_simulator_main = getattr(_collapse, "collapse_simulator_main")
except Exception:

    def collapse_simulator_main(*args, **kwargs):  # pragma: no cover
        raise RuntimeError(
            "collapse_simulator_main not yet wired. "
            "Use lukhas.tools.collapse.collapse_simulator_main or update tests."
        )


# Optional subpackages expected by tests: tools.scripts / tools.acceptance_gate_ast / tools.security
# Provide light proxies so imports resolve; real modules should replace these.
try:
    from . import scripts  # type: ignore
except Exception:

    class scripts:  # type: ignore  # pragma: no cover
        pass


try:
    from . import acceptance_gate_ast  # type: ignore
except Exception:

    class acceptance_gate_ast:  # type: ignore  # pragma: no cover
        pass


try:
    from . import security  # type: ignore
except Exception:

    class security:  # type: ignore  # pragma: no cover
        pass
