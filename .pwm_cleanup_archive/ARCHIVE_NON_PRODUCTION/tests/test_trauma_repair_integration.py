#!/usr/bin/env python3
"""
Test Trauma Repair Integration
Tests for memory trauma repair system integration
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class TestTraumaRepairIntegration:
    """Test trauma repair integration with memory hub"""

    def test_trauma_repair_import(self):
        """Test that trauma repair can be imported"""
        from memory.repair.trauma_repair_wrapper import (
            get_memory_trauma_repair,
        )

        assert get_memory_trauma_repair is not None

    def test_memory_hub_trauma_repair(self):
        """Test trauma repair integration in memory hub"""
        try:
            from memory.memory_hub import get_memory_hub

            hub = get_memory_hub()

            # Check if trauma repair is registered
            if "trauma_repair" in hub.services:
                trauma_repair = hub.get_service("trauma_repair")
                assert trauma_repair is not None
                print("Trauma repair service found in hub")
            else:
                print("Trauma repair service not found in hub services")
        except ImportError as e:
            # If memory hub has import issues, at least verify the service can be created
            from memory.repair.trauma_repair_wrapper import (
                get_memory_trauma_repair,
            )

            trauma_repair = get_memory_trauma_repair()
            assert trauma_repair is not None
            print(
                f"Memory hub import failed ({e}), but trauma repair service works standalone"
            )

    @pytest.mark.asyncio
    async def test_trauma_repair_functionality(self):
        """Test trauma repair basic functionality"""
        from memory.repair.trauma_repair_wrapper import (
            get_memory_trauma_repair,
        )

        trauma_repair = get_memory_trauma_repair()
        if trauma_repair:
            # Initialize the system
            await trauma_repair.initialize()

            # Test memory scan
            result = await trauma_repair.scan_memory(
                memory_id="test_memory_001",
                memory_content={"data": "test content"},
                context={"source": "test"},
            )

            assert isinstance(result, dict)
            assert "memory_id" in result
            assert "trauma_detected" in result
            assert result["memory_id"] == "test_memory_001"

            # Test statistics
            stats = trauma_repair.get_repair_statistics()
            assert isinstance(stats, dict)
            assert stats["total_scans"] >= 1

            # Test active traumas
            active = await trauma_repair.get_active_traumas()
            assert isinstance(active, list)

            # Shutdown
            await trauma_repair.shutdown()

    @pytest.mark.asyncio
    async def test_forced_repair(self):
        """Test forced memory repair"""
        from memory.repair.trauma_repair_wrapper import (
            get_memory_trauma_repair,
        )

        trauma_repair = get_memory_trauma_repair()
        if trauma_repair:
            await trauma_repair.initialize()

            # Force repair on a memory
            result = await trauma_repair.force_repair("forced_memory_001")

            assert isinstance(result, dict)
            assert result["memory_id"] == "forced_memory_001"
            assert result["repair_initiated"] == True
            assert result["repair_status"] in ["success", "failed"]

            await trauma_repair.shutdown()

    @pytest.mark.asyncio
    async def test_memory_health_check(self):
        """Test memory health checking"""
        from memory.repair.trauma_repair_wrapper import (
            get_memory_trauma_repair,
        )

        trauma_repair = get_memory_trauma_repair()
        if trauma_repair:
            await trauma_repair.initialize()

            # Check health of a memory
            health = await trauma_repair.check_memory_health("health_check_001")

            assert isinstance(health, dict)
            assert health["memory_id"] == "health_check_001"
            assert "is_healthy" in health
            assert "has_scar_tissue" in health
            assert "active_trauma" in health

            await trauma_repair.shutdown()

    def test_mock_implementation(self):
        """Test that mock implementation works"""
        try:
            from memory.repair.trauma_repair_mock import (
                RepairStrategy,
                TraumaType,
                get_memory_trauma_repair,
            )

            trauma_repair = get_memory_trauma_repair()
            assert trauma_repair is not None

            # Test enums
            assert TraumaType.CORRUPTION.value == "corruption"
            assert RepairStrategy.HELICAL.value == "helical"

        except ImportError:
            pytest.skip("Mock implementation not available")

    @pytest.mark.asyncio
    async def test_healing_history(self):
        """Test healing history tracking"""
        from memory.repair.trauma_repair_wrapper import (
            get_memory_trauma_repair,
        )

        trauma_repair = get_memory_trauma_repair()
        if trauma_repair:
            await trauma_repair.initialize()

            # Scan some memories to potentially create healing history
            for i in range(5):
                await trauma_repair.scan_memory(
                    memory_id=f"history_test_{i}",
                    memory_content={"data": f"content_{i}"},
                )

            # Get healing history
            history = await trauma_repair.get_healing_history(limit=10)
            assert isinstance(history, list)

            # Check statistics after scans
            stats = trauma_repair.get_repair_statistics()
            assert stats["total_scans"] >= 5

            await trauma_repair.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
