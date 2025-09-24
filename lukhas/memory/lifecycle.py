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
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Callable
import logging

from lukhas.memory.backends.base import VectorDocument, AbstractVectorStore
from lukhas.observability.metrics import get_metrics_collector
from lukhas.core.logging import get_logger

logger = get_logger(__name__)
metrics = get_metrics_collector()


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
    identity_id: Optional[str]

    # Deletion metadata
    deleted_at: datetime
    deletion_reason: str  # "expiration", "gdpr_request", "manual", "policy"
    requested_by: Optional[str] = None

    # Retention metadata (non-personal)
    original_created_at: datetime
    original_lane: str
    original_fold_id: Optional[str]
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
        max_documents: Optional[int] = None
    ) -> LifecycleStats:
        """
        Clean up expired documents according to retention policies.

        Args:
            batch_size: Number of documents to process per batch
            max_documents: Maximum documents to process (None = all)

        Returns:
            Cleanup statistics
        """
        start_time = time.perf_counter()
        cleanup_stats = LifecycleStats()

        try:
            # Get expired documents
            now = datetime.now(timezone.utc)

            # This would need to be implemented by the vector store
            # For now, we'll simulate with a placeholder
            expired_docs = []  # await self.vector_store.list_expired_documents(now, batch_size)

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

            # Record metrics
            metrics.record_histogram(
                "lifecycle_cleanup_duration_ms",
                cleanup_stats.cleanup_duration_ms
            )
            metrics.increment_counter(
                "lifecycle_documents_processed",
                processed_count
            )
            metrics.increment_counter(
                "lifecycle_documents_deleted",
                cleanup_stats.documents_deleted
            )

            logger.info(
                "Document cleanup completed",
                processed=processed_count,
                deleted=cleanup_stats.documents_deleted,
                archived=cleanup_stats.documents_archived,
                duration_ms=cleanup_stats.cleanup_duration_ms
            )

            return cleanup_stats

        except Exception as e:
            logger.error(
                "Document cleanup failed",
                error=str(e),
                duration_ms=(time.perf_counter() - start_time) * 1000
            )
            raise

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

        start_time = time.perf_counter()

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

            logger.info(
                "Document archived successfully",
                document_id=document.id,
                archive_id=archive_id,
                tier=rule.archive_tier.value,
                compressed=rule.compress_on_archive,
                duration_ms=duration_ms
            )

            return archive_id

        except Exception as e:
            logger.error(
                "Failed to archive document",
                document_id=document.id,
                error=str(e)
            )
            raise

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
        start_time = time.perf_counter()

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

                logger.debug(
                    "Document deleted with tombstone",
                    document_id=document.id,
                    reason=deletion_reason,
                    duration_ms=duration_ms
                )

            return success

        except Exception as e:
            logger.error(
                "Failed to delete document with tombstone",
                document_id=document.id,
                error=str(e)
            )
            raise

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

            metrics.increment_counter("lifecycle_gdpr_requests_processed")
            metrics.record_histogram("lifecycle_gdpr_processing_duration_ms", duration_ms)

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