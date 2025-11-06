#!/usr/bin/env python3
"""
Quick validation script for LUKHAS Advanced Security & Caching Infrastructure

Tests basic functionality without external dependencies.
"""

import asyncio
import shutil
import tempfile
import time


async def test_security_framework():
    """Test security framework basic functionality."""
    print("🔐 Testing Security Framework...")

    try:
        # Import our security framework
        import sys
        sys.path.append('/Users/A_G_I/GitHub/Lukhas')

        from security.security_framework import (
            LUKHASSecurityFramework,
            SecurityConfig,
            UserPrincipal,
        )

        # Create security framework
        config = SecurityConfig(
            jwt_secret_key="test_secret_for_validation",
            encryption_key="test_encryption_key_32_chars!!",
            audit_logging_enabled=True
        )

        framework = LUKHASSecurityFramework(config)
        await framework.initialize()

        # Test JWT operations
        user = UserPrincipal(
            user_id="test_user",
            username="testuser",
            email="test@example.com",
            roles={"user"},
            permissions={"read", "write"}
        )

        token = await framework.jwt_service.generate_token(user)
        print(f"  ✅ JWT token generated: {len(token)} chars")

        decoded_user = await framework.jwt_service.validate_token(token)
        print(f"  ✅ JWT token validated: {decoded_user.username}")

        # Test encryption
        test_data = "Sensitive data for testing"
        encrypted = await framework.encryption_service.encrypt(test_data)
        decrypted = await framework.encryption_service.decrypt(encrypted)

        assert decrypted == test_data
        print("  ✅ Encryption/decryption working")

        # Test rate limiting
        allowed = await framework.rate_limiter.is_allowed("test_client")
        print(f"  ✅ Rate limiting operational: {allowed}")

        # Test threat detection
        threat_detected = await framework.threat_detector.detect_threat(
            "sql_injection", "'; DROP TABLE users; --"
        )
        print(f"  ✅ Threat detection working: {threat_detected}")

        await framework.shutdown()
        print("  ✅ Security framework validation complete")
        return True

    except Exception as e:
        print(f"  ❌ Security framework error: {e}")
        return False


async def test_caching_system():
    """Test caching system basic functionality."""
    print("💾 Testing Caching System...")

    try:
        from caching.cache_system import CacheConfig, HierarchicalCacheManager, MemoryCacheBackend

        # Test memory cache backend
        cache = MemoryCacheBackend(max_size=100)

        # Basic operations
        await cache.set("test_key", "test_value")
        value = await cache.get("test_key")
        assert value == "test_value"
        print("  ✅ Memory cache basic operations working")

        # Test hierarchical cache manager
        config = CacheConfig(l1_max_size=50, warming_enabled=False)
        manager = HierarchicalCacheManager(config)
        await manager.initialize()

        await manager.set("complex_key", {"data": "complex_value"})
        retrieved = await manager.get("complex_key")
        assert retrieved == {"data": "complex_value"}
        print("  ✅ Hierarchical cache manager working")

        # Test statistics
        stats = await manager.get_statistics()
        assert "global" in stats
        assert "l1_memory" in stats
        print("  ✅ Cache statistics collection working")

        await manager.shutdown()
        print("  ✅ Caching system validation complete")
        return True

    except Exception as e:
        print(f"  ❌ Caching system error: {e}")
        return False


async def test_distributed_storage():
    """Test distributed storage basic functionality."""
    print("🗄️  Testing Distributed Storage...")

    try:
        from storage.distributed_storage import (
            DataClassification,
            DistributedStorageManager,
            StorageConfig,
            StoragePolicy,
        )

        # Create temporary directory
        temp_dir = tempfile.mkdtemp()

        try:
            # Create storage manager
            config = StorageConfig(
                base_path=temp_dir,
                enable_lifecycle_management=False,
                backup_enabled=False
            )

            manager = DistributedStorageManager(config)
            await manager.initialize()

            # Test basic operations
            test_data = "Test data for distributed storage validation"

            success = await manager.put(
                "test/document.txt",
                test_data,
                content_type="text/plain",
                classification=DataClassification.INTERNAL,
                storage_policy=StoragePolicy.HOT
            )
            assert success
            print("  ✅ Storage put operation working")

            retrieved_data = await manager.get("test/document.txt")
            assert retrieved_data.decode() == test_data
            print("  ✅ Storage get operation working")

            # Test object info
            obj_info = await manager.get_object_info("test/document.txt")
            assert obj_info is not None
            assert obj_info.key == "test/document.txt"
            print("  ✅ Object metadata retrieval working")

            # Test metrics
            metrics = await manager.get_metrics()
            assert "total_objects" in metrics
            assert metrics["total_objects"] >= 1
            print("  ✅ Storage metrics collection working")

            await manager.shutdown()
            print("  ✅ Distributed storage validation complete")
            return True

        finally:
            shutil.rmtree(temp_dir)

    except Exception as e:
        print(f"  ❌ Distributed storage error: {e}")
        return False


