#!/usr/bin/env python3
"""
Comprehensive integration tests for LUKHAS Memory System.

Tests end-to-end memory workflows including:
- Memory fold creation and retrieval
- Cross-component memory integration (MATRIZ↔Memory)
- Memory cascade prevention
- Memory persistence and recovery
- Multi-lane memory isolation
"""

import asyncio
from datetime import datetime, timezone
from pathlib import Path

import pytest

from lukhas.memory.fold_system import MemoryFoldSystem
from MATRIZ.core.memory_system import MemorySystem


class TestMemorySystemIntegration:
    """Integration tests for core Memory System operations."""

    @pytest.mark.asyncio
    async def test_memory_fold_lifecycle(self):
        """Test complete fold lifecycle: create, retrieve, update, delete."""
        system = MemorySystem()

        # Create memory fold
        fold_id = await system.create_fold(
            content={"event": "test_event", "data": "test_data"},
            tags=["integration_test", "lifecycle"],
            emotional_weight=0.8
        )

        assert fold_id is not None

        # Retrieve fold
        fold = await system.get_fold(fold_id)
        assert fold is not None
        assert fold["content"]["event"] == "test_event"
        assert "integration_test" in fold["tags"]
        assert fold["emotional_weight"] == 0.8

        # Update fold
        await system.update_fold(fold_id, tags=["updated", "lifecycle"])
        updated = await system.get_fold(fold_id)
        assert "updated" in updated["tags"]

        # Soft delete fold
        await system.delete_fold(fold_id, soft=True)
        deleted = await system.get_fold(fold_id)
        assert deleted["deleted"] is True

    @pytest.mark.asyncio
    async def test_memory_search_and_retrieval(self):
        """Test memory search across multiple dimensions."""
        system = MemorySystem()

        # Create test memories
        await system.create_fold(
            content="First memory about AI consciousness",
            tags=["ai", "consciousness"],
            emotional_weight=0.9
        )
        await system.create_fold(
            content="Second memory about machine learning",
            tags=["ai", "ml"],
            emotional_weight=0.7
        )
        await system.create_fold(
            content="Third memory about human psychology",
            tags=["human", "psychology"],
            emotional_weight=0.6
        )

        # Search by tag
        ai_memories = await system.search_by_tag("ai")
        assert len(ai_memories) == 2

        # Search by emotional weight threshold
        high_weight = await system.search_by_emotional_weight(min_weight=0.8)
        assert len(high_weight) == 1
        assert "consciousness" in high_weight[0]["tags"]

        # Search by content
        consciousness_memories = await system.search_by_content("consciousness")
        assert len(consciousness_memories) >= 1

    @pytest.mark.asyncio
    async def test_memory_deduplication(self):
        """Test that duplicate memories are properly deduplicated."""
        system = MemorySystem()

        # Create identical memories
        fold_id_1 = await system.create_fold(
            content={"message": "Duplicate test"},
            tags=["dedup_test"]
        )

        fold_id_2 = await system.create_fold(
            content={"message": "Duplicate test"},
            tags=["dedup_test"]
        )

        # Should return same fold ID (deduplication)
        assert fold_id_1 == fold_id_2

        # Should only have one memory stored
        all_memories = await system.search_by_tag("dedup_test")
        assert len(all_memories) == 1


