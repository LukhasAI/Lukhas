import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

from abas.tiny_abas_gate import GateDecision, TinyABASGate, abas_gate

# \u039bTAG: gate

def test_check_gate_blocks_during_quiet_hours():
    gate = TinyABASGate()
    user_state = {"hour": 23}
    opportunity = {"risk": {"alignment": 0.9}}

    result = gate.check_gate(user_state, opportunity)

    assert not result.approved
    assert result.reason == "quiet_hours"
    assert result.confidence == pytest.approx(0.7)


def test_check_gate_allows_under_normal_conditions():
    gate = TinyABASGate()
    user_state = {"hour": 10, "stress": 0.2}
    opportunity = {"risk": {"alignment": 0.8}}

    result = gate.check_gate(user_state, opportunity)

    assert result.approved
    assert result.reason is None
    assert 0 < result.confidence <= 1


def test_abas_gate_returns_human_readable_reason():
    user_state = {"stress": 0.9}
    opportunity = {"risk": {"alignment": 0.9}}

    result = abas_gate(user_state, opportunity)

    assert not result["approved"]
    assert result["reason"] == "stress_block"
    assert "stressed" in result["explanation"].lower()


def test_is_quiet_hours_daytime_range():
    gate = TinyABASGate()
    gate.quiet_hours_start = 1
    gate.quiet_hours_end = 5

    assert gate._is_quiet_hours(3) is True
    assert gate._is_quiet_hours(10) is False
