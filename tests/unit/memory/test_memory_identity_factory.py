"""Tests for :mod:`memory.memory_identity` factory."""

import os
import sys

import pytest

if "memory" in sys.modules:
    del sys.modules["memory"]

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from memory.memory_identity import MemoryIdentityFactory


# ΛTAG: memory_identity
def test_memory_identity_factory_creates_identity_with_metrics(caplog):
    factory = MemoryIdentityFactory()
    attributes = {"role": "tester", "affect_vector": [0.2, 0.6, 0.4]}

    with caplog.at_level("DEBUG"):
        identity = factory.create("user-1", attributes)

    assert identity.identifier == "user-1"
    assert identity.attributes["role"] == "tester"
    telemetry = identity.attributes.get("telemetry", {})
    assert telemetry["affect_delta"] >= 0.0
    assert telemetry["driftScore"] >= 0.0
    registry_metrics = factory.registry.get_metrics("user-1")
    assert registry_metrics["affect_delta"] == telemetry["affect_delta"]
    assert "MemoryIdentity_created" in caplog.text


def test_memory_identity_factory_validates_inputs():
    factory = MemoryIdentityFactory()

    with pytest.raises(ValueError):
        factory.create("", {})

    with pytest.raises(TypeError):
        factory.create("user-2", ["not", "a", "dict"])  # type: ignore[arg-type]

