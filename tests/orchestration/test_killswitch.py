#!/usr/bin/env python3
"""
Guardian kill-switch tests
==========================

Ensures the emergency disable file is honored within a single request cycle.
"""

import pytest
from core.ethics.guardian_drift_bands import GuardianBand, GuardianBandResult
from core.orchestration.plan_verifier import PlanVerifier, VerificationContext


@pytest.mark.guardian
def test_emergency_disable_takes_effect(monkeypatch, tmp_path):
    """Kill-switch file should disable enforcement immediately."""
    kill_switch = tmp_path / "guardian_emergency_disable"
    monkeypatch.setenv("GUARDIAN_EMERGENCY_DISABLE_PATH", str(kill_switch))
    monkeypatch.setenv("ENFORCE_ETHICS_DSL", "1")
    monkeypatch.setenv("LUKHAS_CANARY_PERCENT", "100")
    monkeypatch.setenv("LUKHAS_LANE", "labs")
    monkeypatch.setenv("LUKHAS_GUARDIAN_ENFORCED_LANES", "labs")

    verifier = PlanVerifier()
    verifier.guardian_bands.evaluate = lambda *args, **kwargs: GuardianBandResult(
        band=GuardianBand.ALLOW,
        action="allow",
        drift_score=0.01,
        ethics_action="allow",
        evaluation_time_ms=0.0,
        plan_hash="stub",
        transition=None,
        guardrails=[],
        human_requirements=[],
        audit_context={},
    )
    plan = {"action": "noop", "params": {}}

    ctx = VerificationContext(user_id="guardian", session_id="baseline")
    outcome_before = verifier.verify(plan, ctx)

    assert outcome_before.allow
    assert ctx.metadata.get("guardian_enforced") is True
    assert ctx.metadata.get("guardian_emergency_disabled") is False

    # Activate kill-switch and validate it is observed on the next request cycle
    kill_switch.touch()

    followup_ctx = VerificationContext(user_id="guardian", session_id="baseline", request_id="next")
    outcome_after = verifier.verify(plan, followup_ctx)

    assert outcome_after.allow
    assert followup_ctx.metadata.get("guardian_enforced") is False
    assert followup_ctx.metadata.get("guardian_emergency_disabled") is True
    assert kill_switch.exists(), "Kill-switch file should remain for external monitors"
