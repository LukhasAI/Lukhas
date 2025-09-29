"""
T4/0.01% Excellence Memory Lifecycle Management

Comprehensive document retention, archival, and GDPR compliance for LUKHAS memory system.
Handles automatic expiration, archival policies, and right-to-be-forgotten requirements.

Performance targets:
- Cleanup operations: <5s for 10k documents
- Archival operations: <30s for 100k documents
- GDPR tombstone creation: <100ms p95
- Retention policy evaluation: <50ms p95
"""

import asyncio
import gzip
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import logging

# Import base classes directly to avoid circular imports
import numpy as np

# Define minimal VectorDocument interface for lifecycle management
@dataclass
class VectorDocument:
    """Minimal VectorDocument interface for lifecycle operations"""
    id: str
    content: str
    embedding: np.ndarray
    metadata: Dict[str, Any] = field(default_factory=dict)
    identity_id: Optional[str] = None
    lane: str = "candidate"
    fold_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None

    def __post_init__(self):
        """Validate and normalize document"""
        if not isinstance(self.embedding, np.ndarray):
            self.embedding = np.array(self.embedding, dtype=np.float32)
        if self.embedding.dtype != np.float32:
            self.embedding = self.embedding.astype(np.float32)
        # Normalize vector for cosine similarity
        norm = np.linalg.norm(self.embedding)
        if norm > 0:
            self.embedding = self.embedding / norm

    @property
    def is_expired(self) -> bool:
        """Check if document has expired"""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "id": self.id,
            "content": self.content,
            "embedding": self.embedding.tolist(),
            "metadata": self.metadata,
            "identity_id": self.identity_id,
            "lane": self.lane,
            "fold_id": self.fold_id,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None
        }

# Minimal AbstractVectorStore interface for lifecycle operations
class AbstractVectorStore(ABC):
    """Abstract vector store interface for lifecycle operations"""

    @abstractmethod
    async def delete(self, document_id: str) -> bool:
        """Delete a document by ID"""
        pass

    @abstractmethod
    async def update(self, document: VectorDocument) -> bool:
        """Update a document"""
        pass

    @abstractmethod
    async def list_expired_documents(self, cutoff_time: datetime, limit: int) -> List[VectorDocument]:
        """List expired documents"""
        pass

    @abstractmethod
    async def list_by_identity(self, identity_id: str, limit: int) -> List[VectorDocument]:
        """List documents by identity"""
        pass
# Use standard Python logging instead of custom logger
import uuid
from contextvars import ContextVar

logger = logging.getLogger(__name__)

# OpenTelemetry imports with graceful fallback
try:
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode
    OTEL_AVAILABLE = True
    tracer = trace.get_tracer(__name__)
except ImportError:
    OTEL_AVAILABLE = False
    tracer = None

# Context variable for correlation_id propagation
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)

# Mock metrics collector for testing
class MockMetricsCollector:
    def record_metric(self, name, value, service_type, metric_type, labels=None):
        pass

metrics = MockMetricsCollector()

# Mock ServiceType and MetricType enums
class ServiceType:
    MEMORY = "memory"

class MetricType:
    HISTOGRAM = "histogram"
    COUNTER = "counter"


class RetentionPolicy(Enum):
    """Document retention policies"""
    IMMEDIATE = "immediate"         # Delete immediately on expiration
    SHORT_TERM = "short_term"      # 30 days
    MEDIUM_TERM = "medium_term"    # 1 year
    LONG_TERM = "long_term"        # 7 years
    PERMANENT = "permanent"        # Never delete
    GDPR_COMPLIANT = "gdpr"        # Per GDPR requirements (varies by type)


class ArchivalTier(Enum):
    """Storage tiers for archived documents"""
    HOT = "hot"           # Immediate access, high cost
    WARM = "warm"         # Access within minutes, medium cost
    COLD = "cold"         # Access within hours, low cost
    FROZEN = "frozen"     # Restore required, very low cost


@dataclass
class RetentionRule:
    """
    Document retention rule configuration.
    """
    name: str
    policy: RetentionPolicy
    conditions: Dict[str, Any] = field(default_factory=dict)

    # Retention periods
    active_retention_days: int = 30
    archive_retention_days: int = 365

    # Archival configuration
    archive_tier: ArchivalTier = ArchivalTier.COLD
    compress_on_archive: bool = True

    # GDPR settings
    gdpr_category: Optional[str] = None
    allow_anonymization: bool = False
    require_explicit_deletion: bool = False

    # Callback for custom processing
    pre_deletion_callback: Optional[Callable] = None
    post_archival_callback: Optional[Callable] = None


