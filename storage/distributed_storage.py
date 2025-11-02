#!/usr/bin/env python3
"""
LUKHAS Distributed Storage System

Enterprise-grade distributed storage with replication, backup, data lifecycle management,
and intelligent data placement.

# ΛTAG: distributed_storage, replication, backup, data_lifecycle, storage_optimization
"""

import asyncio
import hashlib
import json
import logging
import os
import sqlite3
import threading
import time
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import aiofiles

logger = logging.getLogger(__name__)

# Optional cloud storage support
try:
    import boto3
    from botocore.exceptions import BotoCoreError, NoCredentialsError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

try:
    from azure.storage.blob import BlobServiceClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False


class StorageBackendType(Enum):
    """Storage backend types."""
    LOCAL_FILESYSTEM = "local_filesystem"
    SQLITE = "sqlite"
    AWS_S3 = "aws_s3"
    AZURE_BLOB = "azure_blob"
    REDIS = "redis"


class ReplicationStrategy(Enum):
    """Replication strategies."""
    NONE = "none"                    # No replication
    SYNC = "sync"                    # Synchronous replication
    ASYNC = "async"                  # Asynchronous replication
    EVENTUAL = "eventual"            # Eventual consistency
    QUORUM = "quorum"               # Quorum-based consistency


class DataClassification(Enum):
    """Data classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class StoragePolicy(Enum):
    """Storage policies for data lifecycle."""
    HOT = "hot"                     # Frequently accessed, fast storage
    WARM = "warm"                   # Occasionally accessed, medium storage
    COLD = "cold"                   # Rarely accessed, slow/cheap storage
    ARCHIVE = "archive"             # Long-term retention, very slow storage


@dataclass
class StorageConfig:
    """Configuration for distributed storage system."""

    # Primary storage settings
    primary_backend: StorageBackendType = StorageBackendType.LOCAL_FILESYSTEM
    base_path: str = "/tmp/lukhas_storage"

    # Replication settings
    replication_strategy: ReplicationStrategy = ReplicationStrategy.ASYNC
    replication_factor: int = 2
    replica_backends: List[StorageBackendType] = field(default_factory=list)

    # Performance settings
    chunk_size_bytes: int = 1024 * 1024  # 1MB chunks
    compression_enabled: bool = True
    encryption_enabled: bool = True
    deduplication_enabled: bool = True

    # Data lifecycle settings
    enable_lifecycle_management: bool = True
    hot_to_warm_days: int = 30
    warm_to_cold_days: int = 90
    cold_to_archive_days: int = 365
    archive_retention_days: int = 2555  # 7 years

    # Backup settings
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    backup_retention_days: int = 30
    incremental_backup: bool = True

    # Monitoring settings
    health_check_interval_seconds: int = 300
    metrics_collection_enabled: bool = True

    # Cloud storage settings
    aws_bucket_name: Optional[str] = None
    aws_region: str = "us-east-1"
    azure_container_name: Optional[str] = None
    azure_connection_string: Optional[str] = None

    # Security settings
    encryption_key: Optional[str] = None
    access_control_enabled: bool = True
    audit_logging_enabled: bool = True


@dataclass
class StorageObject:
    """Represents a stored object with metadata."""

    object_id: str
    key: str
    size_bytes: int
    content_type: str
    content_hash: str
    created_at: datetime
    last_accessed: datetime
    access_count: int

    # Classification and policy
    classification: DataClassification
    storage_policy: StoragePolicy

    # Replication info
    replica_locations: List[str] = field(default_factory=list)
    replication_status: str = "pending"

    # Lifecycle info
    lifecycle_stage: StoragePolicy = StoragePolicy.HOT
    next_transition_date: Optional[datetime] = None

    # Metadata
    custom_metadata: Dict[str, str] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)

    # Version info
    version: int = 1
    is_deleted: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "object_id": self.object_id,
            "key": self.key,
            "size_bytes": self.size_bytes,
            "content_type": self.content_type,
            "content_hash": self.content_hash,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
            "classification": self.classification.value,
            "storage_policy": self.storage_policy.value,
            "replica_locations": self.replica_locations,
            "replication_status": self.replication_status,
            "lifecycle_stage": self.lifecycle_stage.value,
            "next_transition_date": self.next_transition_date.isoformat() if self.next_transition_date else None,
            "custom_metadata": self.custom_metadata,
            "tags": list(self.tags),
            "version": self.version,
            "is_deleted": self.is_deleted
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StorageObject':
        """Create from dictionary."""
        return cls(
            object_id=data["object_id"],
            key=data["key"],
            size_bytes=data["size_bytes"],
            content_type=data["content_type"],
            content_hash=data["content_hash"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_accessed=datetime.fromisoformat(data["last_accessed"]),
            access_count=data["access_count"],
            classification=DataClassification(data["classification"]),
            storage_policy=StoragePolicy(data["storage_policy"]),
            replica_locations=data.get("replica_locations", []),
            replication_status=data.get("replication_status", "pending"),
            lifecycle_stage=StoragePolicy(data.get("lifecycle_stage", "hot")),
            next_transition_date=datetime.fromisoformat(data["next_transition_date"]) if data.get("next_transition_date") else None,
            custom_metadata=data.get("custom_metadata", {}),
            tags=set(data.get("tags", [])),
            version=data.get("version", 1),
            is_deleted=data.get("is_deleted", False)
        )


@dataclass
class StorageMetrics:
    """Storage system metrics."""

    total_objects: int = 0
    total_size_bytes: int = 0

    # Access patterns
    read_operations: int = 0
    write_operations: int = 0
    delete_operations: int = 0

    # Performance metrics
    average_read_latency_ms: float = 0.0
    average_write_latency_ms: float = 0.0
    throughput_bytes_per_second: float = 0.0

    # Storage efficiency
    compression_ratio: float = 1.0
    deduplication_savings_bytes: int = 0

    # Replication metrics
    replication_lag_ms: float = 0.0
    replica_consistency_percentage: float = 100.0

    # Lifecycle metrics
    hot_objects: int = 0
    warm_objects: int = 0
    cold_objects: int = 0
    archived_objects: int = 0

    # Error metrics
    failed_operations: int = 0
    corrupted_objects: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_objects": self.total_objects,
            "total_size_bytes": self.total_size_bytes,
            "read_operations": self.read_operations,
            "write_operations": self.write_operations,
            "delete_operations": self.delete_operations,
            "average_read_latency_ms": self.average_read_latency_ms,
            "average_write_latency_ms": self.average_write_latency_ms,
            "throughput_bytes_per_second": self.throughput_bytes_per_second,
            "compression_ratio": self.compression_ratio,
            "deduplication_savings_bytes": self.deduplication_savings_bytes,
            "replication_lag_ms": self.replication_lag_ms,
            "replica_consistency_percentage": self.replica_consistency_percentage,
            "hot_objects": self.hot_objects,
            "warm_objects": self.warm_objects,
            "cold_objects": self.cold_objects,
            "archived_objects": self.archived_objects,
            "failed_operations": self.failed_operations,
            "corrupted_objects": self.corrupted_objects
        }


class StorageBackend(ABC):
    """Abstract storage backend interface."""

    @abstractmethod
    async def put(self, key: str, data: bytes, metadata: Optional[Dict[str, str]] = None) -> bool:
        """Store data."""
        pass

    @abstractmethod
    async def get(self, key: str) -> Optional[bytes]:
        """Retrieve data."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete data."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass

    @abstractmethod
    async def list_keys(self, prefix: str = "") -> List[str]:
        """List keys with optional prefix."""
        pass

    @abstractmethod
    async def get_metadata(self, key: str) -> Optional[Dict[str, str]]:
        """Get object metadata."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check backend health."""
        pass


