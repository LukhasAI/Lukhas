import json
from pathlib import Path

from matriz.adapters.consciousness_adapter import ConsciousnessAdapter

from MATRIZ.adapters.consciousness_adapter import ConsciousnessAdapter
from tests.util.mk_msg import mk_msg_from_json

GOLDEN = Path("tests/fixtures/golden/consciousness_adapter")

def _load(name):
    return json.loads((GOLDEN / name).read_text())

def test_consciousness_golden_1():
    msg = mk_msg_from_json(_load("input_1.json"))
    res = ConsciousnessAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("consciousness_processed" in s for s in res.guardian_log)
    assert "consciousness_enter" in res.trace

def test_consciousness_golden_2():
    msg = mk_msg_from_json(_load("input_2.json"))
    res = ConsciousnessAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("consciousness_processed" in s for s in res.guardian_log)
    assert "consciousness_enter" in res.trace

def test_consciousness_golden_3():
    msg = mk_msg_from_json(_load("input_3.json"))
    res = ConsciousnessAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("consciousness_processed" in s for s in res.guardian_log)
    assert "consciousness_enter" in res.trace
