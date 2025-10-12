"""
Bridge API - QRS Manager Implementation

Quantum Response Signature (QRS) manager for cryptographic response verification.

Part of BATCH-JULES-API-GOVERNANCE-02
Task: TODO-HIGH-BRIDGE-API-k7l8m9n0

Trinity Framework:
- 🧠 Consciousness: Response integrity verification
- 🛡️ Guardian: Cryptographic audit trails
- ⚛️ Identity: Service authentication
"""

import hashlib
import hmac
import secrets
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class QRSAlgorithm(Enum):
    """Supported QRS hash algorithms."""
    SHA256_QRS = "SHA256-QRS"
    SHA512_QRS = "SHA512-QRS"
    # Aliases for test compatibility
    SHA256 = "SHA256"
    SHA512 = "SHA512"


class QRSStatus(Enum):
    """QRS verification status."""
    VALID = "valid"
    INVALID = "invalid"
    TAMPERED = "tampered"
    EXPIRED = "expired"
    UNKNOWN_ALGORITHM = "unknown_algorithm"
    INVALID_FORMAT = "invalid_format"


@dataclass
class QRSSignature:
    """Quantum Response Signature data structure."""
    qrs_id: str
    signature: str
    hash: str
    algorithm: str
    created_at: int
    request_id: str
    service: str
    nonce: str = field(default_factory=lambda: secrets.token_hex(16))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class QRSVerificationResult:
    """Result of QRS verification."""
    valid: bool
    status: QRSStatus
    qrs_id: str
    verified_at: Optional[int] = None
    reason: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result['status'] = self.status.value
        return result


