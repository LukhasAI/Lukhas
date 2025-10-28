import json
from pathlib import Path

from matriz.adapters.bio_adapter import BioAdapter

from tests.util.mk_msg import mk_msg_from_json

from MATRIZ.adapters.bio_adapter import BioAdapter

GOLDEN = Path("tests/fixtures/golden/bio_adapter")

def _load(name):
    return json.loads((GOLDEN / name).read_text())

def test_bio_golden_1():
    msg = mk_msg_from_json(_load("input_1.json"))
    res = BioAdapter().handle(msg)
    assert res.ok
    assert res.payload == _load("output_1.json")
    assert res.guardian_log and any("bio_processed" in s for s in res.guardian_log)
    assert "bio_enter" in res.trace

def test_bio_golden_2():
    msg = mk_msg_from_json(_load("input_2.json"))
    res = BioAdapter().handle(msg)
    assert res.ok
    assert res.payload == _load("output_2.json")
    assert res.guardian_log and any("bio_processed" in s for s in res.guardian_log)
    assert "bio_enter" in res.trace

def test_bio_golden_3():
    msg = mk_msg_from_json(_load("input_3.json"))
    res = BioAdapter().handle(msg)
    assert res.ok
    assert res.payload == _load("output_3.json")
    assert res.guardian_log and any("bio_processed" in s for s in res.guardian_log)
    assert "bio_enter" in res.trace
