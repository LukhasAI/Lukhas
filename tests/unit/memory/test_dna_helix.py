"""
Tests for DNA Helix Immutable Memory Architecture
"""

import asyncio
import shutil
import tempfile
from pathlib import Path

import pytest

from lukhas.memory.dna_helix import (
    DNAHealixCore,
    MemoryHelix,
    RepairMethod,
    SymbolicRepairLoop,
    SymbolicStrand,
)
from lukhas.memory.dna_helix.helix_vault import HelixVault


class TestSymbolicStrand:
    """Test symbolic strand functionality"""

    def test_strand_creation(self):
        """Test creating symbolic strands"""
        glyphs = ["TRUST", "PROTECT", "LEARN"]
        strand = SymbolicStrand(glyphs)

        assert len(strand) == 3
        assert strand[0] == "TRUST"
        assert strand.sequence == ("TRUST", "PROTECT", "LEARN")

    def test_strand_immutability(self):
        """Test that strands are immutable"""
        glyphs = ["A", "B", "C"]
        strand = SymbolicStrand(glyphs)

        # Should not be able to modify
        with pytest.raises(TypeError):
            strand.sequence[0] = "X"

    def test_entropy_calculation(self):
        """Test entropy calculation"""
        # Low entropy (repetitive)
        low_entropy = SymbolicStrand(["A", "A", "A", "A"])
        assert low_entropy.entropy() == 0.0

        # High entropy (diverse)
        high_entropy = SymbolicStrand(["A", "B", "C", "D"])
        assert high_entropy.entropy() > 0.9

        # Medium entropy
        medium_entropy = SymbolicStrand(["A", "A", "B", "B"])
        assert 0.4 < medium_entropy.entropy() < 0.6

    def test_hash_generation(self):
        """Test cryptographic hash generation"""
        strand1 = SymbolicStrand(["A", "B", "C"])
        strand2 = SymbolicStrand(["A", "B", "C"])
        strand3 = SymbolicStrand(["X", "Y", "Z"])

        # Same content should have same hash
        assert strand1.hash() == strand2.hash()

        # Different content should have different hash
        assert strand1.hash() != strand3.hash()

        # Hash should be consistent
        assert strand1.hash() == strand1.hash()

    def test_distance_calculation(self):
        """Test distance calculations between strands"""
        strand1 = SymbolicStrand(["A", "B", "C", "D"])
        strand2 = SymbolicStrand(["A", "B", "X", "D"])
        strand3 = SymbolicStrand(["W", "X", "Y", "Z"])

        # Edit distance
        assert strand1.distance_to(strand1, "edit") == 0
        assert strand1.distance_to(strand2, "edit") == 1
        assert strand1.distance_to(strand3, "edit") == 4

        # Cosine distance
        assert (
            abs(strand1.distance_to(strand1, "cosine")) < 1e-10
        )  # Should be exactly 0
        assert strand1.distance_to(strand2, "cosine") < strand1.distance_to(
            strand3, "cosine"
        )


