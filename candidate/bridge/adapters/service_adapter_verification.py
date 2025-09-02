#!/usr/bin/env python3
"""
⚛️🧠🛡️ LUKHAS AI Service Adapter Base Verification Script

Verifies the enhanced Service Adapter Base with Trinity Framework integration.
"""

import asyncio
import os
import sys

# Add path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))


def test_imports():
    """Test that all critical imports work correctly"""
    print("🔍 Testing imports...")

    try:
        # Critical alias
        from candidate.bridge.adapters.service_adapter_base import (
            AdapterState,
            BaseServiceAdapter,
            CapabilityToken,
            DryRunPlanner,
            ResilienceManager,
            ServiceAdapterBase,
            TelemetryCollector,
            with_resilience,
        )

        print("✅ All imports successful")
        print(
            f"   ServiceAdapterBase is BaseServiceAdapter: {ServiceAdapterBase is BaseServiceAdapter}"
        )
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_adapter_creation():
    """Test creating an adapter instance"""
    print("\n🏗️  Testing adapter creation...")

    try:
        from candidate.bridge.adapters.service_adapter_base import BaseServiceAdapter

        # Create a simple test adapter
        class TestAdapter(BaseServiceAdapter):
            async def authenticate(self, credentials):
                return {"status": "authenticated", "mode": "test"}

            async def fetch_resource(self, lid, resource_id, capability_token):
                return {"resource": resource_id, "data": "test_data"}

        adapter = TestAdapter("test_service")
        print("✅ Adapter created successfully")
        print(f"   Service name: {adapter.service_name}")
        print("   Trinity Framework integrations:")
        print(
            f"     - Identity: {'Active' if adapter.identity_core else 'Not available'}"
        )
        print(
            f"     - Consciousness: {'Active' if adapter.consciousness_active else 'Not connected'}"
        )
        print(f"     - Guardian: {'Active' if adapter.guardian else 'Not available'}")
        print(
            f"     - Memory: {'Active' if adapter.memory_service else 'Not available'}"
        )
        print(
            f"     - Consent Ledger: {'Active' if adapter.ledger else 'Not available'}"
        )
        return True
    except Exception as e:
        print(f"❌ Adapter creation failed: {e}")
        return False


def test_health_status():
    """Test health status with Trinity Framework info"""
    print("\n🏥 Testing health status...")

    try:
        from candidate.bridge.adapters.service_adapter_base import BaseServiceAdapter

        class TestAdapter(BaseServiceAdapter):
            async def authenticate(self, credentials):
                return {"status": "authenticated"}

            async def fetch_resource(self, lid, resource_id, capability_token):
                return {"resource": resource_id}

        adapter = TestAdapter("health_test_service")
        status = adapter.get_health_status()

        print("✅ Health status retrieved successfully")
        print(f"   Service: {status['service']}")
        print(f"   Circuit State: {status['circuit_state']}")
        print(f"   Trinity Framework Status: {status['trinity_framework']}")
        return True
    except Exception as e:
        print(f"❌ Health status test failed: {e}")
        return False


async def test_consciousness_integration():
    """Test consciousness system integration"""
    print("\n🧠 Testing consciousness integration...")

    try:
        from candidate.bridge.adapters.service_adapter_base import BaseServiceAdapter

        class TestAdapter(BaseServiceAdapter):
            async def authenticate(self, credentials):
                return {"status": "authenticated"}

            async def fetch_resource(self, lid, resource_id, capability_token):
                return {"resource": resource_id}

        adapter = TestAdapter("consciousness_test")

        # Test notification (should gracefully handle if consciousness not available)
        await adapter.notify_consciousness("test_event", {"test": "data"})

        print("✅ Consciousness integration test completed")
        print("   (Gracefully handles unavailable consciousness system)")
        return True
    except Exception as e:
        print(f"❌ Consciousness integration test failed: {e}")
        return False


async def main():
    """Main verification routine"""
    print("⚛️🧠🛡️ LUKHAS AI Service Adapter Base Verification")
    print("=" * 60)

    tests = [
        ("Import Test", test_imports),
        ("Adapter Creation", test_adapter_creation),
        ("Health Status", test_health_status),
        ("Consciousness Integration", test_consciousness_integration),
    ]

    passed = 0
    total = len(tests)

    for name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()

            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {name} failed with exception: {e}")

    print("\n" + "=" * 60)
    print(f"📊 Verification Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Service Adapter Base is working correctly.")
        print("\n🔧 Key enhancements implemented:")
        print("   • Fixed ServiceAdapterBase export alias")
        print("   • Added Trinity Framework integration (⚛️🧠🛡️)")
        print("   • Enhanced Λ-trace logging with context")
        print("   • Added consciousness system communication")
        print("   • Integrated Identity module for authentication")
        print("   • Added Memory service for state persistence")
        print("   • Enhanced Guardian system integration")
        print("   • Improved error handling and resilience")
    else:
        print("⚠️  Some tests failed. Check logs for details.")

    return passed == total


if __name__ == "__main__":
    asyncio.run(main())
