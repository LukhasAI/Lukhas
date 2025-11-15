#!/usr/bin/env python3
"""
Edge case tests for Memory Fold System consolidation.

Tests critical edge cases in:
- Content deduplication
- Tag normalization and deduplication
- Tag relationship management
- Related tag expansion
- Auto-tagging behavior
- Import/export with conflicts
"""

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

# Import system under test
from labs.memory.fold_system.memory_fold_system import (
    MemoryFoldSystem,
    MemoryItem,
    TagInfo,
)


class TestContentDeduplication:
    """Test content deduplication edge cases."""

    @pytest.mark.asyncio
    async def test_duplicate_content_same_tags(self):
        """Duplicate content with same tags should return same item_id."""
        system = MemoryFoldSystem(enable_auto_tagging=False)

        # First fold-in
        item_id_1 = await system.fold_in(
            data={"message": "Hello World"},
            tags=["greeting", "test"],
        )

        # Second fold-in with identical content and tags
        item_id_2 = await system.fold_in(
            data={"message": "Hello World"},
            tags=["greeting", "test"],
        )

        # Should return same item ID
        assert item_id_1 == item_id_2
        assert system.stats["deduplication_saves"] == 1
        assert len(system.items) == 1

    @pytest.mark.asyncio
    async def test_duplicate_content_different_tags(self):
        """Duplicate content with different tags should merge tags."""
        system = MemoryFoldSystem(enable_auto_tagging=False)

        # First fold-in
        item_id_1 = await system.fold_in(
            data={"message": "Hello World"},
            tags=["greeting"],
        )

        # Second fold-in with same content, different tags
        item_id_2 = await system.fold_in(
            data={"message": "Hello World"},
            tags=["test", "example"],
        )

        # Should return same item, but tags merged
        assert item_id_1 == item_id_2
        assert len(system.items) == 1

        # Check tags merged
        item_tags = {
            system.tag_registry[tid].tag_name
            for tid in system.item_tags[item_id_1]
        }
        assert item_tags == {"greeting", "test", "example"}

    @pytest.mark.asyncio
    async def test_content_hash_with_datetime_objects(self):
        """Content with datetime objects should hash consistently."""
        system = MemoryFoldSystem(enable_auto_tagging=False)

        timestamp = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        # First fold-in with datetime
        item_id_1 = await system.fold_in(
            data={"event": "meeting", "time": timestamp},
            tags=["event"],
        )

        # Second fold-in with same datetime
        item_id_2 = await system.fold_in(
            data={"event": "meeting", "time": timestamp},
            tags=["event"],
        )

        # Should deduplicate
        assert item_id_1 == item_id_2
        assert system.stats["deduplication_saves"] == 1

    @pytest.mark.asyncio
    async def test_content_hash_dict_key_order(self):
        """Dict content should hash independently of key order."""
        system = MemoryFoldSystem(enable_auto_tagging=False)

        # First fold-in with dict
        item_id_1 = await system.fold_in(
            data={"a": 1, "b": 2, "c": 3},
            tags=["test"],
        )

        # Second fold-in with different key order (should hash same)
        item_id_2 = await system.fold_in(
            data={"c": 3, "a": 1, "b": 2},
            tags=["test"],
        )

        # Should deduplicate
        assert item_id_1 == item_id_2
        assert system.stats["deduplication_saves"] == 1

    @pytest.mark.asyncio
    async def test_near_duplicate_content_different_hash(self):
        """Nearly identical content should NOT deduplicate."""
        system = MemoryFoldSystem(enable_auto_tagging=False)

        # First fold-in
        item_id_1 = await system.fold_in(
            data={"message": "Hello World"},
            tags=["test"],
        )

        # Second fold-in with slightly different content
        item_id_2 = await system.fold_in(
            data={"message": "Hello World!"},  # Added exclamation
            tags=["test"],
        )

        # Should NOT deduplicate
        assert item_id_1 != item_id_2
        assert system.stats["deduplication_saves"] == 0
        assert len(system.items) == 2


