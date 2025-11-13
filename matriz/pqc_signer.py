from oqs import Signature


class PQCCheckpointSigner:
    def __init__(self):
        self.sig = Signature('Dilithium2')
        self.public_key = self.sig.generate_keypair()

    def sign_checkpoint(self, checkpoint_data: bytes) -> bytes:
        '''Sign checkpoint with Dilithium2'''
        return self.sig.sign(checkpoint_data)

    def verify_checkpoint(self, checkpoint_data: bytes, signature: bytes) -> bool:
        '''Verify Dilithium2 signature'''
        return self.sig.verify(checkpoint_data, signature, self.public_key)
