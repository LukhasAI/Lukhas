import json
from pathlib import Path

from matriz.adapters.governance_adapter import UgovernanceAdapter

from tests.util.mk_msg import mk_msg_from_json

GOLDEN = Path("tests/fixtures/golden/governance_adapter")


def _load(name):
    return json.loads((GOLDEN / name).read_text())


def test_governance_golden_1():
    msg = mk_msg_from_json(_load("input_1.json"))
    res = UgovernanceAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("governance_processed" in s for s in res.guardian_log)
    assert "governance_enter" in res.trace


def test_governance_golden_2():
    msg = mk_msg_from_json(_load("input_2.json"))
    res = UgovernanceAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("governance_processed" in s for s in res.guardian_log)
    assert "governance_enter" in res.trace


def test_governance_golden_3():
    msg = mk_msg_from_json(_load("input_3.json"))
    res = UgovernanceAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("governance_processed" in s for s in res.guardian_log)
    assert "governance_enter" in res.trace
