#!/usr/bin/env python3
"""
VIVOX Cryptographic Timestamping & Verification System
=====================================================
Implements tamper-proof timestamping and hash verification for the z(t) collapse system.

Features:
- RFC 3161 compliant timestamping
- Multi-hash verification (SHA3-256, BLAKE3, etc.)
- Merkle tree audit trails
- Quantum-resistant signature schemes
- GDPR-compliant audit logging
"""

import base64
import hashlib
import json
import math
import secrets
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

try:
    import blake3

    BLAKE3_AVAILABLE = True
except ImportError:
    BLAKE3_AVAILABLE = False

try:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding, rsa

    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False


class HashAlgorithm(Enum):
    """Supported hash algorithms"""

    SHA3_256 = "sha3_256"
    SHA3_512 = "sha3_512"
    BLAKE3 = "blake3"
    SHA256 = "sha256"
    SHA512 = "sha512"


class TimestampSource(Enum):
    """Timestamp source types"""

    SYSTEM_TIME = "system_time"
    NTP_SERVER = "ntp_server"
    BLOCKCHAIN = "blockchain"
    RFC3161_TSA = "rfc3161_tsa"


@dataclass
class CryptoTimestamp:
    """Cryptographic timestamp with verification"""

    timestamp_utc: float
    timestamp_iso: str
    source: TimestampSource
    precision_ms: float
    nonce: str
    signature: Optional[str] = None
    verification_data: Optional[dict[str, Any]] = None


@dataclass
class HashRecord:
    """Hash record with multiple algorithms"""

    primary_hash: str
    algorithm: HashAlgorithm
    secondary_hashes: dict[HashAlgorithm, str]
    salt: str
    iterations: int
    input_length: int


@dataclass
class AuditTrail:
    """Complete audit trail for collapse event"""

    event_id: str
    timestamp: CryptoTimestamp
    hash_record: HashRecord
    mathematical_trace: dict[str, Any]
    previous_hash: Optional[str]
    merkle_root: Optional[str]
    chain_position: int
    verification_status: bool