class QRSManager:
    """
    Quantum Response Signature Manager
    
    Provides cryptographic signing and verification for API responses using
    quantum-inspired signature algorithms.
    
    Features:
    - SHA256/SHA512 cryptographic hashing
    - Timestamp-based uniqueness
    - Tamper detection
    - ΛTRACE audit integration
    
    Trinity Integration:
    - 🧠 Consciousness: Response integrity verification
    - 🛡️ Guardian: Constitutional AI validation
    - ⚛️ Identity: Service authentication
    """

    # Configuration
    MAX_PAYLOAD_SIZE = 10 * 1024 * 1024  # 10MB limit
    TIMESTAMP_TOLERANCE = 300  # 5 minutes tolerance for timestamp validation
    DEFAULT_TTL = 3600  # 1 hour default TTL for signatures

    def __init__(
        self,
        secret_key: Optional[str] = None,
        default_algorithm: QRSAlgorithm = QRSAlgorithm.SHA256_QRS,
        trace_logger: Optional[Any] = None
    ):
        """
        Initialize QRS Manager.
        
        Args:
            secret_key: Secret key for HMAC signature generation (optional)
            default_algorithm: Default hash algorithm to use
            trace_logger: Optional ΛTRACE logger for audit trails
        """
        self.secret_key = secret_key or "default_qrs_secret"
        self.default_algorithm = default_algorithm
        self.trace_logger = trace_logger
        
        # Statistics for monitoring
        self._stats = {
            'created': 0,
            'verified': 0,
            'failed': 0,
            'tampered_detected': 0
        }
        
        # Nonce tracking for replay prevention
        self._used_nonces: set = set()
        
        # Audit trail storage
        self._audit_trail: List[Dict[str, Any]] = []
        
        # Rate limit configuration (requests per minute by tier)
        self._rate_limits = {
            "alpha": 300,   # 3x multiplier
            "beta": 200,    # 2x multiplier
            "gamma": 150,   # 1.5x multiplier
            "delta": 100    # 1x multiplier (baseline)
        }

    async def create_qrs(
        self,
        data: Dict[str, Any],
        algorithm: Optional[QRSAlgorithm] = None,
        ttl: Optional[int] = None
    ) -> QRSSignature:
        """
        Create a Quantum Response Signature for given data.
        
        Args:
            data: Dictionary containing:
                - request_id: Unique request identifier
                - response_payload: Response data to sign
                - timestamp: Request timestamp
                - service: Service identifier
            algorithm: Hash algorithm to use (defaults to SHA256-QRS)
            ttl: Time-to-live in seconds (defaults to 1 hour)
        
        Returns:
            QRSSignature object
        
        Raises:
            ValueError: If required fields missing or invalid data
        
        Task: TODO-HIGH-BRIDGE-API-k7l8m9n0 (QRS manager logic)
        """
        # Validate required fields
        required_fields = ['request_id', 'response_payload', 'timestamp', 'service']
        missing = [f for f in required_fields if f not in data]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
        
        # Validate timestamp
        current_time = int(time.time())
        request_timestamp = int(data['timestamp'])
        
        if request_timestamp > current_time + self.TIMESTAMP_TOLERANCE:
            raise ValueError(f"Invalid timestamp: Request timestamp is in the future")
        
        # Validate payload size
        payload_str = str(data['response_payload'])
        if len(payload_str.encode('utf-8')) > self.MAX_PAYLOAD_SIZE:
            raise ValueError(f"Response payload exceeds maximum size of {self.MAX_PAYLOAD_SIZE} bytes")
        
        # Select algorithm
        algo = algorithm or self.default_algorithm
        
        # Generate nonce for uniqueness
        nonce = secrets.token_hex(16)
        
        # Create hash
        hash_value = self._compute_hash(
            request_id=data['request_id'],
            response_payload=data['response_payload'],
            timestamp=request_timestamp,
            service=data['service'],
            nonce=nonce,
            algorithm=algo
        )
        
        # Generate QRS ID
        qrs_id = f"qrs_{secrets.token_hex(12)}"
        
        # Create signature (simplified - real implementation would use asymmetric crypto)
        signature = f"0x{hashlib.sha256(f'{hash_value}{nonce}'.encode()).hexdigest()}"
        
        # Create QRS signature object
        created_at = int(time.time())
        qrs = QRSSignature(
            qrs_id=qrs_id,
            signature=signature,
            hash=hash_value,
            algorithm=algo.value,
            created_at=created_at,
            request_id=data['request_id'],
            service=data['service'],
            nonce=nonce,
            metadata={
                'ttl': ttl or self.DEFAULT_TTL,
                'expires_at': created_at + (ttl or self.DEFAULT_TTL),
                'payload_size': len(payload_str)
            }
        )
        
        # Update statistics
        self._stats['created'] += 1
        
        # Log to ΛTRACE if available
        if self.trace_logger:
            await self._log_qrs_creation(qrs, data)
        
        return qrs

    async def verify_qrs(
        self,
        qrs_data: Dict[str, Any],
        original_data: Optional[Dict[str, Any]] = None
    ) -> QRSVerificationResult:
        """
        Verify a Quantum Response Signature.
        
        Args:
            qrs_data: QRS signature data to verify
            original_data: Optional original request data for verification
        
        Returns:
            QRSVerificationResult with verification status
        
        Task: TODO-HIGH-BRIDGE-API-k7l8m9n0 (QRS manager logic)
        """
        verified_at = int(time.time())
        
        # Validate QRS format
        required = ['qrs_id', 'signature', 'hash', 'algorithm']
        missing = [f for f in required if f not in qrs_data]
        if missing:
            self._stats['failed'] += 1
            return QRSVerificationResult(
                valid=False,
                status=QRSStatus.INVALID_FORMAT,
                qrs_id=qrs_data.get('qrs_id', 'unknown'),
                verified_at=verified_at,
                reason=f"Missing required fields: {', '.join(missing)}"
            )
        
        # Check algorithm support
        algorithm_str = qrs_data['algorithm']
        try:
            algorithm = QRSAlgorithm(algorithm_str)
        except ValueError:
            self._stats['failed'] += 1
            return QRSVerificationResult(
                valid=False,
                status=QRSStatus.UNKNOWN_ALGORITHM,
                qrs_id=qrs_data['qrs_id'],
                verified_at=verified_at,
                reason=f"Unsupported algorithm: {algorithm_str}"
            )
        
        # Check expiration if metadata available
        if 'metadata' in qrs_data and 'expires_at' in qrs_data['metadata']:
            if verified_at > qrs_data['metadata']['expires_at']:
                self._stats['failed'] += 1
                return QRSVerificationResult(
                    valid=False,
                    status=QRSStatus.EXPIRED,
                    qrs_id=qrs_data['qrs_id'],
                    verified_at=verified_at,
                    reason="QRS signature has expired"
                )
        
        # Verify signature integrity
        hash_value = qrs_data["hash"]
        nonce_value = qrs_data.get("nonce", "")
        signature_data = f"{hash_value}{nonce_value}"
        expected_signature = f"0x{hashlib.sha256(signature_data.encode()).hexdigest()}"
        
        if qrs_data['signature'] != expected_signature:
            self._stats['tampered_detected'] += 1
            return QRSVerificationResult(
                valid=False,
                status=QRSStatus.TAMPERED,
                qrs_id=qrs_data['qrs_id'],
                verified_at=verified_at,
                reason="Signature does not match - possible tampering detected"
            )
        
        # If original data provided, verify hash
        if original_data:
            expected_hash = self._compute_hash(
                request_id=original_data.get('request_id', ''),
                response_payload=original_data.get('response_payload', {}),
                timestamp=original_data.get('timestamp', 0),
                service=original_data.get('service', ''),
                nonce=qrs_data.get('nonce', ''),
                algorithm=algorithm
            )
            
            if qrs_data['hash'] != expected_hash:
                self._stats['tampered_detected'] += 1
                return QRSVerificationResult(
                    valid=False,
                    status=QRSStatus.TAMPERED,
                    qrs_id=qrs_data['qrs_id'],
                    verified_at=verified_at,
                    reason="Hash does not match original data - tampering detected"
                )
        
        # Signature is valid
        self._stats['verified'] += 1
        
        # Log to ΛTRACE if available
        if self.trace_logger:
            await self._log_qrs_verification(qrs_data, True)
        
        return QRSVerificationResult(
            valid=True,
            status=QRSStatus.VALID,
            qrs_id=qrs_data['qrs_id'],
            verified_at=verified_at,
            details={
                'algorithm': algorithm_str,
                'service': qrs_data.get('service', 'unknown')
            }
        )

    async def batch_verify(
        self,
        qrs_list: List[Dict[str, Any]]
    ) -> List[QRSVerificationResult]:
        """
        Verify multiple QRS signatures in batch.
        
        Args:
            qrs_list: List of QRS signature data dictionaries
        
        Returns:
            List of QRSVerificationResult objects
        
        Task: TODO-HIGH-BRIDGE-API-k7l8m9n0 (QRS manager logic)
        """
        results = []
        for qrs_data in qrs_list:
            result = await self.verify_qrs(qrs_data)
            results.append(result)
        return results

    def get_stats(self) -> Dict[str, int]:
        """
        Get QRS manager statistics.
        
        Returns:
            Dictionary with creation/verification statistics
        """
        return self._stats.copy()

    def _compute_hash(
        self,
        request_id: str,
        response_payload: Any,
        timestamp: int,
        service: str,
        nonce: str,
        algorithm: QRSAlgorithm
    ) -> str:
        """
        Compute cryptographic hash of QRS data.
        
        Args:
            request_id: Request identifier
            response_payload: Response data
            timestamp: Request timestamp
            service: Service identifier
            nonce: Random nonce
            algorithm: Hash algorithm to use
        
        Returns:
            Hex-encoded hash string
        """
        # Canonicalize payload
        payload_str = str(response_payload)
        
        # Combine fields for hashing
        data = f"{request_id}:{payload_str}:{timestamp}:{service}:{nonce}"
        data_bytes = data.encode('utf-8')
        
        # Compute hash based on algorithm
        if algorithm == QRSAlgorithm.SHA256_QRS:
            return hashlib.sha256(data_bytes).hexdigest()
        elif algorithm == QRSAlgorithm.SHA512_QRS:
            return hashlib.sha512(data_bytes).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

    async def _log_qrs_creation(self, qrs: QRSSignature, original_data: Dict[str, Any]) -> None:
        """
        Log QRS creation to ΛTRACE audit trail.
        
        Args:
            qrs: Created QRS signature
            original_data: Original request data
        """
        if not self.trace_logger:
            return
        
        try:
            # ΛTRACE logging format
            await self.trace_logger.log({
                'event': 'qrs_created',
                'qrs_id': qrs.qrs_id,
                'request_id': qrs.request_id,
                'service': qrs.service,
                'algorithm': qrs.algorithm,
                'timestamp': qrs.created_at,
                'trinity_tag': '🧠 Consciousness'
            })
        except Exception:
            # Silent failure - don't break QRS creation if logging fails
            pass

    async def _log_qrs_verification(self, qrs_data: Dict[str, Any], valid: bool) -> None:
        """
        Log QRS verification to ΛTRACE audit trail.
        
        Args:
            qrs_data: QRS data being verified
            valid: Whether verification succeeded
        """
        if not self.trace_logger:
            return
        
        try:
            await self.trace_logger.log({
                'event': 'qrs_verified',
                'qrs_id': qrs_data.get('qrs_id', 'unknown'),
                'valid': valid,
                'timestamp': int(time.time()),
                'trinity_tag': '🛡️ Guardian'
            })
        except Exception:
            pass

    # ========================================================================
    # Synchronous Methods for Test Compatibility
    # ========================================================================

    def generate_signature(
        self,
        request_data: Dict[str, Any],
        algorithm: QRSAlgorithm = QRSAlgorithm.SHA256
    ) -> str:
        """
        Generate HMAC signature for request data (synchronous).
        
        Args:
            request_data: Request data dictionary
            algorithm: Hash algorithm (SHA256 or SHA512)
        
        Returns:
            Hex-encoded HMAC signature string
        
        Task: TEST-HIGH-API-QRS-01 (signature generation)
        """
        import hmac
        import json
        
        # Canonicalize request data
        canonical_data = json.dumps(request_data, sort_keys=True)
        data_bytes = canonical_data.encode('utf-8')
        key_bytes = self.secret_key.encode('utf-8')
        
        # Generate HMAC based on algorithm
        if algorithm in (QRSAlgorithm.SHA256, QRSAlgorithm.SHA256_QRS):
            signature = hmac.new(key_bytes, data_bytes, hashlib.sha256).hexdigest()
        elif algorithm in (QRSAlgorithm.SHA512, QRSAlgorithm.SHA512_QRS):
            signature = hmac.new(key_bytes, data_bytes, hashlib.sha512).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        return signature

    def verify_signature(
        self,
        request_data: Dict[str, Any],
        signature: str,
        algorithm: QRSAlgorithm = QRSAlgorithm.SHA256
    ) -> bool:
        """
        Verify HMAC signature for request data (synchronous).
        
        Args:
            request_data: Request data dictionary
            signature: Expected signature to verify
            algorithm: Hash algorithm used
        
        Returns:
            True if signature is valid, False otherwise
        
        Task: TEST-HIGH-API-QRS-01 (signature verification)
        """
        try:
            expected_signature = self.generate_signature(request_data, algorithm)
            return hmac.compare_digest(signature, expected_signature)
        except Exception:
            return False

    def create_audit_entry(
        self,
        request_data: Dict[str, Any],
        signature: str,
        verification_result: bool
    ) -> Dict[str, Any]:
        """
        Create ΛTRACE audit trail entry.
        
        Args:
            request_data: Original request data
            signature: Generated/verified signature
            verification_result: Whether verification succeeded
        
        Returns:
            Audit entry dictionary with ΛTRACE format
        
        Task: TEST-HIGH-API-QRS-02 (audit trail integration)
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Create audit entry
        audit_entry = {
            "timestamp": timestamp,
            "lambda_id": request_data.get("lambda_id", "unknown"),
            "signature": signature,
            "verification_result": verification_result,
            "action": "signature_verification",
            "method": request_data.get("method", "UNKNOWN"),
            "path": request_data.get("path", "/"),
        }
        
        # Add failure reason if verification failed
        if not verification_result:
            audit_entry["failure_reason"] = "signature_mismatch"
            audit_entry["error"] = "Signature verification failed"
        
        # Calculate entry hash for chain integrity
        entry_str = f"{timestamp}{audit_entry['lambda_id']}{signature}{verification_result}"
        entry_hash = hashlib.sha256(entry_str.encode()).hexdigest()
        audit_entry["entry_hash"] = entry_hash
        
        # Add previous hash for chain linkage
        if self._audit_trail:
            audit_entry["previous_hash"] = self._audit_trail[-1].get("entry_hash", "0" * 64)
        else:
            # Genesis entry
            audit_entry["previous_hash"] = "0" * 64
        
        # Store in audit trail
        self._audit_trail.append(audit_entry)
        
        return audit_entry

    def validate_timestamp(
        self,
        timestamp_str: str,
        max_age_seconds: int = 300
    ) -> bool:
        """
        Validate request timestamp for freshness.
        
        Args:
            timestamp_str: ISO format timestamp string
            max_age_seconds: Maximum allowed age in seconds
        
        Returns:
            True if timestamp is recent, False otherwise
        
        Task: TEST-HIGH-API-QRS-01 (timestamp validation)
        """
        try:
            # Parse ISO format timestamp
            # Handle both with and without microseconds
            if '.' in timestamp_str:
                # Has microseconds
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                # No microseconds
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            
            # Ensure timezone awareness
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            
            # Get current time
            now = datetime.now(timezone.utc)
            
            # Calculate age
            age_seconds = (now - timestamp).total_seconds()
            
            # Check if within acceptable range
            return 0 <= age_seconds <= max_age_seconds
        except Exception:
            return False

    def check_nonce(self, nonce: str) -> bool:
        """
        Check if nonce is new (replay prevention).
        
        Args:
            nonce: Unique nonce string
        
        Returns:
            True if nonce is new, False if already used (replay)
        
        Task: TEST-HIGH-API-QRS-01 (replay prevention)
        """
        if nonce in self._used_nonces:
            return False  # Replay detected
        
        # Mark nonce as used
        self._used_nonces.add(nonce)
        return True  # New nonce

    def get_rate_limit(self, lambda_id: str) -> int:
        """
        Get rate limit for ΛID based on tier.
        
        Args:
            lambda_id: Lambda ID in format Λ_<tier>_<user_id>
        
        Returns:
            Rate limit (requests per minute) for the tier
        
        Task: TEST-HIGH-API-QRS-01 (rate limiting)
        """
        # Extract tier from ΛID
        parts = lambda_id.split('_')
        if len(parts) >= 2:
            tier = parts[1].lower()
            return self._rate_limits.get(tier, 100)  # Default to delta tier
        
        return 100  # Default rate limit


# Module-level convenience functions
async def create_qrs(data: Dict[str, Any], **kwargs) -> QRSSignature:
    """
    Convenience function to create QRS signature.
    
    Args:
        data: Request/response data
        **kwargs: Additional arguments for QRSManager
    
    Returns:
        QRSSignature object
    """
    manager = QRSManager()
    return await manager.create_qrs(data, **kwargs)


async def verify_qrs(qrs_data: Dict[str, Any], **kwargs) -> QRSVerificationResult:
    """
    Convenience function to verify QRS signature.
    
    Args:
        qrs_data: QRS signature data
        **kwargs: Additional arguments for QRSManager
    
    Returns:
        QRSVerificationResult object
    """
    manager = QRSManager()
    return await manager.verify_qrs(qrs_data, **kwargs)