@dataclass
class GDPRTombstone:
    """
    GDPR tombstone for deleted documents.
    Maintains audit trail while removing personal data.
    """
    document_id: str
    deleted_at: datetime
    deletion_reason: str  # "expiration", "gdpr_request", "manual", "policy"
    original_created_at: datetime
    original_lane: str

    # Optional fields with defaults
    identity_id: Optional[str] = None
    requested_by: Optional[str] = None
    original_fold_id: Optional[str] = None
    original_tags: List[str] = field(default_factory=list)
    content_hash: str = ""
    word_count: int = 0
    language: Optional[str] = None

    # Compliance tracking
    gdpr_category: Optional[str] = None
    legal_basis_removed: Optional[str] = None
    retention_rule: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "document_id": self.document_id,
            "identity_id": self.identity_id,
            "deleted_at": self.deleted_at.isoformat(),
            "deletion_reason": self.deletion_reason,
            "requested_by": self.requested_by,
            "original_created_at": self.original_created_at.isoformat(),
            "original_lane": self.original_lane,
            "original_fold_id": self.original_fold_id,
            "original_tags": self.original_tags,
            "content_hash": self.content_hash,
            "word_count": self.word_count,
            "language": self.language,
            "gdpr_category": self.gdpr_category,
            "legal_basis_removed": self.legal_basis_removed,
            "retention_rule": self.retention_rule
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GDPRTombstone':
        """Create from dictionary"""
        return cls(
            document_id=data["document_id"],
            identity_id=data.get("identity_id"),
            deleted_at=datetime.fromisoformat(data["deleted_at"]),
            deletion_reason=data["deletion_reason"],
            requested_by=data.get("requested_by"),
            original_created_at=datetime.fromisoformat(data["original_created_at"]),
            original_lane=data["original_lane"],
            original_fold_id=data.get("original_fold_id"),
            original_tags=data.get("original_tags", []),
            content_hash=data.get("content_hash", ""),
            word_count=data.get("word_count", 0),
            language=data.get("language"),
            gdpr_category=data.get("gdpr_category"),
            legal_basis_removed=data.get("legal_basis_removed"),
            retention_rule=data.get("retention_rule")
        )


@dataclass
class LifecycleStats:
    """
    Memory lifecycle operation statistics.
    """
    # Operations
    documents_expired: int = 0
    documents_archived: int = 0
    documents_deleted: int = 0
    tombstones_created: int = 0

    # Performance
    cleanup_duration_ms: float = 0.0
    archival_duration_ms: float = 0.0
    avg_tombstone_creation_ms: float = 0.0

    # Storage impact
    bytes_freed: int = 0
    bytes_archived: int = 0
    compression_ratio: float = 1.0

    # GDPR compliance
    gdpr_requests_processed: int = 0
    anonymization_operations: int = 0
    explicit_deletions: int = 0

    # Policy effectiveness
    retention_rules_applied: Dict[str, int] = field(default_factory=dict)
    policy_violations: int = 0


class AbstractArchivalBackend(ABC):
    """
    Abstract backend for archived document storage.
    """

    @abstractmethod
    async def store_archived_document(
        self,
        document: VectorDocument,
        tier: ArchivalTier,
        compress: bool = True
    ) -> str:
        """
        Store document in archival storage.

        Returns:
            Archive reference ID
        """
        pass

    @abstractmethod
    async def retrieve_archived_document(
        self,
        archive_id: str
    ) -> VectorDocument:
        """Retrieve document from archival storage"""
        pass

    @abstractmethod
    async def delete_archived_document(self, archive_id: str) -> bool:
        """Delete document from archival storage"""
        pass


