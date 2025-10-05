# cognitive/__init__.py
"""
Cognitive package alias for cognitive_core → cognitive migration.

This package provides compatibility imports during the transition period.
It will be removed after the sunset period.
"""

import os

# Only provide aliases if compat mode is enabled
if os.getenv("MATRIZ_COMPAT_IMPORTS", "1") == "1":
    try:
        # Import from lukhas.core.matrix.nodes when available
        from lukhas.core.matrix.nodes import *  # noqa: F401,F403
    except ImportError:
        # Graceful degradation if nodes aren't implemented yet
        pass

    # Add any other cognitive module aliases here as needed
    # from lukhas.consciousness import *  # noqa: F401,F403
    # from lukhas.memory import *  # noqa: F401,F403

else:
    # Strict mode: avoid exporting aliases
    __all__ = []

# Feature flag documentation for users
__doc__ += """

Environment Variables:
    MATRIZ_COMPAT_IMPORTS: Set to "0" to disable legacy import aliases.
                          Defaults to "1" for backward compatibility.

Migration Path:
    1. Update imports from 'cognitive_core.*' to 'candidate.core.matrix.*'
    2. Set MATRIZ_COMPAT_IMPORTS=0 in production
    3. Remove this package after all systems are migrated
"""
