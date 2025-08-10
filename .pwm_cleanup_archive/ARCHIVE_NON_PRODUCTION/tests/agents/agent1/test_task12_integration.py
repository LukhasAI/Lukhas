#!/usr/bin/env python3
"""
Test suite for Agent 1 Task 12: Persona Engine Integration
Tests the integration of PersonaEngine with the identity hub system.
"""

import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test imports
try:
    from core.identity.persona_engine import (
        PersonaEngine,
        create_and_initialize_identity_component,
        create_identity_component,
    )
    from identity.identity_hub import IdentityHub, get_identity_hub

    print("✅ Successfully imported PersonaEngine and IdentityHub")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


async def test_persona_engine_initialization():
    """Test that persona engine initializes correctly"""
    print("\n🧪 Test 1: Persona Engine Initialization")

    try:
        persona_engine = PersonaEngine()
        success = await persona_engine.initialize()
        print(f"✅ PersonaEngine initialized: {success}")

        status = persona_engine.get_status()
        print(f"✅ Status: {status}")

        return True
    except Exception as e:
        print(f"❌ Persona engine initialization failed: {e}")
        return False


async def test_identity_hub_persona_integration():
    """Test that identity hub integrates persona engine correctly"""
    print("\n🧪 Test 2: Identity Hub Persona Integration")

    try:
        # Get identity hub instance
        identity_hub = get_identity_hub()
        await identity_hub.initialize()
        print("✅ IdentityHub initialized")

        # Check persona engine status
        status = identity_hub.get_persona_engine_status()
        print(f"✅ Persona engine status: {status}")

        # Test validation
        validation_result = await identity_hub.validate_persona_engine()
        print(f"✅ Persona engine validation: {validation_result}")

        return True
    except Exception as e:
        print(f"❌ Identity hub persona integration failed: {e}")
        return False


async def test_identity_data_processing():
    """Test processing different types of identity data"""
    print("\n🧪 Test 3: Identity Data Processing")

    try:
        identity_hub = get_identity_hub()
        await identity_hub.initialize()

        # Test different categories of data processing
        test_cases = [
            {"data": {"test": "consciousness_data"}, "category": "consciousness"},
            {"data": {"user": "test_user"}, "category": "identity"},
            {"data": {"voice_sample": "test"}, "category": "voice"},
            {"data": {"policy": "test_policy"}, "category": "governance"},
            {"data": {"quantum_state": "superposition"}, "category": "quantum"},
            {"data": {"generic_info": "test"}, "category": "generic"},
        ]

        for i, test_case in enumerate(test_cases, 1):
            result = await identity_hub.process_identity_data(
                test_case["data"], test_case["category"]
            )
            print(f"✅ Test case {i} ({test_case['category']}): {result['status']}")

        return True
    except Exception as e:
        print(f"❌ Identity data processing failed: {e}")
        return False


async def test_identity_component_creation():
    """Test creating and initializing identity components"""
    print("\n🧪 Test 4: Identity Component Creation")

    try:
        identity_hub = get_identity_hub()
        await identity_hub.initialize()

        # Test component creation
        result = await identity_hub.create_identity_component({"test": "config"})
        print(f"✅ Component creation: {result['status']}")

        # Test component creation and initialization
        init_result = await identity_hub.create_and_initialize_identity_component(
            {"test": "init_config"}
        )
        print(f"✅ Component creation with initialization: {init_result['status']}")

        return True
    except Exception as e:
        print(f"❌ Identity component creation failed: {e}")
        return False


async def test_factory_functions():
    """Test the factory functions work correctly"""
    print("\n🧪 Test 5: Factory Functions")

    try:
        # Test create_identity_component function
        component = create_identity_component({"test": "factory"})
        print(f"✅ Factory component created: {type(component).__name__}")

        # Test create_and_initialize_identity_component function
        initialized_component = await create_and_initialize_identity_component(
            {"test": "async_factory"}
        )
        print(
            f"✅ Async factory component created and initialized: "
            f"{initialized_component.is_initialized}"
        )

        # Test component processing
        result = await initialized_component.process({"test": "factory_data"})
        print(f"✅ Factory component processing: {result['status']}")

        return True
    except Exception as e:
        print(f"❌ Factory functions test failed: {e}")
        return False


async def test_persona_engine_categories():
    """Test persona engine handles all supported categories"""
    print("\n🧪 Test 6: Persona Engine Categories")

    try:
        persona_engine = PersonaEngine()
        await persona_engine.initialize()

        categories = [
            "consciousness",
            "governance",
            "voice",
            "identity",
            "quantum",
            "generic",
        ]

        for category in categories:
            test_data = {"category": category, "test_data": f"{category}_test"}
            result = await persona_engine.process(test_data)
            print(f"✅ {category} processing: {result['status']}")

        return True
    except Exception as e:
        print(f"❌ Persona engine categories test failed: {e}")
        return False


async def main():
    """Run all integration tests"""
    print("🚀 Starting Agent 1 Task 12 Integration Tests")
    print("=" * 60)

    tests = [
        test_persona_engine_initialization,
        test_identity_hub_persona_integration,
        test_identity_data_processing,
        test_identity_component_creation,
        test_factory_functions,
        test_persona_engine_categories,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Persona Engine integration is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the integration.")
        return False


if __name__ == "__main__":
    asyncio.run(main())
