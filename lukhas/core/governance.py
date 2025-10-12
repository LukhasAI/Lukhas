"""Shim: lukhas.core.governance → governance or candidate.governance."""
try:
    from lukhas.governance import *  # noqa: F401, F403
except ImportError:
    try:
        from labs.governance import *  # noqa: F401, F403
    except ImportError:
        pass
