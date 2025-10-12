"""Tests for :mod:`memory.memory_event` factory."""

import os
import sys

import pytest

if "lukhas.memory" in sys.modules:
    del sys.modules["lukhas.memory"]

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from lukhas.memory.memory_event import MemoryEventFactory


# ΛTAG: memory_event
def test_memory_event_factory_creates_event_with_metrics(caplog):
    factory = MemoryEventFactory()
    data = {"emotional_signature": {"valence": 0.8, "arousal": 0.6}}
    metadata = {"source": "test"}

    with caplog.at_level("INFO"):
        event = factory.create(data, metadata)

    assert event.data["emotional_signature"]["valence"] == 0.8
    assert event.metadata["source"] == "test"
    metrics = event.metadata["metrics"]
    assert metrics["affect_delta"] >= 0.0
    assert metrics["driftScore"] >= 0.0
    assert "timestamp_utc" in event.metadata
    assert "MemoryEvent_created" in caplog.text


def test_memory_event_factory_tracks_drift_history():
    factory = MemoryEventFactory()

    first_event = factory.create({"affect_delta": 0.2}, {})
    assert first_event.metadata["metrics"]["driftScore"] == pytest.approx(0.2)

    second_event = factory.create({"affect_delta": 0.8}, {})
    drift_score = second_event.metadata["metrics"]["driftScore"]
    assert drift_score == pytest.approx(0.6)
    assert second_event.metadata["metrics"]["driftTrend"] == pytest.approx((0.2 + 0.6) / 2)

