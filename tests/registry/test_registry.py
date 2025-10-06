# tests/registry/test_registry.py
from core.registry import register, resolve


def test_registry_roundtrip():
    register("memory", object())
    got = resolve("memory")
    assert got is not None
