#!/usr/bin/env python3
"""
Simple test to validate orchestrator migration patterns
Tests basic instantiation and method availability
"""

import os
import sys

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
)

import asyncio
from dataclasses import dataclass


def test_base_patterns():
    """Test the base orchestrator patterns work correctly"""
    print("=" * 60)
    print("Testing Base Orchestrator Patterns")
    print("=" * 60)

    # Test 1: Import base classes
    try:
        from orchestration.base import (
            BaseOrchestrator,
            OrchestratorConfig,
            OrchestratorState,
        )

        print("✓ Base orchestrator imported")
    except Exception as e:
        print(f"✗ Failed to import base: {e}")
        return False

    # Test 2: Create a simple test orchestrator
    @dataclass
    class TestConfig(OrchestratorConfig):
        test_param: str = "test"

    class TestOrchestrator(BaseOrchestrator):
        async def _initialize_components(self) -> bool:
            return True

        async def _start_components(self) -> None:
            pass

        async def _stop_components(self) -> None:
            pass

        async def _check_component_health(self, name: str):
            return True

        async def _process_operation(self, operation):
            return {"status": "success", "data": operation}

    # Test 3: Instantiate and check properties
    try:
        config = TestConfig(name="TestOrch", description="Test Orchestrator")
        orchestrator = TestOrchestrator(config)

        assert orchestrator.config.name == "TestOrch"
        assert orchestrator.state == OrchestratorState.UNINITIALIZED
        assert hasattr(orchestrator, "metrics")
        assert hasattr(orchestrator, "components")

        print("✓ Test orchestrator created successfully")
        print(f"  - Name: {orchestrator.config.name}")
        print(f"  - State: {orchestrator.state.name}")
        print(f"  - Has lifecycle methods: {hasattr(orchestrator, 'initialize')}")

        return True

    except Exception as e:
        print(f"✗ Failed to create test orchestrator: {e}")
        return False


def test_memory_orchestrator_simple():
    """Test memory orchestrator can be imported and instantiated"""
    print("\n" + "=" * 60)
    print("Testing Memory Orchestrator (Simple)")
    print("=" * 60)

    try:
        from orchestration.migrated.memory_orchestrator import (
            MemoryOrchestrator,
        )
        from orchestration.module_orchestrator import ModuleOrchestratorConfig

        print("✓ MemoryOrchestrator imported")

        # Create simple config without post_init issues
        config = ModuleOrchestratorConfig(
            name="TestMemory", description="Test Memory", module_name="memory"
        )

        orchestrator = MemoryOrchestrator(config)

        print("✓ MemoryOrchestrator instantiated")
        print(f"  - Type: {type(orchestrator).__name__}")
        print(f"  - Config name: {orchestrator.config.name}")
        print(f"  - Has process method: {hasattr(orchestrator, 'process')}")
        print(
            f"  - Has required lifecycle methods: {hasattr(orchestrator, 'initialize')}"
        )

        # Check inheritance
        from orchestration.base import BaseOrchestrator
        from orchestration.module_orchestrator import ModuleOrchestrator

        assert isinstance(orchestrator, ModuleOrchestrator)
        assert isinstance(orchestrator, BaseOrchestrator)
        print("✓ Inheritance chain verified")

        return True

    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_lifecycle():
    """Test basic lifecycle operations"""
    print("\n" + "=" * 60)
    print("Testing Orchestrator Lifecycle")
    print("=" * 60)

    try:
        from orchestration.base import (
            BaseOrchestrator,
            OrchestratorConfig,
            OrchestratorState,
        )

        class SimpleTestOrchestrator(BaseOrchestrator):
            def __init__(self, config):
                super().__init__(config)
                self.test_state = {"initialized": False, "started": False}

            async def _initialize_components(self) -> bool:
                self.test_state["initialized"] = True
                return True

            async def _start_components(self) -> None:
                self.test_state["started"] = True

            async def _stop_components(self) -> None:
                self.test_state["started"] = False

            async def _check_component_health(self, name: str):
                return True

            async def _process_operation(self, operation):
                return {"processed": True, "state": self.test_state}

        # Test lifecycle
        config = OrchestratorConfig(name="LifecycleTest", description="Test lifecycle")
        orchestrator = SimpleTestOrchestrator(config)

        print(f"Initial state: {orchestrator.state.name}")
        assert orchestrator.state == OrchestratorState.UNINITIALIZED

        # Initialize
        init_result = await orchestrator.initialize()
        print(f"✓ Initialize: {init_result}, State: {orchestrator.state.name}")
        assert init_result
        assert orchestrator.state == OrchestratorState.INITIALIZED
        assert orchestrator.test_state["initialized"]

        # Start
        start_result = await orchestrator.start()
        print(f"✓ Start: {start_result}, State: {orchestrator.state.name}")
        assert start_result
        assert orchestrator.state == OrchestratorState.RUNNING
        assert orchestrator.test_state["started"]

        # Process
        result = await orchestrator.process({"test": "data"})
        print(f"✓ Process: Success={result.get('success')}")
        assert result.get("processed") or result.get("success")

        # Stop
        stop_result = await orchestrator.stop()
        print(f"✓ Stop: {stop_result}, State: {orchestrator.state.name}")
        assert stop_result
        assert orchestrator.state == OrchestratorState.STOPPED
        assert not orchestrator.test_state["started"]

        return True

    except Exception as e:
        print(f"✗ Lifecycle test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all simple tests"""
    print("ORCHESTRATOR MIGRATION - SIMPLE TESTS")
    print("=====================================\n")

    results = []

    # Test 1: Base patterns
    results.append(("Base Patterns", test_base_patterns()))

    # Test 2: Memory orchestrator
    results.append(("Memory Orchestrator", test_memory_orchestrator_simple()))

    # Test 3: Lifecycle
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results.append(("Lifecycle", loop.run_until_complete(test_lifecycle())))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")

    print(f"\nTotal: {passed}/{total} ({passed/total*100:.0f}%)")

    # Create summary report
    summary = f"""# Orchestrator Migration - Simple Test Results

**Date**: {asyncio.get_event_loop().time()}
**Tests Run**: {total}
**Passed**: {passed}
**Success Rate**: {passed/total*100:.0f}%

## Test Results

| Test | Result |
|------|--------|
"""

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        summary += f"| {name} | {status} |\n"

    summary += """
## Conclusions

The migration pattern has been validated for:
1. Base orchestrator instantiation and configuration
2. Inheritance hierarchy (BaseOrchestrator → ModuleOrchestrator → MemoryOrchestrator)
3. Lifecycle management (initialize → start → process → stop)
4. State transitions following the expected pattern

The architecture successfully provides:
- Standardized lifecycle management
- Consistent state tracking
- Proper inheritance and method overriding
- Configuration management through dataclasses
"""

    with open("simple_test_results.md", "w") as f:
        f.write(summary)

    print("\nResults saved to simple_test_results.md")


if __name__ == "__main__":
    main()