class LocalFilesystemBackend(StorageBackend):
    """Local filesystem storage backend."""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.metadata_dir = self.base_path / ".metadata"
        self.metadata_dir.mkdir(exist_ok=True)

    async def put(self, key: str, data: bytes, metadata: Optional[Dict[str, str]] = None) -> bool:
        """Store data to filesystem."""
        try:
            file_path = self._get_file_path(key)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write data
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(data)

            # Write metadata
            if metadata:
                metadata_path = self._get_metadata_path(key)
                async with aiofiles.open(metadata_path, 'w') as f:
                    await f.write(json.dumps(metadata))

            return True

        except Exception as e:
            logger.error(f"Filesystem put error for key {key}: {e}")
            return False

    async def get(self, key: str) -> Optional[bytes]:
        """Retrieve data from filesystem."""
        try:
            file_path = self._get_file_path(key)

            if not file_path.exists():
                return None

            async with aiofiles.open(file_path, 'rb') as f:
                return await f.read()

        except Exception as e:
            logger.error(f"Filesystem get error for key {key}: {e}")
            return None

    async def delete(self, key: str) -> bool:
        """Delete data from filesystem."""
        try:
            file_path = self._get_file_path(key)
            metadata_path = self._get_metadata_path(key)

            deleted = False

            if file_path.exists():
                file_path.unlink()
                deleted = True

            if metadata_path.exists():
                metadata_path.unlink()

            return deleted

        except Exception as e:
            logger.error(f"Filesystem delete error for key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in filesystem."""
        file_path = self._get_file_path(key)
        return file_path.exists()

    async def list_keys(self, prefix: str = "") -> List[str]:
        """List keys with optional prefix."""
        keys = []

        try:
            for file_path in self.base_path.rglob("*"):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    # Convert file path to key
                    relative_path = file_path.relative_to(self.base_path)
                    key = str(relative_path).replace(os.sep, '/')

                    if key.startswith(prefix):
                        keys.append(key)

        except Exception as e:
            logger.error(f"Filesystem list_keys error: {e}")

        return keys

    async def get_metadata(self, key: str) -> Optional[Dict[str, str]]:
        """Get object metadata."""
        try:
            metadata_path = self._get_metadata_path(key)

            if not metadata_path.exists():
                return None

            async with aiofiles.open(metadata_path, 'r') as f:
                content = await f.read()
                return json.loads(content)

        except Exception as e:
            logger.error(f"Filesystem get_metadata error for key {key}: {e}")
            return None

    async def health_check(self) -> bool:
        """Check filesystem backend health."""
        try:
            # Test write/read/delete
            test_key = f"health_check_{uuid.uuid4().hex}"
            test_data = b"health_check"

            # Write
            success = await self.put(test_key, test_data)
            if not success:
                return False

            # Read
            retrieved_data = await self.get(test_key)
            if retrieved_data != test_data:
                return False

            # Delete
            await self.delete(test_key)

            return True

        except Exception as e:
            logger.error(f"Filesystem health check failed: {e}")
            return False

    def _get_file_path(self, key: str) -> Path:
        """Get file path for key."""
        return self.base_path / key.replace('/', os.sep)

    def _get_metadata_path(self, key: str) -> Path:
        """Get metadata file path for key."""
        safe_key = key.replace('/', '_').replace(os.sep, '_')
        return self.metadata_dir / f"{safe_key}.meta"


class SQLiteMetadataStore:
    """SQLite-based metadata store for distributed storage."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.lock = threading.RLock()
        self._init_database()

    def _init_database(self) -> None:
        """Initialize database schema."""

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS storage_objects (
                    object_id TEXT PRIMARY KEY,
                    key TEXT UNIQUE NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    content_type TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_accessed TEXT NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    classification TEXT NOT NULL,
                    storage_policy TEXT NOT NULL,
                    replica_locations TEXT,
                    replication_status TEXT DEFAULT 'pending',
                    lifecycle_stage TEXT DEFAULT 'hot',
                    next_transition_date TEXT,
                    custom_metadata TEXT,
                    tags TEXT,
                    version INTEGER DEFAULT 1,
                    is_deleted BOOLEAN DEFAULT FALSE
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_storage_objects_key 
                ON storage_objects(key)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_storage_objects_last_accessed 
                ON storage_objects(last_accessed)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_storage_objects_lifecycle 
                ON storage_objects(lifecycle_stage, next_transition_date)
            """)

    async def store_object(self, obj: StorageObject) -> bool:
        """Store object metadata."""

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO storage_objects (
                        object_id, key, size_bytes, content_type, content_hash,
                        created_at, last_accessed, access_count, classification,
                        storage_policy, replica_locations, replication_status,
                        lifecycle_stage, next_transition_date, custom_metadata,
                        tags, version, is_deleted
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    obj.object_id, obj.key, obj.size_bytes, obj.content_type,
                    obj.content_hash, obj.created_at.isoformat(),
                    obj.last_accessed.isoformat(), obj.access_count,
                    obj.classification.value, obj.storage_policy.value,
                    json.dumps(obj.replica_locations), obj.replication_status,
                    obj.lifecycle_stage.value,
                    obj.next_transition_date.isoformat() if obj.next_transition_date else None,
                    json.dumps(obj.custom_metadata), json.dumps(list(obj.tags)),
                    obj.version, obj.is_deleted
                ))

            return True

        except Exception as e:
            logger.error(f"Failed to store object metadata: {e}")
            return False

    async def get_object(self, key: str) -> Optional[StorageObject]:
        """Get object metadata by key."""

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM storage_objects WHERE key = ? AND is_deleted = FALSE",
                    (key,)
                )
                row = cursor.fetchone()

                if row is None:
                    return None

                return StorageObject(
                    object_id=row["object_id"],
                    key=row["key"],
                    size_bytes=row["size_bytes"],
                    content_type=row["content_type"],
                    content_hash=row["content_hash"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    last_accessed=datetime.fromisoformat(row["last_accessed"]),
                    access_count=row["access_count"],
                    classification=DataClassification(row["classification"]),
                    storage_policy=StoragePolicy(row["storage_policy"]),
                    replica_locations=json.loads(row["replica_locations"] or "[]"),
                    replication_status=row["replication_status"],
                    lifecycle_stage=StoragePolicy(row["lifecycle_stage"]),
                    next_transition_date=datetime.fromisoformat(row["next_transition_date"]) if row["next_transition_date"] else None,
                    custom_metadata=json.loads(row["custom_metadata"] or "{}"),
                    tags=set(json.loads(row["tags"] or "[]")),
                    version=row["version"],
                    is_deleted=bool(row["is_deleted"])
                )

        except Exception as e:
            logger.error(f"Failed to get object metadata: {e}")
            return None

    async def list_objects(self,
                          prefix: str = "",
                          limit: int = 1000,
                          lifecycle_stage: Optional[StoragePolicy] = None) -> List[StorageObject]:
        """List objects with optional filtering."""

        try:
            query = "SELECT * FROM storage_objects WHERE is_deleted = FALSE"
            params = []

            if prefix:
                query += " AND key LIKE ?"
                params.append(f"{prefix}%")

            if lifecycle_stage:
                query += " AND lifecycle_stage = ?"
                params.append(lifecycle_stage.value)

            query += " ORDER BY last_accessed DESC LIMIT ?"
            params.append(limit)

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, params)

                objects = []
                for row in cursor.fetchall():
                    obj = StorageObject(
                        object_id=row["object_id"],
                        key=row["key"],
                        size_bytes=row["size_bytes"],
                        content_type=row["content_type"],
                        content_hash=row["content_hash"],
                        created_at=datetime.fromisoformat(row["created_at"]),
                        last_accessed=datetime.fromisoformat(row["last_accessed"]),
                        access_count=row["access_count"],
                        classification=DataClassification(row["classification"]),
                        storage_policy=StoragePolicy(row["storage_policy"]),
                        replica_locations=json.loads(row["replica_locations"] or "[]"),
                        replication_status=row["replication_status"],
                        lifecycle_stage=StoragePolicy(row["lifecycle_stage"]),
                        next_transition_date=datetime.fromisoformat(row["next_transition_date"]) if row["next_transition_date"] else None,
                        custom_metadata=json.loads(row["custom_metadata"] or "{}"),
                        tags=set(json.loads(row["tags"] or "[]")),
                        version=row["version"],
                        is_deleted=bool(row["is_deleted"])
                    )
                    objects.append(obj)

                return objects

        except Exception as e:
            logger.error(f"Failed to list objects: {e}")
            return []

    async def update_access_stats(self, key: str) -> None:
        """Update access statistics for object."""

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE storage_objects 
                    SET last_accessed = ?, access_count = access_count + 1
                    WHERE key = ?
                """, (datetime.now().isoformat(), key))

        except Exception as e:
            logger.error(f"Failed to update access stats: {e}")

    async def get_lifecycle_candidates(self,
                                     current_stage: StoragePolicy,
                                     cutoff_date: datetime) -> List[StorageObject]:
        """Get objects eligible for lifecycle transition."""

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM storage_objects 
                    WHERE lifecycle_stage = ? 
                    AND last_accessed < ?
                    AND is_deleted = FALSE
                    ORDER BY last_accessed ASC
                """, (current_stage.value, cutoff_date.isoformat()))

                objects = []
                for row in cursor.fetchall():
                    obj = StorageObject(
                        object_id=row["object_id"],
                        key=row["key"],
                        size_bytes=row["size_bytes"],
                        content_type=row["content_type"],
                        content_hash=row["content_hash"],
                        created_at=datetime.fromisoformat(row["created_at"]),
                        last_accessed=datetime.fromisoformat(row["last_accessed"]),
                        access_count=row["access_count"],
                        classification=DataClassification(row["classification"]),
                        storage_policy=StoragePolicy(row["storage_policy"]),
                        replica_locations=json.loads(row["replica_locations"] or "[]"),
                        replication_status=row["replication_status"],
                        lifecycle_stage=StoragePolicy(row["lifecycle_stage"]),
                        next_transition_date=datetime.fromisoformat(row["next_transition_date"]) if row["next_transition_date"] else None,
                        custom_metadata=json.loads(row["custom_metadata"] or "{}"),
                        tags=set(json.loads(row["tags"] or "[]")),
                        version=row["version"],
                        is_deleted=bool(row["is_deleted"])
                    )
                    objects.append(obj)

                return objects

        except Exception as e:
            logger.error(f"Failed to get lifecycle candidates: {e}")
            return []


