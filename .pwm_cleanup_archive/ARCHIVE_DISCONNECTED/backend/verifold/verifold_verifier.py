"""
verifold_verifier.py

Verifies the authenticity of a symbolic Verifold hash using post-quantum SPHINCS+ signatures.

Requirements:
- pip install oqs

Author: LUKHAS AGI Core
"""

import binascii

import oqs


def verify_verifold_signature(
    verifold_hash: str, signature_hex: str, public_key_hex: str
) -> bool:
    """
    Verifies a SPHINCS+ digital signature for a given Verifold hash.

    Parameters:
        verifold_hash (str): The original hash (hex string) generated at collapse time.
        signature_hex (str): The SPHINCS+ digital signature (hex).
        public_key_hex (str): The public key used to verify the signature (hex).

    Returns:
        bool: True if the signature is valid, False otherwise.
    """
    signature = binascii.unhexlify(signature_hex)
    public_key = binascii.unhexlify(public_key_hex)

    with oqs.Signature("SPHINCS+-SHAKE256-128f-simple") as verifier:
        verifier.set_public_key(public_key)
        return verifier.verify(verifold_hash.encode(), signature)


# 🧪 Example usage
if __name__ == "__main__":
    sample = {
        "verifold_hash": "4c8a9d8c0eeb292aa65efb59e98de9a6a9990a563fce14a5f89de38b26a17a3c",
        "signature": "e54c....",  # Replace with real hex signature
        "public_key": "a1b2...",  # Replace with real hex public key
    }

    is_valid = verify_verifold_signature(
        sample["verifold_hash"], sample["signature"], sample["public_key"]
    )

    print("✅ Signature valid." if is_valid else "❌ Signature INVALID.")
