"""Tests for :mod:`memory.memory_identity` factory."""

import os, sys
if "memory" in sys.modules:
    del sys.modules["memory"]

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from memory.memory_identity import MemoryIdentityFactory


# ΛTAG: memory_identity
def test_memory_identity_factory_creates_identity(caplog):
    factory = MemoryIdentityFactory()
    with caplog.at_level("DEBUG"):
        identity = factory.create("user-1", {"role": "tester"})
    assert identity.identifier == "user-1"
    assert identity.attributes["role"] == "tester"
    assert "Creating MemoryIdentity" in caplog.text