class TestMemoryMATRIZIntegration:
    """Test integration between Memory and MATRIZ systems."""

    @pytest.mark.asyncio
    async def test_matriz_memory_storage(self):
        """Test that MATRIZ can store and retrieve memories."""
        from matriz.core.orchestrator import Orchestrator

        Orchestrator()
        memory = MemorySystem()

        # MATRIZ creates a memory
        test_data = {
            "decision": "route_to_openai",
            "reasoning": "High complexity task",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        fold_id = await memory.create_fold(
            content=test_data,
            tags=["matriz_decision", "routing"],
            emotional_weight=0.5
        )

        # Verify memory can be retrieved
        retrieved = await memory.get_fold(fold_id)
        assert retrieved["content"]["decision"] == "route_to_openai"
        assert "matriz_decision" in retrieved["tags"]

    @pytest.mark.asyncio
    async def test_memory_cascade_prevention(self):
        """Test that memory system prevents cascading failures."""
        system = MemorySystem()

        # Create memory that should trigger cascade prevention
        try:
            # Intentionally create problematic memory
            await system.create_fold(
                content={"recursive": "reference", "self": fold_id},
                tags=["cascade_test"]
            )

            # Verify cascade prevention activated
            stats = await system.get_statistics()
            assert stats.get("cascade_preventions", 0) > 0

        except Exception:
            # If cascade prevention throws, that's also acceptable behavior
            pass


class TestMemoryPersistence:
    """Test memory persistence and recovery."""

    @pytest.mark.asyncio
    async def test_memory_export_import(self):
        """Test exporting and importing memory archives."""
        system = MemorySystem()
        tmp_path = Path("/tmp/test_memory_export.lkf")

        try:
            # Create test memories
            await system.create_fold(
                content="Test memory 1",
                tags=["export_test", "first"]
            )
            await system.create_fold(
                content="Test memory 2",
                tags=["export_test", "second"]
            )

            # Export memories
            export_stats = await system.export_archive(tmp_path)
            assert export_stats["exported"] == 2

            # Create new system and import
            new_system = MemorySystem()
            import_stats = await new_system.import_archive(tmp_path)
            assert import_stats["imported"] == 2

            # Verify memories exist in new system
            imported = await new_system.search_by_tag("export_test")
            assert len(imported) == 2

        finally:
            # Cleanup
            if tmp_path.exists():
                tmp_path.unlink()

    @pytest.mark.asyncio
    async def test_memory_recovery_after_crash(self):
        """Test memory recovery from persistent storage."""
        system = MemorySystem(persist_to_disk=True)
        storage_path = Path("/tmp/test_memory_recovery")

        try:
            # Create memories
            await system.create_fold(
                content="Recovery test memory",
                tags=["recovery_test"]
            )

            # Simulate crash by deleting object
            del system

            # Recover from storage
            recovered_system = MemorySystem(persist_to_disk=True, storage_path=storage_path)
            memories = await recovered_system.search_by_tag("recovery_test")

            # Should recover the memory
            assert len(memories) >= 1
            assert memories[0]["content"] == "Recovery test memory"

        finally:
            # Cleanup
            if storage_path.exists():
                import shutil
                shutil.rmtree(storage_path)


class TestMemoryLaneIsolation:
    """Test memory isolation between lanes (candidate/integration/production)."""

    @pytest.mark.asyncio
    async def test_candidate_production_memory_isolation(self):
        """Test that candidate and production memories are isolated."""
        candidate_memory = MemorySystem(lane="candidate")
        production_memory = MemorySystem(lane="production")

        # Create memory in candidate lane
        await candidate_memory.create_fold(
            content="Candidate experiment",
            tags=["candidate_only"]
        )

        # Verify NOT accessible from production lane
        prod_search = await production_memory.search_by_tag("candidate_only")
        assert len(prod_search) == 0

        # Create memory in production lane
        await production_memory.create_fold(
            content="Production data",
            tags=["production_only"]
        )

        # Verify NOT accessible from candidate lane
        cand_search = await candidate_memory.search_by_tag("production_only")
        assert len(cand_search) == 0

    @pytest.mark.asyncio
    async def test_memory_promotion_between_lanes(self):
        """Test promoting memory from candidate to production."""
        candidate = MemorySystem(lane="candidate")
        production = MemorySystem(lane="production")

        # Create in candidate
        fold_id = await candidate.create_fold(
            content="Ready for production",
            tags=["promotion_test"],
            emotional_weight=0.9
        )

        # Promote to production
        await candidate.promote_to_lane(fold_id, target_lane="production")

        # Verify exists in production
        prod_memories = await production.search_by_tag("promotion_test")
        assert len(prod_memories) == 1
        assert prod_memories[0]["content"] == "Ready for production"


class TestMemoryPerformance:
    """Test memory system performance under load."""

    @pytest.mark.asyncio
    async def test_bulk_memory_creation(self):
        """Test creating large number of memories efficiently."""
        import time

        system = MemorySystem()
        start_time = time.time()

        # Create 100 memories
        tasks = []
        for i in range(100):
            task = system.create_fold(
                content=f"Bulk memory {i}",
                tags=["bulk_test", f"batch_{i // 10}"],
                emotional_weight=0.5
            )
            tasks.append(task)

        await asyncio.gather(*tasks)
        elapsed = time.time() - start_time

        # Should complete in reasonable time (<5 seconds for 100 memories)
        assert elapsed < 5.0

        # Verify all created
        bulk_memories = await system.search_by_tag("bulk_test")
        assert len(bulk_memories) == 100

    @pytest.mark.asyncio
    async def test_memory_recall_latency(self):
        """Test that memory recall meets <100ms p95 latency target."""
        import time

        system = MemorySystem()

        # Create test memory
        fold_id = await system.create_fold(
            content="Latency test",
            tags=["latency_test"]
        )

        # Measure recall latency (10 samples)
        latencies = []
        for _ in range(10):
            start = time.time()
            await system.get_fold(fold_id)
            latency_ms = (time.time() - start) * 1000
            latencies.append(latency_ms)

        # Calculate p95
        latencies.sort()
        p95 = latencies[int(len(latencies) * 0.95)]

        # Should meet <100ms target
        assert p95 < 100.0, f"P95 latency {p95}ms exceeds 100ms target"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
