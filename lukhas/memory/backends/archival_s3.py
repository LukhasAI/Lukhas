#!/usr/bin/env python3
"""
T4/0.01% Excellence S3 Archival Backend
=====================================

Production-grade archival storage backend with S3/local file system support,
gzip compression, and manifest tracking for GDPR compliance.

Features:
- S3 and local filesystem storage
- Gzip compression for storage efficiency
- JSON manifest tracking with metadata
- Atomic operations with rollback
- Performance optimized for large archives

Performance Targets:
- Archival: <30s for 100k documents
- Manifest updates: <100ms p95
- Compression ratio: >70% for text documents
- Retrieval: <5s from cold storage

Author: LUKHAS AI System
Version: 1.0.0
Phase: Memory Lifecycle Production Grade
"""

import asyncio
import gzip
import hashlib
import json
import shutil
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4
import numpy as np

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

from lukhas.memory.lifecycle import AbstractArchivalBackend, ArchivalTier
from lukhas.memory.backends.base import VectorDocument
from lukhas.observability.service_metrics import get_metrics_collector
from lukhas.core.common.logger import get_logger

logger = get_logger(__name__)
metrics = get_metrics_collector()


@dataclass
class ArchivalManifestEntry:
    """Manifest entry for archived documents"""
    document_id: str
    archive_id: str
    original_size_bytes: int
    compressed_size_bytes: int
    compression_ratio: float
    tier: ArchivalTier
    archived_at: datetime
    expires_at: Optional[datetime]
    checksum_sha256: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ArchivalManifest:
    """Archive manifest for GDPR compliance and tracking"""
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    total_documents: int = 0
    total_size_bytes: int = 0
    total_compressed_bytes: int = 0
    entries: Dict[str, ArchivalManifestEntry] = field(default_factory=dict)

    def add_entry(self, entry: ArchivalManifestEntry):
        """Add entry to manifest with statistics update"""
        self.entries[entry.document_id] = entry
        self.total_documents += 1
        self.total_size_bytes += entry.original_size_bytes
        self.total_compressed_bytes += entry.compressed_size_bytes
        self.updated_at = datetime.now(timezone.utc)

    def remove_entry(self, document_id: str):
        """Remove entry from manifest with statistics update"""
        if document_id in self.entries:
            entry = self.entries[document_id]
            del self.entries[document_id]
            self.total_documents -= 1
            self.total_size_bytes -= entry.original_size_bytes
            self.total_compressed_bytes -= entry.compressed_size_bytes
            self.updated_at = datetime.now(timezone.utc)

    @property
    def compression_ratio(self) -> float:
        """Calculate overall compression ratio"""
        if self.total_size_bytes == 0:
            return 0.0
        return 1.0 - (self.total_compressed_bytes / self.total_size_bytes)


