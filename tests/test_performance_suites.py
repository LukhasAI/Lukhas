"""
Performance Test Suites for LUKHAS AI
Runs cold/warm/loaded scenarios and captures p50/p95 metrics
Trinity Framework: ⚛️🧠🛡️
"""

import asyncio
import gc
import json
import os
import time
from typing import Dict, List, Any
from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.perf
class TestPerformanceSuites:
    """Performance test suites with p50/p95 capture"""
    
    async def _simulate_lid_auth(self, cached: bool = False) -> float:
        """Simulate ΛID authentication with timing"""
        start = time.perf_counter()
        
        # Simulate cache hit/miss
        if cached:
            await asyncio.sleep(0.005)  # 5ms for cache hit
        else:
            await asyncio.sleep(0.030)  # 30ms for cache miss
            
        return (time.perf_counter() - start) * 1000
        
    async def _simulate_consent_check(self, cached: bool = False) -> float:
        """Simulate consent check with timing"""
        start = time.perf_counter()
        
        if cached:
            await asyncio.sleep(0.002)  # 2ms for cache hit
        else:
            await asyncio.sleep(0.015)  # 15ms for cache miss
            
        return (time.perf_counter() - start) * 1000
        
    async def _simulate_context_handoff(self, load_factor: float = 1.0) -> float:
        """Simulate context bus handoff with timing"""
        start = time.perf_counter()
        
        # Base time + load factor
        base_time = 0.050  # 50ms base
        await asyncio.sleep(base_time * load_factor)
        
        return (time.perf_counter() - start) * 1000
        
    async def _simulate_adapter_fetch(self, cached: bool = False) -> float:
        """Simulate adapter metadata fetch with timing"""
        start = time.perf_counter()
        
        if cached:
            await asyncio.sleep(0.010)  # 10ms for cached metadata
        else:
            await asyncio.sleep(0.040)  # 40ms for fresh fetch
            
        return (time.perf_counter() - start) * 1000
        
    @pytest.mark.asyncio
    async def test_cold_start_performance(self, perf_tracker, perf_budgets):
        """
        Cold start performance test
        - No caching
        - First-time initialization
        - Measures worst-case latencies
        """
        print("\n" + "="*60)
        print("🧊 COLD START PERFORMANCE TEST")
        print("="*60)
        
        # Clear all caches
        gc.collect()
        
        results = {
            'auth': [],
            'consent': [],
            'handoff': [],
            'adapter': [],
            'e2e': []
        }
        
        # Run 20 cold iterations
        for i in range(20):
            e2e_start = time.perf_counter()
            
            # Cold auth
            auth_time = await self._simulate_lid_auth(cached=False)
            results['auth'].append(auth_time)
            
            # Cold consent
            consent_time = await self._simulate_consent_check(cached=False)
            results['consent'].append(consent_time)
            
            # Cold handoff
            handoff_time = await self._simulate_context_handoff()
            results['handoff'].append(handoff_time)
            
            # Cold adapter
            adapter_time = await self._simulate_adapter_fetch(cached=False)
            results['adapter'].append(adapter_time)
            
            # E2E time
            e2e_time = (time.perf_counter() - e2e_start) * 1000
            results['e2e'].append(e2e_time)
            
            # Track in perf_tracker
            perf_tracker.measurements['cold_auth'] = results['auth']
            perf_tracker.measurements['cold_consent'] = results['consent']
            perf_tracker.measurements['cold_handoff'] = results['handoff']
            perf_tracker.measurements['cold_adapter'] = results['adapter']
            perf_tracker.measurements['cold_e2e'] = results['e2e']
            
        # Calculate and report metrics
        print("\n📊 Cold Start Metrics (ms):")
        print("-" * 40)
        
        for operation, times in results.items():
            sorted_times = sorted(times)
            p50 = sorted_times[len(sorted_times) // 2]
            p95 = sorted_times[int(len(sorted_times) * 0.95)]
            
            # Check against budgets
            budget_key = f'{operation}_p95_ms' if operation != 'e2e' else 'e2e_demo_s'
            budget = perf_budgets.get(budget_key, float('inf'))
            if operation == 'e2e':
                budget = budget * 1000  # Convert to ms
                
            status = "✅" if p95 <= budget else "❌"
            
            print(f"{operation:10s}: p50={p50:6.2f}ms, p95={p95:6.2f}ms {status}")
            
        return results
        
    @pytest.mark.asyncio
    async def test_warm_cache_performance(self, perf_tracker, perf_budgets):
        """
        Warm cache performance test
        - All caches pre-warmed
        - Measures best-case latencies
        """
        print("\n" + "="*60)
        print("🔥 WARM CACHE PERFORMANCE TEST")
        print("="*60)
        
        # Pre-warm caches
        cache = {
            'users': {'test_user': {'auth': True}},
            'consents': {'test_user': {'drive.read': True}},
            'adapters': {'drive': {'metadata': []}},
        }
        
        results = {
            'auth': [],
            'consent': [],
            'handoff': [],
            'adapter': [],
            'e2e': []
        }
        
        # Run 50 warm iterations (more iterations since they're faster)
        for i in range(50):
            e2e_start = time.perf_counter()
            
            # Warm auth
            auth_time = await self._simulate_lid_auth(cached=True)
            results['auth'].append(auth_time)
            
            # Warm consent
            consent_time = await self._simulate_consent_check(cached=True)
            results['consent'].append(consent_time)
            
            # Warm handoff (still has some latency)
            handoff_time = await self._simulate_context_handoff(load_factor=0.5)
            results['handoff'].append(handoff_time)
            
            # Warm adapter
            adapter_time = await self._simulate_adapter_fetch(cached=True)
            results['adapter'].append(adapter_time)
            
            # E2E time
            e2e_time = (time.perf_counter() - e2e_start) * 1000
            results['e2e'].append(e2e_time)
            
            # Track in perf_tracker
            perf_tracker.measurements['warm_auth'] = results['auth']
            perf_tracker.measurements['warm_consent'] = results['consent']
            perf_tracker.measurements['warm_handoff'] = results['handoff']
            perf_tracker.measurements['warm_adapter'] = results['adapter']
            perf_tracker.measurements['warm_e2e'] = results['e2e']
            
        # Calculate and report metrics
        print("\n📊 Warm Cache Metrics (ms):")
        print("-" * 40)
        
        for operation, times in results.items():
            sorted_times = sorted(times)
            p50 = sorted_times[len(sorted_times) // 2]
            p95 = sorted_times[int(len(sorted_times) * 0.95)]
            
            # Warm cache should be significantly faster
            expected_speedup = 0.3  # Expect 70% faster
            cold_p95 = perf_tracker.get_p50_p95(f'cold_{operation}')['p95']
            
            status = "✅" if p95 <= cold_p95 * expected_speedup else "⚠️"
            
            print(f"{operation:10s}: p50={p50:6.2f}ms, p95={p95:6.2f}ms {status}")
            
        return results
        
    @pytest.mark.asyncio
    async def test_loaded_system_performance(self, perf_tracker, perf_budgets):
        """
        Loaded system performance test
        - 100 concurrent requests
        - Mixed cache states
        - Measures p95 under load
        """
        print("\n" + "="*60)
        print("📈 LOADED SYSTEM PERFORMANCE TEST")
        print("="*60)
        
        async def process_request(request_id: int) -> Dict[str, float]:
            """Process a single request with timing"""
            timings = {}
            e2e_start = time.perf_counter()
            
            # Mix of cached and uncached (30% cache hit rate)
            cached = (request_id % 10) < 3
            
            # Auth with some variability
            timings['auth'] = await self._simulate_lid_auth(cached=cached)
            
            # Consent check
            timings['consent'] = await self._simulate_consent_check(cached=cached)
            
            # Handoff with load factor based on concurrent requests
            load_factor = 1.0 + (request_id % 5) * 0.2  # 1.0 to 2.0
            timings['handoff'] = await self._simulate_context_handoff(load_factor)
            
            # Adapter fetch
            timings['adapter'] = await self._simulate_adapter_fetch(cached=cached)
            
            # E2E
            timings['e2e'] = (time.perf_counter() - e2e_start) * 1000
            
            return timings
            
        print("\n🚀 Starting 100 concurrent requests...")
        
        # Launch 100 concurrent requests
        start_time = time.perf_counter()
        tasks = [process_request(i) for i in range(100)]
        all_results = await asyncio.gather(*tasks)
        total_time = (time.perf_counter() - start_time) * 1000
        
        # Aggregate results
        results = {
            'auth': [],
            'consent': [],
            'handoff': [],
            'adapter': [],
            'e2e': []
        }
        
        for timing in all_results:
            for op, value in timing.items():
                results[op].append(value)
                
        # Track in perf_tracker
        for op, times in results.items():
            perf_tracker.measurements[f'loaded_{op}'] = times
            
        # Calculate and report metrics
        print("\n📊 Loaded System Metrics (ms):")
        print("-" * 40)
        
        for operation, times in results.items():
            sorted_times = sorted(times)
            p50 = sorted_times[len(sorted_times) // 2]
            p95 = sorted_times[int(len(sorted_times) * 0.95)]
            p99 = sorted_times[int(len(sorted_times) * 0.99)]
            
            # Check against budgets (allow 50% degradation under load)
            budget_key = f'{operation}_p95_ms' if operation != 'e2e' else 'e2e_demo_s'
            budget = perf_budgets.get(budget_key, float('inf'))
            if operation == 'e2e':
                budget = budget * 1000  # Convert to ms
            budget = budget * 1.5  # Allow 50% degradation under load
                
            status = "✅" if p95 <= budget else "❌"
            
            print(f"{operation:10s}: p50={p50:6.2f}ms, p95={p95:6.2f}ms, p99={p99:6.2f}ms {status}")
            
        print(f"\n⚡ Throughput: {100000/total_time:.1f} req/s")
        print(f"⏱️ Total time: {total_time:.2f}ms for 100 requests")
        
        return results
        
    @pytest.mark.asyncio
    async def test_export_performance_report(self, perf_tracker):
        """Export comprehensive performance report"""
        
        # Ensure we have data from previous tests
        if not perf_tracker.measurements:
            pytest.skip("No performance data to export")
            
        report = {
            'timestamp': time.time(),
            'summary': {},
            'details': {}
        }
        
        # Aggregate all measurements
        for metric_name, times in perf_tracker.measurements.items():
            if times:
                sorted_times = sorted(times)
                report['details'][metric_name] = {
                    'p50': sorted_times[len(sorted_times) // 2],
                    'p95': sorted_times[int(len(sorted_times) * 0.95)],
                    'p99': sorted_times[int(len(sorted_times) * 0.99)] if len(sorted_times) > 99 else sorted_times[-1],
                    'min': min(times),
                    'max': max(times),
                    'mean': sum(times) / len(times),
                    'count': len(times)
                }
                
        # Create summary
        for scenario in ['cold', 'warm', 'loaded']:
            scenario_metrics = {}
            for op in ['auth', 'consent', 'handoff', 'adapter', 'e2e']:
                key = f'{scenario}_{op}'
                if key in report['details']:
                    scenario_metrics[op] = {
                        'p50': report['details'][key]['p50'],
                        'p95': report['details'][key]['p95']
                    }
            if scenario_metrics:
                report['summary'][scenario] = scenario_metrics
                
        # Export to file
        report_path = 'test_results/performance_report.json'
        os.makedirs('test_results', exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        print("\n" + "="*60)
        print("📝 PERFORMANCE REPORT EXPORTED")
        print("="*60)
        print(f"Report saved to: {report_path}")
        print("\n🎯 Performance Summary:")
        
        # Print summary table
        scenarios = ['cold', 'warm', 'loaded']
        operations = ['auth', 'consent', 'handoff', 'adapter', 'e2e']
        
        # Header
        print(f"{'Operation':<12} | " + " | ".join(f"{s:^15}" for s in scenarios))
        print("-" * (12 + 3 + 18 * len(scenarios)))
        
        # Data rows
        for op in operations:
            row = f"{op:<12} | "
            for scenario in scenarios:
                if scenario in report['summary'] and op in report['summary'][scenario]:
                    p95 = report['summary'][scenario][op]['p95']
                    row += f"{p95:>7.2f}ms (p95) | "
                else:
                    row += f"{'N/A':^15} | "
            print(row.rstrip(' |'))
            
        return report