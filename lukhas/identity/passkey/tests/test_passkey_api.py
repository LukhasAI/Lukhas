import os
os.environ.setdefault("FEATURE_IDENTITY_PASSKEY","false")

from lukhas.identity.passkey.api import verify_passkey

def test_passkey_verify_null_provider_dryrun():
    out = verify_passkey({"challenge":"xyz"})
    assert out["ok"] is True
    assert out["provider"] == "null"
    assert out["challenge"] == "xyz"