class LocalFileSystemArchivalBackend(AbstractArchivalBackend):
    """
    Local filesystem archival backend with gzip compression.

    Suitable for single-node deployments or shared filesystem environments.
    """

    def __init__(
        self,
        archive_root: Path,
        enable_compression: bool = True,
        manifest_update_interval: int = 100  # Update manifest every N operations
    ):
        self.archive_root = Path(archive_root)
        self.enable_compression = enable_compression
        self.manifest_update_interval = manifest_update_interval

        # Create directory structure
        self.archive_root.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.archive_root / "manifest.json"

        # Initialize manifest
        self._manifest: Optional[ArchivalManifest] = None
        self._manifest_lock = asyncio.Lock()
        self._operations_since_manifest_update = 0

    async def _load_manifest(self) -> ArchivalManifest:
        """Load manifest from disk"""
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path, 'r') as f:
                    data = json.load(f)

                # Convert string dates back to datetime objects
                manifest = ArchivalManifest(
                    version=data["version"],
                    created_at=datetime.fromisoformat(data["created_at"]),
                    updated_at=datetime.fromisoformat(data["updated_at"]),
                    total_documents=data["total_documents"],
                    total_size_bytes=data["total_size_bytes"],
                    total_compressed_bytes=data["total_compressed_bytes"]
                )

                # Load entries
                for doc_id, entry_data in data["entries"].items():
                    entry = ArchivalManifestEntry(
                        document_id=entry_data["document_id"],
                        archive_id=entry_data["archive_id"],
                        original_size_bytes=entry_data["original_size_bytes"],
                        compressed_size_bytes=entry_data["compressed_size_bytes"],
                        compression_ratio=entry_data["compression_ratio"],
                        tier=ArchivalTier(entry_data["tier"]),
                        archived_at=datetime.fromisoformat(entry_data["archived_at"]),
                        expires_at=datetime.fromisoformat(entry_data["expires_at"]) if entry_data["expires_at"] else None,
                        checksum_sha256=entry_data["checksum_sha256"],
                        metadata=entry_data.get("metadata", {})
                    )
                    manifest.entries[doc_id] = entry

                return manifest

            except Exception as e:
                logger.warning(f"Failed to load manifest, creating new one: {e}")

        return ArchivalManifest()

    async def _save_manifest(self, manifest: ArchivalManifest):
        """Save manifest to disk atomically"""
        # Convert to serializable format
        data = {
            "version": manifest.version,
            "created_at": manifest.created_at.isoformat(),
            "updated_at": manifest.updated_at.isoformat(),
            "total_documents": manifest.total_documents,
            "total_size_bytes": manifest.total_size_bytes,
            "total_compressed_bytes": manifest.total_compressed_bytes,
            "entries": {}
        }

        for doc_id, entry in manifest.entries.items():
            data["entries"][doc_id] = {
                "document_id": entry.document_id,
                "archive_id": entry.archive_id,
                "original_size_bytes": entry.original_size_bytes,
                "compressed_size_bytes": entry.compressed_size_bytes,
                "compression_ratio": entry.compression_ratio,
                "tier": entry.tier.value,
                "archived_at": entry.archived_at.isoformat(),
                "expires_at": entry.expires_at.isoformat() if entry.expires_at else None,
                "checksum_sha256": entry.checksum_sha256,
                "metadata": entry.metadata
            }

        # Atomic write with backup
        temp_path = self.manifest_path.with_suffix('.tmp')
        backup_path = self.manifest_path.with_suffix('.bak')

        try:
            # Write to temp file
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2)

            # Backup existing manifest
            if self.manifest_path.exists():
                shutil.copy2(self.manifest_path, backup_path)

            # Atomic move
            temp_path.rename(self.manifest_path)

            # Clean up backup after successful write
            if backup_path.exists():
                backup_path.unlink()

        except Exception as e:
            # Restore from backup if needed
            if backup_path.exists() and not self.manifest_path.exists():
                backup_path.rename(self.manifest_path)

            # Clean up temp file
            if temp_path.exists():
                temp_path.unlink()

            raise RuntimeError(f"Failed to save manifest: {e}")

    async def _get_manifest(self) -> ArchivalManifest:
        """Get manifest with lazy loading"""
        async with self._manifest_lock:
            if self._manifest is None:
                self._manifest = await self._load_manifest()
            return self._manifest

    async def _update_manifest_if_needed(self):
        """Update manifest to disk if update interval reached"""
        self._operations_since_manifest_update += 1

        if self._operations_since_manifest_update >= self.manifest_update_interval:
            manifest = await self._get_manifest()
            await self._save_manifest(manifest)
            self._operations_since_manifest_update = 0

    async def store_archived_document(
        self,
        document: VectorDocument,
        tier: ArchivalTier,
        compress: bool = True
    ) -> str:
        """Store document in local filesystem archive"""
        start_time = time.perf_counter()

        try:
            # Generate unique archive ID
            archive_id = f"{document.id}_{uuid4().hex[:8]}"

            # Serialize document
            document_data = {
                "id": document.id,
                "content": document.content,
                "embedding": document.embedding.tolist(),
                "metadata": document.metadata,
                "identity_id": document.identity_id,
                "lane": document.lane,
                "fold_id": document.fold_id,
                "tags": document.tags,
                "created_at": document.created_at.isoformat(),
                "updated_at": document.updated_at.isoformat(),
                "expires_at": document.expires_at.isoformat() if document.expires_at else None,
                "access_count": document.access_count,
                "last_accessed": document.last_accessed.isoformat() if document.last_accessed else None
            }

            document_json = json.dumps(document_data, indent=2).encode('utf-8')
            original_size = len(document_json)

            # Apply compression if enabled
            if compress and self.enable_compression:
                compressed_data = gzip.compress(document_json, compresslevel=6)
                file_extension = ".json.gz"
            else:
                compressed_data = document_json
                file_extension = ".json"

            compressed_size = len(compressed_data)
            compression_ratio = 1.0 - (compressed_size / original_size) if original_size > 0 else 0.0

            # Create tier directory
            tier_dir = self.archive_root / tier.value
            tier_dir.mkdir(exist_ok=True)

            # Write archived document
            archive_path = tier_dir / f"{archive_id}{file_extension}"
            with open(archive_path, 'wb') as f:
                f.write(compressed_data)

            # Calculate checksum
            checksum = hashlib.sha256(compressed_data).hexdigest()

            # Update manifest
            manifest = await self._get_manifest()
            entry = ArchivalManifestEntry(
                document_id=document.id,
                archive_id=archive_id,
                original_size_bytes=original_size,
                compressed_size_bytes=compressed_size,
                compression_ratio=compression_ratio,
                tier=tier,
                archived_at=datetime.now(timezone.utc),
                expires_at=document.expires_at,
                checksum_sha256=checksum
            )
            manifest.add_entry(entry)

            # Update manifest to disk periodically
            await self._update_manifest_if_needed()

            # Record metrics
            duration_ms = (time.perf_counter() - start_time) * 1000

            metrics.histogram(
                "lukhas_memory_archival_duration_ms",
                duration_ms,
                {"tier": tier.value, "compressed": str(compress)}
            )

            metrics.histogram(
                "lukhas_memory_archival_compression_ratio",
                compression_ratio,
                {"tier": tier.value}
            )

            metrics.counter(
                "lukhas_memory_archived_total",
                {"tier": tier.value}
            )

            logger.info(
                "Document archived successfully",
                document_id=document.id,
                archive_id=archive_id,
                tier=tier.value,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                duration_ms=duration_ms
            )

            return archive_id

        except Exception as e:
            metrics.counter("lukhas_memory_archival_errors_total", {"tier": tier.value})
            logger.error(f"Failed to archive document {document.id}: {e}")
            raise

    async def retrieve_archived_document(
        self,
        archive_id: str
    ) -> Optional[VectorDocument]:
        """Retrieve document from local filesystem archive"""
        start_time = time.perf_counter()

        try:
            manifest = await self._get_manifest()

            # Find the document in manifest
            entry = None
            for doc_entry in manifest.entries.values():
                if doc_entry.archive_id == archive_id:
                    entry = doc_entry
                    break

            if not entry:
                return None

            # Construct file path
            tier_dir = self.archive_root / entry.tier.value

            # Try both compressed and uncompressed versions
            for extension in [".json.gz", ".json"]:
                archive_path = tier_dir / f"{archive_id}{extension}"

                if archive_path.exists():
                    # Read file
                    with open(archive_path, 'rb') as f:
                        file_data = f.read()

                    # Decompress if needed
                    if extension == ".json.gz":
                        document_json = gzip.decompress(file_data).decode('utf-8')
                    else:
                        document_json = file_data.decode('utf-8')

                    # Parse document
                    document_data = json.loads(document_json)

                    # Reconstruct VectorDocument
                    document = VectorDocument(
                        id=document_data["id"],
                        content=document_data["content"],
                        embedding=np.array(document_data["embedding"], dtype=np.float32),
                        metadata=document_data["metadata"],
                        identity_id=document_data["identity_id"],
                        lane=document_data["lane"],
                        fold_id=document_data["fold_id"],
                        tags=document_data["tags"],
                        created_at=datetime.fromisoformat(document_data["created_at"]),
                        updated_at=datetime.fromisoformat(document_data["updated_at"]),
                        expires_at=datetime.fromisoformat(document_data["expires_at"]) if document_data["expires_at"] else None,
                        access_count=document_data["access_count"],
                        last_accessed=datetime.fromisoformat(document_data["last_accessed"]) if document_data["last_accessed"] else None
                    )

                    # Record metrics
                    duration_ms = (time.perf_counter() - start_time) * 1000
                    metrics.histogram(
                        "lukhas_memory_retrieval_duration_ms",
                        duration_ms,
                        {"tier": entry.tier.value, "source": "archive"}
                    )

                    return document

            return None

        except Exception as e:
            metrics.counter("lukhas_memory_retrieval_errors_total", {"source": "archive"})
            logger.error(f"Failed to retrieve archived document {archive_id}: {e}")
            raise

    async def delete_archived_document(self, archive_id: str) -> bool:
        """Delete document from local filesystem archive"""
        try:
            manifest = await self._get_manifest()

            # Find the document in manifest
            entry = None
            doc_id = None
            for document_id, doc_entry in manifest.entries.items():
                if doc_entry.archive_id == archive_id:
                    entry = doc_entry
                    doc_id = document_id
                    break

            if not entry:
                return False

            # Delete file
            tier_dir = self.archive_root / entry.tier.value
            deleted = False

            for extension in [".json.gz", ".json"]:
                archive_path = tier_dir / f"{archive_id}{extension}"
                if archive_path.exists():
                    archive_path.unlink()
                    deleted = True

            if deleted:
                # Remove from manifest
                manifest.remove_entry(doc_id)
                await self._save_manifest(manifest)

                metrics.counter("lukhas_memory_gdpr_deleted_total", {"source": "archive"})

                logger.info(
                    "Archived document deleted",
                    archive_id=archive_id,
                    document_id=doc_id
                )

            return deleted

        except Exception as e:
            logger.error(f"Failed to delete archived document {archive_id}: {e}")
            return False


