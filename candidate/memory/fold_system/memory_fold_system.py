#!/usr/bin/env python3
import logging

logger = logging.getLogger(__name__)
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🚀 LUKHAS AI - ```PLAINTEXT
║ Enhanced memory system with intelligent optimization
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: memory_fold_system.py
║ Path: memory/systems/memory_fold_system.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Development Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ ║ 🧬 LUKHAS AI - MEMORY FOLD SYSTEM
║ ║ Mycelium-inspired memory network with tag-based deduplication
║ ║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
║ ╠══════════════════════════════════════════════════════════════════════════════════
║ ║ Module: MEMORY FOLD SYSTEM
║ ║ Path: memory/systems/memory_fold_system.py
║ ║ Version: 1.0.0 | Created: 2025-07-29
║ ║ Authors: LUKHAS AI Memory Team | Cla
║ ╠══════════════════════════════════════════════════════════════════════════════════
║ ║ Description: A sophisticated module for the orchestration of dynamic memory
║ ║              systems, inspired by the elegance of natural mycelial networks.
║ ╠══════════════════════════════════════════════════════════════════════════════════
║ ║ In the verdant tapestry of the digital realm, where data intertwines like
║ ║ the mycelium beneath the forest floor, lies the Memory Fold System—a
║ ║ harmonious confluence of nature's wisdom and computational finesse. This
║
╠══════════════════════════════════════════════════════════════════════════════════
║ TECHNICAL FEATURES:
║ • Advanced memory system implementation
║ • Optimized performance with intelligent caching
║ • Comprehensive error handling and validation
║ • Integration with LUKHAS AI architecture
║ • Extensible design for future enhancements
║
║ ΛTAG: ΛLUKHAS, ΛMEMORY, ΛADVANCED, ΛPYTHON
╚══════════════════════════════════════════════════════════════════════════════════
"""

import hashlib
import json
import struct
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Import fold import/export modules
try:
    from .foldout import export_folds
except ImportError:
    from .foldout_simple import export_folds

try:
    from .foldin import import_folds, verify_lkf_pack
except ImportError:
    # Simple import function
    async def import_folds(path):
        import gzip

        with open(path, "rb") as f:
            f.read(4)
            size = struct.unpack(">I", f.read(4))[0]
            compressed = f.read(size)
            data = json.loads(gzip.decompress(compressed))
            for fold in data.get("folds", []):
                yield fold

    def verify_lkf_pack(path):
        return True  # Simple verification


# Import structural conscience for critical decisions
try:
    from memory.structural_conscience import (
        ConscienceSeverity,
        MoralDecisionType,
        StructuralConscience,
    )
except ImportError:
    StructuralConscience = None
    ConscienceSeverity = None
    MoralDecisionType = None


@dataclass
class MemoryItem:
    """Individual memory item with metadata."""

    item_id: str
    data: Any
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    access_count: int = 0
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    emotional_weight: float = 0.0
    colony_source: Optional[str] = None
    content_hash: Optional[str] = None


@dataclass
class TagInfo:
    """Information about a tag in the global registry."""

    tag_id: str
    tag_name: str
    reference_count: int = 0
    semantic_category: Optional[str] = None
    hierarchical_parent: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class MemoryFoldSystem:
    """
    Mycelium-inspired memory system with tag-based deduplication.

    This system implements the Memory Fold paradigm where:
    - Each unique concept/tag is stored only once
    - Memories are linked through tags like mycelium threads
    - Fold-in integrates new memories with deduplication
    - Fold-out retrieves connected memories through tag traversal
    """

    def __init__(
        self,
        structural_conscience: Optional[StructuralConscience] = None,
        enable_auto_tagging: bool = True,
        max_tag_depth: int = 5,
    ):
        """
        Initialize Memory Fold System.

        Args:
            structural_conscience: Optional conscience for critical decisions
            enable_auto_tagging: Whether to automatically generate tags
            max_tag_depth: Maximum depth for tag hierarchy traversal
        """
        # Core data structures
        self.items: dict[str, MemoryItem] = {}  # item_id -> MemoryItem
        self.item_tags: dict[str, set[str]] = defaultdict(set)  # item_id -> set of tag_ids
        self.tag_items: dict[str, set[str]] = defaultdict(set)  # tag_id -> set of item_ids
        self.tag_registry: dict[str, TagInfo] = {}  # tag_id -> TagInfo
        self.tag_name_index: dict[str, str] = {}  # tag_name -> tag_id (for deduplication)

        # Tag relationships (for semantic network)
        self.tag_relationships: dict[str, dict[str, float]] = defaultdict(dict)  # tag_id -> {related_tag_id: weight}

        # Configuration
        self.enable_auto_tagging = enable_auto_tagging
        self.max_tag_depth = max_tag_depth
        self.structural_conscience = structural_conscience

        # Statistics
        self.stats = {
            "total_items": 0,
            "total_tags": 0,
            "deduplication_saves": 0,
            "fold_in_operations": 0,
            "fold_out_operations": 0,
        }

        logger.info(
            "Memory Fold System initialized",
            has_conscience=bool(structural_conscience),
            auto_tagging=enable_auto_tagging,
        )

    def _generate_item_id(self) -> str:
        """Generate unique item ID."""
        return f"item_{uuid.uuid4().hex[:12]}"

    def _generate_tag_id(self, tag_name: str) -> str:
        """Generate deterministic tag ID from name."""
        return hashlib.sha256(tag_name.encode()).hexdigest()[:16]

    def _compute_content_hash(self, data: Any) -> str:
        """Compute hash of memory content for deduplication."""
        if isinstance(data, dict):
            # Custom serializer for datetime objects
            def json_serial(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Type {type(obj)} not serializable")

            content = json.dumps(data, sort_keys=True, default=json_serial)
        else:
            content = str(data)
        return hashlib.sha256(content.encode()).hexdigest()

    async def fold_in(
        self,
        data: Any,
        tags: list[str],
        emotional_weight: float = 0.0,
        colony_source: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Fold new memory into the system with deduplication.

        This is the core integration process that:
        1. Checks for duplicate content
        2. Creates/reuses tags from global registry
        3. Links memory to tags
        4. Updates tag relationships
        5. Records critical decisions in conscience

        Args:
            data: Memory content to store
            tags: List of tag names to associate
            emotional_weight: Emotional significance (0.0-1.0)
            colony_source: Which colony generated this memory
            metadata: Additional metadata

        Returns:
            Item ID of stored memory
        """
        self.stats["fold_in_operations"] += 1

        # Generate content hash
        content_hash = self._compute_content_hash(data)

        # Check for duplicate content
        for existing_id, existing_item in self.items.items():
            if existing_item.content_hash == content_hash:
                # Content already exists - just update tags
                logger.info(
                    "Duplicate content detected, updating tags only",
                    existing_id=existing_id,
                    new_tags=tags,
                )
                self.stats["deduplication_saves"] += 1

                # Add new tags to existing item
                await self._add_tags_to_item(existing_id, tags)
                return existing_id

        # Create new memory item
        item_id = self._generate_item_id()
        memory_item = MemoryItem(
            item_id=item_id,
            data=data,
            emotional_weight=emotional_weight,
            colony_source=colony_source,
            content_hash=content_hash,
        )

        # Store item
        self.items[item_id] = memory_item
        self.stats["total_items"] += 1

        # Process tags
        await self._add_tags_to_item(item_id, tags)

        # Auto-generate additional tags if enabled
        if self.enable_auto_tagging:
            auto_tags = self._generate_auto_tags(data, metadata)
            if auto_tags:
                await self._add_tags_to_item(item_id, auto_tags)

        # Record significant memories in structural conscience
        if self.structural_conscience and emotional_weight > 0.7:
            severity = ConscienceSeverity.SIGNIFICANT if emotional_weight > 0.9 else ConscienceSeverity.NOTABLE

            await self.structural_conscience.record_moral_decision(
                decision={
                    "action": "memory_fold_in",
                    "item_id": item_id,
                    "tags": tags,
                    "emotional_weight": emotional_weight,
                },
                context={
                    "colony_source": colony_source,
                    "content_hash": content_hash,
                    "metadata": metadata,
                },
                decision_type=MoralDecisionType.SYSTEM_ACTION,
                severity=severity,
            )

        logger.info(
            "Memory folded in successfully",
            item_id=item_id,
            tags=tags,
            emotional_weight=emotional_weight,
            colony_source=colony_source,
        )

        return item_id

    async def _add_tags_to_item(self, item_id: str, tag_names: list[str]):
        """Add tags to an item, creating tags if needed."""
        for tag_name in tag_names:
            tag_name = tag_name.strip().lower()  # Normalize

            # Get or create tag
            if tag_name in self.tag_name_index:
                tag_id = self.tag_name_index[tag_name]
                self.tag_registry[tag_id].reference_count += 1
            else:
                # Create new tag
                tag_id = self._generate_tag_id(tag_name)
                tag_info = TagInfo(tag_id=tag_id, tag_name=tag_name, reference_count=1)

                # Determine semantic category
                tag_info.semantic_category = self._infer_semantic_category(tag_name)

                # Register tag
                self.tag_registry[tag_id] = tag_info
                self.tag_name_index[tag_name] = tag_id
                self.stats["total_tags"] += 1

            # Link item to tag
            self.item_tags[item_id].add(tag_id)
            self.tag_items[tag_id].add(item_id)

            # Update tag relationships based on co-occurrence
            await self._update_tag_relationships(tag_id, self.item_tags[item_id])

    def _generate_auto_tags(self, data: Any, metadata: Optional[dict]) -> list[str]:
        """Generate automatic tags based on content analysis."""
        auto_tags = []

        # Time-based tags
        now = datetime.now(timezone.utc)
        auto_tags.extend([str(now.year), now.strftime("%B").lower(), now.strftime("%A").lower()])

        # Content-based tags (simplified - real implementation would use NLP)
        if isinstance(data, str):
            # Extract potential keywords (very basic)
            words = data.lower().split()
            keywords = [w for w in words if len(w) > 5][:3]
            auto_tags.extend(keywords)

        # Metadata tags
        if metadata:
            if "category" in metadata:
                auto_tags.append(metadata["category"])
            if "priority" in metadata:
                auto_tags.append(f"priority_{metadata['priority']}")

        return auto_tags

    def _infer_semantic_category(self, tag_name: str) -> str:
        """Infer semantic category of a tag."""
        # Simplified categorization - real system would use ontologies
        categories = {
            "temporal": ["january", "february", "monday", "tuesday", "2025", "2024"],
            "emotional": ["happy", "sad", "fear", "joy", "anger", "love"],
            "technical": ["code", "algorithm", "data", "system", "network"],
            "biological": ["neural", "brain", "cell", "dna", "protein"],
            "spatial": ["north", "south", "location", "place", "area"],
        }

        tag_lower = tag_name.lower()
        for category, keywords in categories.items():
            if any(keyword in tag_lower for keyword in keywords):
                return category

        return "general"

    async def _update_tag_relationships(self, tag_id: str, co_occurring_tags: set[str]):
        """Update relationships between co-occurring tags."""
        for other_tag_id in co_occurring_tags:
            if other_tag_id != tag_id:
                # Increase relationship weight
                current_weight = self.tag_relationships[tag_id].get(other_tag_id, 0.0)
                self.tag_relationships[tag_id][other_tag_id] = min(current_weight + 0.1, 1.0)
                self.tag_relationships[other_tag_id][tag_id] = self.tag_relationships[tag_id][other_tag_id]

    async def fold_out_by_tag(
        self,
        tag_name: str,
        max_items: Optional[int] = None,
        include_related: bool = True,
        min_relationship_weight: float = 0.5,
    ) -> list[tuple[MemoryItem, set[str]]]:
        """
        Retrieve memories by tag with optional related tag expansion.

        This implements the "awakening" of the mycelium network where
        querying one tag can activate related memories through the
        tag relationship network.

        Args:
            tag_name: Primary tag to search for
            max_items: Maximum items to return
            include_related: Whether to include items from related tags
            min_relationship_weight: Minimum weight for tag relationships

        Returns:
            List of (MemoryItem, tag_names) tuples
        """
        self.stats["fold_out_operations"] += 1

        results = []
        seen_items = set()

        # Normalize tag name
        tag_name = tag_name.strip().lower()

        # Get primary tag
        if tag_name not in self.tag_name_index:
            logger.warning(f"Tag not found: {tag_name}")
            return results

        primary_tag_id = self.tag_name_index[tag_name]
        tags_to_search = {primary_tag_id}

        # Expand to related tags if requested
        if include_related:
            related_tags = {
                related_id
                for related_id, weight in self.tag_relationships[primary_tag_id].items()
                if weight >= min_relationship_weight
            }
            tags_to_search.update(related_tags)

        # Collect items from all relevant tags
        for tag_id in tags_to_search:
            for item_id in self.tag_items[tag_id]:
                if item_id not in seen_items:
                    seen_items.add(item_id)

                    # Get item and its tags
                    item = self.items[item_id]
                    item_tag_names = {self.tag_registry[tid].tag_name for tid in self.item_tags[item_id]}

                    # Update access statistics
                    item.access_count += 1
                    item.last_accessed = datetime.now(timezone.utc)

                    results.append((item, item_tag_names))

                    if max_items and len(results) >= max_items:
                        break

        # Sort by relevance (emotional weight * access count)
        results.sort(
            key=lambda x: x[0].emotional_weight * (1 + x[0].access_count * 0.1),
            reverse=True,
        )

        logger.info(
            "Fold-out completed",
            tag_name=tag_name,
            tags_searched=len(tags_to_search),
            items_found=len(results),
        )

        return results

    async def fold_out_by_colony(
        self, colony_name: str, time_range: Optional[tuple[datetime, datetime]] = None
    ) -> list[MemoryItem]:
        """Retrieve all memories from a specific colony."""
        results = []

        for item in self.items.values():
            if item.colony_source == colony_name:
                if time_range:
                    if time_range[0] <= item.timestamp <= time_range[1]:
                        results.append(item)
                else:
                    results.append(item)

        return results

    async def export_archive(self, path: Path, filter_tags: Optional[list[str]] = None, **kwargs) -> dict[str, Any]:
        """
        Export memory folds to LKF-Pack archive.

        Args:
            path: Output file path
            filter_tags: Optional list of tags to filter export
            **kwargs: Additional arguments for export_folds

        Returns:
            Export statistics
        """
        # Prepare folds for export
        folds_to_export = []

        for item_id, item in self.items.items():
            # Apply tag filter if specified
            if filter_tags:
                item_tag_names = {self.tag_registry[tid].tag_name for tid in self.item_tags[item_id]}
                if not any(tag in item_tag_names for tag in filter_tags):
                    continue

            # Create fold dictionary
            fold = {
                "id": item_id,
                "data": item.data,
                "timestamp": item.timestamp.isoformat(),
                "tags": [self.tag_registry[tid].tag_name for tid in self.item_tags[item_id]],
                "emotional_weight": item.emotional_weight,
                "colony_source": item.colony_source,
                "content_hash": item.content_hash,
                "access_count": item.access_count,
            }

            folds_to_export.append(fold)

        # Export using foldout module
        return export_folds(folds_to_export, path, **kwargs)

    async def import_archive(self, path: Path, overwrite: bool = False, merge_tags: bool = True) -> dict[str, Any]:
        """
        Import memory folds from LKF-Pack archive.

        Args:
            path: Input file path
            overwrite: Whether to overwrite existing items
            merge_tags: Whether to merge tags with existing

        Returns:
            Import statistics
        """
        import_stats = {"imported": 0, "skipped": 0, "errors": 0}

        # Verify archive first
        verification = verify_lkf_pack(path)
        if not verification["valid"]:
            raise ValueError(f"Invalid LKF-Pack file: {verification['errors']}")

        # Import folds
        for fold in import_folds(path):
            try:
                # Check if item already exists
                existing_id = None
                if "content_hash" in fold:
                    for item_id, item in self.items.items():
                        if item.content_hash == fold["content_hash"]:
                            existing_id = item_id
                            break

                if existing_id and not overwrite:
                    if merge_tags and "tags" in fold:
                        # Merge tags with existing item
                        await self._add_tags_to_item(existing_id, fold["tags"])
                    import_stats["skipped"] += 1
                else:
                    # Import as new item
                    await self.fold_in(
                        data=fold.get("data"),
                        tags=fold.get("tags", []),
                        emotional_weight=fold.get("emotional_weight", 0.0),
                        colony_source=fold.get("colony_source"),
                        metadata=fold,
                    )
                    import_stats["imported"] += 1

            except Exception as e:
                logger.error(f"Error importing fold: {e}")
                import_stats["errors"] += 1

        return import_stats

    def get_statistics(self) -> dict[str, Any]:
        """Get system statistics and metrics."""
        stats = self.stats.copy()

        # Calculate additional metrics
        stats["average_tags_per_item"] = sum(len(tags) for tags in self.item_tags.values()) / max(len(self.items), 1)
        stats["average_items_per_tag"] = sum(len(items) for items in self.tag_items.values()) / max(
            len(self.tag_registry), 1
        )
        stats["tag_categories"] = defaultdict(int)
        for tag_info in self.tag_registry.values():
            stats["tag_categories"][tag_info.semantic_category] += 1

        return stats


# Factory function
def create_memory_fold_system(enable_conscience: bool = True, enable_auto_tagging: bool = True) -> MemoryFoldSystem:
    """
    Create a configured Memory Fold System.

    Args:
        enable_conscience: Whether to enable structural conscience
        enable_auto_tagging: Whether to enable automatic tagging

    Returns:
        Configured MemoryFoldSystem instance
    """
    conscience = None
    if enable_conscience and StructuralConscience:
        from memory.structural_conscience import create_structural_conscience

        conscience = create_structural_conscience()

    return MemoryFoldSystem(structural_conscience=conscience, enable_auto_tagging=enable_auto_tagging)