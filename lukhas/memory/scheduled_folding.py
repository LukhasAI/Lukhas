#!/usr/bin/env python3
"""
LUKHAS Scheduled Memory Folding System
Enhanced folding with LRU eviction, compression, and background scheduling.

Features:
- LRU-based fold eviction for optimal memory usage
- Content compression and deduplication
- Background scheduling with configurable intervals
- Fold health monitoring and adaptive consolidation
- Integration with adaptive memory system
"""

import hashlib
import json
import threading
import zlib
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from enum import Enum

from .adaptive_memory import MemoryFold, MemoryItem, MemoryType


class FoldStatus(Enum):
    """Status of memory folds"""
    ACTIVE = "active"
    SCHEDULED = "scheduled"
    COMPRESSED = "compressed"
    EVICTED = "evicted"
    ERROR = "error"


class CompressionLevel(Enum):
    """Compression levels for fold storage"""
    NONE = 0
    LIGHT = 1
    MEDIUM = 6
    HEAVY = 9


@dataclass
class FoldMetrics:
    """Metrics for fold performance tracking"""
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    compression_ratio: float = 1.0
    consolidation_count: int = 0
    size_bytes: int = 0
    item_count: int = 0


@dataclass
class ScheduledFold:
    """Enhanced memory fold with scheduling and compression"""
    fold: MemoryFold
    status: FoldStatus = FoldStatus.ACTIVE
    metrics: FoldMetrics = field(default_factory=FoldMetrics)
    compressed_data: Optional[bytes] = None
    compression_level: CompressionLevel = CompressionLevel.NONE
    content_hash: Optional[str] = None
    dependencies: Set[str] = field(default_factory=set)
    tags: Set[str] = field(default_factory=set)

    def __post_init__(self):
        """Initialize fold metadata"""
        if not self.content_hash:
            self._calculate_content_hash()
        self._update_metrics()

    def _calculate_content_hash(self):
        """Calculate content hash for deduplication"""
        content_str = json.dumps(
            [str(item.content) for item in self.fold.items],
            sort_keys=True
        )
        self.content_hash = hashlib.sha256(content_str.encode()).hexdigest()[:16]

    def _update_metrics(self):
        """Update fold metrics"""
        self.metrics.item_count = len(self.fold.items)
        self.metrics.size_bytes = sum(
            len(str(item.content)) for item in self.fold.items
        )

    def compress(self, level: CompressionLevel = CompressionLevel.MEDIUM) -> bool:
        """Compress fold content"""
        try:
            if self.status == FoldStatus.COMPRESSED:
                return True

            # Serialize fold items
            data = {
                "items": [
                    {
                        "id": item.id,
                        "content": item.content,
                        "timestamp": item.timestamp.isoformat(),
                        "memory_type": item.memory_type.value,
                        "importance": item.importance,
                        "context_tags": item.context_tags,
                        "causal_chain": item.causal_chain,
                    }
                    for item in self.fold.items
                ],
                "metadata": {
                    "created": self.fold.created.isoformat(),
                    "size_bytes": self.fold.size_bytes,
                }
            }

            # Compress data
            json_data = json.dumps(data, separators=(',', ':')).encode()
            self.compressed_data = zlib.compress(json_data, level.value)

            # Calculate compression ratio
            original_size = len(json_data)
            compressed_size = len(self.compressed_data)
            self.metrics.compression_ratio = compressed_size / original_size

            self.compression_level = level
            self.status = FoldStatus.COMPRESSED

            return True

        except Exception:
            self.status = FoldStatus.ERROR
            return False

    def decompress(self) -> bool:
        """Decompress fold content"""
        try:
            if self.status != FoldStatus.COMPRESSED or not self.compressed_data:
                return True

            # Decompress data
            json_data = zlib.decompress(self.compressed_data)
            data = json.loads(json_data.decode())

            # Recreate fold items
            items = []
            for item_data in data["items"]:
                item = MemoryItem(
                    id=item_data["id"],
                    content=item_data["content"],
                    timestamp=datetime.fromisoformat(item_data["timestamp"]),
                    memory_type=MemoryType(item_data["memory_type"]),
                    importance=item_data["importance"],
                    context_tags=item_data["context_tags"],
                    causal_chain=item_data["causal_chain"],
                )
                items.append(item)

            self.fold.items = items
            self.status = FoldStatus.ACTIVE
            self.compressed_data = None

            return True

        except Exception:
            self.status = FoldStatus.ERROR
            return False

    def access(self):
        """Record fold access"""
        self.metrics.last_accessed = datetime.now()
        self.metrics.access_count += 1


