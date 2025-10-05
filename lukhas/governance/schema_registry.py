"""Shim: lukhas.governance.schema_registry → governance.schema_registry."""
try:
    from governance.schema_registry import *  # noqa: F401, F403
except ImportError:
    try:
        from candidate.governance.schema_registry import *  # noqa: F401, F403
    except ImportError:
        pass
