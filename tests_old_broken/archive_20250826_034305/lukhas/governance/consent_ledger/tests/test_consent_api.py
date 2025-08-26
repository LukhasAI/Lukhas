import os
os.environ.setdefault("FEATURE_GOVERNANCE_LEDGER","false")

from lukhas.governance.consent_ledger.api import record_consent

def test_record_consent_null_provider_dryrun():
    out = record_consent("usr_123","gmail.read",{"just":"testing"})
    assert out["ok"] is True
    assert out["provider"] == "null"
    assert out["entry"]["user_id"] == "usr_123"