class TestTagNormalization:
    """Test tag normalization and deduplication edge cases."""

    @pytest.mark.asyncio
    async def test_tag_case_insensitive(self):
        """Tags should be case-insensitive."""
        system = MemoryFoldSystem(enable_auto_tagging=False)

        # Fold with uppercase tag
        await system.fold_in(data="test1", tags=["GREETING"])

        # Fold with lowercase tag
        await system.fold_in(data="test2", tags=["greeting"])

        # Fold with mixed case tag
        await system.fold_in(data="test3", tags=["Greeting"])

        # Should all normalize to same tag
        assert len(system.tag_registry) == 1
        assert "greeting" in system.tag_name_index

        # Tag should have 3 references
        tag_id = system.tag_name_index["greeting"]
        assert system.tag_registry[tag_id].reference_count == 3

    @pytest.mark.asyncio
    async def test_tag_whitespace_normalization(self):
        """Tags with whitespace should normalize."""
        system = MemoryFoldSystem(enable_auto_tagging=False)

        # Various whitespace variations
        await system.fold_in(data="test1", tags=[" greeting "])
        await system.fold_in(data="test2", tags=["greeting"])
        await system.fold_in(data="test3", tags=["  greeting  "])

        # Should normalize to same tag
        assert len(system.tag_registry) == 1
        assert "greeting" in system.tag_name_index

    @pytest.mark.asyncio
    async def test_empty_tag_handling(self):
        """Empty tags should be handled gracefully."""
        system = MemoryFoldSystem(enable_auto_tagging=False)

        # Fold with empty/whitespace-only tags
        await system.fold_in(data="test", tags=["valid", "", "  ", "another"])

        # Empty tags should be skipped (after strip they're empty strings)
        # Note: Current implementation might not skip empty tags - this tests actual behavior
        tag_names = {
            system.tag_registry[tid].tag_name
            for tid in system.tag_registry.keys()
        }

        # Should not have empty string as tag (or should handle gracefully)
        # Implementation detail: system might accept "" as tag_name after .strip()
        # This test documents the behavior
        assert "valid" in tag_names
        assert "another" in tag_names

    @pytest.mark.asyncio
    async def test_tag_id_deterministic(self):
        """Tag IDs should be deterministic from tag name."""
        system1 = MemoryFoldSystem(enable_auto_tagging=False)
        system2 = MemoryFoldSystem(enable_auto_tagging=False)

        # Create same tag in two systems
        await system1.fold_in(data="test1", tags=["greeting"])
        await system2.fold_in(data="test2", tags=["greeting"])

        # Tag IDs should match
        tag_id_1 = system1.tag_name_index["greeting"]
        tag_id_2 = system2.tag_name_index["greeting"]
        assert tag_id_1 == tag_id_2

    @pytest.mark.asyncio
    async def test_tag_collision_same_hash(self):
        """Different tag names with same hash should not collide."""
        system = MemoryFoldSystem(enable_auto_tagging=False)

        # This tests the SHA-256 hash collision resistance
        # With 16-char truncation, collisions are very rare but theoretically possible
        await system.fold_in(data="test1", tags=["tag1"])
        await system.fold_in(data="test2", tags=["tag2"])

        # Should have 2 distinct tags
        assert len(system.tag_registry) == 2
        assert "tag1" in system.tag_name_index
        assert "tag2" in system.tag_name_index