class TestDNAHealixCore:
    """Test DNA helix core functionality"""

    def test_helix_creation(self):
        """Test creating DNA helix core"""
        origin = SymbolicStrand(["TRUST", "PROTECT", "LEARN"])
        helix = DNAHealixCore(origin)

        assert helix.origin == origin
        assert helix.current.sequence == origin.sequence
        assert len(helix.repair_history) == 0

    def test_drift_calculation(self):
        """Test drift calculation methods"""
        origin = SymbolicStrand(["A", "B", "C", "D"])
        helix = DNAHealixCore(origin)

        # No drift initially
        assert abs(helix.calculate_drift()) < 1e-10  # Use tolerance for floating point

        # Introduce drift
        helix.current = SymbolicStrand(["A", "X", "C", "D"])

        # Test different methods
        edit_drift = helix.calculate_drift("edit")
        assert 0.2 < edit_drift < 0.3  # 1/4 = 0.25

        cosine_drift = helix.calculate_drift("cosine")
        assert cosine_drift > 0

        entropy_drift = helix.calculate_drift("entropy")
        assert entropy_drift >= 0

        combined_drift = helix.calculate_drift("combined")
        assert combined_drift > 0

    def test_repair_methods(self):
        """Test different repair methods"""
        origin = SymbolicStrand(["A", "B", "C", "D", "E", "F"])
        helix = DNAHealixCore(origin)

        # Introduce significant drift
        helix.current = SymbolicStrand(["X", "Y", "C", "D", "Z", "W"])
        initial_drift = helix.calculate_drift()

        # Test full reset
        helix.repair(RepairMethod.FULL_RESET)
        assert helix.current.sequence == origin.sequence
        assert abs(helix.calculate_drift()) < 1e-10  # Use tolerance for floating point

        # Test partial heal
        helix.current = SymbolicStrand(["X", "Y", "C", "D", "Z", "W"])
        helix.repair(RepairMethod.PARTIAL_HEAL)
        assert helix.calculate_drift() < initial_drift

        # Test selective repair
        helix.current = SymbolicStrand(["X", "Y", "C", "D", "Z", "W"])
        helix.repair(RepairMethod.SELECTIVE, positions=[0, 1])
        assert helix.current[0] == "A"
        assert helix.current[1] == "B"
        assert helix.current[2] == "C"  # Unchanged

    def test_consensus_repair(self):
        """Test consensus-based repair"""
        origin = SymbolicStrand(["A", "B", "C", "D"])
        helix = DNAHealixCore(origin)

        # Create drifted state
        helix.current = SymbolicStrand(["X", "Y", "Z", "W"])

        # Create quorum strands
        quorum = [
            SymbolicStrand(["A", "B", "C", "D"]),  # Matches origin
            SymbolicStrand(["A", "B", "X", "D"]),  # Slight variation
            SymbolicStrand(["A", "Y", "C", "D"]),  # Another variation
        ]

        helix.repair(RepairMethod.CONSENSUS, quorum_strands=quorum)

        # Should converge towards consensus (mostly origin)
        assert helix.current[0] == "A"  # Strong consensus
        assert helix.current[3] == "D"  # Strong consensus

    def test_repair_history(self):
        """Test repair history tracking"""
        origin = SymbolicStrand(["A", "B", "C"])
        helix = DNAHealixCore(origin)

        # Perform repairs
        helix.current = SymbolicStrand(["X", "Y", "Z"])
        helix.repair(RepairMethod.FULL_RESET, cause="Test repair 1")

        helix.current = SymbolicStrand(["A", "Y", "C"])
        helix.repair(RepairMethod.PARTIAL_HEAL, cause="Test repair 2")

        # Check history
        assert len(helix.repair_history) == 2

        # Check first repair
        repair1 = helix.repair_history[0]
        assert repair1.repair_method == RepairMethod.FULL_RESET
        assert repair1.cause == "Test repair 1"
        assert abs(repair1.drift_after) < 1e-10  # Use tolerance for floating point

        # Check second repair
        repair2 = helix.repair_history[1]
        assert repair2.repair_method == RepairMethod.PARTIAL_HEAL
        assert repair2.cause == "Test repair 2"


class TestSymbolicRepairLoop:
    """Test automatic repair loop"""

    @pytest.mark.asyncio
    async def test_repair_loop_start_stop(self):
        """Test starting and stopping repair loop"""
        origin = SymbolicStrand(["A", "B", "C"])
        helix = DNAHealixCore(origin)
        loop = SymbolicRepairLoop(helix, check_interval=0.1)

        # Start loop
        await loop.start()
        assert loop.running

        # Let it run briefly
        await asyncio.sleep(0.2)

        # Stop loop
        await loop.stop()
        assert not loop.running

    @pytest.mark.asyncio
    async def test_auto_repair(self):
        """Test automatic repair functionality"""
        origin = SymbolicStrand(["A", "B", "C", "D"])
        helix = DNAHealixCore(origin)
        helix.drift_threshold = 0.3  # Low threshold for testing

        loop = SymbolicRepairLoop(helix, check_interval=0.1, auto_repair=True)

        # Introduce drift
        helix.current = SymbolicStrand(["X", "Y", "Z", "W"])

        # Start loop
        await loop.start()

        # Wait for auto-repair
        await asyncio.sleep(0.3)

        # Should have repaired
        assert helix.calculate_drift() < helix.drift_threshold
        assert len(helix.repair_history) > 0

        await loop.stop()


