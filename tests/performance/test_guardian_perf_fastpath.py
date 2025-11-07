import importlib as _importlib
import time

import pytest

_mod = _importlib.import_module("labs.governance.guardian_system_integration")
GuardianSystemIntegration = _mod.GuardianSystemIntegration
GuardianValidationRequest = _mod.GuardianValidationRequest

pytestmark = pytest.mark.asyncio


async def test_guardian_validate_action_fast_when_checks_disabled():
    gi = GuardianSystemIntegration({})
    req = GuardianValidationRequest(
        request_id="perf2",
        timestamp=None,
        user_id="u1",
        session_id="s1",
        action="noop",
        resource="res",
        context={},
    )
    from datetime import datetime, timezone

    req.timestamp = datetime.now(timezone.utc)
    # Disable heavy checks to validate fast path
    req.require_consent = False
    req.require_ethics_check = False
    req.require_drift_check = False

    start = time.time()
    res = await gi.validate_action(req)
    elapsed = time.time() - start
    assert res is not None
    assert elapsed < 0.1
