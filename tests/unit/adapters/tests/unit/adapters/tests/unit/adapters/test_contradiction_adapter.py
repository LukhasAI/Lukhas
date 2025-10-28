import json
from pathlib import Path

from MATRIZ.adapters.contradiction_adapter import ContradictionAdapter
from tests.util.mk_msg import mk_msg_from_json

GOLDEN = Path("tests/fixtures/golden/contradiction_adapter")

def _load(name):
    return json.loads((GOLDEN / name).read_text())

def test_contradiction_golden_1():
    msg = mk_msg_from_json(_load("input_1.json"))
    res = ContradictionAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("contradiction_processed" in s for s in res.guardian_log)
    assert "contradiction_enter" in res.trace

def test_contradiction_golden_2():
    msg = mk_msg_from_json(_load("input_2.json"))
    res = ContradictionAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("contradiction_processed" in s for s in res.guardian_log)
    assert "contradiction_enter" in res.trace

def test_contradiction_golden_3():
    msg = mk_msg_from_json(_load("input_3.json"))
    res = ContradictionAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("contradiction_processed" in s for s in res.guardian_log)
    assert "contradiction_enter" in res.trace
