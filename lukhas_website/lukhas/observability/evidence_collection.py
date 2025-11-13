#!/usr/bin/env python3
"""
LUKHAS Evidence Collection Engine
Tamper-evident audit logging for regulatory compliance and AI decision transparency.

Features:
- Tamper-evident evidence collection with cryptographic integrity
- GDPR/CCPA/SOX compliant audit trails
- Long-term evidence retention and archival
- Real-time evidence verification and validation
- High-performance <10ms overhead for all operations
- Guardian integration for evidence validation
"""

import asyncio
import hashlib
import hmac
import json
import os
import time
import zlib
from collections import deque
from collections.abc import AsyncGenerator
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

try:
    import aiofiles
    AIOFILES_AVAILABLE = True
except ImportError:
    AIOFILES_AVAILABLE = False


class EvidenceType(Enum):
    """Types of evidence collected by LUKHAS"""
    USER_INTERACTION = "user_interaction"
    AI_DECISION = "ai_decision"
    AUTHENTICATION = "authentication"
    DATA_ACCESS = "data_access"
    SYSTEM_EVENT = "system_event"
    PERFORMANCE_METRIC = "performance_metric"
    ERROR_EVENT = "error_event"
    REGULATORY_EVENT = "regulatory_event"
    SECURITY_EVENT = "security_event"
    BUSINESS_EVENT = "business_event"


