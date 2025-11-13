"""Tests for Supervisor custom handler registration."""

import pytest
from core.fault_tolerance import SupervisionStrategy, Supervisor


def test_agent_specific_custom_handler_precedence():
    """Agent-specific handler should take precedence over others."""
    supervisor = Supervisor(strategy=SupervisionStrategy.STOP)
    call_order = []

    def exception_handler(agent_id, exc, context):
        call_order.append("exception")
        return {"action": "exception"}

    def agent_handler(agent_id, exc, context):
        call_order.append("agent")
        return {"action": "agent_override", "agent_id": agent_id}

    supervisor.register_custom_handler(ValueError, exception_handler)
    supervisor.register_custom_handler("agent-007", agent_handler)

    result = supervisor.handle_failure("agent-007", ValueError("boom"))

    # ΛTAG: handler_precedence_validation
    assert result["action"] == "agent_override"
    assert call_order == ["agent"]


def test_exception_specific_custom_handler_invoked_when_available():
    """Exception-specific handler should run when agent handler missing."""
    supervisor = Supervisor(strategy=SupervisionStrategy.RESTART)
    invoked = {"called": False}

    def runtime_handler(agent_id, exc, context):
        invoked["called"] = True
        return {"action": "exception_override", "agent_id": agent_id}

    supervisor.register_custom_handler(RuntimeError, runtime_handler)

    result = supervisor.handle_failure("agent-311", RuntimeError("drift detected"))

    assert invoked["called"] is True
    assert result["action"] == "exception_override"


def test_register_custom_handler_rejects_invalid_targets():
    """Invalid targets should raise a TypeError."""
    supervisor = Supervisor()

    with pytest.raises(TypeError):
        supervisor.register_custom_handler(123, lambda *_: {})