class ScheduledFoldingManager:
    """
    Advanced folding manager with LRU eviction, compression, and scheduling.
    Integrates with adaptive memory system for optimal performance.
    """

    def __init__(
        self,
        max_active_folds: int = 1000,
        max_compressed_folds: int = 5000,
        compression_threshold_mb: int = 10,
        folding_interval: int = 60,  # seconds
        eviction_batch_size: int = 100,
    ):
        """
        Initialize scheduled folding manager.

        Args:
            max_active_folds: Maximum active (uncompressed) folds
            max_compressed_folds: Maximum compressed folds before eviction
            compression_threshold_mb: Size threshold for compression (MB)
            folding_interval: Background folding interval in seconds
            eviction_batch_size: Number of folds to evict per batch
        """
        self.max_active_folds = max_active_folds
        self.max_compressed_folds = max_compressed_folds
        self.compression_threshold_bytes = compression_threshold_mb * 1024 * 1024
        self.folding_interval = folding_interval
        self.eviction_batch_size = eviction_batch_size

        # Storage
        self.active_folds: OrderedDict[str, ScheduledFold] = OrderedDict()
        self.compressed_folds: Dict[str, ScheduledFold] = {}
        self.content_hashes: Dict[str, str] = {}  # hash -> fold_id mapping

        # Background processing
        self._folding_thread: Optional[threading.Thread] = None
        self._stop_folding = threading.Event()
        self._lock = threading.RLock()

        # Metrics
        self.metrics = {
            "folds_created": 0,
            "folds_compressed": 0,
            "folds_evicted": 0,
            "compression_saves_bytes": 0,
            "deduplication_saves": 0,
            "total_size_bytes": 0,
        }

        self._start_background_folding()

    def register_fold(self, fold: MemoryFold, tags: Optional[Set[str]] = None) -> str:
        """
        Register a fold for scheduled management.

        Args:
            fold: Memory fold to register
            tags: Optional tags for categorization

        Returns:
            Fold ID for tracking
        """
        with self._lock:
            scheduled_fold = ScheduledFold(
                fold=fold,
                tags=tags or set(),
            )

            # Check for deduplication
            if scheduled_fold.content_hash in self.content_hashes:
                existing_id = self.content_hashes[scheduled_fold.content_hash]
                self.metrics["deduplication_saves"] += 1
                return existing_id

            # Register new fold
            fold_id = fold.id
            self.active_folds[fold_id] = scheduled_fold
            self.content_hashes[scheduled_fold.content_hash] = fold_id
            self.metrics["folds_created"] += 1
            self._update_total_size()

            # Check if we need immediate compression/eviction
            self._check_compression_trigger()
            self._check_eviction_trigger()

            return fold_id

    def access_fold(self, fold_id: str) -> Optional[MemoryFold]:
        """
        Access a fold, handling decompression if needed.

        Args:
            fold_id: ID of fold to access

        Returns:
            Memory fold if found, None otherwise
        """
        with self._lock:
            # Check active folds first
            if fold_id in self.active_folds:
                scheduled_fold = self.active_folds[fold_id]
                scheduled_fold.access()
                # Move to end (most recently used)
                self.active_folds.move_to_end(fold_id)
                return scheduled_fold.fold

            # Check compressed folds
            if fold_id in self.compressed_folds:
                scheduled_fold = self.compressed_folds[fold_id]
                scheduled_fold.access()

                # Decompress if needed
                if scheduled_fold.decompress():
                    # Move to active storage
                    del self.compressed_folds[fold_id]
                    self.active_folds[fold_id] = scheduled_fold
                    self._check_eviction_trigger()
                    return scheduled_fold.fold

            return None

    def _check_compression_trigger(self):
        """Check if compression should be triggered"""
        total_size = sum(
            fold.metrics.size_bytes
            for fold in self.active_folds.values()
        )

        if (total_size > self.compression_threshold_bytes or
            len(self.active_folds) > self.max_active_folds):
            self._compress_lru_folds()

    def _check_eviction_trigger(self):
        """Check if eviction should be triggered"""
        if len(self.compressed_folds) > self.max_compressed_folds:
            self._evict_lru_folds()

    def _compress_lru_folds(self):
        """Compress least recently used folds"""
        # Always compress at least 1 fold if over limit
        if len(self.active_folds) > self.max_active_folds:
            compress_count = min(
                self.eviction_batch_size,
                max(1, len(self.active_folds) - self.max_active_folds // 2)
            )
        else:
            return

        if compress_count <= 0:
            return

        # Get LRU folds (from beginning of OrderedDict)
        folds_to_compress = list(self.active_folds.items())[:compress_count]

        for fold_id, scheduled_fold in folds_to_compress:
            if scheduled_fold.compress():
                # Move to compressed storage
                del self.active_folds[fold_id]
                self.compressed_folds[fold_id] = scheduled_fold
                self.metrics["folds_compressed"] += 1

                # Track compression savings
                original_size = scheduled_fold.metrics.size_bytes
                compressed_size = len(scheduled_fold.compressed_data or b"")
                self.metrics["compression_saves_bytes"] += (original_size - compressed_size)

        self._update_total_size()

    def _evict_lru_folds(self):
        """Evict least recently used compressed folds"""
        evict_count = min(
            self.eviction_batch_size,
            len(self.compressed_folds) - self.max_compressed_folds
        )

        if evict_count <= 0:
            return

        # Sort by last access time (oldest first)
        sorted_folds = sorted(
            self.compressed_folds.items(),
            key=lambda x: x[1].metrics.last_accessed or datetime.min
        )

        for fold_id, scheduled_fold in sorted_folds[:evict_count]:
            # Remove from storage
            del self.compressed_folds[fold_id]
            if scheduled_fold.content_hash in self.content_hashes:
                del self.content_hashes[scheduled_fold.content_hash]

            scheduled_fold.status = FoldStatus.EVICTED
            self.metrics["folds_evicted"] += 1

        self._update_total_size()

    def _update_total_size(self):
        """Update total size metrics"""
        active_size = sum(
            fold.metrics.size_bytes
            for fold in self.active_folds.values()
        )
        compressed_size = sum(
            len(fold.compressed_data or b"")
            for fold in self.compressed_folds.values()
        )
        self.metrics["total_size_bytes"] = active_size + compressed_size

    def _background_folding_worker(self):
        """Background thread for scheduled folding operations"""
        while not self._stop_folding.wait(self.folding_interval):
            try:
                with self._lock:
                    self._run_scheduled_maintenance()
            except Exception as e:
                print(f"Folding maintenance error: {e}")

    def _run_scheduled_maintenance(self):
        """Run scheduled maintenance operations"""
        # Compress old active folds
        cutoff_time = datetime.now() - timedelta(minutes=30)
        candidates_for_compression = [
            (fold_id, fold) for fold_id, fold in self.active_folds.items()
            if (fold.metrics.last_accessed or fold.metrics.created_at) < cutoff_time
        ]

        for fold_id, scheduled_fold in candidates_for_compression[:50]:  # Limit batch size
            if scheduled_fold.compress():
                del self.active_folds[fold_id]
                self.compressed_folds[fold_id] = scheduled_fold
                self.metrics["folds_compressed"] += 1

        # Check for evictions
        self._check_eviction_trigger()
        self._update_total_size()

    def _start_background_folding(self):
        """Start background folding thread"""
        if self._folding_thread is None:
            self._folding_thread = threading.Thread(
                target=self._background_folding_worker,
                daemon=True,
                name="FoldingManager"
            )
            self._folding_thread.start()

    def get_status(self) -> Dict[str, Any]:
        """Get folding manager status"""
        with self._lock:
            total_folds = len(self.active_folds) + len(self.compressed_folds)
            compression_ratio = (
                self.metrics["compression_saves_bytes"] /
                max(1, self.metrics["total_size_bytes"])
            )

            return {
                "active_folds": len(self.active_folds),
                "compressed_folds": len(self.compressed_folds),
                "total_folds": total_folds,
                "max_active": self.max_active_folds,
                "max_compressed": self.max_compressed_folds,
                "total_size_mb": self.metrics["total_size_bytes"] / (1024 * 1024),
                "compression_ratio": compression_ratio,
                "metrics": self.metrics.copy(),
                "health_status": {
                    "active_capacity": len(self.active_folds) / self.max_active_folds,
                    "compressed_capacity": len(self.compressed_folds) / self.max_compressed_folds,
                    "memory_healthy": total_folds < (self.max_active_folds + self.max_compressed_folds),
                }
            }

    def find_folds_by_tags(self, tags: Set[str]) -> List[str]:
        """Find fold IDs matching given tags"""
        with self._lock:
            matching_ids = []

            # Search active folds
            for fold_id, scheduled_fold in self.active_folds.items():
                if tags.intersection(scheduled_fold.tags):
                    matching_ids.append(fold_id)

            # Search compressed folds
            for fold_id, scheduled_fold in self.compressed_folds.items():
                if tags.intersection(scheduled_fold.tags):
                    matching_ids.append(fold_id)

            return matching_ids

    def shutdown(self):
        """Clean shutdown of folding manager"""
        if self._folding_thread:
            self._stop_folding.set()
            self._folding_thread.join(timeout=5)


# Global instance
_folding_manager: Optional[ScheduledFoldingManager] = None


def get_folding_manager() -> ScheduledFoldingManager:
    """Get or create folding manager singleton"""
    global _folding_manager
    if _folding_manager is None:
        _folding_manager = ScheduledFoldingManager()
    return _folding_manager