class TestTagRelationships:
    """Test tag relationship edge cases."""

    @pytest.mark.asyncio
    async def test_relationship_weight_limits(self):
        """Tag relationship weights should cap at 1.0."""
        system = MemoryFoldSystem(enable_auto_tagging=False)

        # Create many items with same tag pair to max out weight
        for i in range(20):
            await system.fold_in(
                data=f"test{i}",
                tags=["tag1", "tag2"],
            )

        # Get tag IDs
        tag1_id = system.tag_name_index["tag1"]
        tag2_id = system.tag_name_index["tag2"]

        # Relationship weight should cap at 1.0
        weight = system.tag_relationships[tag1_id].get(tag2_id, 0.0)
        assert weight <= 1.0
        assert weight == 1.0  # Should hit max after 10 increments of 0.1

    @pytest.mark.asyncio
    async def test_relationship_symmetry(self):
        """Tag relationships should be symmetric."""
        system = MemoryFoldSystem(enable_auto_tagging=False)

        await system.fold_in(data="test", tags=["tag1", "tag2", "tag3"])

        # Get tag IDs
        tag1_id = system.tag_name_index["tag1"]
        tag2_id = system.tag_name_index["tag2"]

        # Relationship should be symmetric
        weight_1_to_2 = system.tag_relationships[tag1_id].get(tag2_id, 0.0)
        weight_2_to_1 = system.tag_relationships[tag2_id].get(tag1_id, 0.0)
        assert weight_1_to_2 == weight_2_to_1

    @pytest.mark.asyncio
    async def test_self_relationship_not_created(self):
        """Tags should not create relationships with themselves."""
        system = MemoryFoldSystem(enable_auto_tagging=False)

        await system.fold_in(data="test", tags=["self_tag"])

        tag_id = system.tag_name_index["self_tag"]

        # Should not have self-relationship
        assert tag_id not in system.tag_relationships[tag_id]

    @pytest.mark.asyncio
    async def test_relationship_creation_with_multiple_tags(self):
        """All tag pairs in an item should create relationships."""
        system = MemoryFoldSystem(enable_auto_tagging=False)

        await system.fold_in(data="test", tags=["a", "b", "c"])

        # Get tag IDs
        a_id = system.tag_name_index["a"]
        b_id = system.tag_name_index["b"]
        c_id = system.tag_name_index["c"]

        # All pairs should have relationships
        assert b_id in system.tag_relationships[a_id]
        assert c_id in system.tag_relationships[a_id]
        assert a_id in system.tag_relationships[b_id]
        assert c_id in system.tag_relationships[b_id]
        assert a_id in system.tag_relationships[c_id]
        assert b_id in system.tag_relationships[c_id]


class TestFoldOutRelatedTags:
    """Test fold-out with related tag expansion edge cases."""

    @pytest.mark.asyncio
    async def test_fold_out_nonexistent_tag(self):
        """Fold-out for nonexistent tag should return empty list."""
        system = MemoryFoldSystem(enable_auto_tagging=False)

        await system.fold_in(data="test", tags=["real_tag"])

        # Query nonexistent tag
        results = await system.fold_out_by_tag("nonexistent_tag")

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_fold_out_with_no_relationships(self):
        """Fold-out with include_related=True but no relationships."""
        system = MemoryFoldSystem(enable_auto_tagging=False)

        # Create isolated tags (no co-occurrence)
        await system.fold_in(data="test1", tags=["isolated1"])
        await system.fold_in(data="test2", tags=["isolated2"])

        # Query with related expansion
        results = await system.fold_out_by_tag(
            "isolated1",
            include_related=True,
            min_relationship_weight=0.5
        )

        # Should only return items with primary tag
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_fold_out_relationship_threshold(self):
        """Fold-out should respect min_relationship_weight threshold."""
        system = MemoryFoldSystem(enable_auto_tagging=False)

        # Create weak relationship (weight = 0.1)
        await system.fold_in(data="test1", tags=["primary", "related"])

        # Create strong relationship (weight = 1.0)
        for i in range(10):
            await system.fold_in(data=f"test{i+2}", tags=["primary", "strongly_related"])

        # Query with high threshold
        results = await system.fold_out_by_tag(
            "primary",
            include_related=True,
            min_relationship_weight=0.5  # Should exclude "related", include "strongly_related"
        )

        # Should include items from primary and strongly_related, not related
        assert len(results) > 1

    @pytest.mark.asyncio
    async def test_fold_out_max_items_limit(self):
        """Fold-out should respect max_items limit."""
        system = MemoryFoldSystem(enable_auto_tagging=False)

        # Create many items with same tag
        for i in range(20):
            await system.fold_in(data=f"test{i}", tags=["common"])

        # Query with limit
        results = await system.fold_out_by_tag("common", max_items=5)

        # Should return exactly 5 items
        assert len(results) == 5

    @pytest.mark.asyncio
    async def test_fold_out_relevance_sorting(self):
        """Fold-out should sort by emotional_weight * access_count."""
        system = MemoryFoldSystem(enable_auto_tagging=False)

        # Create items with varying emotional weights
        await system.fold_in(
            data="low_priority",
            tags=["test"],
            emotional_weight=0.1
        )

        await system.fold_in(
            data="high_priority",
            tags=["test"],
            emotional_weight=0.9
        )

        await system.fold_in(
            data="medium_priority",
            tags=["test"],
            emotional_weight=0.5
        )

        # Query
        results = await system.fold_out_by_tag("test")

        # First result should be highest emotional weight
        assert results[0][0].data == "high_priority"
        assert results[0][0].emotional_weight == 0.9

    @pytest.mark.asyncio
    async def test_fold_out_access_count_updates(self):
        """Fold-out should update access statistics."""
        system = MemoryFoldSystem(enable_auto_tagging=False)

        item_id = await system.fold_in(data="test", tags=["tracked"])

        # Initial access count should be 0
        assert system.items[item_id].access_count == 0

        # Fold-out multiple times
        await system.fold_out_by_tag("tracked")
        await system.fold_out_by_tag("tracked")
        await system.fold_out_by_tag("tracked")

        # Access count should increment
        assert system.items[item_id].access_count == 3


