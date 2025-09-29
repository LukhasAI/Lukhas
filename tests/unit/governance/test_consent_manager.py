import json
from pathlib import Path

import pytest

from lukhas.governance.consent.consent_manager import (
    AdvancedConsentManager,
    ConsentMethod,
)

pytestmark = pytest.mark.asyncio


async def test_consent_grant_and_withdraw_audit(tmp_path: Path):
    cfg = {
        "enable_consent_audit": True,
        "consent_audit_log_path": str(tmp_path / "consent.log"),
        "consent_audit_report_path": str(tmp_path / "consent.jsonl"),
    }
    mgr = AdvancedConsentManager(cfg)
    await mgr.initialize()

    # Grant consent for a standard purpose
    res = await mgr.request_consent(
        user_id="u1",
        purpose_ids=["service_improvement"],
        method=ConsentMethod.WEB_FORM,
        context={
            "ip_address": "127.0.0.1",
            "user_agent": "pytest",
            "withdrawal_info_provided": True,
            "privacy_policy_accessible": True,
            "necessity_assessed": True,
            "consent_text": "I consent to processing my data for service improvement.",
        },
    )
    assert "service_improvement" in res
    consent = res["service_improvement"]
    assert consent.status.value == "granted"

    # Withdraw it
    ok = await mgr.withdraw_consent(
        "u1",
        ["service_improvement"],
        method=ConsentMethod.WEB_FORM,
        reason="user-request",
    )
    assert ok is True

    # Audit file exists with entries
    jsonl = tmp_path / "consent.jsonl"
    assert jsonl.exists()
    lines = jsonl.read_text().strip().splitlines()
    events = [json.loads(l) for l in lines]
    kinds = {e.get("event") for e in events}
    assert "consent_created" in kinds
    assert "consent_withdrawn" in kinds
