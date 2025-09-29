"""Tests for the MoralAgentTemplate."""

# ΛTAG: moral_agent_template_test
from lukhas.governance.ethics.moral_agent_template import MoralAgentTemplate


def test_process_signal_help():
    agent = MoralAgentTemplate()
    result = agent.process_signal({"action": "help"})
    assert result["judgment"] == "approve"
    assert result["metrics"]["affect_delta"] == 1.0


def test_process_signal_harm():
    agent = MoralAgentTemplate()
    result = agent.process_signal({"action": "harm"})
    assert result["judgment"] == "reject"
    assert result["metrics"]["affect_delta"] == -1.0
