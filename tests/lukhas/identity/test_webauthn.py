from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

def load_webauthn_module():
    repo_root = Path(__file__).resolve().parents[3]
    module_path = repo_root / " lukhas" / "identity" / "webauthn.py"
    spec = spec_from_file_location("webauthn", module_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_device_type_distribution():  # ΛTAG: device_distribution_test
    webauthn = load_webauthn_module()
    manager = webauthn.WebAuthnManager()
    cred = webauthn.WebAuthnCredential({"credential_id": "c1", "device_type": "platform"})
    manager.credentials["u1"] = [cred]
    assert manager._get_device_type_distribution() == {"platform": 1}