class S3ArchivalBackend(AbstractArchivalBackend):
    """
    S3-based archival backend with intelligent storage class selection.

    Automatically selects appropriate S3 storage class based on ArchivalTier.
    """

    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region: str = "us-east-1",
        prefix: str = "lukhas-archive/"
    ):
        if not BOTO3_AVAILABLE:
            raise RuntimeError("boto3 is required for S3ArchivalBackend")

        self.bucket_name = bucket_name
        self.prefix = prefix

        # Initialize S3 client
        session_kwargs = {"region_name": region}
        if aws_access_key_id and aws_secret_access_key:
            session_kwargs["aws_access_key_id"] = aws_access_key_id
            session_kwargs["aws_secret_access_key"] = aws_secret_access_key

        self.s3_client = boto3.client("s3", **session_kwargs)

        # Storage class mapping
        self.storage_class_mapping = {
            ArchivalTier.HOT: "STANDARD",
            ArchivalTier.WARM: "STANDARD_IA",
            ArchivalTier.COLD: "GLACIER",
            ArchivalTier.FROZEN: "DEEP_ARCHIVE"
        }

    def _get_s3_key(self, archive_id: str, tier: ArchivalTier) -> str:
        """Generate S3 key for archived document"""
        return f"{self.prefix}{tier.value}/{archive_id}.json.gz"

    async def store_archived_document(
        self,
        document: VectorDocument,
        tier: ArchivalTier,
        compress: bool = True
    ) -> str:
        """Store document in S3 archive"""
        start_time = time.perf_counter()

        try:
            # Generate unique archive ID
            archive_id = f"{document.id}_{uuid4().hex[:8]}"

            # Serialize and compress document (S3 always uses compression for efficiency)
            document_data = asdict(document)
            document_data["embedding"] = document.embedding.tolist()
            document_json = json.dumps(document_data).encode('utf-8')
            compressed_data = gzip.compress(document_json, compresslevel=6)

            # Upload to S3
            s3_key = self._get_s3_key(archive_id, tier)
            storage_class = self.storage_class_mapping[tier]

            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=compressed_data,
                    StorageClass=storage_class,
                    ContentType="application/gzip",
                    Metadata={
                        "document-id": document.id,
                        "archive-id": archive_id,
                        "tier": tier.value,
                        "original-size": str(len(document_json)),
                        "compressed-size": str(len(compressed_data))
                    }
                )
            )

            # Record metrics
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.histogram(
                "lukhas_memory_archival_duration_ms",
                duration_ms,
                {"tier": tier.value, "backend": "s3"}
            )

            compression_ratio = 1.0 - (len(compressed_data) / len(document_json))
            metrics.histogram(
                "lukhas_memory_archival_compression_ratio",
                compression_ratio,
                {"tier": tier.value}
            )

            logger.info(
                "Document archived to S3",
                document_id=document.id,
                archive_id=archive_id,
                tier=tier.value,
                storage_class=storage_class,
                s3_key=s3_key
            )

            return archive_id

        except ClientError as e:
            metrics.counter("lukhas_memory_archival_errors_total", {"backend": "s3", "error": "client"})
            logger.error(f"S3 client error archiving document: {e}")
            raise
        except Exception as e:
            metrics.counter("lukhas_memory_archival_errors_total", {"backend": "s3", "error": "unknown"})
            logger.error(f"Failed to archive document to S3: {e}")
            raise

    async def retrieve_archived_document(
        self,
        archive_id: str
    ) -> Optional[VectorDocument]:
        """Retrieve document from S3 archive"""
        # Note: This is a simplified implementation
        # In production, you'd need to search across all tiers
        # or maintain a separate index
        raise NotImplementedError("S3 retrieval requires tier information or separate indexing")

    async def delete_archived_document(self, archive_id: str) -> bool:
        """Delete document from S3 archive"""
        # Note: This is a simplified implementation
        # In production, you'd need to search across all tiers
        # or maintain a separate index
        raise NotImplementedError("S3 deletion requires tier information or separate indexing")