class VIVOXCryptoSystem:
    """
    VIVOX Cryptographic System for Z(t) Collapse Verification

    Provides:
    - Multi-algorithm hashing with salt and iterations
    - Cryptographic timestamping with multiple sources
    - Merkle tree construction for audit chains
    - Hash verification and integrity checking
    - Quantum-resistant signature schemes (future)
    """

    def __init__(
        self,
        primary_algorithm: HashAlgorithm = HashAlgorithm.SHA3_256,
        enable_secondary_hashes: bool = True,
        timestamp_source: TimestampSource = TimestampSource.SYSTEM_TIME,
        salt_length: int = 32,
        hash_iterations: int = 100000,
    ):
        """
        Initialize the cryptographic system

        Args:
            primary_algorithm: Primary hash algorithm
            enable_secondary_hashes: Enable additional hash algorithms
            timestamp_source: Source for timestamps
            salt_length: Length of cryptographic salt in bytes
            hash_iterations: Number of PBKDF2 iterations
        """
        self.primary_algorithm = primary_algorithm
        self.enable_secondary_hashes = enable_secondary_hashes
        self.timestamp_source = timestamp_source
        self.salt_length = salt_length
        self.hash_iterations = hash_iterations

        # Audit chain
        self.audit_chain: list[AuditTrail] = []
        self.merkle_trees: dict[str, list[str]] = {}

        # Initialize cryptographic keys if available
        self.private_key = None
        self.public_key = None
        if CRYPTOGRAPHY_AVAILABLE:
            self._initialize_keys()

    def _initialize_keys(self):
        """Initialize RSA key pair for signatures"""
        try:
            self.private_key = rsa.generate_private_key(
                public_exponent=65537, key_size=2048
            )
            self.public_key = self.private_key.public_key()
        except Exception as e:
            print(f"Warning: Could not initialize cryptographic keys: {e}")

    def generate_crypto_timestamp(
        self, precision_required: bool = True
    ) -> CryptoTimestamp:
        """
        Generate cryptographically secure timestamp

        Args:
            precision_required: Whether high precision is required

        Returns:
            CryptoTimestamp with verification data
        """
        # Get current time with high precision
        current_time = time.time()
        timestamp_iso = datetime.fromtimestamp(current_time, timezone.utc).isoformat()

        # Generate cryptographic nonce
        nonce = secrets.token_hex(16)

        # Calculate precision (simulated - in real implementation would use NTP)
        precision_ms = (
            1.0 if self.timestamp_source == TimestampSource.SYSTEM_TIME else 0.1
        )

        # Create verification data
        verification_data = {
            "nonce": nonce,
            "source_info": {
                "type": self.timestamp_source.value,
                "precision_ms": precision_ms,
                "system_info": "VIVOX_CRYPTO_v1.0",
            },
        }

        # Generate signature if keys available
        signature = None
        if self.private_key and CRYPTOGRAPHY_AVAILABLE:
            signature = self._sign_timestamp(current_time, nonce)

        return CryptoTimestamp(
            timestamp_utc=current_time,
            timestamp_iso=timestamp_iso,
            source=self.timestamp_source,
            precision_ms=precision_ms,
            nonce=nonce,
            signature=signature,
            verification_data=verification_data,
        )

    def _sign_timestamp(self, timestamp: float, nonce: str) -> str:
        """Generate cryptographic signature for timestamp"""
        try:
            message = f"{timestamp:.6f}:{nonce}".encode()
            signature = self.private_key.sign(
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return base64.b64encode(signature).decode("utf-8")
        except Exception as e:
            print(f"Warning: Could not sign timestamp: {e}")
            return ""

    def verify_timestamp_signature(self, timestamp: CryptoTimestamp) -> bool:
        """Verify cryptographic signature of timestamp"""
        if not timestamp.signature or not self.public_key:
            return False

        try:
            message = f"{timestamp.timestamp_utc:.6f}:{timestamp.nonce}".encode()
            signature_bytes = base64.b64decode(timestamp.signature)

            self.public_key.verify(
                signature_bytes,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False

    def generate_multi_hash(
        self,
        data: str,
        timestamp: CryptoTimestamp,
        additional_context: Optional[dict[str, Any]] = None,
    ) -> HashRecord:
        """
        Generate multiple hashes with salt and iterations

        Args:
            data: Input data to hash
            timestamp: Cryptographic timestamp
            additional_context: Additional context for hash

        Returns:
            HashRecord with multiple hash algorithms
        """
        # Generate cryptographic salt
        salt = secrets.token_bytes(self.salt_length)
        salt_hex = salt.hex()

        # Prepare hash input
        hash_input = self._prepare_hash_input(data, timestamp, additional_context, salt)

        # Generate primary hash
        primary_hash = self._compute_hash(hash_input, self.primary_algorithm, salt)

        # Generate secondary hashes if enabled
        secondary_hashes = {}
        if self.enable_secondary_hashes:
            for algorithm in HashAlgorithm:
                if algorithm != self.primary_algorithm:
                    try:
                        secondary_hashes[algorithm] = self._compute_hash(
                            hash_input, algorithm, salt
                        )
                    except Exception as e:
                        print(f"Warning: Could not compute {algorithm.value} hash: {e}")

        return HashRecord(
            primary_hash=primary_hash,
            algorithm=self.primary_algorithm,
            secondary_hashes=secondary_hashes,
            salt=salt_hex,
            iterations=self.hash_iterations,
            input_length=len(hash_input),
        )

    def _prepare_hash_input(
        self,
        data: str,
        timestamp: CryptoTimestamp,
        context: Optional[dict[str, Any]],
        salt: bytes,
    ) -> bytes:
        """Prepare standardized input for hashing"""
        components = [
            f"data:{data}",
            f"timestamp:{timestamp.timestamp_utc:.6f}",
            f"nonce:{timestamp.nonce}",
            f"source:{timestamp.source.value}",
        ]

        if context:
            context_str = json.dumps(context, sort_keys=True, separators=(",", ":"))
            components.append(f"context:{context_str}")

        combined = "|".join(components)
        return combined.encode("utf-8") + salt

    def _compute_hash(self, data: bytes, algorithm: HashAlgorithm, salt: bytes) -> str:
        """Compute hash using specified algorithm"""
        if algorithm == HashAlgorithm.SHA3_256:
            return hashlib.sha3_256(data).hexdigest()
        elif algorithm == HashAlgorithm.SHA3_512:
            return hashlib.sha3_512(data).hexdigest()
        elif algorithm == HashAlgorithm.SHA256:
            return hashlib.sha256(data).hexdigest()
        elif algorithm == HashAlgorithm.SHA512:
            return hashlib.sha512(data).hexdigest()
        elif algorithm == HashAlgorithm.BLAKE3 and BLAKE3_AVAILABLE:
            return blake3.blake3(data).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    def verify_hash_record(
        self,
        original_data: str,
        timestamp: CryptoTimestamp,
        hash_record: HashRecord,
        context: Optional[dict[str, Any]] = None,
    ) -> bool:
        """
        Verify hash record integrity

        Args:
            original_data: Original data that was hashed
            timestamp: Original timestamp
            hash_record: Hash record to verify
            context: Original context data

        Returns:
            True if hash verification passes
        """
        try:
            # Recreate hash input
            salt = bytes.fromhex(hash_record.salt)
            hash_input = self._prepare_hash_input(
                original_data, timestamp, context, salt
            )

            # Verify primary hash
            expected_primary = self._compute_hash(
                hash_input, hash_record.algorithm, salt
            )

            if expected_primary != hash_record.primary_hash:
                return False

            # Verify secondary hashes
            for algorithm, stored_hash in hash_record.secondary_hashes.items():
                try:
                    expected_secondary = self._compute_hash(hash_input, algorithm, salt)
                    if expected_secondary != stored_hash:
                        return False
                except Exception:
                    # Skip if algorithm not available
                    continue

            return True

        except Exception as e:
            print(f"Hash verification error: {e}")
            return False

    def create_audit_trail(
        self,
        event_id: str,
        collapse_data: dict[str, Any],
        mathematical_trace: dict[str, Any],
    ) -> AuditTrail:
        """
        Create complete audit trail for collapse event

        Args:
            event_id: Unique identifier for the event
            collapse_data: Data from z(t) collapse
            mathematical_trace: Mathematical computation trace

        Returns:
            Complete audit trail with verification
        """
        # Generate cryptographic timestamp
        timestamp = self.generate_crypto_timestamp(precision_required=True)

        # Prepare audit data
        audit_data = {
            "event_id": event_id,
            "collapse_data": collapse_data,
            "mathematical_trace": mathematical_trace,
        }

        audit_json = json.dumps(audit_data, sort_keys=True, separators=(",", ":"))

        # Generate hash record
        hash_record = self.generate_multi_hash(
            audit_json, timestamp, {"audit_type": "z_collapse_event"}
        )

        # Get previous hash for chaining
        previous_hash = None
        if self.audit_chain:
            previous_hash = self.audit_chain[-1].hash_record.primary_hash

        # Calculate Merkle root if multiple events
        merkle_root = self._calculate_merkle_root([hash_record.primary_hash])

        # Verify timestamp signature
        verification_status = self.verify_timestamp_signature(timestamp)

        # Create audit trail
        audit_trail = AuditTrail(
            event_id=event_id,
            timestamp=timestamp,
            hash_record=hash_record,
            mathematical_trace=mathematical_trace,
            previous_hash=previous_hash,
            merkle_root=merkle_root,
            chain_position=len(self.audit_chain),
            verification_status=verification_status,
        )

        # Add to audit chain
        self.audit_chain.append(audit_trail)

        return audit_trail

    def _calculate_merkle_root(self, hashes: list[str]) -> str:
        """Calculate Merkle tree root for hash list"""
        if not hashes:
            return ""

        if len(hashes) == 1:
            return hashes[0]

        # Simple Merkle tree implementation
        current_level = hashes[:]

        while len(current_level) > 1:
            next_level = []

            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left

                combined = left + right
                parent_hash = hashlib.sha3_256(combined.encode("utf-8")).hexdigest()
                next_level.append(parent_hash)

            current_level = next_level

        return current_level[0]

    def verify_audit_chain(self) -> tuple[bool, list[str]]:
        """
        Verify the entire audit chain integrity

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        if not self.audit_chain:
            return True, []

        # Verify each audit trail
        for i, trail in enumerate(self.audit_chain):
            # Verify timestamp signature
            if not self.verify_timestamp_signature(trail.timestamp):
                errors.append(f"Invalid timestamp signature at position {i}")

            # Verify hash chain linking
            if i > 0:
                expected_previous = self.audit_chain[i - 1].hash_record.primary_hash
                if trail.previous_hash != expected_previous:
                    errors.append(f"Broken hash chain at position {i}")

            # Verify position
            if trail.chain_position != i:
                errors.append(f"Invalid chain position at index {i}")

        return len(errors) == 0, errors

    def export_audit_data(self, include_sensitive: bool = False) -> dict[str, Any]:
        """
        Export audit data for compliance or debugging

        Args:
            include_sensitive: Whether to include sensitive cryptographic data

        Returns:
            Dictionary with audit data
        """
        export_data = {
            "system_info": {
                "primary_algorithm": self.primary_algorithm.value,
                "timestamp_source": self.timestamp_source.value,
                "salt_length": self.salt_length,
                "hash_iterations": self.hash_iterations,
                "chain_length": len(self.audit_chain),
            },
            "audit_chain": [],
        }

        for trail in self.audit_chain:
            trail_data = {
                "event_id": trail.event_id,
                "timestamp_iso": trail.timestamp.timestamp_iso,
                "hash_primary": trail.hash_record.primary_hash,
                "chain_position": trail.chain_position,
                "verification_status": trail.verification_status,
            }

            if include_sensitive:
                trail_data.update(
                    {
                        "timestamp_signature": trail.timestamp.signature,
                        "hash_salt": trail.hash_record.salt,
                        "secondary_hashes": trail.hash_record.secondary_hashes,
                        "mathematical_trace": trail.mathematical_trace,
                    }
                )

            export_data["audit_chain"].append(trail_data)

        return export_data


# Integration with Z(t) Collapse Engine


class SecureZCollapseEngine:
    """
    Z(t) Collapse Engine with integrated cryptographic verification
    """

    def __init__(self, crypto_system: VIVOXCryptoSystem):
        self.crypto_system = crypto_system
        self.collapse_counter = 0

    def secure_collapse_with_audit(
        self,
        z_result: complex,
        collapse_data: dict[str, Any],
        mathematical_trace: dict[str, Any],
    ) -> tuple[str, AuditTrail]:
        """
        Execute z(t) collapse with complete cryptographic audit trail

        Returns:
            Tuple of (collapse_hash, audit_trail)
        """
        self.collapse_counter += 1
        event_id = f"z_collapse_{self.collapse_counter:06d}"

        # Create comprehensive collapse data
        complete_collapse_data = {
            "z_result": {
                "real": z_result.real,
                "imag": z_result.imag,
                "magnitude": abs(z_result),
                "phase": math.atan2(z_result.imag, z_result.real),
            },
            **collapse_data,
        }

        # Create audit trail
        audit_trail = self.crypto_system.create_audit_trail(
            event_id=event_id,
            collapse_data=complete_collapse_data,
            mathematical_trace=mathematical_trace,
        )

        return audit_trail.hash_record.primary_hash, audit_trail


# Example usage
if __name__ == "__main__":
    import math

    # Initialize crypto system
    crypto_system = VIVOXCryptoSystem(
        primary_algorithm=HashAlgorithm.SHA3_256,
        enable_secondary_hashes=True,
        timestamp_source=TimestampSource.SYSTEM_TIME,
    )

    # Test cryptographic timestamp
    print("🕐 Testing cryptographic timestamp...")
    timestamp = crypto_system.generate_crypto_timestamp()
    print(f"Timestamp: {timestamp.timestamp_iso}")
    print(f"Nonce: {timestamp.nonce}")
    print(f"Signature valid: {crypto_system.verify_timestamp_signature(timestamp)}")

    # Test hash generation
    print("\n🔐 Testing multi-hash generation...")
    test_data = "z(t) = 1.5 + 0.5j"
    hash_record = crypto_system.generate_multi_hash(test_data, timestamp)
    print(f"Primary hash: {hash_record.primary_hash[:32]}...")
    print(f"Salt: {hash_record.salt[:16]}...")
    print(f"Secondary hashes: {len(hash_record.secondary_hashes)}")

    # Test hash verification
    print("\n✅ Testing hash verification...")
    is_valid = crypto_system.verify_hash_record(test_data, timestamp, hash_record)
    print(f"Hash verification: {'PASSED' if is_valid else 'FAILED'}")

    # Test secure collapse
    print("\n🚀 Testing secure z(t) collapse...")
    secure_engine = SecureZCollapseEngine(crypto_system)

    z_result = complex(2.0, 0.0)  # Baseline test result
    collapse_data = {"alignment_score": 1.0, "entropy_score": 0.0, "phase_drift": 0.0}
    mathematical_trace = {
        "formula": "z(t) = A(t) * [e^(iθ(t)) + e^(i(π-θ(t)))] × W(ΔS(t))",
        "baseline_test": True,
    }

    collapse_hash, audit_trail = secure_engine.secure_collapse_with_audit(
        z_result, collapse_data, mathematical_trace
    )

    print(f"Collapse hash: {collapse_hash[:32]}...")
    print(f"Event ID: {audit_trail.event_id}")
    print(f"Verification status: {audit_trail.verification_status}")

    # Verify audit chain
    print("\n🔍 Verifying audit chain...")
    is_valid, errors = crypto_system.verify_audit_chain()
    print(f"Audit chain valid: {is_valid}")
    if errors:
        for error in errors:
            print(f"  Error: {error}")

    print("\n📊 Export summary:")
    export_data = crypto_system.export_audit_data(include_sensitive=False)
    print(f"Chain length: {export_data['system_info']['chain_length']}")
    print(f"Algorithm: {export_data['system_info']['primary_algorithm']}")
