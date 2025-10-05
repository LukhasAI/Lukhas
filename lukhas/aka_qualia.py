"""Shim: lukhas.aka_qualia → aka_qualia or candidate.aka_qualia."""
try:
    from aka_qualia import *  # noqa: F401, F403
except ImportError:
    try:
        from candidate.aka_qualia import *  # noqa: F401, F403
    except ImportError:
        pass
