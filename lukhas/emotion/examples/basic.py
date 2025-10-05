"""Shim: lukhas.emotion.examples.basic → emotion.examples.basic or candidate.emotion.examples.basic."""
try:
    from emotion.examples.basic import *  # noqa: F401, F403
except ImportError:
    try:
        from candidate.emotion.examples.basic import *  # noqa: F401, F403
    except ImportError:
        pass
