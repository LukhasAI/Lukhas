#!/usr/bin/env python3
"""
Simple Test Runner for LUKHAS Infrastructure

Creates a test report that we can read to verify tests are working.
"""

import sys
import os
import traceback
import json
from datetime import datetime


def run_infrastructure_tests():
    """Run infrastructure tests and save results."""
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": []
    }
    
    print("🚀 LUKHAS Infrastructure Test Runner")
    print("=" * 50)
    
    # Test 1: Basic Python functionality
    print("\n🐍 Testing Basic Python...")
    try:
        import asyncio, json, time, tempfile, hashlib
        results["tests"].append({
            "name": "basic_python",
            "status": "PASS",
            "message": "Basic Python imports successful"
        })
        print("  ✅ Basic Python functionality working")
    except Exception as e:
        results["tests"].append({
            "name": "basic_python", 
            "status": "FAIL",
            "message": str(e)
        })
        print(f"  ❌ Basic Python failed: {e}")
    
    # Test 2: Security Framework
    print("\n🔐 Testing Security Framework...")
    try:
        # Check if file exists
        security_path = "security/security_framework.py"
        if os.path.exists(security_path):
            print(f"  ✅ Security framework file exists: {security_path}")
            
            # Try to import
            sys.path.insert(0, '.')
            from security.security_framework import SecurityConfig, LUKHASSecurityFramework
            
            # Try to create instance
            config = SecurityConfig(
                jwt_secret_key="test_key_for_testing_only",
                encryption_key="test_encryption_key_32_chars!!"
            )
            framework = LUKHASSecurityFramework(config)
            
            results["tests"].append({
                "name": "security_framework",
                "status": "PASS", 
                "message": "Security framework import and instantiation successful"
            })
            print("  ✅ Security framework working")
        else:
            results["tests"].append({
                "name": "security_framework",
                "status": "FAIL",
                "message": f"Security framework file not found: {security_path}"
            })
            print(f"  ❌ Security framework file not found: {security_path}")
            
    except Exception as e:
        results["tests"].append({
            "name": "security_framework",
            "status": "FAIL", 
            "message": str(e)
        })
        print(f"  ❌ Security framework failed: {e}")
    
    # Test 3: Caching System
    print("\n💾 Testing Caching System...")
    try:
        cache_path = "caching/cache_system.py"
        if os.path.exists(cache_path):
            print(f"  ✅ Caching system file exists: {cache_path}")
            
            from caching.cache_system import CacheConfig, HierarchicalCacheManager
            
            config = CacheConfig(warming_enabled=False)
            manager = HierarchicalCacheManager(config)
            
            results["tests"].append({
                "name": "caching_system",
                "status": "PASS",
                "message": "Caching system import and instantiation successful"
            })
            print("  ✅ Caching system working")
        else:
            results["tests"].append({
                "name": "caching_system",
                "status": "FAIL",
                "message": f"Caching system file not found: {cache_path}"
            })
            print(f"  ❌ Caching system file not found: {cache_path}")
            
    except Exception as e:
        results["tests"].append({
            "name": "caching_system", 
            "status": "FAIL",
            "message": str(e)
        })
        print(f"  ❌ Caching system failed: {e}")
    
    # Test 4: Storage System
    print("\n🗄️ Testing Storage System...")
    try:
        storage_path = "storage/distributed_storage.py"
        if os.path.exists(storage_path):
            print(f"  ✅ Storage system file exists: {storage_path}")
            
            from storage.distributed_storage import StorageConfig, DistributedStorageManager
            
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                config = StorageConfig(
                    base_path=tmpdir,
                    enable_lifecycle_management=False,
                    backup_enabled=False
                )
                manager = DistributedStorageManager(config)
            
            results["tests"].append({
                "name": "storage_system",
                "status": "PASS",
                "message": "Storage system import and instantiation successful"  
            })
            print("  ✅ Storage system working")
        else:
            results["tests"].append({
                "name": "storage_system",
                "status": "FAIL", 
                "message": f"Storage system file not found: {storage_path}"
            })
            print(f"  ❌ Storage system file not found: {storage_path}")
            
    except Exception as e:
        results["tests"].append({
            "name": "storage_system",
            "status": "FAIL",
            "message": str(e)
        })
        print(f"  ❌ Storage system failed: {e}")
    
    # Test 5: Infrastructure Manager  
    print("\n🏗️ Testing Infrastructure Manager...")
    try:
        infra_path = "infrastructure/advanced_infrastructure.py"
        if os.path.exists(infra_path):
            print(f"  ✅ Infrastructure manager file exists: {infra_path}")
            
            from infrastructure.advanced_infrastructure import LUKHASInfrastructureManager
            
            manager = LUKHASInfrastructureManager()
            
            results["tests"].append({
                "name": "infrastructure_manager",
                "status": "PASS",
                "message": "Infrastructure manager import and instantiation successful"
            })
            print("  ✅ Infrastructure manager working")
        else:
            results["tests"].append({
                "name": "infrastructure_manager", 
                "status": "FAIL",
                "message": f"Infrastructure manager file not found: {infra_path}"
            })
            print(f"  ❌ Infrastructure manager file not found: {infra_path}")
            
    except Exception as e:
        results["tests"].append({
            "name": "infrastructure_manager",
            "status": "FAIL",
            "message": str(e)
        })
        print(f"  ❌ Infrastructure manager failed: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    total_tests = len(results["tests"])
    passed_tests = len([t for t in results["tests"] if t["status"] == "PASS"])
    failed_tests = total_tests - passed_tests
    
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Failed: {failed_tests}")
    
    for test in results["tests"]:
        status_emoji = "✅" if test["status"] == "PASS" else "❌"
        print(f"  {status_emoji} {test['name']}: {test['status']}")
    
    results["summary"] = {
        "total": total_tests,
        "passed": passed_tests, 
        "failed": failed_tests,
        "success_rate": passed_tests / total_tests if total_tests > 0 else 0
    }
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Results saved to: test_results.json")
    
    if failed_tests == 0:
        print("🎉 All infrastructure tests passed!")
        return True
    else:
        print(f"⚠️ {failed_tests} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_infrastructure_tests()
    sys.exit(0 if success else 1)