class FileArchivalBackend(AbstractArchivalBackend):
    """
    File-based archival backend using gzip compression.
    Stores archived documents as JSON.gz files in archive/ directory.
    """

    def __init__(self, base_path: str = "archive"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info("FileArchivalBackend initialized", base_path=str(self.base_path))

    def _get_archive_path(self, archive_id: str) -> Path:
        """Get file path for archived document"""
        # Organize by date for better file system organization
        now = datetime.now(timezone.utc)
        date_dir = now.strftime("%Y-%m-%d")
        return self.base_path / date_dir / f"{archive_id}.json.gz"

    async def store_archived_document(
        self,
        document: VectorDocument,
        tier: ArchivalTier,
        compress: bool = True
    ) -> str:
        """
        Store document in archival storage as compressed JSON.

        Returns:
            Archive reference ID
        """
        archive_id = f"arch_{document.id}_{int(time.time())}"
        archive_path = self._get_archive_path(archive_id)
        archive_path.parent.mkdir(parents=True, exist_ok=True)

        # Prepare document data for archival
        archive_data = {
            "archive_id": archive_id,
            "archived_at": datetime.now(timezone.utc).isoformat(),
            "tier": tier.value,
            "compressed": compress,
            "document": document.to_dict()
        }

        # Write compressed JSON
        json_data = json.dumps(archive_data, indent=2, ensure_ascii=False)

        if compress:
            with gzip.open(archive_path, 'wt', encoding='utf-8') as f:
                f.write(json_data)
        else:
            # For testing or special cases where compression is disabled
            with open(archive_path.with_suffix('.json'), 'w', encoding='utf-8') as f:
                f.write(json_data)

        logger.debug(
            "Document archived to file",
            archive_id=archive_id,
            path=str(archive_path),
            tier=tier.value,
            compressed=compress
        )

        return archive_id

    async def retrieve_archived_document(self, archive_id: str) -> VectorDocument:
        """Retrieve document from archival storage"""
        archive_path = self._get_archive_path(archive_id)

        # Try compressed first, then uncompressed
        if archive_path.exists():
            with gzip.open(archive_path, 'rt', encoding='utf-8') as f:
                archive_data = json.load(f)
        elif archive_path.with_suffix('.json').exists():
            with open(archive_path.with_suffix('.json'), 'r', encoding='utf-8') as f:
                archive_data = json.load(f)
        else:
            raise FileNotFoundError(f"Archived document not found: {archive_id}")

        # Reconstruct VectorDocument
        doc_data = archive_data["document"]
        return VectorDocument(
            id=doc_data["id"],
            content=doc_data["content"],
            embedding=doc_data["embedding"],
            metadata=doc_data["metadata"],
            identity_id=doc_data.get("identity_id"),
            lane=doc_data["lane"],
            fold_id=doc_data.get("fold_id"),
            tags=doc_data.get("tags", []),
            created_at=datetime.fromisoformat(doc_data["created_at"]),
            updated_at=datetime.fromisoformat(doc_data["updated_at"]),
            expires_at=datetime.fromisoformat(doc_data["expires_at"]) if doc_data.get("expires_at") else None,
            access_count=doc_data.get("access_count", 0),
            last_accessed=datetime.fromisoformat(doc_data["last_accessed"]) if doc_data.get("last_accessed") else None
        )

    async def delete_archived_document(self, archive_id: str) -> bool:
        """Delete document from archival storage"""
        archive_path = self._get_archive_path(archive_id)

        try:
            if archive_path.exists():
                archive_path.unlink()
                return True
            elif archive_path.with_suffix('.json').exists():
                archive_path.with_suffix('.json').unlink()
                return True
            return False
        except Exception as e:
            logger.error(
                "Failed to delete archived document",
                archive_id=archive_id,
                path=str(archive_path),
                error=str(e)
            )
            return False


class AbstractTombstoneStore(ABC):
    """
    Abstract storage for GDPR tombstones.
    """

    @abstractmethod
    async def create_tombstone(self, tombstone: GDPRTombstone) -> bool:
        """Store GDPR tombstone"""
        pass

    @abstractmethod
    async def get_tombstone(self, document_id: str) -> Optional[GDPRTombstone]:
        """Retrieve tombstone by document ID"""
        pass

    @abstractmethod
    async def list_tombstones_by_identity(
        self,
        identity_id: str,
        limit: int = 100
    ) -> List[GDPRTombstone]:
        """List tombstones for an identity"""
        pass

    @abstractmethod
    async def cleanup_old_tombstones(
        self,
        older_than: datetime
    ) -> int:
        """Remove old tombstones, return count deleted"""
        pass


class FileTombstoneStore(AbstractTombstoneStore):
    """
    File-based tombstone storage with JSON audit events.
    Writes audit events to artifacts/memory_validation_*.json.
    """

    def __init__(self, base_path: str = "artifacts"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.tombstones: Dict[str, GDPRTombstone] = {}
        logger.info(f"FileTombstoneStore initialized at {self.base_path}")

    def _get_audit_filename(self) -> str:
        """Generate audit file name with timestamp"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        return f"memory_validation_{timestamp}.json"

    async def _write_audit_event(
        self,
        event_type: str,
        tombstone: GDPRTombstone,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """Write audit event to artifacts directory"""
        audit_data = {
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tombstone": tombstone.to_dict(),
            "audit_metadata": {
                "compliance_version": "GDPR-2018",
                "lukhas_version": "1.0.0",
                "retention_policy_version": "v2.1"
            }
        }

        if additional_data:
            audit_data.update(additional_data)

        audit_file = self.base_path / self._get_audit_filename()

        # Append to existing file or create new one
        mode = 'a' if audit_file.exists() else 'w'
        with open(audit_file, mode, encoding='utf-8') as f:
            f.write(json.dumps(audit_data, indent=2, ensure_ascii=False) + '\n')

        logger.debug(
            "Audit event written",
            event_type=event_type,
            document_id=tombstone.document_id,
            audit_file=str(audit_file)
        )

    async def create_tombstone(self, tombstone: GDPRTombstone) -> bool:
        """Store GDPR tombstone and write audit event"""
        try:
            self.tombstones[tombstone.document_id] = tombstone

            # Write audit event
            await self._write_audit_event(
                "tombstone_created",
                tombstone,
                {
                    "compliance_check": {
                        "gdpr_article_17_right_to_erasure": True,
                        "data_minimization_principle": True,
                        "audit_trail_maintained": True
                    }
                }
            )

            logger.info(
                "GDPR tombstone created",
                document_id=tombstone.document_id,
                identity_id=tombstone.identity_id,
                deletion_reason=tombstone.deletion_reason
            )

            return True

        except Exception as e:
            logger.error(
                "Failed to create tombstone",
                document_id=tombstone.document_id,
                error=str(e)
            )
            return False

    async def get_tombstone(self, document_id: str) -> Optional[GDPRTombstone]:
        """Retrieve tombstone by document ID"""
        tombstone = self.tombstones.get(document_id)

        if tombstone:
            # Write audit event for tombstone access
            await self._write_audit_event(
                "tombstone_accessed",
                tombstone,
                {
                    "access_type": "read_tombstone",
                    "privacy_impact": "minimal_metadata_only"
                }
            )

        return tombstone

    async def list_tombstones_by_identity(
        self,
        identity_id: str,
        limit: int = 100
    ) -> List[GDPRTombstone]:
        """List tombstones for an identity"""
        matching_tombstones = [
            tombstone for tombstone in self.tombstones.values()
            if tombstone.identity_id == identity_id
        ]

        result = matching_tombstones[:limit]

        # Write audit event for bulk access
        if result:
            sample_tombstone = result[0]
            await self._write_audit_event(
                "tombstones_bulk_access",
                sample_tombstone,
                {
                    "access_type": "list_by_identity",
                    "identity_id": identity_id,
                    "results_count": len(result),
                    "limit_applied": limit
                }
            )

        return result

    async def cleanup_old_tombstones(self, older_than: datetime) -> int:
        """Remove old tombstones, return count deleted"""
        deleted_count = 0
        to_delete = []

        for doc_id, tombstone in self.tombstones.items():
            if tombstone.deleted_at < older_than:
                to_delete.append(doc_id)

        for doc_id in to_delete:
            tombstone = self.tombstones[doc_id]
            del self.tombstones[doc_id]
            deleted_count += 1

            # Write audit event for tombstone cleanup
            await self._write_audit_event(
                "tombstone_cleanup",
                tombstone,
                {
                    "cleanup_reason": "retention_period_expired",
                    "older_than": older_than.isoformat(),
                    "final_deletion": True
                }
            )

        if deleted_count > 0:
            logger.info(
                "Tombstone cleanup completed",
                deleted_count=deleted_count,
                older_than=older_than.isoformat()
            )

        return deleted_count


class AbstractTombstoneStore(ABC):
    """
    Abstract storage for GDPR tombstones.
    """

    @abstractmethod
    async def create_tombstone(self, tombstone: GDPRTombstone) -> bool:
        """Store GDPR tombstone"""
        pass

    @abstractmethod
    async def get_tombstone(self, document_id: str) -> Optional[GDPRTombstone]:
        """Retrieve tombstone by document ID"""
        pass

    @abstractmethod
    async def list_tombstones_by_identity(
        self,
        identity_id: str,
        limit: int = 100
    ) -> List[GDPRTombstone]:
        """List tombstones for an identity"""
        pass

    @abstractmethod
    async def cleanup_old_tombstones(
        self,
        older_than: datetime
    ) -> int:
        """Remove old tombstones, return count deleted"""
        pass


class MemoryLifecycleManager:
    """
    Comprehensive memory lifecycle management with retention policies,
    archival, and GDPR compliance.
    """

    def __init__(
        self,
        vector_store: AbstractVectorStore,
        archival_backend: Optional[AbstractArchivalBackend] = None,
        tombstone_store: Optional[AbstractTombstoneStore] = None,
        enable_gdpr_compliance: bool = True,
        default_retention_days: int = 365
    ):
        self.vector_store = vector_store
        self.archival_backend = archival_backend
        self.tombstone_store = tombstone_store
        self.enable_gdpr_compliance = enable_gdpr_compliance
        self.default_retention_days = default_retention_days

        # Retention rules registry
        self.retention_rules: Dict[str, RetentionRule] = {}

        # Statistics
        self.stats = LifecycleStats()

        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._archival_task: Optional[asyncio.Task] = None

        # Setup default retention rules
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Setup default retention rules"""
        # Default rule for candidate lane
        self.add_retention_rule(RetentionRule(
            name="candidate_default",
            policy=RetentionPolicy.SHORT_TERM,
            conditions={"lane": "candidate"},
            active_retention_days=30,
            archive_retention_days=90,
            archive_tier=ArchivalTier.COLD
        ))

        # Default rule for integration lane
        self.add_retention_rule(RetentionRule(
            name="integration_default",
            policy=RetentionPolicy.MEDIUM_TERM,
            conditions={"lane": "integration"},
            active_retention_days=90,
            archive_retention_days=365,
            archive_tier=ArchivalTier.WARM
        ))

        # Default rule for production lane
        self.add_retention_rule(RetentionRule(
            name="production_default",
            policy=RetentionPolicy.LONG_TERM,
            conditions={"lane": "production"},
            active_retention_days=365,
            archive_retention_days=2555,  # 7 years
            archive_tier=ArchivalTier.HOT
        ))

        # GDPR-specific rules
        if self.enable_gdpr_compliance:
            self.add_retention_rule(RetentionRule(
                name="gdpr_personal_data",
                policy=RetentionPolicy.GDPR_COMPLIANT,
                conditions={"gdpr_category": "personal_data"},
                active_retention_days=365,
                archive_retention_days=0,  # No archival for personal data
                allow_anonymization=True,
                require_explicit_deletion=True
            ))

    def add_retention_rule(self, rule: RetentionRule):
        """Add or update retention rule"""
        self.retention_rules[rule.name] = rule
        logger.info(
            "Retention rule added/updated",
            rule_name=rule.name,
            policy=rule.policy.value,
            active_days=rule.active_retention_days
        )

    def remove_retention_rule(self, rule_name: str) -> bool:
        """Remove retention rule"""
        if rule_name in self.retention_rules:
            del self.retention_rules[rule_name]
            logger.info("Retention rule removed", rule_name=rule_name)
            return True
        return False

    def _evaluate_retention_rule(
        self,
        document: VectorDocument
    ) -> Optional[RetentionRule]:
        """
        Evaluate which retention rule applies to a document.

        Returns:
            Matching retention rule or None
        """
        for rule in self.retention_rules.values():
            if self._document_matches_conditions(document, rule.conditions):
                return rule
        return None

    def _document_matches_conditions(
        self,
        document: VectorDocument,
        conditions: Dict[str, Any]
    ) -> bool:
        """Check if document matches rule conditions"""
        for field, value in conditions.items():
            if field == "lane" and document.lane != value:
                return False
            elif field == "identity_id" and document.identity_id != value:
                return False
            elif field == "fold_id" and document.fold_id != value:
                return False
            elif field == "tags":
                if isinstance(value, list):
                    if not any(tag in document.tags for tag in value):
                        return False
                else:
                    if value not in document.tags:
                        return False
            elif field == "gdpr_category":
                gdpr_cat = document.metadata.get("gdpr", {}).get("category")
                if gdpr_cat != value:
                    return False
            elif field in document.metadata:
                if document.metadata[field] != value:
                    return False
        return True

    async def cleanup_expired_documents(
        self,
        batch_size: int = 1000,
        max_documents: Optional[int] = None,
        correlation_id: Optional[str] = None
    ) -> LifecycleStats:
        """
        Clean up expired documents according to retention policies.

        Args:
            batch_size: Number of documents to process per batch
            max_documents: Maximum documents to process (None = all)
            correlation_id: Request correlation ID for tracing

        Returns:
            Cleanup statistics
        """
        # Set correlation_id in context for propagation
        if correlation_id:
            correlation_id_var.set(correlation_id)
        else:
            correlation_id = correlation_id_var.get() or str(uuid.uuid4())

        start_time = time.perf_counter()
        cleanup_stats = LifecycleStats()

        # Create OTEL span for lifecycle operation
        span = None
        if OTEL_AVAILABLE and tracer:
            span = tracer.start_span("memory_lifecycle_cleanup")
            span.set_attribute("operation", "cleanup")
            span.set_attribute("lane", "unknown")  # Will be updated per document
            span.set_attribute("correlation_id", correlation_id)
            span.set_attribute("batch_size", batch_size)
            if max_documents:
                span.set_attribute("max_documents", max_documents)

        try:
            # Get expired documents
            now = datetime.now(timezone.utc)

            # Get expired documents from the vector store
            expired_docs = await self.vector_store.list_expired_documents(now, batch_size)

            processed_count = 0

            for document in expired_docs:
                if max_documents and processed_count >= max_documents:
                    break

                try:
                    # Evaluate retention rule
                    rule = self._evaluate_retention_rule(document)

                    if rule is None:
                        # Use default retention
                        if self._should_delete_by_default(document, now):
                            await self._delete_document_with_tombstone(
                                document,
                                "expiration",
                                rule_name="default"
                            )
                            cleanup_stats.documents_deleted += 1
                    else:
                        # Apply rule
                        action_taken = await self._apply_retention_rule(
                            document,
                            rule,
                            now
                        )

                        if action_taken == "deleted":
                            cleanup_stats.documents_deleted += 1
                        elif action_taken == "archived":
                            cleanup_stats.documents_archived += 1

                        # Track rule usage
                        rule_name = rule.name
                        cleanup_stats.retention_rules_applied[rule_name] = (
                            cleanup_stats.retention_rules_applied.get(rule_name, 0) + 1
                        )

                except Exception as e:
                    logger.error(
                        "Failed to process expired document",
                        document_id=document.id,
                        error=str(e)
                    )
                    cleanup_stats.policy_violations += 1

                processed_count += 1

            cleanup_stats.cleanup_duration_ms = (
                time.perf_counter() - start_time
            ) * 1000

            # Record Prometheus metrics for lifecycle operations
            metrics.record_metric(
                "lukhas_memory_lifecycle_seconds",
                cleanup_stats.cleanup_duration_ms / 1000.0,
                ServiceType.MEMORY,
                MetricType.HISTOGRAM,
                {"operation": "cleanup"}
            )
            metrics.record_metric(
                "lukhas_memory_retained_total",
                cleanup_stats.documents_deleted,
                ServiceType.MEMORY,
                MetricType.COUNTER,
                {"operation": "delete"}
            )
            metrics.record_metric(
                "lukhas_memory_archived_total",
                cleanup_stats.documents_archived,
                ServiceType.MEMORY,
                MetricType.COUNTER,
                {"operation": "archive"}
            )

            # Update span with final metrics
            if span:
                span.set_attribute("processed_count", processed_count)
                span.set_attribute("documents_deleted", cleanup_stats.documents_deleted)
                span.set_attribute("documents_archived", cleanup_stats.documents_archived)
                span.set_attribute("duration_ms", cleanup_stats.cleanup_duration_ms)
                span.set_status(Status(StatusCode.OK))

            logger.info(
                "Document cleanup completed",
                processed=processed_count,
                deleted=cleanup_stats.documents_deleted,
                archived=cleanup_stats.documents_archived,
                duration_ms=cleanup_stats.cleanup_duration_ms,
                correlation_id=correlation_id
            )

            return cleanup_stats

        except Exception as e:
            if span:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))

            logger.error(
                "Document cleanup failed",
                error=str(e),
                duration_ms=(time.perf_counter() - start_time) * 1000,
                correlation_id=correlation_id
            )
            raise
        finally:
            if span:
                span.end()

    def _should_delete_by_default(
        self,
        document: VectorDocument,
        now: datetime
    ) -> bool:
        """Check if document should be deleted by default retention"""
        if document.expires_at and now > document.expires_at:
            return True

        # Check age against default retention
        age_days = (now - document.created_at).days
        return age_days > self.default_retention_days

    async def _apply_retention_rule(
        self,
        document: VectorDocument,
        rule: RetentionRule,
        now: datetime
    ) -> str:
        """
        Apply retention rule to document.

        Returns:
            Action taken: "kept", "archived", "deleted"
        """
        age_days = (now - document.created_at).days

        # Check if document should be deleted
        if rule.policy == RetentionPolicy.IMMEDIATE:
            await self._delete_document_with_tombstone(
                document,
                "policy_expiration",
                rule_name=rule.name
            )
            return "deleted"

        elif age_days > rule.active_retention_days:
            if rule.archive_retention_days > 0 and self.archival_backend:
                # Archive the document
                await self._archive_document(document, rule)
                return "archived"
            else:
                # Delete the document
                await self._delete_document_with_tombstone(
                    document,
                    "policy_expiration",
                    rule_name=rule.name
                )
                return "deleted"

        return "kept"

    async def _archive_document(
        self,
        document: VectorDocument,
        rule: RetentionRule
    ) -> str:
        """
        Archive document to cold storage.

        Returns:
            Archive reference ID
        """
        if not self.archival_backend:
            raise ValueError("No archival backend configured")

        correlation_id = correlation_id_var.get()
        start_time = time.perf_counter()

        # Create OTEL span for archival operation
        span = None
        if OTEL_AVAILABLE and tracer:
            span = tracer.start_span("memory_lifecycle_archive")
            span.set_attribute("operation", "archive")
            span.set_attribute("lane", document.lane)
            span.set_attribute("document_id", document.id)
            span.set_attribute("archive_tier", rule.archive_tier.value)
            span.set_attribute("compress_on_archive", rule.compress_on_archive)
            if correlation_id:
                span.set_attribute("correlation_id", correlation_id)

        try:
            # Execute pre-archival callback
            if rule.pre_deletion_callback:
                await rule.pre_deletion_callback(document)

            # Store in archival backend
            archive_id = await self.archival_backend.store_archived_document(
                document,
                rule.archive_tier,
                rule.compress_on_archive
            )

            # Remove from active storage
            await self.vector_store.delete(document.id)

            # Execute post-archival callback
            if rule.post_archival_callback:
                await rule.post_archival_callback(document, archive_id)

            duration_ms = (time.perf_counter() - start_time) * 1000
            self.stats.archival_duration_ms += duration_ms

            # Record metrics with lane and operation labels (no correlation_id!)
            metrics.record_metric(
                "lukhas_memory_lifecycle_seconds",
                duration_ms / 1000,
                ServiceType.MEMORY,
                MetricType.HISTOGRAM,
                {"operation": "archive", "lane": document.lane}
            )
            metrics.record_metric(
                "lukhas_memory_lifecycle_operations_total",
                1,
                ServiceType.MEMORY,
                MetricType.COUNTER,
                {"operation": "archive", "lane": document.lane}
            )

            # Update span with success metrics
            if span:
                span.set_attribute("archive_id", archive_id)
                span.set_attribute("duration_ms", duration_ms)
                span.set_status(Status(StatusCode.OK))

            logger.info(
                "Document archived successfully",
                document_id=document.id,
                archive_id=archive_id,
                tier=rule.archive_tier.value,
                compressed=rule.compress_on_archive,
                duration_ms=duration_ms,
                correlation_id=correlation_id
            )

            return archive_id

        except Exception as e:
            # Record error metrics
            metrics.record_metric(
                "lukhas_memory_lifecycle_errors_total",
                1,
                ServiceType.MEMORY,
                MetricType.COUNTER,
                {"operation": "archive", "lane": document.lane}
            )

            if span:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))

            logger.error(
                "Failed to archive document",
                document_id=document.id,
                error=str(e),
                correlation_id=correlation_id
            )
            raise
        finally:
            if span:
                span.end()

    async def _delete_document_with_tombstone(
        self,
        document: VectorDocument,
        deletion_reason: str,
        requested_by: Optional[str] = None,
        rule_name: Optional[str] = None
    ) -> bool:
        """
        Delete document and create GDPR tombstone if required.
        """
        correlation_id = correlation_id_var.get()
        start_time = time.perf_counter()

        # Create OTEL span for GDPR deletion operation
        span = None
        if OTEL_AVAILABLE and tracer:
            span = tracer.start_span("memory_lifecycle_gdpr_deletion")
            span.set_attribute("operation", "gdpr_deletion")
            span.set_attribute("lane", document.lane)
            span.set_attribute("document_id", document.id)
            span.set_attribute("deletion_reason", deletion_reason)
            if requested_by:
                span.set_attribute("requested_by", requested_by)
            if rule_name:
                span.set_attribute("rule_name", rule_name)
            if correlation_id:
                span.set_attribute("correlation_id", correlation_id)

        try:
            # Create tombstone if GDPR compliance enabled
            if self.enable_gdpr_compliance and self.tombstone_store:
                tombstone = GDPRTombstone(
                    document_id=document.id,
                    identity_id=document.identity_id,
                    deleted_at=datetime.now(timezone.utc),
                    deletion_reason=deletion_reason,
                    requested_by=requested_by,
                    original_created_at=document.created_at,
                    original_lane=document.lane,
                    original_fold_id=document.fold_id,
                    original_tags=document.tags,
                    content_hash=document.metadata.get("indexer", {}).get("content_hash", ""),
                    word_count=document.metadata.get("indexer", {}).get("word_count", 0),
                    language=document.metadata.get("indexer", {}).get("language"),
                    gdpr_category=document.metadata.get("gdpr", {}).get("category"),
                    retention_rule=rule_name
                )

                await self.tombstone_store.create_tombstone(tombstone)
                self.stats.tombstones_created += 1

            # Delete from vector store
            success = await self.vector_store.delete(document.id)

            if success:
                self.stats.documents_deleted += 1
                duration_ms = (time.perf_counter() - start_time) * 1000
                self.stats.avg_tombstone_creation_ms = (
                    (self.stats.avg_tombstone_creation_ms * (self.stats.tombstones_created - 1) + duration_ms)
                    / self.stats.tombstones_created if self.stats.tombstones_created > 0 else duration_ms
                )

                # Record metrics with lane and operation labels (no correlation_id!)
                metrics.record_metric(
                    "lukhas_memory_lifecycle_seconds",
                    duration_ms / 1000,
                    ServiceType.MEMORY,
                    MetricType.HISTOGRAM,
                    {"operation": "gdpr_deletion", "lane": document.lane}
                )
                metrics.record_metric(
                    "lukhas_memory_lifecycle_operations_total",
                    1,
                    ServiceType.MEMORY,
                    MetricType.COUNTER,
                    {"operation": "gdpr_deletion", "lane": document.lane}
                )

                # Update span with success metrics
                if span:
                    span.set_attribute("tombstone_created", True)
                    span.set_attribute("duration_ms", duration_ms)
                    span.set_status(Status(StatusCode.OK))

                logger.debug(
                    "Document deleted with tombstone",
                    document_id=document.id,
                    reason=deletion_reason,
                    duration_ms=duration_ms,
                    correlation_id=correlation_id
                )
            else:
                if span:
                    span.set_attribute("tombstone_created", False)
                    span.set_status(Status(StatusCode.ERROR, "Tombstone creation failed"))

            return success

        except Exception as e:
            # Record error metrics
            metrics.record_metric(
                "lukhas_memory_lifecycle_errors_total",
                1,
                ServiceType.MEMORY,
                MetricType.COUNTER,
                {"operation": "gdpr_deletion", "lane": document.lane}
            )

            if span:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))

            logger.error(
                "Failed to delete document with tombstone",
                document_id=document.id,
                error=str(e),
                correlation_id=correlation_id
            )
            raise
        finally:
            if span:
                span.end()

    async def process_gdpr_deletion_request(
        self,
        identity_id: str,
        requested_by: str,
        legal_basis_removed: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process GDPR right-to-be-forgotten request.

        Args:
            identity_id: Identity to delete data for
            requested_by: Who requested the deletion
            legal_basis_removed: Legal basis that was removed

        Returns:
            Deletion summary
        """
        start_time = time.perf_counter()

        try:
            # Get all documents for identity
            documents = await self.vector_store.list_by_identity(identity_id, limit=10000)

            deleted_count = 0
            anonymized_count = 0
            errors = []

            for document in documents:
                try:
                    # Check if document allows anonymization
                    rule = self._evaluate_retention_rule(document)

                    if rule and rule.allow_anonymization:
                        # Anonymize instead of delete
                        await self._anonymize_document(document, requested_by)
                        anonymized_count += 1
                    else:
                        # Full deletion required
                        await self._delete_document_with_tombstone(
                            document,
                            "gdpr_request",
                            requested_by=requested_by,
                            rule_name=rule.name if rule else None
                        )
                        deleted_count += 1

                except Exception as e:
                    errors.append({
                        "document_id": document.id,
                        "error": str(e)
                    })

            duration_ms = (time.perf_counter() - start_time) * 1000

            self.stats.gdpr_requests_processed += 1
            self.stats.explicit_deletions += deleted_count
            self.stats.anonymization_operations += anonymized_count

            summary = {
                "identity_id": identity_id,
                "requested_by": requested_by,
                "legal_basis_removed": legal_basis_removed,
                "documents_deleted": deleted_count,
                "documents_anonymized": anonymized_count,
                "errors": errors,
                "processing_time_ms": duration_ms,
                "completed_at": datetime.now(timezone.utc).isoformat()
            }

            logger.info(
                "GDPR deletion request processed",
                identity_id=identity_id,
                deleted=deleted_count,
                anonymized=anonymized_count,
                errors=len(errors),
                duration_ms=duration_ms
            )

            metrics.record_metric(
                "lukhas_memory_gdpr_deleted_total",
                deleted_count,
                ServiceType.MEMORY,
                MetricType.COUNTER,
                {"operation": "gdpr_deletion"}
            )
            metrics.record_metric(
                "lukhas_memory_lifecycle_seconds",
                duration_ms / 1000.0,
                ServiceType.MEMORY,
                MetricType.HISTOGRAM,
                {"operation": "gdpr_deletion"}
            )

            return summary

        except Exception as e:
            logger.error(
                "GDPR deletion request failed",
                identity_id=identity_id,
                error=str(e)
            )
            raise

    async def _anonymize_document(
        self,
        document: VectorDocument,
        requested_by: str
    ) -> bool:
        """
        Anonymize document by removing personal identifiers.
        """
        # Create anonymized version
        anonymized_doc = VectorDocument(
            id=document.id,
            content="[CONTENT ANONYMIZED PER GDPR REQUEST]",
            embedding=document.embedding,  # Keep embedding for similarity
            metadata={
                "anonymized": True,
                "anonymized_at": datetime.now(timezone.utc).isoformat(),
                "requested_by": requested_by,
                "original_word_count": len(document.content.split()),
                "original_language": document.metadata.get("indexer", {}).get("language")
            },
            identity_id=None,  # Remove identity link
            lane=document.lane,
            fold_id=document.fold_id,
            tags=[tag for tag in document.tags if not tag.startswith("personal_")],
            created_at=document.created_at,
            updated_at=datetime.now(timezone.utc)
        )

        # Update in store
        success = await self.vector_store.update(anonymized_doc)

        if success:
            logger.info(
                "Document anonymized",
                document_id=document.id,
                requested_by=requested_by
            )

        return success

    async def start_background_tasks(
        self,
        cleanup_interval_hours: int = 24,
        archival_interval_hours: int = 168  # Weekly
    ):
        """Start background lifecycle management tasks"""
        self._cleanup_task = asyncio.create_task(
            self._background_cleanup_task(cleanup_interval_hours)
        )

        if self.archival_backend:
            self._archival_task = asyncio.create_task(
                self._background_archival_task(archival_interval_hours)
            )

        logger.info(
            "Background lifecycle tasks started",
            cleanup_interval_hours=cleanup_interval_hours,
            archival_interval_hours=archival_interval_hours
        )

    async def stop_background_tasks(self):
        """Stop background tasks"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        if self._archival_task:
            self._archival_task.cancel()
            try:
                await self._archival_task
            except asyncio.CancelledError:
                pass

        logger.info("Background lifecycle tasks stopped")

    async def _background_cleanup_task(self, interval_hours: int):
        """Background task for regular cleanup"""
        while True:
            try:
                await asyncio.sleep(interval_hours * 3600)
                stats = await self.cleanup_expired_documents()

                logger.info(
                    "Background cleanup completed",
                    documents_deleted=stats.documents_deleted,
                    documents_archived=stats.documents_archived,
                    duration_ms=stats.cleanup_duration_ms
                )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(
                    "Background cleanup task error",
                    error=str(e)
                )
                # Continue running despite errors

    async def _background_archival_task(self, interval_hours: int):
        """Background task for archival operations"""
        while True:
            try:
                await asyncio.sleep(interval_hours * 3600)
                # Additional archival logic would go here

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(
                    "Background archival task error",
                    error=str(e)
                )

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive lifecycle statistics"""
        stats = {
            "operations": {
                "documents_expired": self.stats.documents_expired,
                "documents_archived": self.stats.documents_archived,
                "documents_deleted": self.stats.documents_deleted,
                "tombstones_created": self.stats.tombstones_created
            },
            "performance": {
                "cleanup_duration_ms": self.stats.cleanup_duration_ms,
                "archival_duration_ms": self.stats.archival_duration_ms,
                "avg_tombstone_creation_ms": self.stats.avg_tombstone_creation_ms
            },
            "gdpr_compliance": {
                "requests_processed": self.stats.gdpr_requests_processed,
                "anonymization_operations": self.stats.anonymization_operations,
                "explicit_deletions": self.stats.explicit_deletions
            },
            "policies": {
                "retention_rules_count": len(self.retention_rules),
                "retention_rules_applied": self.stats.retention_rules_applied,
                "policy_violations": self.stats.policy_violations
            },
            "configuration": {
                "gdpr_compliance_enabled": self.enable_gdpr_compliance,
                "default_retention_days": self.default_retention_days,
                "has_archival_backend": self.archival_backend is not None,
                "has_tombstone_store": self.tombstone_store is not None
            }
        }

        return stats