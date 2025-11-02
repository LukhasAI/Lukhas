import json
from pathlib import Path

from matriz.adapters.identity_adapter import UidentityAdapter

from tests.util.mk_msg import mk_msg_from_json

GOLDEN = Path("tests/fixtures/golden/identity_adapter")


def _load(name):
    return json.loads((GOLDEN / name).read_text())


def test_identity_golden_1():
    msg = mk_msg_from_json(_load("input_1.json"))
    res = UidentityAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("identity_processed" in s for s in res.guardian_log)
    assert "identity_enter" in res.trace


def test_identity_golden_2():
    msg = mk_msg_from_json(_load("input_2.json"))
    res = UidentityAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("identity_processed" in s for s in res.guardian_log)
    assert "identity_enter" in res.trace


def test_identity_golden_3():
    msg = mk_msg_from_json(_load("input_3.json"))
    res = UidentityAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("identity_processed" in s for s in res.guardian_log)
    assert "identity_enter" in res.trace
