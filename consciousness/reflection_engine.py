"""Bridge: reflection_engine -> lukhas_website implementation."""
from __future__ import annotations

try:
    from lukhas_website.consciousness.reflection_engine import ReflectionEngine, reflect_on_state
    __all__ = ["ReflectionEngine", "reflect_on_state"]
except ImportError:
    __all__ = []
