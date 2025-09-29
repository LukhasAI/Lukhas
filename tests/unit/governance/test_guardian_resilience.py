import asyncio
from datetime import datetime, timedelta, timezone

import pytest

from lukhas.governance.guardian_system_integration import (
    GuardianSystemIntegration,
    GuardianValidationRequest,
)

pytestmark = pytest.mark.asyncio


async def test_ethics_component_timeout_triggers_skip_and_circuit(monkeypatch):
    # Configure aggressive breaker to open after first failure
    gi = GuardianSystemIntegration(
        {
            "component_timeout_ms": 10,
            "breaker_failure_threshold": 1,
            "breaker_open_seconds": 1,
        }
    )

    # Attach a dummy ethics engine by monkeypatching _validate_ethics to sleep past timeout
    async def slow_ethics(req):
        await asyncio.sleep(0.05)
        return {"status": "completed", "ethical_score": 1.0}

    monkeypatch.setattr(gi, "ethics_engine", object())
    monkeypatch.setattr(gi, "_validate_ethics", slow_ethics)

    # Build minimal request
    req = GuardianValidationRequest(
        request_id="r1",
        timestamp=datetime.now(timezone.utc),
        user_id="u1",
        session_id="s1",
        action="test",
        resource="res",
        context={},
    )

    res = await gi.validate_action(req)
    # Ethics should be skipped due to timeout
    assert res.ethics_result is not None
    assert res.ethics_result.get("status") == "skipped"

    # Second call should be immediately skipped due to circuit open
    res2 = await gi.validate_action(req)
    assert res2.ethics_result is not None
    assert res2.ethics_result.get("status") == "skipped"


async def test_circuit_open_skips_component(monkeypatch):
    gi = GuardianSystemIntegration({})
    # Manually open breaker for ethics
    br = gi._breakers["ethics"]
    br["state"] = "open"
    br["open_until"] = datetime.now(timezone.utc) + timedelta(seconds=5)
    monkeypatch.setattr(gi, "ethics_engine", object())

    req = GuardianValidationRequest(
        request_id="r2",
        timestamp=datetime.now(timezone.utc),
        user_id="u1",
        session_id="s1",
        action="test",
        resource="res",
        context={},
    )

    res = await gi.validate_action(req)
    assert res.ethics_result is not None
    assert res.ethics_result.get("status") == "skipped"
    assert res.ethics_result.get("reason") == "circuit_open"
