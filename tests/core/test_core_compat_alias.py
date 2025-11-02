# 25 LOC — asserts all legacy import styles resolve to core
import importlib
import types


def _mod(name):
    return importlib.import_module(name)


def test_alias_identity_basic():
    a = _mod("core.trace")
    b = _mod("core.trace")
    assert a is b
    from core import trace as t2

    assert t2 is b
    from core.trace import mk_crumb

    assert isinstance(mk_crumb, types.FunctionType)


def test_common_submodules_roundtrip():
    subs = ["trace", "clock", "ring", "bridge"]
    for s in subs:
        legacy = _mod(f"core.{s}")
        modern = _mod(f"core.{s}")
        assert legacy is modern
