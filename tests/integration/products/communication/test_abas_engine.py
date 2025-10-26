"""Tests for ABAS engine ethics integration."""

import pytest
from products.communication.abas_candidate.core.abas_engine import ABASRegistry


class DummyEthics:
    """Minimal ethics stub for testing."""

    def __init__(self) -> None:
        self.called = False

    async def evaluate_action(self, action, context, system):  # ΛTAG: ethics_mock
        self.called = True

        class Decision:
            decision_type = type("dt", (), {"value": "allow"})

        return Decision()


@pytest.mark.asyncio
async def test_register_policy_calls_ethics():
    registry = ABASRegistry()
    dummy = DummyEthics()
    registry.ethics = dummy
    await registry.register_policy({"id": "p1"})
    assert dummy.called
    assert registry.policies