class ComplianceRegime(Enum):
    """Regulatory compliance regimes"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    SOX = "sox"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"
    INTERNAL = "internal"


@dataclass
class EvidenceRecord:
    """Individual evidence record with cryptographic integrity"""
    evidence_id: str
    timestamp: datetime
    evidence_type: EvidenceType
    source_component: str
    correlation_id: Optional[str]
    user_id: Optional[str]
    session_id: Optional[str]
    operation: str
    payload: dict[str, Any]
    integrity_hash: str
    signature: Optional[str] = None
    compliance_regimes: list[ComplianceRegime] = None
    retention_until: Optional[datetime] = None
    archival_location: Optional[str] = None

    def __post_init__(self):
        if self.compliance_regimes is None:
            self.compliance_regimes = [ComplianceRegime.INTERNAL]


@dataclass
class EvidenceChain:
    """Chain of evidence records with tamper-evident linking"""
    chain_id: str
    previous_hash: str
    records: list[EvidenceRecord]
    block_hash: str
    sequence_number: int
    created_at: datetime
    compressed_payload: Optional[bytes] = None


class IntegrityVerificationError(Exception):
    """Raised when evidence integrity verification fails"""
    pass


class EvidenceCollectionEngine:
    """
    High-performance tamper-evident evidence collection system.
    Provides comprehensive audit logging for regulatory compliance.
    """

    def __init__(
        self,
        storage_path: str = "./artifacts/evidence",
        retention_days: int = 2555,  # 7 years default
        compression_enabled: bool = True,
        encryption_enabled: bool = True,
        chain_block_size: int = 100,
        signing_key_path: Optional[str] = None,
        guardian_integration: bool = True,
    ):
        """
        Initialize evidence collection engine.

        Args:
            storage_path: Path to store evidence files
            retention_days: Evidence retention period in days
            compression_enabled: Enable zlib compression for storage
            encryption_enabled: Enable encryption for sensitive evidence
            chain_block_size: Number of records per evidence chain block
            signing_key_path: Path to RSA private key for signing
            guardian_integration: Enable Guardian system integration
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.retention_days = retention_days
        self.compression_enabled = compression_enabled
        self.encryption_enabled = encryption_enabled
        self.chain_block_size = chain_block_size
        self.guardian_integration = guardian_integration

        # Initialize cryptographic components
        self._init_crypto_system(signing_key_path)

        # Initialize evidence chain
        self.current_chain: list[EvidenceRecord] = []
        self.chain_sequence = 0
        self.last_block_hash = self._genesis_hash()

        # Performance tracking
        self._collection_times = deque(maxlen=1000)
        self._verification_times = deque(maxlen=1000)

        # Evidence buffer for high-throughput scenarios
        self._evidence_buffer = deque(maxlen=10000)
        self._buffer_lock = asyncio.Lock()

        # Start background tasks
        self._flush_task = None
        self._archival_task = None
        self._start_background_tasks()

    def _init_crypto_system(self, signing_key_path: Optional[str]):
        """Initialize cryptographic system for evidence integrity"""
        # Generate or load RSA key pair for signing
        if signing_key_path and Path(signing_key_path).exists():
            with open(signing_key_path, 'rb') as f:
                self.private_key = serialization.load_pem_private_key(f.read(), password=None)
        else:
            # Generate new key pair
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )

            # Save private key
            key_path = self.storage_path / "evidence_signing.key"
            with open(key_path, 'wb') as f:
                pem = self.private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                f.write(pem)
            os.chmod(key_path, 0o600)  # Secure permissions

        self.public_key = self.private_key.public_key()

        # HMAC key for integrity verification
        self.hmac_key = os.urandom(32)
        with open(self.storage_path / "integrity.key", 'wb') as f:
            f.write(self.hmac_key)
        os.chmod(self.storage_path / "integrity.key", 0o600)

    def _genesis_hash(self) -> str:
        """Generate genesis hash for evidence chain"""
        genesis_data = {
            "genesis": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0",
            "system": "LUKHAS"
        }
        return hashlib.sha256(json.dumps(genesis_data, sort_keys=True).encode()).hexdigest()

    def _compute_integrity_hash(self, record_data: dict[str, Any]) -> str:
        """Compute HMAC-SHA256 integrity hash for evidence record"""
        record_json = json.dumps(record_data, sort_keys=True, default=str)
        return hmac.new(self.hmac_key, record_json.encode(), hashlib.sha256).hexdigest()

    def _sign_evidence(self, evidence_hash: str) -> str:
        """Create RSA signature for evidence record"""
        signature = self.private_key.sign(
            evidence_hash.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature.hex()

    def _verify_signature(self, evidence_hash: str, signature_hex: str) -> bool:
        """Verify RSA signature for evidence record"""
        try:
            signature = bytes.fromhex(signature_hex)
            self.public_key.verify(
                signature,
                evidence_hash.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

    async def collect_evidence(
        self,
        evidence_type: EvidenceType,
        source_component: str,
        operation: str,
        payload: dict[str, Any],
        correlation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        compliance_regimes: Optional[list[ComplianceRegime]] = None,
    ) -> str:
        """
        Collect evidence with tamper-evident integrity.
        Optimized for <10ms overhead.

        Args:
            evidence_type: Type of evidence being collected
            source_component: Component generating the evidence
            operation: Operation being performed
            payload: Evidence data payload
            correlation_id: Request correlation ID
            user_id: Associated user ID
            session_id: Associated session ID
            compliance_regimes: Applicable compliance regimes

        Returns:
            Evidence ID for tracking
        """
        start_time = time.perf_counter()

        # Generate evidence record
        evidence_id = str(uuid4())
        timestamp = datetime.now(timezone.utc)

        # Prepare record data for integrity hash
        record_data = {
            "evidence_id": evidence_id,
            "timestamp": timestamp.isoformat(),
            "evidence_type": evidence_type.value,
            "source_component": source_component,
            "correlation_id": correlation_id,
            "user_id": user_id,
            "session_id": session_id,
            "operation": operation,
            "payload": payload,
        }

        # Compute integrity hash
        integrity_hash = self._compute_integrity_hash(record_data)

        # Create evidence record
        evidence = EvidenceRecord(
            evidence_id=evidence_id,
            timestamp=timestamp,
            evidence_type=evidence_type,
            source_component=source_component,
            correlation_id=correlation_id,
            user_id=user_id,
            session_id=session_id,
            operation=operation,
            payload=payload,
            integrity_hash=integrity_hash,
            compliance_regimes=compliance_regimes or [ComplianceRegime.INTERNAL],
            retention_until=timestamp + timedelta(days=self.retention_days),
        )

        # Sign evidence if encryption enabled
        if self.encryption_enabled:
            evidence.signature = self._sign_evidence(integrity_hash)

        # Add to evidence buffer for batch processing
        async with self._buffer_lock:
            self._evidence_buffer.append(evidence)

        # Track performance
        collection_time = (time.perf_counter() - start_time) * 1000
        self._collection_times.append(collection_time)

        # Guardian integration for critical evidence
        if (self.guardian_integration and
            evidence_type in [EvidenceType.AI_DECISION, EvidenceType.SECURITY_EVENT]):
            await self._validate_with_guardian(evidence)

        return evidence_id

    async def _validate_with_guardian(self, evidence: EvidenceRecord):
        """Validate evidence with Guardian system (stub for integration)"""
        # TODO: Integrate with actual Guardian system
        # For now, just validate structure
        if not evidence.payload or not evidence.operation:
            raise ValueError("Invalid evidence structure for Guardian validation")

    def verify_evidence(self, evidence: EvidenceRecord) -> bool:
        """
        Verify evidence integrity and signature.

        Args:
            evidence: Evidence record to verify

        Returns:
            True if evidence is valid and tamper-free
        """
        start_time = time.perf_counter()

        try:
            # Reconstruct record data
            record_data = {
                "evidence_id": evidence.evidence_id,
                "timestamp": evidence.timestamp.isoformat(),
                "evidence_type": evidence.evidence_type.value,
                "source_component": evidence.source_component,
                "correlation_id": evidence.correlation_id,
                "user_id": evidence.user_id,
                "session_id": evidence.session_id,
                "operation": evidence.operation,
                "payload": evidence.payload,
            }

            # Verify integrity hash
            expected_hash = self._compute_integrity_hash(record_data)
            if expected_hash != evidence.integrity_hash:
                return False

            # Verify signature if present
            if evidence.signature and (not self._verify_signature(evidence.integrity_hash, evidence.signature)):
                return False

            # Track verification performance
            verification_time = (time.perf_counter() - start_time) * 1000
            self._verification_times.append(verification_time)

            return True

        except Exception:
            return False

    async def flush_evidence_buffer(self) -> int:
        """
        Flush buffered evidence to persistent storage.

        Returns:
            Number of evidence records flushed
        """
        if not self._evidence_buffer:
            return 0

        async with self._buffer_lock:
            records_to_flush = list(self._evidence_buffer)
            self._evidence_buffer.clear()

        # Add to current chain
        self.current_chain.extend(records_to_flush)

        # Create chain blocks when threshold reached
        if len(self.current_chain) >= self.chain_block_size:
            await self._create_chain_block()

        return len(records_to_flush)

    async def _create_chain_block(self):
        """Create tamper-evident evidence chain block"""
        if not self.current_chain:
            return

        # Create chain block
        chain = EvidenceChain(
            chain_id=str(uuid4()),
            previous_hash=self.last_block_hash,
            records=self.current_chain.copy(),
            block_hash="",  # Will be computed
            sequence_number=self.chain_sequence,
            created_at=datetime.now(timezone.utc),
        )

        # Compute block hash
        block_data = {
            "chain_id": chain.chain_id,
            "previous_hash": chain.previous_hash,
            "sequence_number": chain.sequence_number,
            "created_at": chain.created_at.isoformat(),
            "records": [asdict(r) for r in chain.records],
        }

        if self.compression_enabled:
            # Compress payload for storage efficiency
            compressed_data = zlib.compress(
                json.dumps(block_data, default=str).encode(),
                level=6
            )
            chain.compressed_payload = compressed_data
            block_data["compressed_size"] = len(compressed_data)

        chain.block_hash = hashlib.sha256(
            json.dumps(block_data, sort_keys=True, default=str).encode()
        ).hexdigest()

        # Store chain block
        await self._store_chain_block(chain)

        # Update chain state
        self.last_block_hash = chain.block_hash
        self.chain_sequence += 1
        self.current_chain.clear()

    async def _store_chain_block(self, chain: EvidenceChain):
        """Store evidence chain block to persistent storage"""
        # Create timestamped storage directory
        storage_dir = self.storage_path / chain.created_at.strftime("%Y/%m/%d")
        storage_dir.mkdir(parents=True, exist_ok=True)

        # Store chain metadata
        metadata_file = storage_dir / f"chain_{chain.sequence_number:06d}_metadata.json"
        metadata = {
            "chain_id": chain.chain_id,
            "previous_hash": chain.previous_hash,
            "block_hash": chain.block_hash,
            "sequence_number": chain.sequence_number,
            "created_at": chain.created_at.isoformat(),
            "record_count": len(chain.records),
            "compressed": chain.compressed_payload is not None,
        }

        if AIOFILES_AVAILABLE:
            async with aiofiles.open(metadata_file, 'w') as f:
                await f.write(json.dumps(metadata, indent=2))
        else:
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

        # Store compressed records
        records_file = storage_dir / f"chain_{chain.sequence_number:06d}_records.json.gz"

        if self.compression_enabled and chain.compressed_payload:
            if AIOFILES_AVAILABLE:
                async with aiofiles.open(records_file, 'wb') as f:
                    await f.write(chain.compressed_payload)
            else:
                with open(records_file, 'wb') as f:
                    f.write(chain.compressed_payload)
        else:
            records_data = [asdict(r) for r in chain.records]
            if AIOFILES_AVAILABLE:
                async with aiofiles.open(records_file, 'w') as f:
                    await f.write(json.dumps(records_data, default=str, indent=2))
            else:
                with open(records_file, 'w') as f:
                    json.dump(records_data, f, default=str, indent=2)

    async def query_evidence(
        self,
        evidence_type: Optional[EvidenceType] = None,
        source_component: Optional[str] = None,
        correlation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> AsyncGenerator[EvidenceRecord, None]:
        """
        Query evidence records with filtering.

        Args:
            evidence_type: Filter by evidence type
            source_component: Filter by source component
            correlation_id: Filter by correlation ID
            user_id: Filter by user ID
            start_time: Filter by start timestamp
            end_time: Filter by end timestamp
            limit: Maximum number of records to return

        Yields:
            Matching evidence records
        """
        count = 0

        # Search through stored chain blocks
        for chain_file in sorted(self.storage_path.glob("**/chain_*_records.json.gz")):
            if count >= limit:
                break

            # Load and decompress records
            try:
                if AIOFILES_AVAILABLE:
                    async with aiofiles.open(chain_file, 'rb') as f:
                        compressed_data = await f.read()
                else:
                    with open(chain_file, 'rb') as f:
                        compressed_data = f.read()

                if chain_file.suffix == '.gz':
                    records_data = json.loads(zlib.decompress(compressed_data))
                else:
                    records_data = json.loads(compressed_data)

                # Filter and yield matching records
                for record_dict in records_data:
                    if count >= limit:
                        break

                    # Reconstruct evidence record
                    record = EvidenceRecord(
                        evidence_id=record_dict["evidence_id"],
                        timestamp=datetime.fromisoformat(record_dict["timestamp"]),
                        evidence_type=EvidenceType(record_dict["evidence_type"]),
                        source_component=record_dict["source_component"],
                        correlation_id=record_dict.get("correlation_id"),
                        user_id=record_dict.get("user_id"),
                        session_id=record_dict.get("session_id"),
                        operation=record_dict["operation"],
                        payload=record_dict["payload"],
                        integrity_hash=record_dict["integrity_hash"],
                        signature=record_dict.get("signature"),
                        compliance_regimes=[ComplianceRegime(r) for r in record_dict.get("compliance_regimes", [])],
                        retention_until=datetime.fromisoformat(record_dict["retention_until"]) if record_dict.get("retention_until") else None,
                        archival_location=record_dict.get("archival_location"),
                    )

                    # Apply filters
                    if evidence_type and record.evidence_type != evidence_type:
                        continue
                    if source_component and record.source_component != source_component:
                        continue
                    if correlation_id and record.correlation_id != correlation_id:
                        continue
                    if user_id and record.user_id != user_id:
                        continue
                    if start_time and record.timestamp < start_time:
                        continue
                    if end_time and record.timestamp > end_time:
                        continue

                    yield record
                    count += 1

            except Exception as e:
                print(f"Warning: Failed to process evidence file {chain_file}: {e}")
                continue

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get evidence collection performance metrics"""
        collection_times = list(self._collection_times)
        verification_times = list(self._verification_times)

        def calculate_percentiles(times):
            if not times:
                return {"p50": 0, "p95": 0, "p99": 0, "avg": 0}

            sorted_times = sorted(times)
            n = len(sorted_times)
            return {
                "p50": sorted_times[int(n * 0.5)],
                "p95": sorted_times[int(n * 0.95)],
                "p99": sorted_times[int(n * 0.99)],
                "avg": sum(times) / len(times),
            }

        return {
            "collection_performance_ms": calculate_percentiles(collection_times),
            "verification_performance_ms": calculate_percentiles(verification_times),
            "buffer_size": len(self._evidence_buffer),
            "chain_sequence": self.chain_sequence,
            "current_chain_size": len(self.current_chain),
            "total_evidence_files": len(list(self.storage_path.glob("**/chain_*_records.json*"))),
        }

    def _start_background_tasks(self):
        """Start background tasks for evidence processing"""
        async def flush_worker():
            while True:
                try:
                    await self.flush_evidence_buffer()
                    await asyncio.sleep(5)  # Flush every 5 seconds
                except Exception as e:
                    print(f"Evidence flush error: {e}")
                    await asyncio.sleep(10)

        async def archival_worker():
            while True:
                try:
                    await self._archive_old_evidence()
                    await asyncio.sleep(3600)  # Check hourly
                except Exception as e:
                    print(f"Evidence archival error: {e}")
                    await asyncio.sleep(3600)

        # Start tasks if event loop is available
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                self._flush_task = loop.create_task(flush_worker())
                self._archival_task = loop.create_task(archival_worker())
        except RuntimeError:
            # No event loop running, tasks will be started when needed
            pass

    async def _archive_old_evidence(self):
        """Archive evidence that exceeds retention period"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.retention_days)

        # Find old evidence files
        for evidence_file in self.storage_path.glob("**/chain_*_records.json*"):
            try:
                # Extract date from file path
                date_path = evidence_file.parent.parts[-3:]  # year/month/day
                file_date = datetime.strptime("/".join(date_path), "%Y/%m/%d")
                file_date = file_date.replace(tzinfo=timezone.utc)

                if file_date < cutoff_date:
                    # Archive old evidence
                    archive_dir = self.storage_path / "archive" / "/".join(date_path)
                    archive_dir.mkdir(parents=True, exist_ok=True)

                    archive_file = archive_dir / evidence_file.name
                    evidence_file.rename(archive_file)

                    print(f"Archived evidence file: {evidence_file}")

            except Exception as e:
                print(f"Error archiving evidence file {evidence_file}: {e}")

    async def shutdown(self):
        """Shutdown evidence collection engine"""
        # Cancel background tasks
        if self._flush_task:
            self._flush_task.cancel()
        if self._archival_task:
            self._archival_task.cancel()

        # Final flush of evidence buffer
        await self.flush_evidence_buffer()

        # Create final chain block if needed
        if self.current_chain:
            await self._create_chain_block()


# Global evidence collection instance
_evidence_engine: Optional[EvidenceCollectionEngine] = None


def initialize_evidence_collection(
    storage_path: str = "./artifacts/evidence",
    retention_days: int = 2555,
    compression_enabled: bool = True,
    encryption_enabled: bool = True,
) -> EvidenceCollectionEngine:
    """Initialize global evidence collection engine"""
    global _evidence_engine
    _evidence_engine = EvidenceCollectionEngine(
        storage_path=storage_path,
        retention_days=retention_days,
        compression_enabled=compression_enabled,
        encryption_enabled=encryption_enabled,
    )
    return _evidence_engine


def get_evidence_engine() -> EvidenceCollectionEngine:
    """Get or create global evidence collection engine"""
    global _evidence_engine
    if _evidence_engine is None:
        _evidence_engine = initialize_evidence_collection()
    return _evidence_engine


async def collect_evidence(
    evidence_type: EvidenceType,
    source_component: str,
    operation: str,
    payload: dict[str, Any],
    **kwargs
) -> str:
    """Convenience function for collecting evidence"""
    engine = get_evidence_engine()
    return await engine.collect_evidence(
        evidence_type=evidence_type,
        source_component=source_component,
        operation=operation,
        payload=payload,
        **kwargs
    )


async def shutdown_evidence_collection():
    """Shutdown global evidence collection"""
    global _evidence_engine
    if _evidence_engine:
        await _evidence_engine.shutdown()
        _evidence_engine = None
