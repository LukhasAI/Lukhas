import pytest
from matriz.pqc_signer import PQCCheckpointSigner


@pytest.fixture
def signer():
    return PQCCheckpointSigner()

def test_sign_and_verify(signer):
    data = b"test data"
    signature = signer.sign_checkpoint(data)
    assert signer.verify_checkpoint(data, signature)

def test_verify_invalid_signature(signer):
    data = b"test data"
    signature = signer.sign_checkpoint(data)
    invalid_signature = b"a" * len(signature)
    assert not signer.verify_checkpoint(data, invalid_signature)
