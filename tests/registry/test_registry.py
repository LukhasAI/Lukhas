# tests/registry/test_registry.py
from core.registry import register, resolve


def test_registry_roundtrip():
    register("lukhas.memory", object())
    got = resolve("lukhas.memory")
    assert got is not None