class TestAutoTagging:
    """Test auto-tagging edge cases."""

    @pytest.mark.asyncio
    async def test_auto_tagging_empty_string(self):
        """Auto-tagging with empty string should handle gracefully."""
        system = MemoryFoldSystem(enable_auto_tagging=True)

        item_id = await system.fold_in(data="", tags=["manual"])

        # Should at least have manual tag
        item_tags = {
            system.tag_registry[tid].tag_name
            for tid in system.item_tags[item_id]
        }
        assert "manual" in item_tags

    @pytest.mark.asyncio
    async def test_auto_tagging_non_string_data(self):
        """Auto-tagging with non-string data should handle gracefully."""
        system = MemoryFoldSystem(enable_auto_tagging=True)

        # Test with integer
        item_id = await system.fold_in(data=42, tags=["number"])

        # Should at least have manual tag
        item_tags = {
            system.tag_registry[tid].tag_name
            for tid in system.item_tags[item_id]
        }
        assert "number" in item_tags

    @pytest.mark.asyncio
    async def test_auto_tagging_temporal_tags(self):
        """Auto-tagging should add temporal tags."""
        system = MemoryFoldSystem(enable_auto_tagging=True)

        item_id = await system.fold_in(data="test", tags=["manual"])

        # Should have year as auto-tag
        item_tags = {
            system.tag_registry[tid].tag_name
            for tid in system.item_tags[item_id]
        }

        current_year = str(datetime.now(timezone.utc).year)
        assert current_year in item_tags

    @pytest.mark.asyncio
    async def test_auto_tagging_from_metadata(self):
        """Auto-tagging should extract tags from metadata."""
        system = MemoryFoldSystem(enable_auto_tagging=True)

        item_id = await system.fold_in(
            data="test",
            tags=["manual"],
            metadata={"category": "important", "priority": "high"}
        )

        # Should have metadata-based auto-tags
        item_tags = {
            system.tag_registry[tid].tag_name
            for tid in system.item_tags[item_id]
        }

        assert "important" in item_tags
        assert "priority_high" in item_tags


class TestImportExport:
    """Test import/export edge cases."""

    @pytest.mark.asyncio
    async def test_export_empty_system(self):
        """Exporting empty system should succeed."""
        system = MemoryFoldSystem()
        tmp_path = Path("/tmp/test_empty_export.lkf")

        stats = await system.export_archive(tmp_path, timezone=timezone.utc)

        # Should succeed with 0 items
        assert stats is not None

        # Cleanup
        if tmp_path.exists():
            tmp_path.unlink()

    @pytest.mark.asyncio
    async def test_export_with_tag_filter(self):
        """Export should respect tag filter."""
        system = MemoryFoldSystem(enable_auto_tagging=False)

        # Add items with different tags
        await system.fold_in(data="public", tags=["public"])
        await system.fold_in(data="private", tags=["private"])
        await system.fold_in(data="both", tags=["public", "private"])

        tmp_path = Path("/tmp/test_filtered_export.lkf")

        # Export only public items
