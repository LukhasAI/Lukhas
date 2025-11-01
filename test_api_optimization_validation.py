#!/usr/bin/env python3
"""
LUKHAS API Optimization System - Validation Test Runner

Simple test runner to validate our API optimization system components
without complex pytest dependencies.
"""

import asyncio
import sys
import time
from typing import Dict, List, Any
import traceback

# Add current directory to path for imports
sys.path.insert(0, '/Users/A_G_I/GitHub/Lukhas')

async def test_optimizer_creation():
    """Test basic optimizer creation"""
    try:
        from api.optimization.advanced_api_optimizer import (
            create_api_optimizer, OptimizationStrategy, OptimizationConfig
        )
        
        print("🧪 Testing optimizer creation...")
        
        config = OptimizationConfig(
            strategy=OptimizationStrategy.BALANCED,
            enable_rate_limiting=True,
            enable_caching=True,
            enable_analytics=True
        )
        
        optimizer = await create_api_optimizer(config=config)
        
        # Test basic stats
        stats = await optimizer.get_optimization_stats()
        assert 'rate_limiter' in stats
        assert 'cache' in stats
        assert 'analytics' in stats
        
        print("✅ Optimizer creation: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Optimizer creation: FAILED - {e}")
        traceback.print_exc()
        return False

async def test_middleware_pipeline():
    """Test middleware pipeline creation"""
    try:
        from api.optimization.advanced_middleware import (
            create_middleware_pipeline, MiddlewareConfig
        )
        
        print("🧪 Testing middleware pipeline...")
        
        config = MiddlewareConfig(
            enable_security=True,
            enable_validation=True,
            enable_analytics=True,
            enable_optimization=True
        )
        
        pipeline = await create_middleware_pipeline(config)
        
        # Test pipeline stats
        stats = await pipeline.get_pipeline_stats()
        assert 'security' in stats
        assert 'validation' in stats
        assert 'analytics' in stats
        
        print("✅ Middleware pipeline: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Middleware pipeline: FAILED - {e}")
        traceback.print_exc()
        return False

async def test_analytics_dashboard():
    """Test analytics dashboard creation"""
    try:
        from api.optimization.analytics_dashboard import (
            create_analytics_dashboard, AnalyticsConfig
        )
        
        print("🧪 Testing analytics dashboard...")
        
        config = AnalyticsConfig(
            enable_metrics=True,
            enable_alerts=True,
            enable_intelligence=True
        )
        
        dashboard = await create_analytics_dashboard(config)
        
        # Test dashboard data
        data = await dashboard.get_dashboard_data()
        assert 'summary' in data
        assert 'insights' in data
        
        print("✅ Analytics dashboard: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Analytics dashboard: FAILED - {e}")
        traceback.print_exc()
        return False

async def test_integration_hub():
    """Test integration hub creation"""
    try:
        from api.optimization.integration_hub import (
            create_optimization_hub, IntegrationConfig, IntegrationMode
        )
        
        print("🧪 Testing integration hub...")
        
        config = IntegrationConfig(
            mode=IntegrationMode.DEVELOPMENT,
            enable_optimizer=True,
            enable_middleware=True,
            enable_analytics=True
        )
        
        hub = await create_optimization_hub(config)
        
        # Test hub status
        status = await hub.get_optimization_status()
        assert 'components' in status
        assert 'performance' in status
        assert 'hub' in status
        
        print("✅ Integration hub: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Integration hub: FAILED - {e}")
        traceback.print_exc()
        return False

async def test_request_processing():
    """Test end-to-end request processing"""
    try:
        from api.optimization.integration_hub import (
            create_optimization_hub, IntegrationConfig, IntegrationMode
        )
        
        print("🧪 Testing request processing...")
        
        config = IntegrationConfig(
            mode=IntegrationMode.DEVELOPMENT,
            enable_optimizer=True,
            enable_middleware=True,
            enable_analytics=True
        )
        
        hub = await create_optimization_hub(config)
        
        # Process a test request
        allowed, result = await hub.process_api_request(
            endpoint="/api/v1/test",
            method="GET",
            headers={"Authorization": "Bearer test"},
            user_id="test_user",
            data={}
        )
        
        assert allowed is True
        assert 'request_id' in result
        
        # Complete the request
        await hub.complete_api_request(
            result['request_id'], 
            {"status": "success"}, 
            200
        )
        
        print("✅ Request processing: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Request processing: FAILED - {e}")
        traceback.print_exc()
        return False

async def run_performance_benchmark():
    """Run basic performance benchmark"""
    try:
        from api.optimization.integration_hub import (
            create_optimization_hub, IntegrationConfig, IntegrationMode
        )
        
        print("🚀 Running performance benchmark...")
        
        config = IntegrationConfig(
            mode=IntegrationMode.HIGH_PERFORMANCE,
            enable_optimizer=True,
            enable_middleware=True,
            enable_analytics=True
        )
        
        hub = await create_optimization_hub(config)
        
        # Run 100 requests and measure performance
        start_time = time.time()
        successful_requests = 0
        
        for i in range(100):
            try:
                allowed, result = await hub.process_api_request(
                    endpoint=f"/api/v1/test/{i}",
                    method="GET",
                    headers={"Authorization": "Bearer test"},
                    user_id="benchmark_user",
                    data={}
                )
                
                if allowed:
                    await hub.complete_api_request(
                        result['request_id'], 
                        {"index": i}, 
                        200
                    )
                    successful_requests += 1
                    
            except Exception as e:
                print(f"Request {i} failed: {e}")
        
        end_time = time.time()
        duration = end_time - start_time
        throughput = successful_requests / duration
        
        print(f"📊 Benchmark Results:")
        print(f"   • Successful requests: {successful_requests}/100")
        print(f"   • Total time: {duration:.2f}s")
        print(f"   • Throughput: {throughput:.1f} requests/second")
        print(f"   • Avg response time: {(duration / successful_requests * 1000):.1f}ms")
        
        # Get optimization status
        status = await hub.get_optimization_status()
        print(f"   • Cache hit rate: {status['performance']['cache_hit_rate_percent']:.1f}%")
        print(f"   • Rate limit violations: {status['components']['optimizer']['rate_limit_violations']}")
        
        print("✅ Performance benchmark: COMPLETED")
        return True
        
    except Exception as e:
        print(f"❌ Performance benchmark: FAILED - {e}")
        traceback.print_exc()
        return False

async def main():
    """Run all validation tests"""
    print("🚀 LUKHAS API Optimization System - Validation Suite")
    print("=" * 60)
    
    start_time = time.time()
    
    tests = [
        ("Optimizer Creation", test_optimizer_creation),
        ("Middleware Pipeline", test_middleware_pipeline),
        ("Analytics Dashboard", test_analytics_dashboard),
        ("Integration Hub", test_integration_hub),
        ("Request Processing", test_request_processing),
        ("Performance Benchmark", run_performance_benchmark)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 40)
        
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: FAILED - {e}")
            results.append((test_name, False))
    
    end_time = time.time()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
    
    print("-" * 60)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print(f"Total Time: {end_time - start_time:.2f}s")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! API Optimization System is ready!")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please review errors above.")
    
    return passed == total

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test runner failed: {e}")
        traceback.print_exc()
        sys.exit(1)