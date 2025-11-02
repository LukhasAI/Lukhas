import json
from pathlib import Path

from matriz.adapters.bridge_adapter import BridgeAdapter

from tests.util.mk_msg import mk_msg_from_json

GOLDEN = Path("tests/fixtures/golden/bridge_adapter")


def _load(name):
    return json.loads((GOLDEN / name).read_text())


def test_bridge_golden_1():
    msg = mk_msg_from_json(_load("input_1.json"))
    res = BridgeAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("bridge_processed" in s for s in res.guardian_log)
    assert "bridge_enter" in res.trace


def test_bridge_golden_2():
    msg = mk_msg_from_json(_load("input_2.json"))
    res = BridgeAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("bridge_processed" in s for s in res.guardian_log)
    assert "bridge_enter" in res.trace


def test_bridge_golden_3():
    msg = mk_msg_from_json(_load("input_3.json"))
    res = BridgeAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("bridge_processed" in s for s in res.guardian_log)
    assert "bridge_enter" in res.trace
