#!/usr/bin/env python3
"""
Test script for validating priority modules functionality
"""

import asyncio
import sys
from datetime import datetime

from core.colonies.creativity_colony import CreativityColony
from core.colonies.memory_colony_enhanced import MemoryColony
from core.colonies.reasoning_colony import ReasoningColony
from core.integration_hub import IntegrationConfig, UnifiedIntegration

# Import priority modules
from core.task_manager import LukhλsTaskManager


async def test_task_manager():
    """Test task manager functionality"""
    print("\n🧪 Testing Task Manager...")

    task_manager = LukhλsTaskManager()

    # Create test tasks
    task1_id = task_manager.create_task(
        name="Test Symbol Validation",
        description="Validate test symbols",
        handler="symbol_validation",
    )

    task2_id = task_manager.create_task(
        name="Test File Processing",
        description="Process test files",
        handler="file_processing",
    )

    # Execute tasks
    success1 = await task_manager.execute_task(task1_id)
    success2 = await task_manager.execute_task(task2_id)

    # Get status
    status = task_manager.get_system_status()

    print("   - Created 2 test tasks")
    print(f"   - Task 1 execution: {'✅ Success' if success1 else '❌ Failed'}")
    print(f"   - Task 2 execution: {'✅ Success' if success2 else '❌ Failed'}")
    print(f"   - Total tasks: {status['total_tasks']}")
    print(f"   - Completed tasks: {status['task_counts']['completed']}")

    return success1 and success2


def test_integration_hub():
    """Test integration hub functionality"""
    print("\n🧪 Testing Integration Hub...")

    config = IntegrationConfig(max_concurrent_operations=5, timeout_seconds=10)
    hub = UnifiedIntegration(config)

    # Register test components
    result1 = hub.register_component("test_component_1", {"type": "test"})
    result2 = hub.register_component("test_component_2", {"type": "test"})

    print(
        f"   - Component 1 registration: {'✅ Success' if result1.success else '❌ Failed'}"
    )
    print(
        f"   - Component 2 registration: {'✅ Success' if result2.success else '❌ Failed'}"
    )
    print(f"   - Total registered components: {len(hub.components)}")

    return result1.success and result2.success


def test_colonies():
    """Test colony modules"""
    print("\n🧪 Testing Colony Modules...")

    try:
        # Test Memory Colony
        memory_colony = MemoryColony("test_memory_colony")
        print("   - Memory Colony Enhanced: ✅ Initialized")

        # Test Creativity Colony
        creativity_colony = CreativityColony("test_creativity_colony")
        print("   - Creativity Colony: ✅ Initialized")

        # Test Reasoning Colony
        reasoning_colony = ReasoningColony("test_reasoning_colony")
        print("   - Reasoning Colony: ✅ Initialized")

        return True
    except Exception as e:
        print(f"   - Colony initialization failed: ❌ {str(e)}")
        return False


async def main():
    """Main test runner"""
    print("🚀 Testing Priority Modules for LUKHAS AI")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    results = []

    # Test Task Manager
    results.append(await test_task_manager())

    # Test Integration Hub
    results.append(test_integration_hub())

    # Test Colonies
    results.append(test_colonies())

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    passed = sum(results)
    total = len(results)
    print(f"   - Tests passed: {passed}/{total}")
    print(f"   - Success rate: {(passed/total)*100:.0f}%")

    if passed == total:
        print("\n✅ All priority modules are functional!")
    else:
        print("\n⚠️ Some modules need attention")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
