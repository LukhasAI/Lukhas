# cognitive/__init__.py
"""
Cognitive package alias for cognitive_core → cognitive migration.

This package provides compatibility imports during the transition period.
It will be removed after the sunset period.
"""

import contextlib
import os

# Only provide aliases if compat mode is enabled
if os.getenv("MATRIZ_COMPAT_IMPORTS", "1") == "1":
    with contextlib.suppress(ImportError):
        # Import from core.matriz.nodes when available
        from core.matriz.nodes import *

    # Add any other cognitive module aliases here as needed
    # from consciousness import *
    # from memory import *

else:
    # Strict mode: avoid exporting aliases
    __all__ = []

# Feature flag documentation for users
__doc__ += """

Environment Variables:
    MATRIZ_COMPAT_IMPORTS: Set to "0" to disable legacy import aliases.
                          Defaults to "1" for backward compatibility.

Migration Path:
    1. Update imports from 'cognitive_core.*' to 'core.matriz.*'
    2. Set MATRIZ_COMPAT_IMPORTS=0 in production
    3. Remove this package after all systems are migrated
"""