async def test_integration():
    """Test integration between components."""
    print("🔗 Testing Component Integration...")

    try:
        # Test security + caching integration
        from caching.cache_system import CacheConfig, HierarchicalCacheManager

        from security.security_framework import LUKHASSecurityFramework, SecurityConfig

        # Initialize components
        security_config = SecurityConfig(
            jwt_secret_key="integration_test_secret",
            encryption_key="integration_test_key_32_chars!"
        )
        security = LUKHASSecurityFramework(security_config)
        await security.initialize()

        cache_config = CacheConfig(warming_enabled=False)
        cache = HierarchicalCacheManager(cache_config)
        await cache.initialize()

        # Test secure caching workflow
        sensitive_data = "Sensitive business information"
        encrypted_data = await security.encryption_service.encrypt(sensitive_data)

        # Cache encrypted data
        await cache.set("secure:data", encrypted_data)
        cached_encrypted = await cache.get("secure:data")

        # Decrypt from cache
        decrypted_data = await security.encryption_service.decrypt(cached_encrypted)
        assert decrypted_data == sensitive_data

        print("  ✅ Security + Caching integration working")

        await security.shutdown()
        await cache.shutdown()

        print("  ✅ Integration validation complete")
        return True

    except Exception as e:
        print(f"  ❌ Integration error: {e}")
        return False


def performance_benchmark():
    """Run basic performance benchmarks."""
    print("⚡ Running Performance Benchmarks...")

    try:
        # Simple cache performance test
        async def cache_benchmark():
            from caching.cache_system import MemoryCacheBackend

            cache = MemoryCacheBackend(max_size=10000)

            # Benchmark writes
            start_time = time.time()
            for i in range(1000):
                await cache.set(f"perf_key_{i}", f"value_{i}")
            write_time = time.time() - start_time

            # Benchmark reads
            start_time = time.time()
            for i in range(1000):
                await cache.get(f"perf_key_{i}")
            read_time = time.time() - start_time

            write_ops_per_sec = 1000 / write_time
            read_ops_per_sec = 1000 / read_time

            print(f"  ✅ Cache write performance: {write_ops_per_sec:.0f} ops/sec")
            print(f"  ✅ Cache read performance: {read_ops_per_sec:.0f} ops/sec")

            return write_ops_per_sec > 5000 and read_ops_per_sec > 10000

        # Run async benchmark
        result = asyncio.run(cache_benchmark())

        if result:
            print("  ✅ Performance benchmarks passed")
        else:
            print("  ⚠️  Performance below expected thresholds")

        return result

    except Exception as e:
        print(f"  ❌ Performance benchmark error: {e}")
        return False


async def main():
    """Run all validation tests."""
    print("🚀 LUKHAS Advanced Security & Caching Infrastructure Validation")
    print("=" * 70)

    results = []

    # Run individual component tests
    results.append(await test_security_framework())
    results.append(await test_caching_system())
    results.append(await test_distributed_storage())
    results.append(await test_integration())

    # Run performance benchmarks
    perf_result = performance_benchmark()
    results.append(perf_result)

    # Summary
    print("\n" + "=" * 70)
    print("📊 Validation Summary:")

    passed = sum(results)
    total = len(results)

    components = [
        "Security Framework",
        "Caching System",
        "Distributed Storage",
        "Component Integration",
        "Performance Benchmarks"
    ]

    for _i, (component, result) in enumerate(zip(components, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {component}: {status}")

    print(f"\nOverall: {passed}/{total} components validated successfully")

    if passed == total:
        print("🎉 All infrastructure components validated successfully!")
        print("\n🏆 Advanced Security & Caching Infrastructure ready for production")
    else:
        print(f"⚠️  {total - passed} components need attention")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
