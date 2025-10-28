import json
from pathlib import Path

from matriz.adapters.emotion_adapter import UemotionAdapter

from tests.util.mk_msg import mk_msg_from_json

from MATRIZ.adapters.emotion_adapter import UemotionAdapter

GOLDEN = Path("tests/fixtures/golden/emotion_adapter")

def _load(name):
    return json.loads((GOLDEN / name).read_text())

def test_emotion_golden_1():
    msg = mk_msg_from_json(_load("input_1.json"))
    res = UemotionAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("emotion_processed" in s for s in res.guardian_log)
    assert "emotion_enter" in res.trace

def test_emotion_golden_2():
    msg = mk_msg_from_json(_load("input_2.json"))
    res = UemotionAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("emotion_processed" in s for s in res.guardian_log)
    assert "emotion_enter" in res.trace

def test_emotion_golden_3():
    msg = mk_msg_from_json(_load("input_3.json"))
    res = UemotionAdapter().handle(msg)
    assert res.ok
    assert res.guardian_log and any("emotion_processed" in s for s in res.guardian_log)
    assert "emotion_enter" in res.trace
