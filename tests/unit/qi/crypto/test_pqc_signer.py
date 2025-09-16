import importlib
import sys

import pytest


@pytest.fixture(autouse=True)
def clear_module_cache():
    """
    A fixture to clear the module from sys.modules to ensure it is re-imported
    for each test case.
    """
    module_name = "candidate.qi.crypto.pqc_signer"
    if module_name in sys.modules:
        del sys.modules[module_name]
    yield
    if module_name in sys.modules:
        del sys.modules[module_name]


def test_pqc_signer_disabled_by_default(monkeypatch):
    """
    Verify that importing pqc_signer raises NotImplementedError when the feature
    flag is not set.
    """
    monkeypatch.delenv("ENABLE_MATRIZ_PQC_SIGNER", raising=False)

    with pytest.raises(NotImplementedError, match="PQC signer requires MATRIZ integration"):
        pass


def test_pqc_signer_explicitly_disabled(monkeypatch):
    """
    Verify that importing pqc_signer raises NotImplementedError when the feature
    flag is explicitly set to 'false'.
    """
    monkeypatch.setenv("ENABLE_MATRIZ_PQC_SIGNER", "false")

    with pytest.raises(NotImplementedError, match="PQC signer requires MATRIZ integration"):
        pass


def test_pqc_signer_enabled_no_client(monkeypatch):
    """
    Verify that importing pqc_signer raises NotImplementedError if the client
    is not available when the flag is enabled.
    """
    monkeypatch.setenv("ENABLE_MATRIZ_PQC_SIGNER", "true")

    with pytest.raises(NotImplementedError, match="MATRIZ client not available"):
        pass


def test_pqc_signer_enabled_functions_raise_error(monkeypatch):
    """
    Verify that the functions in pqc_signer raise NotImplementedError when called,
    assuming the client is available but not implemented.
    """
    monkeypatch.setenv("ENABLE_MATRIZ_PQC_SIGNER", "true")
    # Mock the matriz_client to be importable
    mock_matriz_client = importlib.util.module_from_spec(importlib.util.spec_from_loader("matriz_client", loader=None))
    mock_matriz_client.PQCClient = object()  # Just need the attribute to exist
    sys.modules["matriz_client"] = mock_matriz_client

    from candidate.qi.crypto import pqc_signer

    with pytest.raises(NotImplementedError, match="MATRIZ client integration is not fully implemented yet."):
        pqc_signer.sign_message(b"test")

    with pytest.raises(NotImplementedError, match="MATRIZ client integration is not fully implemented yet."):
        pqc_signer.verify_signature(b"test", {})

    with pytest.warns(DeprecationWarning, match="sign_dilithium is deprecated"):
        with pytest.raises(NotImplementedError, match="MATRIZ client integration is not fully implemented yet."):
            pqc_signer.sign_dilithium(b"test")

    del sys.modules["matriz_client"]
