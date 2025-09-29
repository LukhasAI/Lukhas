from __future__ import annotations

import pytest

from lukhas.emotion.examples.basic import example


def test_compute_affect_delta() -> None:
    assert example.compute_affect_delta((0.1, 0.5)) == pytest.approx(0.4)


def test_compute_drift_score() -> None:
    assert example.compute_drift_score((0.0, 0.3, 0.1)) == pytest.approx((0.3 + 0.2) / 2)


def test_build_emotion_snapshot_and_trace(monkeypatch) -> None:
    monkeypatch.setattr(example.logger, "info", lambda *args, **kwargs: None)
    monkeypatch.setattr(example.logger, "debug", lambda *args, **kwargs: None)

    snapshot = example.build_emotion_snapshot((0.2, 0.3, 0.5))
    assert snapshot.affect_delta == pytest.approx(0.3)
    assert snapshot.drift_score == pytest.approx((0.1 + 0.2) / 2)

    trace = example.render_symbolic_trace(snapshot)
    assert "affect_delta" in trace
    assert "driftScore" in trace

