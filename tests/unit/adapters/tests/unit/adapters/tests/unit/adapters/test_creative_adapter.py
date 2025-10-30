import json
from pathlib import Path

from matriz.adapters.creative_adapter import CreativeAdapter

from MATRIZ.adapters.creative_adapter import CreativeAdapter
from tests.util.mk_msg import mk_msg_from_json

GOLDEN = Path("tests/fixtures/golden/creative_adapter")

def _load(name):
    return json.loads((GOLDEN / name).read_text())

def test_creative_golden_1():
    msg = mk_msg_from_json(_load("input_1.json"))
    res = CreativeAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("creative_processed" in s for s in res.guardian_log)
    assert "creative_enter" in res.trace

def test_creative_golden_2():
    msg = mk_msg_from_json(_load("input_2.json"))
    res = CreativeAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("creative_processed" in s for s in res.guardian_log)
    assert "creative_enter" in res.trace

def test_creative_golden_3():
    msg = mk_msg_from_json(_load("input_3.json"))
    res = CreativeAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("creative_processed" in s for s in res.guardian_log)
    assert "creative_enter" in res.trace
