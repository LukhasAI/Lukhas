import json
from pathlib import Path

from matriz.adapters.memory_adapter import MemoryAdapter
from tests.util.mk_msg import mk_msg_from_json

from MATRIZ.adapters.memory_adapter import MemoryAdapter

GOLDEN = Path("tests/fixtures/golden/memory_adapter")

def _load(name):
    return json.loads((GOLDEN / name).read_text())

def test_memory_golden_1():
    msg = mk_msg_from_json(_load("input_1.json"))
    res = MemoryAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("memory_processed" in s for s in res.guardian_log)
    assert "memory_enter" in res.trace

def test_memory_golden_2():
    msg = mk_msg_from_json(_load("input_2.json"))
    res = MemoryAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("memory_processed" in s for s in res.guardian_log)
    assert "memory_enter" in res.trace

def test_memory_golden_3():
    msg = mk_msg_from_json(_load("input_3.json"))
    res = MemoryAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("memory_processed" in s for s in res.guardian_log)
    assert "memory_enter" in res.trace