class TestMemoryHelix:
    """Test complete memory helix system"""

    def test_memory_creation(self):
        """Test creating memory helix"""
        glyphs = ["REMEMBER", "LEARN", "GROW"]
        memory = MemoryHelix("test_memory", glyphs)

        assert memory.memory_id == "test_memory"
        assert memory.origin_strand.sequence == tuple(glyphs)
        assert memory.access_count == 0
        assert not memory.locked

    def test_memory_access(self):
        """Test memory access tracking"""
        memory = MemoryHelix("test", ["A", "B", "C"])

        # Access memory
        data = memory.access()

        assert data["memory_id"] == "test"
        assert data["origin"] == ["A", "B", "C"]
        assert memory.access_count == 1
        assert memory.last_accessed is not None

    def test_memory_mutation(self):
        """Test memory mutation"""
        memory = MemoryHelix("test", ["A", "B", "C"])

        # Mutate current strand
        memory.mutate(["X", "Y", "Z"])

        # Origin should be unchanged
        assert list(memory.origin_strand.sequence) == ["A", "B", "C"]

        # Current should be changed
        assert list(memory.helix_core.current.sequence) == ["X", "Y", "Z"]

        # Drift should be high
        assert memory.helix_core.calculate_drift() > 0.5

    def test_memory_contexts(self):
        """Test adding different context strands"""
        memory = MemoryHelix("test", ["FACT", "DATA"])

        # Add contexts
        memory.add_emotional_context(["HAPPY", "EXCITED"])
        memory.add_temporal_context(["MORNING", "TUESDAY"])
        memory.add_causal_context(["BECAUSE", "LEARNING"])

        # Check contexts
        assert list(memory.emotional_strand.sequence) == ["HAPPY", "EXCITED"]
        assert list(memory.temporal_strand.sequence) == ["MORNING", "TUESDAY"]
        assert list(memory.causal_strand.sequence) == ["BECAUSE", "LEARNING"]

    def test_memory_locking(self):
        """Test GDPR-compliant memory locking"""
        memory = MemoryHelix("test", ["A", "B", "C"])

        # Lock memory
        memory.lock("GDPR request")
        assert memory.locked
        assert "locked:GDPR request" in memory.tags

        # Should not be able to access
        with pytest.raises(PermissionError):
            memory.access()

        # Should not be able to mutate
        with pytest.raises(PermissionError):
            memory.mutate(["X", "Y", "Z"])

        # Unlock
        memory.unlock()
        assert not memory.locked

        # Should be able to access again
        data = memory.access()
        assert data is not None

    def test_memory_export_import(self):
        """Test memory export and import"""
        # Create and modify memory
        memory = MemoryHelix("test", ["A", "B", "C"])
        memory.add_emotional_context(["HAPPY"])
        memory.mutate(["A", "X", "C"])
        memory.tags.add("important")

        # Export
        exported = memory.export()

        # Import
        restored = MemoryHelix.from_export(exported)

        # Check restoration
        assert restored.memory_id == memory.memory_id
        assert restored.origin_strand.sequence == memory.origin_strand.sequence
        assert (
            restored.helix_core.current.sequence == memory.helix_core.current.sequence
        )
        assert restored.emotional_strand.sequence == memory.emotional_strand.sequence
        assert restored.tags == memory.tags


class TestHelixVault:
    """Test helix vault functionality"""

    @pytest.fixture
    def temp_vault_path(self):
        """Create temporary vault directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    async def test_vault_creation(self, temp_vault_path):
        """Test creating vault"""
        vault = HelixVault(temp_vault_path)
        await vault.start()

        assert len(vault.memories) == 0
        assert vault.running

        await vault.stop()
        assert not vault.running

    @pytest.mark.asyncio
    async def test_memory_management(self, temp_vault_path):
        """Test memory creation and retrieval"""
        vault = HelixVault(temp_vault_path)
        await vault.start()

        # Create memories
        memory1 = vault.create_memory("mem1", ["A", "B", "C"], tags={"test", "alpha"})
        memory2 = vault.create_memory("mem2", ["X", "Y", "Z"], tags={"test", "beta"})

        # Retrieve
        assert vault.get_memory("mem1") == memory1
        assert vault.get_memory("mem2") == memory2
        assert vault.get_memory("nonexistent") is None

        await vault.stop()

    @pytest.mark.asyncio
    async def test_search_functionality(self, temp_vault_path):
        """Test vault search capabilities"""
        vault = HelixVault(temp_vault_path)
        await vault.start()

        # Create test memories
        vault.create_memory("mem1", ["A"], tags={"alpha", "test"})
        vault.create_memory("mem2", ["B"], tags={"beta", "test"})
        vault.create_memory("mem3", ["C"], tags={"alpha", "beta"})

        # Search by tags
        alpha_memories = vault.search_by_tags({"alpha"})
        assert len(alpha_memories) == 2

        test_memories = vault.search_by_tags({"test"})
        assert len(test_memories) == 2

        # Search with match_all
        alpha_test = vault.search_by_tags({"alpha", "test"}, match_all=True)
        assert len(alpha_test) == 1

        await vault.stop()

    @pytest.mark.asyncio
    async def test_persistence(self, temp_vault_path):
        """Test vault persistence"""
        # Create vault and add memories
        vault1 = HelixVault(temp_vault_path)
        await vault1.start()

        vault1.create_memory("persist1", ["A", "B"], tags={"persistent"})
        vault1.create_memory("persist2", ["X", "Y"], tags={"persistent"})

        await vault1.persist_vault()
        await vault1.stop()

        # Create new vault and load
        vault2 = HelixVault(temp_vault_path)
        await vault2.start()

        # Should have loaded memories
        assert len(vault2.memories) == 2
        assert vault2.get_memory("persist1") is not None
        assert vault2.get_memory("persist2") is not None

        await vault2.stop()

    @pytest.mark.asyncio
    async def test_drift_oracle(self, temp_vault_path):
        """Test drift oracle functionality"""
        vault = HelixVault(temp_vault_path)
        await vault.start()

        # Create memories with different drift levels
        vault.create_memory("low_drift", ["A", "B", "C"])
        mem2 = vault.create_memory("high_drift", ["X", "Y", "Z"])

        # Introduce drift
        mem2.mutate(["W", "W", "W"])

        # Create oracle
        oracle = vault.create_drift_oracle()
        analysis = oracle.analyze_drift_patterns()

        assert analysis["total_analyzed"] == 2
        assert analysis["average_drift"] > 0
        assert "high_drift" in analysis["high_drift_memories"]

        await vault.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
