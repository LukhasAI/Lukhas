import json
from pathlib import Path

from matriz.adapters.orchestration_adapter import UorchestrationAdapter

from MATRIZ.adapters.orchestration_adapter import UorchestrationAdapter
from tests.util.mk_msg import mk_msg_from_json

GOLDEN = Path("tests/fixtures/golden/orchestration_adapter")

def _load(name):
    return json.loads((GOLDEN / name).read_text())

def test_orchestration_golden_1():
    msg = mk_msg_from_json(_load("input_1.json"))
    res = UorchestrationAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("orchestration_processed" in s for s in res.guardian_log)
    assert "orchestration_enter" in res.trace

def test_orchestration_golden_2():
    msg = mk_msg_from_json(_load("input_2.json"))
    res = UorchestrationAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("orchestration_processed" in s for s in res.guardian_log)
    assert "orchestration_enter" in res.trace

def test_orchestration_golden_3():
    msg = mk_msg_from_json(_load("input_3.json"))
    res = UorchestrationAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("orchestration_processed" in s for s in res.guardian_log)
    assert "orchestration_enter" in res.trace
