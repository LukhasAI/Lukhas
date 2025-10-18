"""Shim: governance.guardian_system_integration → governance.guardian_system_integration."""
try:
    from governance.guardian_system_integration import *  # noqa: F401, F403
except ImportError:
    try:
        from labs.governance.guardian_system_integration import *  # noqa: F401, F403
    except ImportError:
        pass
