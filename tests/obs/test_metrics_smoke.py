# tests/obs/test_metrics_smoke.py
from lukhas import metrics

def test_metrics_noop_labels_inc_ok(monkeypatch):
    monkeypatch.setenv("ENABLE_PROM", "0")
    metrics.stage_timeouts.labels("INTENT").inc()
    with metrics.stage_latency.labels("INTENT").time():
        pass