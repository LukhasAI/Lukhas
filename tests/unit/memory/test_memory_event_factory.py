"""Tests for :mod:`memory.memory_event` factory."""

import os, sys
if "memory" in sys.modules:
    del sys.modules["memory"]

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from memory.memory_event import MemoryEventFactory


# ΛTAG: memory_event
def test_memory_event_factory_creates_event(caplog):
    factory = MemoryEventFactory()
    with caplog.at_level("DEBUG"):
        event = factory.create({"value": 1}, {"source": "test"})
    assert event.data["value"] == 1
    assert event.metadata["source"] == "test"
    assert "Creating MemoryEvent" in caplog.text