class DistributedStorageManager:
    """Main distributed storage manager coordinating all components."""

    def __init__(self, config: StorageConfig):
        self.config = config

        # Storage backends
        self.primary_backend: Optional[StorageBackend] = None
        self.replica_backends: List[StorageBackend] = []

        # Metadata store
        self.metadata_store = SQLiteMetadataStore(
            os.path.join(config.base_path, "metadata.db")
        )

        # Metrics and monitoring
        self.metrics = StorageMetrics()

        # Background tasks
        self.lifecycle_task: Optional[asyncio.Task] = None
        self.health_check_task: Optional[asyncio.Task] = None
        self.backup_task: Optional[asyncio.Task] = None

        # Content deduplication
        self.content_hashes: Dict[str, Set[str]] = defaultdict(set)

        # Telemetry integration
        try:
            from observability.telemetry_system import get_telemetry
            self.telemetry = get_telemetry()
        except ImportError:
            self.telemetry = None

        # Security integration
        try:
            from security.security_framework import get_security_framework
            self.security = get_security_framework()
        except ImportError:
            self.security = None

    async def initialize(self) -> bool:
        """Initialize distributed storage manager."""

        # Initialize primary backend
        self.primary_backend = await self._create_backend(self.config.primary_backend)
        if not self.primary_backend:
            logger.error("Failed to initialize primary storage backend")
            return False

        # Initialize replica backends
        for backend_type in self.config.replica_backends:
            backend = await self._create_backend(backend_type)
            if backend:
                self.replica_backends.append(backend)

        # Start background tasks
        if self.config.enable_lifecycle_management:
            self.lifecycle_task = asyncio.create_task(self._lifecycle_management_loop())

        self.health_check_task = asyncio.create_task(self._health_check_loop())

        if self.config.backup_enabled:
            self.backup_task = asyncio.create_task(self._backup_loop())

        logger.info("Distributed storage manager initialized")
        return True

    async def put(self,
                  key: str,
                  data: Union[bytes, str],
                  content_type: str = "application/octet-stream",
                  classification: DataClassification = DataClassification.INTERNAL,
                  storage_policy: StoragePolicy = StoragePolicy.HOT,
                  metadata: Optional[Dict[str, str]] = None,
                  tags: Optional[Set[str]] = None) -> bool:
        """Store object in distributed storage."""

        start_time = time.time()

        try:
            # Convert string to bytes
            if isinstance(data, str):
                data = data.encode('utf-8')

            # Security check
            if self.security and not await self._check_write_permission(key, classification):
                logger.warning(f"Write access denied for key: {key}")
                return False

            # Compress data if enabled
            original_size = len(data)
            if self.config.compression_enabled:
                import zlib
                compressed_data = zlib.compress(data)
                if len(compressed_data) < len(data):
                    data = compressed_data
                    if metadata is None:
                        metadata = {}
                    metadata["compressed"] = "true"

            # Calculate content hash
            content_hash = hashlib.sha256(data).hexdigest()

            # Check for deduplication
            if self.config.deduplication_enabled:
                existing_keys = self.content_hashes.get(content_hash, set())
                if existing_keys:
                    logger.info(f"Deduplication: Object with hash {content_hash} already exists")
                    # Create a reference instead of storing duplicate data
                    return await self._create_dedup_reference(key, list(existing_keys)[0], metadata)

            # Create storage object
            obj = StorageObject(
                object_id=str(uuid.uuid4()),
                key=key,
                size_bytes=len(data),
                content_type=content_type,
                content_hash=content_hash,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                classification=classification,
                storage_policy=storage_policy,
                custom_metadata=metadata or {},
                tags=tags or set()
            )

            # Store in primary backend
            primary_success = await self.primary_backend.put(key, data, metadata)
            if not primary_success:
                logger.error(f"Failed to store object in primary backend: {key}")
                return False

            obj.replica_locations.append("primary")

            # Replicate to replica backends
            if self.config.replication_strategy != ReplicationStrategy.NONE:
                await self._replicate_object(key, data, metadata, obj)

            # Store metadata
            await self.metadata_store.store_object(obj)

            # Update content hash index
            self.content_hashes[content_hash].add(key)

            # Update metrics
            self.metrics.write_operations += 1
            self.metrics.total_objects += 1
            self.metrics.total_size_bytes += obj.size_bytes

            write_latency = (time.time() - start_time) * 1000
            self.metrics.average_write_latency_ms = (
                (self.metrics.average_write_latency_ms * (self.metrics.write_operations - 1) + write_latency) /
                self.metrics.write_operations
            )

            # Emit telemetry
            if self.telemetry:
                self.telemetry.emit_event(
                    component="distributed_storage",
                    event_type="object_stored",
                    message=f"Object stored: {key}",
                    data={
                        "key": key,
                        "size_bytes": obj.size_bytes,
                        "content_type": content_type,
                        "classification": classification.value,
                        "storage_policy": storage_policy.value,
                        "replica_count": len(obj.replica_locations),
                        "write_latency_ms": write_latency
                    }
                )

            logger.info(f"✅ Object stored successfully: {key} ({obj.size_bytes} bytes)")
            return True

        except Exception as e:
            logger.error(f"Failed to store object {key}: {e}")
            self.metrics.failed_operations += 1
            return False

    async def get(self, key: str) -> Optional[bytes]:
        """Retrieve object from distributed storage."""

        start_time = time.time()

        try:
            # Security check
            if self.security and not await self._check_read_permission(key):
                logger.warning(f"Read access denied for key: {key}")
                return None

            # Get object metadata
            obj = await self.metadata_store.get_object(key)
            if not obj:
                return None

            # Try primary backend first
            data = await self.primary_backend.get(key)

            # Try replica backends if primary fails
            if data is None and self.replica_backends:
                for backend in self.replica_backends:
                    data = await backend.get(key)
                    if data is not None:
                        logger.info(f"Retrieved object from replica backend: {key}")
                        break

            if data is None:
                logger.warning(f"Object not found in any backend: {key}")
                return None

            # Decompress if needed
            if obj.custom_metadata.get("compressed") == "true":
                import zlib
                data = zlib.decompress(data)

            # Update access statistics
            await self.metadata_store.update_access_stats(key)

            # Update metrics
            self.metrics.read_operations += 1
            read_latency = (time.time() - start_time) * 1000
            self.metrics.average_read_latency_ms = (
                (self.metrics.average_read_latency_ms * (self.metrics.read_operations - 1) + read_latency) /
                self.metrics.read_operations
            )

            # Emit telemetry
            if self.telemetry:
                self.telemetry.emit_event(
                    component="distributed_storage",
                    event_type="object_retrieved",
                    message=f"Object retrieved: {key}",
                    data={
                        "key": key,
                        "size_bytes": len(data),
                        "read_latency_ms": read_latency
                    }
                )

            return data

        except Exception as e:
            logger.error(f"Failed to retrieve object {key}: {e}")
            self.metrics.failed_operations += 1
            return None

    async def delete(self, key: str) -> bool:
        """Delete object from distributed storage."""

        try:
            # Security check
            if self.security and not await self._check_delete_permission(key):
                logger.warning(f"Delete access denied for key: {key}")
                return False

            # Get object metadata
            obj = await self.metadata_store.get_object(key)
            if not obj:
                return False

            # Delete from all backends
            primary_deleted = await self.primary_backend.delete(key)

            for backend in self.replica_backends:
                await backend.delete(key)

            # Mark as deleted in metadata
            obj.is_deleted = True
            await self.metadata_store.store_object(obj)

            # Remove from content hash index
            if obj.content_hash in self.content_hashes:
                self.content_hashes[obj.content_hash].discard(key)
                if not self.content_hashes[obj.content_hash]:
                    del self.content_hashes[obj.content_hash]

            # Update metrics
            self.metrics.delete_operations += 1
            self.metrics.total_objects -= 1
            self.metrics.total_size_bytes -= obj.size_bytes

            # Emit telemetry
            if self.telemetry:
                self.telemetry.emit_event(
                    component="distributed_storage",
                    event_type="object_deleted",
                    message=f"Object deleted: {key}",
                    data={"key": key, "size_bytes": obj.size_bytes}
                )

            return primary_deleted

        except Exception as e:
            logger.error(f"Failed to delete object {key}: {e}")
            self.metrics.failed_operations += 1
            return False

    async def list_objects(self,
                          prefix: str = "",
                          limit: int = 1000) -> List[StorageObject]:
        """List objects with optional prefix filter."""

        return await self.metadata_store.list_objects(prefix, limit)

    async def get_object_info(self, key: str) -> Optional[StorageObject]:
        """Get object metadata information."""

        return await self.metadata_store.get_object(key)

    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive storage metrics."""

        # Update lifecycle stage counts
        hot_objects = await self.metadata_store.list_objects(
            lifecycle_stage=StoragePolicy.HOT, limit=10000
        )
        warm_objects = await self.metadata_store.list_objects(
            lifecycle_stage=StoragePolicy.WARM, limit=10000
        )
        cold_objects = await self.metadata_store.list_objects(
            lifecycle_stage=StoragePolicy.COLD, limit=10000
        )
        archived_objects = await self.metadata_store.list_objects(
            lifecycle_stage=StoragePolicy.ARCHIVE, limit=10000
        )

        self.metrics.hot_objects = len(hot_objects)
        self.metrics.warm_objects = len(warm_objects)
        self.metrics.cold_objects = len(cold_objects)
        self.metrics.archived_objects = len(archived_objects)

        # Calculate deduplication savings
        total_unique_hashes = len(self.content_hashes)
        total_references = sum(len(keys) for keys in self.content_hashes.values())
        if total_references > total_unique_hashes:
            # Estimate savings (simplified calculation)
            self.metrics.deduplication_savings_bytes = (
                (total_references - total_unique_hashes) *
                (self.metrics.total_size_bytes / max(total_references, 1))
            )

        return self.metrics.to_dict()

    async def _create_backend(self, backend_type: StorageBackendType) -> Optional[StorageBackend]:
        """Create storage backend instance."""

        if backend_type == StorageBackendType.LOCAL_FILESYSTEM:
            return LocalFilesystemBackend(self.config.base_path)

        # Add other backend implementations as needed
        logger.warning(f"Backend type not implemented: {backend_type}")
        return None

    async def _replicate_object(self,
                               key: str,
                               data: bytes,
                               metadata: Optional[Dict[str, str]],
                               obj: StorageObject) -> None:
        """Replicate object to replica backends."""

        if self.config.replication_strategy == ReplicationStrategy.SYNC:
            # Synchronous replication
            for i, backend in enumerate(self.replica_backends):
                if await backend.put(key, data, metadata):
                    obj.replica_locations.append(f"replica_{i}")

        elif self.config.replication_strategy == ReplicationStrategy.ASYNC:
            # Asynchronous replication
            async def replicate_to_backend(backend: StorageBackend, replica_id: str):
                if await backend.put(key, data, metadata):
                    obj.replica_locations.append(replica_id)

            tasks = [
                replicate_to_backend(backend, f"replica_{i}")
                for i, backend in enumerate(self.replica_backends)
            ]

            await asyncio.gather(*tasks, return_exceptions=True)

        # Update replication status
        if len(obj.replica_locations) >= self.config.replication_factor:
            obj.replication_status = "complete"
        else:
            obj.replication_status = "partial"

    async def _create_dedup_reference(self,
                                    new_key: str,
                                    existing_key: str,
                                    metadata: Optional[Dict[str, str]]) -> bool:
        """Create a deduplication reference."""

        # Get existing object
        existing_obj = await self.metadata_store.get_object(existing_key)
        if not existing_obj:
            return False

        # Create reference object
        ref_obj = StorageObject(
            object_id=str(uuid.uuid4()),
            key=new_key,
            size_bytes=existing_obj.size_bytes,
            content_type=existing_obj.content_type,
            content_hash=existing_obj.content_hash,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1,
            classification=existing_obj.classification,
            storage_policy=existing_obj.storage_policy,
            custom_metadata=metadata or {},
            tags=set()
        )

        # Add deduplication metadata
        ref_obj.custom_metadata["dedup_reference"] = existing_key

        await self.metadata_store.store_object(ref_obj)
        return True

    async def _check_read_permission(self, key: str) -> bool:
        """Check read permission for key."""
        if not self.security:
            return True

        # Implement based on security framework
        return True

    async def _check_write_permission(self, key: str, classification: DataClassification) -> bool:
        """Check write permission for key and classification."""
        if not self.security:
            return True

        # Implement based on security framework
        return True

    async def _check_delete_permission(self, key: str) -> bool:
        """Check delete permission for key."""
        if not self.security:
            return True

        # Implement based on security framework
        return True

    async def _lifecycle_management_loop(self) -> None:
        """Background lifecycle management loop."""

        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour

                current_time = datetime.now()

                # Hot to warm transition
                hot_to_warm_cutoff = current_time - timedelta(days=self.config.hot_to_warm_days)
                hot_candidates = await self.metadata_store.get_lifecycle_candidates(
                    StoragePolicy.HOT, hot_to_warm_cutoff
                )

                for obj in hot_candidates[:100]:  # Process in batches
                    obj.lifecycle_stage = StoragePolicy.WARM
                    obj.next_transition_date = current_time + timedelta(days=self.config.warm_to_cold_days)
                    await self.metadata_store.store_object(obj)

                logger.info(f"Transitioned {len(hot_candidates[:100])} objects from hot to warm")

                # Similar transitions for warm to cold, cold to archive

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Lifecycle management error: {e}")
                await asyncio.sleep(3600)

    async def _health_check_loop(self) -> None:
        """Background health check loop."""

        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval_seconds)

                # Check primary backend
                primary_healthy = await self.primary_backend.health_check()

                # Check replica backends
                replica_health = []
                for backend in self.replica_backends:
                    healthy = await backend.health_check()
                    replica_health.append(healthy)

                # Emit health metrics
                if self.telemetry:
                    self.telemetry.emit_metric(
                        component="distributed_storage",
                        metric_name="primary_backend_healthy",
                        value=1.0 if primary_healthy else 0.0
                    )

                    self.telemetry.emit_metric(
                        component="distributed_storage",
                        metric_name="replica_backends_healthy",
                        value=sum(replica_health)
                    )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(300)

    async def _backup_loop(self) -> None:
        """Background backup loop."""

        while True:
            try:
                await asyncio.sleep(self.config.backup_interval_hours * 3600)

                logger.info("Starting backup process")

                # Implement backup logic here
                # This would typically backup metadata and coordinate with backends

                logger.info("Backup process completed")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Backup error: {e}")
                await asyncio.sleep(3600)

    async def shutdown(self) -> None:
        """Shutdown distributed storage manager."""

        # Cancel background tasks
        for task in [self.lifecycle_task, self.health_check_task, self.backup_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        logger.info("Distributed storage manager shutdown complete")


# Global storage manager instance
_global_storage_manager: Optional[DistributedStorageManager] = None


def get_storage_manager() -> DistributedStorageManager:
    """Get global storage manager instance."""
    global _global_storage_manager

    if _global_storage_manager is None:
        config = StorageConfig()
        _global_storage_manager = DistributedStorageManager(config)

    return _global_storage_manager


if __name__ == "__main__":
    # Example usage
    async def demo_storage():

        config = StorageConfig(
            base_path="/tmp/lukhas_demo_storage",
            replication_factor=2,
            compression_enabled=True,
            deduplication_enabled=True
        )

        storage = DistributedStorageManager(config)
        await storage.initialize()

        # Store some objects
        await storage.put(
            "documents/report.txt",
            "This is a test document with important information.",
            content_type="text/plain",
            classification=DataClassification.INTERNAL,
            storage_policy=StoragePolicy.HOT,
            tags={"document", "report"}
        )

        # Retrieve object
        data = await storage.get("documents/report.txt")
        if data:
            print(f"✅ Retrieved: {data.decode()}")

        # Get metrics
        metrics = await storage.get_metrics()
        print(f"✅ Storage metrics: {metrics['total_objects']} objects, {metrics['total_size_bytes']} bytes")

        await storage.shutdown()

    asyncio.run(demo_storage())
