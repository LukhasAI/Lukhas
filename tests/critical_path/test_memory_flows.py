#!/usr/bin/env python3
"""
🧠 Memory System Critical Path Tests
====================================
Tests critical memory flows and DNA helix functionality.
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import numpy as np
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestMemoryDNAHelixPath:
    """Test DNA helix memory critical paths"""

    def test_dna_helix_imports(self):
        """Test that DNA helix components import correctly"""
        try:
            from memory.dna_helix.dna_healix import (
                DNAHealixCore,
                MemoryHelix,
                SymbolicStrand,
            )

            assert DNAHealixCore is not None
            assert SymbolicStrand is not None
            assert MemoryHelix is not None
        except ImportError as e:
            pytest.skip(f"DNA helix not available: {e}")

    def test_symbolic_strand_creation(self):
        """Test symbolic strand creation and operations"""
        try:
            from core.common.glyph import GLYPHToken, GLYPHType
            from memory.dna_helix.dna_healix import SymbolicStrand

            # Create test GLYPH token
            test_token = GLYPHToken(
                token_type=GLYPHType.SYMBOLIC,
                content="TEST_MEMORY",
                metadata={"test": True},
            )

            # Create symbolic strand
            strand = SymbolicStrand(
                strand_id="test_strand_001",
                glyph_sequence=[test_token],
                metadata={"origin": "test"},
            )

            assert strand.strand_id == "test_strand_001"
            assert len(strand.glyph_sequence) == 1
            assert strand.glyph_sequence[0].content == "TEST_MEMORY"

        except ImportError:
            pytest.skip("DNA helix components not available")

    @pytest.mark.asyncio
    async def test_memory_helix_storage_retrieval(self):
        """Test memory helix storage and retrieval path"""
        try:
            from core.common.glyph import GLYPHToken, GLYPHType
            from memory.dna_helix.dna_healix import MemoryHelix, SymbolicStrand

            # Create memory helix
            helix = MemoryHelix(helix_id="test_helix")

            # Create test strand
            test_token = GLYPHToken(
                token_type=GLYPHType.SYMBOLIC,
                content="MEMORY_TEST",
                metadata={"importance": 0.8},
            )

            strand = SymbolicStrand(
                strand_id="strand_001",
                glyph_sequence=[test_token],
                metadata={"type": "episodic"},
            )

            # Test storage
            await helix.store_strand(strand)
            assert len(helix.strands) == 1

            # Test retrieval
            retrieved = await helix.retrieve_strand("strand_001")
            assert retrieved is not None
            assert retrieved.strand_id == "strand_001"

        except ImportError:
            pytest.skip("DNA helix components not available")

    @pytest.mark.asyncio
    async def test_drift_detection_path(self):
        """Test memory drift detection critical path"""
        try:
            from memory.dna_helix.dna_healix import DNAHealixCore

            # Create DNA helix core
            core = DNAHealixCore()

            # Test drift detection with mock data
            test_vector = np.array([1.0, 2.0, 3.0])
            original_vector = np.array([1.1, 2.1, 2.9])

            # Should detect minimal drift
            drift_score = core._calculate_drift(test_vector, original_vector)
            assert isinstance(drift_score, (int, float))
            assert drift_score >= 0.0

        except ImportError:
            pytest.skip("DNA helix components not available")


class TestMemorySystemIntegration:
    """Test memory system integration paths"""

    @pytest.mark.asyncio
    async def test_memory_interface_registration(self):
        """Test memory interface registration path"""
        from core.interfaces.memory_interface import (
            MemoryTestInterface,
            get_test_module,
            register_test_module,
        )

        # Create mock test module
        class MockMemoryTestModule(MemoryTestInterface):
            async def test_error_conditions(self):
                return {"status": "passed", "errors": 0}

            async def test_memory_lifecycle(self):
                return {"status": "passed", "lifecycle_tests": 5}

        # Register and retrieve
        mock_module = MockMemoryTestModule()
        register_test_module("test_memory_module", mock_module)

        retrieved = get_test_module("test_memory_module")
        assert retrieved is not None

        # Test interface methods
        error_result = await retrieved.test_error_conditions()
        assert error_result["status"] == "passed"

        lifecycle_result = await retrieved.test_memory_lifecycle()
        assert lifecycle_result["status"] == "passed"

    def test_memory_type_enum_path(self):
        """Test memory type enumeration access path"""
        from core.interfaces.memory_interface import MemoryType

        # Test that all expected memory types are available
        expected_types = [
            "EPISODIC",
            "SEMANTIC",
            "PROCEDURAL",
            "WORKING",
            "LONG_TERM",
            "SHORT_TERM",
        ]

        for memory_type in expected_types:
            assert hasattr(
                MemoryType, memory_type
            ), f"MemoryType.{memory_type} not found"

        # Test enum values
        assert MemoryType.EPISODIC.value == "episodic"
        assert MemoryType.SEMANTIC.value == "semantic"

    @pytest.mark.asyncio
    async def test_memory_orchestrator_initialization_path(self):
        """Test memory orchestrator initialization critical path"""
        with patch(
            "memory.core.unified_memory_orchestrator.get_test_module"
        ) as mock_get_test:
            # Mock successful test module retrieval
            mock_test_module = Mock()
            mock_test_module.test_memory_lifecycle = AsyncMock(
                return_value={"status": "passed"}
            )
            mock_test_module.test_error_conditions = AsyncMock(
                return_value={"status": "passed"}
            )
            mock_get_test.return_value = mock_test_module

            try:
                from memory.core.unified_memory_orchestrator import (
                    UnifiedMemoryOrchestrator,
                )

                # This should not raise circular dependency errors
                orchestrator = UnifiedMemoryOrchestrator(
                    hippocampal_capacity=100, neocortical_capacity=1000
                )

                # Test that comprehensive tester is initialized
                assert hasattr(orchestrator, "comprehensive_memory_tester")
                assert orchestrator.comprehensive_memory_tester["initialized"] is True

            except ImportError as e:
                pytest.skip(f"Memory orchestrator not available: {e}")


class TestMemoryPerformancePaths:
    """Test memory performance critical paths"""

    def test_memory_vector_operations(self):
        """Test memory vector operations path"""
        try:
            from memory.dna_helix.dna_healix import DNAHealixCore

            core = DNAHealixCore()

            # Test vector similarity calculation
            vec1 = np.array([1.0, 2.0, 3.0])
            vec2 = np.array([1.1, 2.1, 3.1])

            similarity = core._calculate_similarity(vec1, vec2)
            assert isinstance(similarity, (int, float))
            assert 0.0 <= similarity <= 1.0

        except ImportError:
            pytest.skip("DNA helix components not available")

    @pytest.mark.asyncio
    async def test_memory_concurrent_access_path(self):
        """Test concurrent memory access path"""
        try:
            from core.common.glyph import GLYPHToken, GLYPHType
            from memory.dna_helix.dna_healix import MemoryHelix, SymbolicStrand

            helix = MemoryHelix(helix_id="concurrent_test")

            # Create multiple strands for concurrent access
            async def store_strand(index):
                token = GLYPHToken(
                    token_type=GLYPHType.SYMBOLIC,
                    content=f"CONCURRENT_TEST_{index}",
                    metadata={"index": index},
                )
                strand = SymbolicStrand(
                    strand_id=f"concurrent_strand_{index}",
                    glyph_sequence=[token],
                    metadata={"concurrent": True},
                )
                await helix.store_strand(strand)
                return strand.strand_id

            # Test concurrent storage
            tasks = [store_strand(i) for i in range(5)]
            results = await asyncio.gather(*tasks)

            # Verify all strands were stored
            assert len(results) == 5
            assert len(helix.strands) == 5

            # Test concurrent retrieval
            async def retrieve_strand(strand_id):
                return await helix.retrieve_strand(strand_id)

            retrieve_tasks = [retrieve_strand(strand_id) for strand_id in results]
            retrieved_strands = await asyncio.gather(*retrieve_tasks)

            # Verify all strands were retrieved
            assert len(retrieved_strands) == 5
            assert all(strand is not None for strand in retrieved_strands)

        except ImportError:
            pytest.skip("DNA helix components not available")


class TestMemoryErrorRecoveryPaths:
    """Test memory error recovery paths"""

    @pytest.mark.asyncio
    async def test_memory_corruption_detection(self):
        """Test memory corruption detection path"""
        try:
            from memory.dna_helix.dna_healix import DNAHealixCore

            core = DNAHealixCore()

            # Simulate corrupted memory vector
            original = np.array([1.0, 2.0, 3.0])
            corrupted = np.array([10.0, 20.0, 30.0])  # Significant drift

            drift_score = core._calculate_drift(original, corrupted)

            # Should detect high drift
            assert drift_score > 0.5, f"Expected high drift, got {drift_score}"

        except ImportError:
            pytest.skip("DNA helix components not available")

    @pytest.mark.asyncio
    async def test_memory_repair_mechanisms(self):
        """Test memory repair mechanisms path"""
        try:
            from memory.dna_helix.dna_healix import MemoryHelix

            helix = MemoryHelix(helix_id="repair_test")

            # Test helix integrity verification
            integrity_result = await helix.verify_integrity()
            assert isinstance(integrity_result, dict)
            assert "status" in integrity_result

        except ImportError:
            pytest.skip("DNA helix components not available")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
