#!/usr/bin/env python3
"""
Test Memory Profiler Integration
Verifies that memory profiler is properly integrated into the memory hub
"""

import asyncio
import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from memory.memory_hub import initialize_memory_system


class TestMemoryProfilerIntegration:
    """Test suite for memory profiler integration"""

    @pytest.mark.asyncio
    async def test_memory_hub_initialization(self):
        """Test that memory hub initializes with profiler"""
        hub = await initialize_memory_system()
        assert hub is not None
        assert hub.is_initialized

        # Check that memory profiler service is registered
        services = hub.list_services()
        assert "memory_profiler" in services

        # Get the profiler service
        profiler = hub.get_service("memory_profiler")
        assert profiler is not None

    @pytest.mark.asyncio
    async def test_memory_profiler_functionality(self):
        """Test basic memory profiler functionality"""
        hub = await initialize_memory_system()
        profiler = hub.get_service("memory_profiler")

        # Test allocation recording
        profiler.record_allocation("test_tensor_1", 1024 * 1024)  # 1MB
        profiler.record_allocation("test_tensor_2", 2 * 1024 * 1024)  # 2MB

        # Test deallocation
        profiler.record_deallocation("test_tensor_1")

        # Test memory analysis
        analysis = profiler.analyze_memory_patterns()
        assert analysis["total_allocations"] >= 2
        assert analysis["total_deallocations"] >= 1
        assert "recommendations" in analysis

        # Test category usage
        category_usage = profiler.get_memory_usage_by_category()
        assert isinstance(category_usage, dict)
        assert len(category_usage) > 0

    @pytest.mark.asyncio
    async def test_memory_profiler_timeline(self):
        """Test memory profiler timeline functionality"""
        hub = await initialize_memory_system()
        profiler = hub.get_service("memory_profiler")

        # Create some events
        for i in range(5):
            profiler.record_allocation(f"test_tensor_{i}", (i + 1) * 1024)

        # Get timeline
        timeline = profiler.get_memory_timeline(limit=10)
        assert isinstance(timeline, list)
        assert len(timeline) >= 5

        # Verify timeline structure
        if timeline:
            event = timeline[0]
            assert "timestamp" in event
            assert "action" in event
            assert "tensor_id" in event

    @pytest.mark.asyncio
    async def test_memory_profiler_reset(self):
        """Test memory profiler reset functionality"""
        hub = await initialize_memory_system()
        profiler = hub.get_service("memory_profiler")

        # Add some data
        profiler.record_allocation("test_tensor", 1024)

        # Reset
        profiler.reset_profiler()

        # Verify reset
        analysis = profiler.analyze_memory_patterns()
        assert analysis["total_allocations"] == 0
        assert analysis["total_deallocations"] == 0
        assert analysis["active_tensors"] == 0


if __name__ == "__main__":
    # Run basic integration test
    async def main():
        print("Testing Memory Profiler Integration...")

        try:
            # Initialize memory system
            hub = await initialize_memory_system()
            print(f"✓ Memory hub initialized with {len(hub.services)} services")

            # Check profiler
            if "memory_profiler" in hub.services:
                print("✓ Memory profiler service registered")
                profiler = hub.get_service("memory_profiler")

                # Test basic functionality
                profiler.record_allocation("test_1", 1024 * 1024)
                profiler.record_allocation("test_2", 2 * 1024 * 1024)
                profiler.record_deallocation("test_1")

                analysis = profiler.analyze_memory_patterns()
                print(
                    f"✓ Memory analysis: {analysis['total_allocations']} allocations, "
                    f"peak {analysis.get('peak_memory_usage_mb', 0):.2f} MB"
                )

                print("\n✅ Memory profiler integration successful!")
            else:
                print("❌ Memory profiler service not found")

        except Exception as e:
            print(f"❌ Integration test failed: {e}")
            import traceback

            traceback.print_exc()

    asyncio.run(main())
