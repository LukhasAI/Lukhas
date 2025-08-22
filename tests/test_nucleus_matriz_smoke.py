from lukhas.core.policy.decision import decide
from lukhas.orchestration.context_bus import build_context
from lukhas.identity.lambda_id import authenticate
from lukhas.governance.consent_ledger import record_consent

def test_matriz_smoke():
    assert isinstance(decide({"x":1}, mode="dry_run"), dict)
    assert isinstance(build_context({"session_id":"s1"}, mode="dry_run"), dict)
    assert isinstance(authenticate("LID-abc", mode="dry_run"), dict)
    assert isinstance(record_consent({"subject":"u1","scopes":["read"]}, mode="dry_run"), dict)