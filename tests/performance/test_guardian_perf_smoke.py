import time

import pytest

from candidate.governance.guardian_system_integration import (
    GuardianSystemIntegration,
    GuardianValidationRequest,
)


pytestmark = pytest.mark.asyncio


async def test_guardian_validate_action_under_threshold():
    gi = GuardianSystemIntegration({})
    req = GuardianValidationRequest(
        request_id="perf1",
        timestamp=None,  # set below
        user_id="u1",
        session_id="s1",
        action="noop",
        resource="res",
        context={},
    )
    # fix timestamp to now
    from datetime import datetime, timezone

    req.timestamp = datetime.now(timezone.utc)
    # Set a generous threshold for smoke performance, e.g., 0.25s
    start = time.time()
    res = await gi.validate_action(req)
    elapsed = time.time() - start
    assert res is not None
    assert elapsed < 0.25
