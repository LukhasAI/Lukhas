#!/usr/bin/env python3
"""
Integration test for memory comprehensive system with unified memory orchestrator
Tests the integration of comprehensive memory testing capabilities
"""

import asyncio
import sys
from pathlib import Path

import pytest
import pytest_asyncio

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the modules under test
from memory.core.unified_memory_orchestrator import (
    MemoryType,
    UnifiedMemoryOrchestrator,
)
from memory.systems.memory_comprehensive import (
    test_error_conditions,
    test_memory_lifecycle,
)


class TestMemoryComprehensiveIntegration:
    """Test comprehensive memory system integration"""

    @pytest_asyncio.fixture
    async def orchestrator(self):
        """Create test orchestrator with memory comprehensive integration"""
        orchestrator = UnifiedMemoryOrchestrator(
            enable_colony_validation=False, enable_distributed=False
        )

        # Wait for background tasks to start
        await asyncio.sleep(0.1)

        yield orchestrator

        # Cleanup - no explicit stop method needed

    @pytest.mark.asyncio
    async def test_comprehensive_memory_tester_initialization(self, orchestrator):
        """Test that comprehensive memory tester is properly initialized"""
        # Check that comprehensive memory tester is initialized
        assert hasattr(orchestrator, "comprehensive_memory_tester")
        assert orchestrator.comprehensive_memory_tester.get("initialized", False)

        # Check that test functions are loaded
        assert "test_memory_lifecycle" in orchestrator.comprehensive_memory_tester
        assert "test_error_conditions" in orchestrator.comprehensive_memory_tester
        assert callable(
            orchestrator.comprehensive_memory_tester["test_memory_lifecycle"]
        )
        assert callable(
            orchestrator.comprehensive_memory_tester["test_error_conditions"]
        )

    @pytest.mark.asyncio
    async def test_memory_lifecycle_interface(self, orchestrator):
        """Test memory lifecycle testing interface"""
        # Test the interface method
        result = orchestrator.run_memory_lifecycle_test()

        # Verify result structure
        assert isinstance(result, dict)
        assert "status" in result
        assert "test_type" in result
        assert "result" in result
        assert "timestamp" in result

        # Verify success status
        assert result["status"] == "success"
        assert result["test_type"] == "memory_lifecycle"

        # Verify test result structure
        test_result = result["result"]
        assert isinstance(test_result, dict)
        assert "status" in test_result

    @pytest.mark.asyncio
    async def test_error_condition_interface(self, orchestrator):
        """Test error condition testing interface"""
        # Test the interface method
        result = orchestrator.run_error_condition_test()

        # Verify result structure
        assert isinstance(result, dict)
        assert "status" in result
        assert "test_type" in result
        assert "result" in result
        assert "timestamp" in result

        # Verify success status
        assert result["status"] == "success"
        assert result["test_type"] == "error_conditions"

        # Verify test result structure
        test_result = result["result"]
        assert isinstance(test_result, dict)
        assert "status" in test_result

    @pytest.mark.asyncio
    async def test_comprehensive_memory_status(self, orchestrator):
        """Test comprehensive memory status interface"""
        # Test the status method
        status = orchestrator.get_comprehensive_memory_status()

        # Verify status structure
        assert isinstance(status, dict)
        assert "comprehensive_tester" in status
        assert "memory_statistics" in status
        assert "system_health" in status

        # Verify comprehensive tester status
        tester_status = status["comprehensive_tester"]
        assert tester_status["initialized"] is True
        assert "test_memory_lifecycle" in tester_status["available_tests"]
        assert "test_error_conditions" in tester_status["available_tests"]
        assert tester_status["test_functions_loaded"] is True

        # Verify memory statistics are included
        assert isinstance(status["memory_statistics"], dict)
        assert "total_memories" in status["memory_statistics"]

    @pytest.mark.asyncio
    async def test_comprehensive_testing_with_real_memory(self, orchestrator):
        """Test comprehensive testing with actual memory operations"""
        # Add some test memories
        await orchestrator.encode_memory(
            content={"test": "lifecycle memory"},
            memory_type=MemoryType.EPISODIC,
            importance=0.7,
            tags=["test", "lifecycle"],
        )

        await orchestrator.encode_memory(
            content={"test": "error condition memory"},
            memory_type=MemoryType.SEMANTIC,
            importance=0.8,
            tags=["test", "error"],
        )

        # Wait for encoding to complete
        await asyncio.sleep(0.2)

        # Run lifecycle test
        lifecycle_result = orchestrator.run_memory_lifecycle_test()
        assert lifecycle_result["status"] == "success"

        # Run error condition test
        error_result = orchestrator.run_error_condition_test()
        assert error_result["status"] == "success"

        # Verify memory statistics reflect the added memories
        status = orchestrator.get_comprehensive_memory_status()
        memory_stats = status["memory_statistics"]
        assert memory_stats["total_memories"] >= 2

    @pytest.mark.asyncio
    async def test_error_handling_uninitialized_tester(self):
        """Test error handling when comprehensive tester is not initialized"""
        # Create orchestrator but don't initialize properly
        orchestrator = UnifiedMemoryOrchestrator(
            enable_colony_validation=False, enable_distributed=False
        )

        # Manually set tester as uninitialized
        orchestrator.comprehensive_memory_tester = {"initialized": False}

        # Test lifecycle method with uninitialized tester
        result = orchestrator.run_memory_lifecycle_test()
        assert result["status"] == "error"
        assert "not initialized" in result["message"]

        # Test error condition method with uninitialized tester
        result = orchestrator.run_error_condition_test()
        assert result["status"] == "error"
        assert "not initialized" in result["message"]

    @pytest.mark.asyncio
    async def test_comprehensive_functions_directly(self, orchestrator):
        """Test that comprehensive memory functions work directly"""
        # Test lifecycle function directly
        lifecycle_result = test_memory_lifecycle(orchestrator)
        assert isinstance(lifecycle_result, dict)
        assert "status" in lifecycle_result

        # Test error condition function directly
        error_result = test_error_conditions(orchestrator)
        assert isinstance(error_result, dict)
        assert "status" in error_result


if __name__ == "__main__":
    # Run tests with asyncio support
    pytest.main([__file__, "-v", "--tb=short"])
    # Run tests with asyncio support
    pytest.main([__file__, "-v", "--tb=short"])
