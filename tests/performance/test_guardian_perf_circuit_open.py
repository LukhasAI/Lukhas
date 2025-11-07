import importlib as _importlib
import time

import pytest

_mod = _importlib.import_module("labs.governance.guardian_system_integration")
GuardianSystemIntegration = _mod.GuardianSystemIntegration
GuardianValidationRequest = _mod.GuardianValidationRequest

pytestmark = pytest.mark.asyncio


async def test_guardian_perf_immediate_skip_when_circuit_open():
    gi = GuardianSystemIntegration({})
    # Open circuit for ethics to force immediate skip
    from datetime import datetime, timedelta, timezone

    br = gi._breakers["ethics"]
    br["state"] = "open"
    br["open_until"] = datetime.now(timezone.utc) + timedelta(seconds=5)

    req = GuardianValidationRequest(
        request_id="perf3",
        timestamp=datetime.now(timezone.utc),
        user_id="u1",
        session_id="s1",
        action="noop",
        resource="res",
        context={},
    )

    start = time.time()
    res = await gi.validate_action(req)
    elapsed = time.time() - start
    assert res is not None
    # With circuit open, should return very quickly
    assert elapsed < 0.05