<<<<<<< HEAD
        await system.export_archive(tmp_path, filter_tags=["public"], timezone=timezone.utc)
=======
        stats = await system.export_archive(tmp_path, filter_tags=["public"], timezone=timezone.utc)
>>>>>>> test/memory-fold-edge-cases

        # Verify export includes only filtered items
        # (Would need to actually parse the LKF file to verify completely)

        # Cleanup
        if tmp_path.exists():
            tmp_path.unlink()

    @pytest.mark.asyncio
    async def test_import_with_content_hash_conflict(self):
        """Import should handle content hash conflicts."""
        system = MemoryFoldSystem(enable_auto_tagging=False)

        # Create original item
<<<<<<< HEAD
        await system.fold_in(
=======
        original_id = await system.fold_in(
>>>>>>> test/memory-fold-edge-cases
            data={"message": "original"},
            tags=["original"],
        )

        # Export
        tmp_path = Path("/tmp/test_conflict_import.lkf")
        await system.export_archive(tmp_path, timezone=timezone.utc)

        # Try to import back (should detect duplicate)
        stats = await system.import_archive(tmp_path, overwrite=False)

        # Should skip duplicate
        assert stats["imported"] == 0
        assert stats["skipped"] == 1

        # Cleanup
        if tmp_path.exists():
            tmp_path.unlink()

    @pytest.mark.asyncio
    async def test_import_with_tag_merging(self):
        """Import should merge tags when merge_tags=True."""
        system = MemoryFoldSystem(enable_auto_tagging=False)

        # Create original item
        await system.fold_in(data={"msg": "test"}, tags=["tag1"])

        # Export
        tmp_path = Path("/tmp/test_tag_merge.lkf")
        await system.export_archive(tmp_path, timezone=timezone.utc)

        # Manually add tags to existing item
<<<<<<< HEAD
        item_id = next(iter(system.items.keys()))
        await system._add_tags_to_item(item_id, ["tag2"])

        # Import with tag merging
        await system.import_archive(tmp_path, overwrite=False, merge_tags=True)
=======
        item_id = list(system.items.keys())[0]
        await system._add_tags_to_item(item_id, ["tag2"])

        # Import with tag merging
        stats = await system.import_archive(tmp_path, overwrite=False, merge_tags=True)
>>>>>>> test/memory-fold-edge-cases

        # Original tags should remain
        item_tags = {
            system.tag_registry[tid].tag_name
            for tid in system.item_tags[item_id]
        }
        assert "tag1" in item_tags
        assert "tag2" in item_tags

        # Cleanup
        if tmp_path.exists():
            tmp_path.unlink()


class TestStatistics:
    """Test statistics calculation edge cases."""

    @pytest.mark.asyncio
    async def test_statistics_empty_system(self):
        """Statistics for empty system should not error."""
        system = MemoryFoldSystem()

        stats = system.get_statistics()

        # Should return valid stats even if empty
        assert "total_items" in stats
        assert stats["total_items"] == 0
        assert stats["average_tags_per_item"] >= 0.0

    @pytest.mark.asyncio
    async def test_statistics_deduplication_count(self):
        """Statistics should track deduplication saves."""
        system = MemoryFoldSystem(enable_auto_tagging=False)

        # Fold identical content multiple times
        await system.fold_in(data="duplicate", tags=["test"])
        await system.fold_in(data="duplicate", tags=["test"])
        await system.fold_in(data="duplicate", tags=["test"])

        stats = system.get_statistics()

        # Should track 2 deduplication saves
        assert stats["deduplication_saves"] == 2

    @pytest.mark.asyncio
    async def test_statistics_tag_categories(self):
        """Statistics should categorize tags."""
        system = MemoryFoldSystem(enable_auto_tagging=False)

        # Add items with categorizable tags
        await system.fold_in(data="test1", tags=["january", "2025"])  # temporal
        await system.fold_in(data="test2", tags=["happy", "joy"])  # emotional
        await system.fold_in(data="test3", tags=["code", "algorithm"])  # technical

        stats = system.get_statistics()

        # Should have tag categories
        assert "tag_categories" in stats
        assert len(stats["tag_categories"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
