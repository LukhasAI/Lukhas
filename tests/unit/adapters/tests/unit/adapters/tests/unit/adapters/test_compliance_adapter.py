import json
from pathlib import Path
from matriz.adapters.compliance_adapter import ComplianceAdapter
from tests.util.mk_msg import mk_msg_from_json

GOLDEN = Path("tests/fixtures/golden/compliance_adapter")

def _load(name):
    return json.loads((GOLDEN / name).read_text())

def test_compliance_golden_1():
    msg = mk_msg_from_json(_load("input_1.json"))
    res = ComplianceAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("compliance_processed" in s for s in res.guardian_log)
    assert "compliance_enter" in res.trace

def test_compliance_golden_2():
    msg = mk_msg_from_json(_load("input_2.json"))
    res = ComplianceAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("compliance_processed" in s for s in res.guardian_log)
    assert "compliance_enter" in res.trace

def test_compliance_golden_3():
    msg = mk_msg_from_json(_load("input_3.json"))
    res = ComplianceAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("compliance_processed" in s for s in res.guardian_log)
    assert "compliance_enter" in res.trace
