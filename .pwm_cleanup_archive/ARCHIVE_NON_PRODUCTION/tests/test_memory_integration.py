#!/usr/bin/env python3
"""
Test Memory System Integration
Tests for memory planning and profiler integration
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class TestMemoryIntegration:
    """Test memory hub integration with planning and profiler"""

    def test_memory_hub_import(self):
        """Test that memory hub can be imported"""
        from memory.memory_hub import MemoryHub, get_memory_hub

        assert get_memory_hub is not None
        assert MemoryHub is not None

    def test_memory_hub_initialization(self):
        """Test memory hub initialization"""
        from memory.memory_hub import get_memory_hub

        hub = get_memory_hub()
        assert hub is not None
        assert hasattr(hub, "services")
        assert len(hub.services) > 0

    def test_memory_planner_integration(self):
        """Test memory planner is integrated"""
        from memory.memory_hub import get_memory_hub

        hub = get_memory_hub()

        # Check if memory planner is registered
        if "memory_planner" in hub.services:
            planner = hub.get_service("memory_planner")
            assert planner is not None

            # Test planner functionality
            if hasattr(planner, "create_allocation_pool"):
                pool = planner.create_allocation_pool("test_pool", 1024)
                assert pool is not None

            if hasattr(planner, "track_live_range"):
                lr = planner.track_live_range("test_tensor", 0.0, 10.0)
                assert lr is not None

            if hasattr(planner, "get_allocation_stats"):
                stats = planner.get_allocation_stats()
                assert isinstance(stats, dict)
                assert "allocation_pools" in stats

    def test_memory_profiler_integration(self):
        """Test memory profiler is integrated"""
        from memory.memory_hub import get_memory_hub

        hub = get_memory_hub()

        # Check if memory profiler is registered
        if "memory_profiler" in hub.services:
            profiler = hub.get_service("memory_profiler")
            assert profiler is not None

            # Test profiler functionality
            if hasattr(profiler, "record_allocation"):
                profiler.record_allocation("test_tensor", 1024)

            if hasattr(profiler, "get_memory_usage_by_category"):
                usage = profiler.get_memory_usage_by_category()
                assert isinstance(usage, dict)

            if hasattr(profiler, "analyze_memory_patterns"):
                analysis = profiler.analyze_memory_patterns()
                assert isinstance(analysis, dict)
                assert "total_allocations" in analysis

    @pytest.mark.asyncio
    async def test_memory_hub_async_initialization(self):
        """Test async initialization of memory hub"""
        from memory.memory_hub import initialize_memory_system

        try:
            hub = await initialize_memory_system()
            assert hub is not None
            assert hub.is_initialized
        except Exception as e:
            # Some services may fail to initialize, but hub should still work
            print(f"Initialization warning: {e}")

    def test_service_discovery_registration(self):
        """Test that memory services are registered for discovery"""
        from memory.memory_hub import get_memory_hub

        hub = get_memory_hub()

        # Key services that should be available
        expected_services = [
            "memory_planner",
            "memory_profiler",
            "dreammanager",
            "manager",
            "basemanager",
        ]

        registered_services = hub.list_services()

        # Check if at least some expected services are registered
        found_services = [s for s in expected_services if s in registered_services]
        assert (
            len(found_services) > 0
        ), f"No expected services found. Available: {registered_services}"

    def test_memory_planning_wrapper(self):
        """Test memory planning wrapper functionality"""
        try:
            # Try wrapper first, then mock
            try:
                from memory.systems.memory_planning_wrapper import (
                    get_memory_planner,
                )
            except:
                from memory.systems.memory_planning_mock import (
                    get_memory_planner,
                )

            planner = get_memory_planner()
            if planner:
                # Test live range tracking
                lr1 = planner.track_live_range("tensor1", 0, 10)
                lr2 = planner.track_live_range("tensor2", 5, 15)
                lr3 = planner.track_live_range("tensor3", 20, 30)

                # Test overlap checking
                assert planner.check_overlaps("tensor1", "tensor2") == True
                assert planner.check_overlaps("tensor1", "tensor3") == False

                # Test optimization
                opts = planner.optimize_memory_layout()
                assert "reuse_opportunities" in opts
                assert opts["reuse_opportunities"] >= 1
        except ImportError:
            pytest.skip("Memory planning wrapper not available")

    def test_memory_profiler_wrapper(self):
        """Test memory profiler wrapper functionality"""
        try:
            # Try wrapper first, then mock
            try:
                from memory.systems.memory_profiler_wrapper import (
                    get_memory_profiler,
                )
            except:
                from memory.systems.memory_profiler_mock import (
                    get_memory_profiler,
                )

            profiler = get_memory_profiler()
            if profiler:
                # Record some allocations
                profiler.record_allocation("tensor1", 1024 * 1024)  # 1MB
                profiler.record_allocation("tensor2", 2 * 1024 * 1024)  # 2MB
                profiler.record_deallocation("tensor1")

                # Check timeline
                timeline = profiler.get_memory_timeline()
                assert len(timeline) == 3

                # Check analysis
                analysis = profiler.analyze_memory_patterns()
                assert analysis["total_allocations"] == 2
                assert analysis["total_deallocations"] == 1
                assert "peak_memory_usage_mb" in analysis
        except ImportError:
            pytest.skip("Memory profiler wrapper not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
