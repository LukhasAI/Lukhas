#!/usr/bin/env python3
"""
TPM Simulation Fallback - Software-based Trusted Platform Module simulation
Provides cryptographic operations when hardware TPM is unavailable
"""

import base64
import hashlib
import json
import logging
import os
import secrets
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

logger = logging.getLogger(__name__)


@dataclass
class TPMKey:
    """Simulated TPM key"""

    key_id: str
    key_type: str  # rsa, aes
    created_at: datetime
    usage_count: int = 0
    last_used: Optional[datetime] = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TPMFallback:
    """
    Software TPM simulation for environments without hardware TPM
    Provides secure key storage and cryptographic operations
    """

    # Simulated TPM capabilities
    TPM_CAPABILITIES = {  # TODO[T4-ISSUE]: {"code":"RUF012","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Mutable class attribute needs ClassVar annotation for type safety","estimate":"15m","priority":"medium","dependencies":"typing imports","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_next_gen_security_tpm_fallback_py_L48"}
        "version": "2.0_simulation",
        "algorithms": ["RSA-2048", "AES-256", "SHA-256", "HMAC-SHA256"],
        "key_storage": "software_protected",
        "entropy_source": "os_random",
        "attestation": "simulated",
    }

    def __init__(
        self,
        keystore_path: str = "tpm_keystore.json",
        master_key_file: str = "tpm_master.key",
    ):
        self.keystore_path = Path(keystore_path)
        self.master_key_file = Path(master_key_file)
        self.keys: dict[str, TPMKey] = {}
        self.key_data: dict[str, bytes] = {}  # Encrypted key storage
        self.master_key: Optional[bytes] = None
        self.platform_measurements: dict[str, str] = {}

        # Initialize TPM simulation
        self._initialize_tpm()

        logger.info("🔐 TPM Fallback initialized")
        logger.info(f"   Keystore: {self.keystore_path}")
        logger.info(f"   Capabilities: {len(self.TPM_CAPABILITIES['algorithms'])} algorithms")

    def _initialize_tpm(self):
        """Initialize the simulated TPM"""
        # Load or create master key
        if self.master_key_file.exists():
            with open(self.master_key_file, "rb") as f:
                self.master_key = f.read()
        else:
            self.master_key = secrets.token_bytes(32)  # 256-bit master key
            with open(self.master_key_file, "wb") as f:
                f.write(self.master_key)
            os.chmod(self.master_key_file, 0o600)  # Secure permissions

        # Load keystore
        self._load_keystore()

        # Initialize platform measurements
        self._initialize_platform_measurements()

    def _load_keystore(self):
        """Load keystore from disk"""
        if self.keystore_path.exists():
            try:
                with open(self.keystore_path) as f:
                    data = json.load(f)

                # Load keys
                for key_id, key_info in data.get("keys", {}).items():
                    self.keys[key_id] = TPMKey(
                        key_id=key_info["key_id"],
                        key_type=key_info["key_type"],
                        created_at=datetime.fromisoformat(key_info["created_at"]),
                        usage_count=key_info.get("usage_count", 0),
                        last_used=(
                            datetime.fromisoformat(key_info["last_used"]) if key_info.get("last_used") else None
                        ),
                        metadata=key_info.get("metadata", {}),
                    )

                # Load encrypted key data
                for key_id, encrypted_data in data.get("key_data", {}).items():
                    self.key_data[key_id] = base64.b64decode(encrypted_data)

            except Exception as e:
                logger.warning(f"Could not load keystore: {e}")

    def _save_keystore(self):
        """Save keystore to disk"""
        data = {
            "version": "1.0.0",
            "tpm_simulation": True,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "keys": {},
            "key_data": {},
        }

        # Save key metadata
        for key_id, key in self.keys.items():
            data["keys"][key_id] = {
                "key_id": key.key_id,
                "key_type": key.key_type,
                "created_at": key.created_at.isoformat(),
                "usage_count": key.usage_count,
                "last_used": key.last_used.isoformat() if key.last_used else None,
                "metadata": key.metadata,
            }

        # Save encrypted key data
        for key_id, key_bytes in self.key_data.items():
            data["key_data"][key_id] = base64.b64encode(key_bytes).decode()

        with open(self.keystore_path, "w") as f:
            json.dump(data, f, indent=2)

    def _initialize_platform_measurements(self):
        """Initialize platform configuration measurements (PCRs)"""
        # Simulate PCR measurements
        self.platform_measurements = {
            "pcr_0": hashlib.sha256(b"bios_measurement").hexdigest(),
            "pcr_1": hashlib.sha256(b"boot_loader").hexdigest(),
            "pcr_2": hashlib.sha256(b"os_kernel").hexdigest(),
            "pcr_3": hashlib.sha256(b"application").hexdigest(),
            "pcr_7": hashlib.sha256(b"secure_boot").hexdigest(),
        }

    def _encrypt_key_data(self, key_data: bytes) -> bytes:
        """Encrypt key data with master key"""
        # Use AES-GCM for authenticated encryption
        iv = secrets.token_bytes(12)  # 96-bit IV for GCM
        cipher = Cipher(algorithms.AES(self.master_key), modes.GCM(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(key_data) + encryptor.finalize()

        # Return IV + tag + ciphertext
        return iv + encryptor.tag + ciphertext

    def _decrypt_key_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt key data with master key"""
        # Extract IV, tag, and ciphertext
        iv = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]

        cipher = Cipher(algorithms.AES(self.master_key), modes.GCM(iv, tag))
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()

    def create_rsa_key(self, key_id: str, key_size: int = 2048) -> bool:
        """Create RSA key pair"""
        if key_id in self.keys:
            logger.warning(f"Key {key_id} already exists")
            return False

        # Generate RSA key pair
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)

        # Serialize private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        # Encrypt and store
        encrypted_key = self._encrypt_key_data(private_pem)
        self.key_data[key_id] = encrypted_key

        # Create key metadata
        self.keys[key_id] = TPMKey(
            key_id=key_id,
            key_type="rsa",
            created_at=datetime.now(timezone.utc),
            metadata={"key_size": key_size, "algorithm": "RSA"},
        )

        self._save_keystore()
        logger.info(f"🔑 Created RSA key: {key_id}")
        return True

    def create_aes_key(self, key_id: str, key_size: int = 256) -> bool:
        """Create AES symmetric key"""
        if key_id in self.keys:
            logger.warning(f"Key {key_id} already exists")
            return False

        # Generate AES key
        aes_key = secrets.token_bytes(key_size // 8)

        # Encrypt and store
        encrypted_key = self._encrypt_key_data(aes_key)
        self.key_data[key_id] = encrypted_key

        # Create key metadata
        self.keys[key_id] = TPMKey(
            key_id=key_id,
            key_type="aes",
            created_at=datetime.now(timezone.utc),
            metadata={"key_size": key_size, "algorithm": "AES"},
        )

        self._save_keystore()
        logger.info(f"🔑 Created AES key: {key_id}")
        return True

    def sign_data(self, key_id: str, data: bytes) -> Optional[bytes]:
        """Sign data with RSA private key"""
        if key_id not in self.keys or self.keys[key_id].key_type != "rsa":
            logger.error(f"RSA key {key_id} not found")
            return None

        try:
            # Decrypt private key
            encrypted_key = self.key_data[key_id]
            private_pem = self._decrypt_key_data(encrypted_key)

            # Load private key
            private_key = serialization.load_pem_private_key(private_pem, password=None)

            # Sign data
            signature = private_key.sign(
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )

            # Update usage statistics
            self.keys[key_id].usage_count += 1
            self.keys[key_id].last_used = datetime.now(timezone.utc)
            self._save_keystore()

            return signature

        except Exception as e:
            logger.error(f"Failed to sign data: {e}")
            return None

    def verify_signature(self, key_id: str, data: bytes, signature: bytes) -> bool:
        """Verify signature with RSA public key"""
        if key_id not in self.keys or self.keys[key_id].key_type != "rsa":
            logger.error(f"RSA key {key_id} not found")
            return False

        try:
            # Decrypt private key and extract public key
            encrypted_key = self.key_data[key_id]
            private_pem = self._decrypt_key_data(encrypted_key)
            private_key = serialization.load_pem_private_key(private_pem, password=None)
            public_key = private_key.public_key()

            # Verify signature
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )

            return True

        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False

    def encrypt_data(self, key_id: str, data: bytes) -> Optional[bytes]:
        """Encrypt data with AES key"""
        if key_id not in self.keys or self.keys[key_id].key_type != "aes":
            logger.error(f"AES key {key_id} not found")
            return None

        try:
            # Decrypt AES key
            encrypted_key = self.key_data[key_id]
            aes_key = self._decrypt_key_data(encrypted_key)

            # Encrypt data
            iv = secrets.token_bytes(12)
            cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv))
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(data) + encryptor.finalize()

            # Update usage statistics
            self.keys[key_id].usage_count += 1
            self.keys[key_id].last_used = datetime.now(timezone.utc)
            self._save_keystore()

            # Return IV + tag + ciphertext
            return iv + encryptor.tag + ciphertext

        except Exception as e:
            logger.error(f"Failed to encrypt data: {e}")
            return None

    def decrypt_data(self, key_id: str, encrypted_data: bytes) -> Optional[bytes]:
        """Decrypt data with AES key"""
        if key_id not in self.keys or self.keys[key_id].key_type != "aes":
            logger.error(f"AES key {key_id} not found")
            return None

        try:
            # Decrypt AES key
            encrypted_key = self.key_data[key_id]
            aes_key = self._decrypt_key_data(encrypted_key)

            # Extract IV, tag, and ciphertext
            iv = encrypted_data[:12]
            tag = encrypted_data[12:28]
            ciphertext = encrypted_data[28:]

            # Decrypt data
            cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv, tag))
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            return plaintext

        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            return None

    def get_platform_measurements(self) -> dict[str, str]:
        """Get platform configuration measurements"""
        return self.platform_measurements.copy()

    def attest_platform(self, nonce: bytes) -> dict[str, Any]:
        """Generate platform attestation (simulated)"""
        # Create attestation data
        attestation_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "nonce": base64.b64encode(nonce).decode(),
            "platform_measurements": self.platform_measurements,
            "tpm_capabilities": self.TPM_CAPABILITIES,
            "simulation_mode": True,
        }

        # Sign attestation with a platform key (create if needed)
        platform_key_id = "platform_attestation_key"
        if platform_key_id not in self.keys:
            self.create_rsa_key(platform_key_id)

        attestation_json = json.dumps(attestation_data, sort_keys=True)
        signature = self.sign_data(platform_key_id, attestation_json.encode())

        return {
            "attestation": attestation_data,
            "signature": base64.b64encode(signature).decode() if signature else None,
            "signing_key": platform_key_id,
        }

    def get_key_info(self, key_id: str) -> Optional[dict]:
        """Get key information"""
        if key_id not in self.keys:
            return None

        return asdict(self.keys[key_id])

    def list_keys(self) -> list[dict]:
        """List all keys"""
        return [asdict(key) for key in self.keys.values()]

    def delete_key(self, key_id: str) -> bool:
        """Delete a key"""
        if key_id not in self.keys:
            return False

        del self.keys[key_id]
        if key_id in self.key_data:
            del self.key_data[key_id]

        self._save_keystore()
        logger.info(f"🗑️ Deleted key: {key_id}")
        return True

    def get_random_bytes(self, length: int) -> bytes:
        """Generate cryptographically secure random bytes"""
        return secrets.token_bytes(length)

    def health_check(self) -> dict[str, Any]:
        """Perform TPM health check"""
        total_keys = len(self.keys)
        active_keys = sum(1 for k in self.keys.values() if k.usage_count > 0)

        return {
            "status": "healthy",
            "simulation_mode": True,
            "total_keys": total_keys,
            "active_keys": active_keys,
            "master_key_status": "present" if self.master_key else "missing",
            "keystore_size": (self.keystore_path.stat().st_size if self.keystore_path.exists() else 0),
            "platform_measurements": len(self.platform_measurements),
            "capabilities": self.TPM_CAPABILITIES,
        }


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    # Create TPM simulation
    tpm = TPMFallback(keystore_path="demo_tpm.json", master_key_file="demo_master.key")

    print("🔐 TPM Fallback Demo")
    print("=" * 60)

    # Create keys
    print("\n🔑 Creating keys...")
    tpm.create_rsa_key("test_rsa", 2048)
    tpm.create_aes_key("test_aes", 256)

    # Test signing
    print("\n✍️ Testing RSA signing...")
    test_data = b"LUKHAS TPM test data"
    signature = tpm.sign_data("test_rsa", test_data)
    if signature:
        print(f"   Signature length: {len(signature)} bytes")

        # Verify signature
        verified = tpm.verify_signature("test_rsa", test_data, signature)
        print(f"   Verification: {'✅ PASS' if verified else '❌ FAIL'}")

    # Test encryption
    print("\n🔒 Testing AES encryption...")
    encrypted = tpm.encrypt_data("test_aes", test_data)
    if encrypted:
        print(f"   Encrypted length: {len(encrypted)} bytes")

        # Decrypt
        decrypted = tpm.decrypt_data("test_aes", encrypted)
        if decrypted:
            print(f"   Decryption: {'✅ PASS' if decrypted == test_data else '❌ FAIL'}")

    # Platform attestation
    print("\n🛡️ Testing platform attestation...")
    nonce = tpm.get_random_bytes(32)
    attestation = tpm.attest_platform(nonce)
    print(f"   Attestation includes {len(attestation['attestation']['platform_measurements'])} PCR values")
    print(f"   Signed: {'✅ YES' if attestation['signature'] else '❌ NO'}")

    # Health check
    print("\n📊 TPM Health Check:")
    health = tpm.health_check()
    for key, value in health.items():
        print(f"   {key}: {value}")

    # Cleanup demo files
    import os

    try:
        os.unlink("demo_tpm.json")
        os.unlink("demo_master.key")
    except BaseException:
        pass
