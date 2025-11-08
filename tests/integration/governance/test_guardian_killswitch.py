
from datetime import datetime, timezone
import asyncio
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from core.governance.guardian_system_integration import (
    GuardianSystemIntegration,
    GuardianValidationRequest,
    ValidationResult,
    check_emergency_killswitch,
)


class TestGuardianKillSwitch(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.guardian = GuardianSystemIntegration()
        await self.guardian.initialize()
        self.test_request = GuardianValidationRequest(
            request_id="test_req_killswitch",
            timestamp=datetime.now(timezone.utc),
            user_id="test_user",
            session_id="test_session_killswitch",
            action="test_action",
            resource="test_resource",
        )

    @patch.dict(os.environ, {"GUARDIAN_EMERGENCY_DISABLE": "1"})
    def test_killswitch_env_var(self):
        self.assertTrue(check_emergency_killswitch())

    def test_killswitch_file(self):
        killswitch_path = Path("/tmp/guardian_emergency_disable")
        killswitch_path.touch()
        self.assertTrue(check_emergency_killswitch())
        killswitch_path.unlink()

    def test_killswitch_inactive(self):
        if "GUARDIAN_EMERGENCY_DISABLE" in os.environ:
            del os.environ["GUARDIAN_EMERGENCY_DISABLE"]
        killswitch_path = Path("/tmp/guardian_emergency_disable")
        if killswitch_path.exists():
            killswitch_path.unlink()
        self.assertFalse(check_emergency_killswitch())

    @patch("core.governance.guardian_system_integration.check_emergency_killswitch", return_value=True)
    async def test_validation_bypassed_when_killswitch_active(self, _):
        response = await self.guardian.validate_action(self.test_request)
        self.assertEqual(response.result, ValidationResult.EMERGENCY_STOP)
        self.assertEqual(response.reasoning, "Emergency kill-switch is active.")

    async def test_ethics_dsl_enforcement_flag(self):
        # Test with enforcement ON
        guardian_on = GuardianSystemIntegration(config={"ENFORCE_ETHICS_DSL": 1})
        await guardian_on.initialize()
        self.assertTrue(guardian_on.enforce_ethics_dsl)

        # Test with enforcement OFF
        guardian_off = GuardianSystemIntegration(config={"ENFORCE_ETHICS_DSL": 0})
        await guardian_off.initialize()
        self.assertFalse(guardian_off.enforce_ethics_dsl)
