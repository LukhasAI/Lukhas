#!/usr/bin/env python3
"""
Infrastructure Components Verification Script

Quick verification that our core infrastructure components are working.
"""

import sys
import asyncio
from pathlib import Path

def test_imports():
    """Test that our infrastructure components can be imported."""
    print("Testing infrastructure component imports...")
    
    try:
        from security.security_framework import LUKHASSecurityFramework, SecurityConfig
        print("✅ Security framework imported successfully")
    except ImportError as e:
        print(f"❌ Security framework import failed: {e}")
        return False
        
    try:
        from caching.cache_system import HierarchicalCacheManager, CacheConfig
        print("✅ Caching system imported successfully")
    except ImportError as e:
        print(f"❌ Caching system import failed: {e}")
        return False
        
    try:
        from storage.distributed_storage import DistributedStorageManager, StorageConfig
        print("✅ Storage system imported successfully")
    except ImportError as e:
        print(f"❌ Storage system import failed: {e}")
        return False
        
    return True

async def test_basic_functionality():
    """Test basic functionality of infrastructure components."""
    print("\nTesting basic functionality...")
    
    # Test Security Framework
    try:
        security_config = SecurityConfig(
            jwt_secret_key="test_key_for_verification",
            encryption_key="test_encryption_key_32_chars_long"
        )
        security_framework = LUKHASSecurityFramework(security_config)
        await security_framework.initialize()
        print("✅ Security framework initializes successfully")
        await security_framework.cleanup()
    except Exception as e:
        print(f"❌ Security framework test failed: {e}")
        return False
        
    # Test Caching System
    try:
        cache_config = CacheConfig(
            max_memory_mb=10,  # Small for testing
            enable_redis=False  # No Redis for quick test
        )
        cache_manager = HierarchicalCacheManager(cache_config)
        await cache_manager.initialize()
        
        # Basic cache operation
        await cache_manager.set("test_key", "test_value")
        value = await cache_manager.get("test_key")
        if value == "test_value":
            print("✅ Caching system works correctly")
        else:
            print("❌ Caching system returned wrong value")
            return False
        await cache_manager.cleanup()
    except Exception as e:
        print(f"❌ Caching system test failed: {e}")
        return False
        
    # Test Storage System
    try:
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_config = StorageConfig(
                primary_backend="local_filesystem",
                storage_backends={
                    "local_filesystem": {"base_path": tmpdir}
                }
            )
            storage_manager = DistributedStorageManager(storage_config)
            await storage_manager.initialize()
            
            # Basic storage operation
            test_data = b"test data for verification"
            object_id = await storage_manager.store_object(
                data=test_data,
                metadata={"test": "metadata"}
            )
            retrieved_data = await storage_manager.retrieve_object(object_id)
            if retrieved_data == test_data:
                print("✅ Storage system works correctly")
            else:
                print("❌ Storage system returned wrong data")
                return False
            await storage_manager.cleanup()
    except Exception as e:
        print(f"❌ Storage system test failed: {e}")
        return False
        
    return True

async def main():
    """Main verification function."""
    print("LUKHAS Infrastructure Components Verification")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed")
        sys.exit(1)
        
    # Test functionality
    if not await test_basic_functionality():
        print("\n❌ Functionality tests failed")
        sys.exit(1)
        
    print("\n🎉 All infrastructure components verified successfully!")
    print("Ready for production deployment")

if __name__ == "__main__":
    asyncio.run(main())