"""governance compatibility - forwards to governance or candidate.governance."""

import sys

# Import and register schema_registry
try:
    from lukhas_website.lukhas.governance import schema_registry
    sys.modules['governance.schema_registry'] = schema_registry
except ImportError:
    pass

# Export submodules for direct import
try:
    from . import ethics
except ImportError:
    ethics = None

try:
    from . import guardian_system
except ImportError:
    guardian_system = None

try:
    from . import identity
except ImportError:
    identity = None

__all__ = []
if ethics is not None:
    __all__.append("ethics")
if guardian_system is not None:
    __all__.append("guardian_system")
if identity is not None:
    __all__.append("identity")
