import os
os.environ.setdefault("FEATURE_ORCHESTRATION_HANDOFF","false")

from lukhas.orchestration.context.api import handoff_context

def test_handoff_context_dryrun():
    out = handoff_context({"foo":"bar"})
    assert out["ok"] is True
    assert out["mode"] == "dryrun"
    assert out["latency_ms"] >= 0