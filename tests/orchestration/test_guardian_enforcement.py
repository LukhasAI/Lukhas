#!/usr/bin/env python3
"""
Guardian enforcement tests
==========================

Validates default-on enforcement behavior for canary traffic when
`ENFORCE_ETHICS_DSL` is unset.
"""

import pytest

from lukhas.core.ethics.guardian_drift_bands import GuardianBand, GuardianBandResult
from lukhas.core.orchestration.plan_verifier import PlanVerifier, VerificationContext


@pytest.mark.guardian
def test_enforce_on_canary_default(monkeypatch):
    """Guardian enforcement should default to ON for canary traffic."""
    # Ensure no explicit override is present
    monkeypatch.delenv("ENFORCE_ETHICS_DSL", raising=False)
    monkeypatch.setenv("LUKHAS_CANARY_PERCENT", "100")
    monkeypatch.setenv("LUKHAS_LANE", "candidate")
    monkeypatch.setenv("LUKHAS_GUARDIAN_ENFORCED_LANES", "candidate")

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
    ctx = VerificationContext(user_id="canary-user", session_id="session-123")

    outcome = verifier.verify(plan, ctx)

    assert outcome.allow, "Baseline plan should be allowed while enforcement is active"
    assert ctx.metadata.get("guardian_lane") == "candidate"
    assert ctx.metadata.get("guardian_enforced") is True
    assert ctx.metadata.get("guardian_emergency_disabled") is False
