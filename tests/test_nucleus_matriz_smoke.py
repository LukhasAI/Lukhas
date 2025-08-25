from candidate.core.policy.decision import decide
from candidate.orchestration.context_bus import build_context
from candidate.identity.lambda_id import authenticate
from candidate.governance.consent_ledger import record_consent

def test_matriz_smoke():
    assert isinstance(decide({"x":1}, mode="dry_run"), dict)
    assert isinstance(build_context({"session_id":"s1"}, mode="dry_run"), dict)
    assert isinstance(authenticate("LID-abc", mode="dry_run"), dict)
    assert isinstance(record_consent({"subject":"u1","scopes":["read"]}, mode="dry_run"), dict)