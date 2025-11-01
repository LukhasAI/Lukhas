#!/usr/bin/env python3
"""
Orchestrator Stress Testing Suite (MP003)
=========================================

Comprehensive stress testing for LUKHAS cognitive orchestrator systems.
Tests high-load scenarios, concurrent processing, and resilience patterns.

P1 Task: MP003 - Add orchestrator stress testing
Priority: High (P1)
Agent: Claude Code (Testing/Documentation)

Constellation Framework: 🧠 Consciousness · 🛡️ Guardian

Features Tested:
- High-volume query processing under load
- Concurrent request handling and resource contention
- Memory pressure and resource exhaustion scenarios
- Failure recovery and cascade prevention
- Performance degradation patterns and limits
- Node registration/deregistration under stress
- MATRIZ graph integrity under concurrent operations
"""

import asyncio
import concurrent.futures
import gc
import logging
import random
import threading
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch

import pytest

try:
<<<<<<< HEAD
    from MATRIZ.core.orchestrator import CognitiveOrchestrator
    from MATRIZ.core.node_interface import CognitiveNode
    from MATRIZ.core.async_orchestrator import AsyncCognitiveOrchestrator
=======
    from matriz.core.async_orchestrator import AsyncCognitiveOrchestrator
    from matriz.core.node_interface import CognitiveNode
    from matriz.core.orchestrator import CognitiveOrchestrator
>>>>>>> origin/main
    MATRIZ_AVAILABLE = True
except ImportError:
    # Fallback for testing without full MATRIZ system
    MATRIZ_AVAILABLE = False
    CognitiveOrchestrator = None
    CognitiveNode = None
    AsyncCognitiveOrchestrator = None


@dataclass
class StressTestMetrics:
    """Metrics collection for stress testing"""
<<<<<<< HEAD
    
=======

>>>>>>> origin/main
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    max_response_time: float = 0.0
    min_response_time: float = float('inf')
    concurrent_peak: int = 0
    memory_peak_mb: float = 0.0
    error_types: Dict[str, int] = None
    throughput_qps: float = 0.0
<<<<<<< HEAD
    
=======

>>>>>>> origin/main
    def __post_init__(self):
        if self.error_types is None:
            self.error_types = defaultdict(int)


class MockCognitiveNode(CognitiveNode):
    """Mock cognitive node for stress testing"""
<<<<<<< HEAD
    
=======

>>>>>>> origin/main
    def __init__(self, name: str, processing_delay: float = 0.01, failure_rate: float = 0.0):
        self.name = name
        self.processing_delay = processing_delay
        self.failure_rate = failure_rate
        self.process_count = 0
        self.last_processed = None
<<<<<<< HEAD
        
=======

>>>>>>> origin/main
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock processing with configurable delay and failure rate"""
        self.process_count += 1
        self.last_processed = datetime.now(timezone.utc)
<<<<<<< HEAD
        
        # Simulate processing delay
        time.sleep(self.processing_delay)
        
        # Simulate random failures
        if random.random() < self.failure_rate:
            raise RuntimeError(f"Mock failure in {self.name}")
            
=======

        # Simulate processing delay
        time.sleep(self.processing_delay)

        # Simulate random failures
        if random.random() < self.failure_rate:
            raise RuntimeError(f"Mock failure in {self.name}")

>>>>>>> origin/main
        # Create mock MATRIZ node
        matriz_node = {
            "id": f"{self.name}_{self.process_count}",
            "type": "MockProcessing",
            "timestamp": self.last_processed.isoformat(),
            "content": {
                "input": data,
                "processing_node": self.name,
                "process_count": self.process_count
            },
            "links": [],
            "metadata": {
                "processing_delay": self.processing_delay,
                "failure_rate": self.failure_rate
            }
        }
<<<<<<< HEAD
        
=======

>>>>>>> origin/main
        return {
            "result": f"Processed by {self.name}: {data.get('query', 'unknown')}",
            "matriz_node": matriz_node,
            "processing_time": self.processing_delay,
            "node_name": self.name
        }


@pytest.mark.skipif(not MATRIZ_AVAILABLE, reason="MATRIZ system not available")
class TestOrchestratorStressScenarios:
    """Test orchestrator under various stress scenarios"""
<<<<<<< HEAD
    
=======

>>>>>>> origin/main
    @pytest.fixture
    def orchestrator(self):
        """Create fresh orchestrator for each test"""
        return CognitiveOrchestrator()
<<<<<<< HEAD
    
=======

>>>>>>> origin/main
    @pytest.fixture
    def stress_nodes(self):
        """Create various mock nodes with different characteristics"""
        return {
            "fast_node": MockCognitiveNode("fast", processing_delay=0.001, failure_rate=0.0),
            "slow_node": MockCognitiveNode("slow", processing_delay=0.1, failure_rate=0.0),
            "unreliable_node": MockCognitiveNode("unreliable", processing_delay=0.01, failure_rate=0.1),
            "heavy_node": MockCognitiveNode("heavy", processing_delay=0.05, failure_rate=0.02),
        }
<<<<<<< HEAD
    
    def test_high_volume_sequential_processing(self, orchestrator, stress_nodes):
        """Test orchestrator under high volume sequential load"""
        
        # Register stress test nodes
        for name, node in stress_nodes.items():
            orchestrator.register_node(name, node)
            
        metrics = StressTestMetrics()
        response_times = []
        
        # Process high volume of requests sequentially
        test_queries = [f"Test query {i}" for i in range(1000)]
        
        start_time = time.perf_counter()
        
        for i, query in enumerate(test_queries):
            request_start = time.perf_counter()
            
            try:
                result = orchestrator.process_query(query)
                request_time = time.perf_counter() - request_start
                
                response_times.append(request_time)
                metrics.successful_requests += 1
                
                # Verify result structure
                assert "trace" in result or "result" in result, "Should return valid result"
                
            except Exception as e:
                metrics.failed_requests += 1
                metrics.error_types[type(e).__name__] += 1
                
            metrics.total_requests += 1
            
            # Progress tracking
            if i % 100 == 0:
                print(f"Processed {i}/1000 requests")
                
        total_time = time.perf_counter() - start_time
        
=======

    def test_high_volume_sequential_processing(self, orchestrator, stress_nodes):
        """Test orchestrator under high volume sequential load"""

        # Register stress test nodes
        for name, node in stress_nodes.items():
            orchestrator.register_node(name, node)

        metrics = StressTestMetrics()
        response_times = []

        # Process high volume of requests sequentially
        test_queries = [f"Test query {i}" for i in range(1000)]

        start_time = time.perf_counter()

        for i, query in enumerate(test_queries):
            request_start = time.perf_counter()

            try:
                result = orchestrator.process_query(query)
                request_time = time.perf_counter() - request_start

                response_times.append(request_time)
                metrics.successful_requests += 1

                # Verify result structure
                assert "trace" in result or "result" in result, "Should return valid result"

            except Exception as e:
                metrics.failed_requests += 1
                metrics.error_types[type(e).__name__] += 1

            metrics.total_requests += 1

            # Progress tracking
            if i % 100 == 0:
                print(f"Processed {i}/1000 requests")

        total_time = time.perf_counter() - start_time

>>>>>>> origin/main
        # Calculate metrics
        if response_times:
            metrics.average_response_time = sum(response_times) / len(response_times)
            metrics.max_response_time = max(response_times)
            metrics.min_response_time = min(response_times)
<<<<<<< HEAD
            
        metrics.throughput_qps = metrics.total_requests / total_time
        
=======

        metrics.throughput_qps = metrics.total_requests / total_time

>>>>>>> origin/main
        # Performance assertions
        assert metrics.successful_requests > 950, f"Too many failures: {metrics.failed_requests}"
        assert metrics.average_response_time < 0.2, f"Average response too slow: {metrics.average_response_time:.3f}s"
        assert metrics.throughput_qps > 10.0, f"Throughput too low: {metrics.throughput_qps:.1f} QPS"
<<<<<<< HEAD
        
        print(f"Sequential stress test: {metrics.throughput_qps:.1f} QPS, {metrics.average_response_time:.3f}s avg")
        
    def test_concurrent_processing_stress(self, orchestrator, stress_nodes):
        """Test orchestrator under concurrent load"""
        
        # Register nodes
        for name, node in stress_nodes.items():
            orchestrator.register_node(name, node)
            
=======

        print(f"Sequential stress test: {metrics.throughput_qps:.1f} QPS, {metrics.average_response_time:.3f}s avg")

    def test_concurrent_processing_stress(self, orchestrator, stress_nodes):
        """Test orchestrator under concurrent load"""

        # Register nodes
        for name, node in stress_nodes.items():
            orchestrator.register_node(name, node)

>>>>>>> origin/main
        metrics = StressTestMetrics()
        concurrent_count = 0
        max_concurrent = 0
        concurrent_lock = threading.Lock()
<<<<<<< HEAD
        
        def process_concurrent_request(query_id: int) -> Dict[str, Any]:
            """Process single request in concurrent scenario"""
            nonlocal concurrent_count, max_concurrent
            
            with concurrent_lock:
                concurrent_count += 1
                max_concurrent = max(max_concurrent, concurrent_count)
                
=======

        def process_concurrent_request(query_id: int) -> Dict[str, Any]:
            """Process single request in concurrent scenario"""
            nonlocal concurrent_count, max_concurrent

            with concurrent_lock:
                concurrent_count += 1
                max_concurrent = max(max_concurrent, concurrent_count)

>>>>>>> origin/main
            try:
                start_time = time.perf_counter()
                result = orchestrator.process_query(f"Concurrent query {query_id}")
                processing_time = time.perf_counter() - start_time
<<<<<<< HEAD
                
=======

>>>>>>> origin/main
                return {
                    "success": True,
                    "result": result,
                    "processing_time": processing_time,
                    "query_id": query_id
                }
<<<<<<< HEAD
                
=======

>>>>>>> origin/main
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "query_id": query_id
                }
            finally:
                with concurrent_lock:
                    concurrent_count -= 1
<<<<<<< HEAD
                    
=======

>>>>>>> origin/main
        # Execute concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [
                executor.submit(process_concurrent_request, i)
                for i in range(200)
            ]
<<<<<<< HEAD
            
=======

>>>>>>> origin/main
            # Collect results
            response_times = []
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                metrics.total_requests += 1
<<<<<<< HEAD
                
=======

>>>>>>> origin/main
                if result["success"]:
                    metrics.successful_requests += 1
                    response_times.append(result["processing_time"])
                else:
                    metrics.failed_requests += 1
                    metrics.error_types[result.get("error_type", "Unknown")] += 1
<<<<<<< HEAD
                    
=======

>>>>>>> origin/main
        # Calculate metrics
        if response_times:
            metrics.average_response_time = sum(response_times) / len(response_times)
            metrics.max_response_time = max(response_times)
            metrics.min_response_time = min(response_times)
<<<<<<< HEAD
            
        metrics.concurrent_peak = max_concurrent
        
=======

        metrics.concurrent_peak = max_concurrent

>>>>>>> origin/main
        # Concurrent processing assertions
        assert metrics.successful_requests > 180, f"Too many concurrent failures: {metrics.failed_requests}"
        assert metrics.concurrent_peak >= 15, f"Concurrent peak too low: {metrics.concurrent_peak}"
        assert metrics.average_response_time < 0.5, f"Concurrent response too slow: {metrics.average_response_time:.3f}s"
<<<<<<< HEAD
        
        print(f"Concurrent stress test: {metrics.concurrent_peak} peak concurrent, {metrics.average_response_time:.3f}s avg")
        
    def test_memory_pressure_stress(self, orchestrator, stress_nodes):
        """Test orchestrator under memory pressure conditions"""
        
        # Register nodes
        for name, node in stress_nodes.items():
            orchestrator.register_node(name, node)
            
=======

        print(f"Concurrent stress test: {metrics.concurrent_peak} peak concurrent, {metrics.average_response_time:.3f}s avg")

    def test_memory_pressure_stress(self, orchestrator, stress_nodes):
        """Test orchestrator under memory pressure conditions"""

        # Register nodes
        for name, node in stress_nodes.items():
            orchestrator.register_node(name, node)

>>>>>>> origin/main
        # Create memory-intensive scenario
        large_queries = []
        for i in range(100):
            # Create queries with large payloads
            large_data = {
                "query": f"Memory pressure test {i}",
                "large_payload": "x" * 10000,  # 10KB payload
                "nested_data": {
                    "arrays": [list(range(1000)) for _ in range(10)],
                    "strings": ["large string data" * 100 for _ in range(10)]
                }
            }
            large_queries.append(large_data)
<<<<<<< HEAD
            
        initial_memory = self._get_memory_usage()
        peak_memory = initial_memory
        
        successful_count = 0
        
=======

        initial_memory = self._get_memory_usage()
        peak_memory = initial_memory

        successful_count = 0

>>>>>>> origin/main
        for i, query_data in enumerate(large_queries):
            try:
                result = orchestrator.process_query(str(query_data))
                successful_count += 1
<<<<<<< HEAD
                
                # Monitor memory usage
                current_memory = self._get_memory_usage()
                peak_memory = max(peak_memory, current_memory)
                
                # Verify MATRIZ graph doesn't grow unbounded
                graph_size = len(orchestrator.matriz_graph)
                assert graph_size < 1000, f"MATRIZ graph growing too large: {graph_size}"
                
                # Periodic garbage collection
                if i % 20 == 0:
                    gc.collect()
                    
=======

                # Monitor memory usage
                current_memory = self._get_memory_usage()
                peak_memory = max(peak_memory, current_memory)

                # Verify MATRIZ graph doesn't grow unbounded
                graph_size = len(orchestrator.matriz_graph)
                assert graph_size < 1000, f"MATRIZ graph growing too large: {graph_size}"

                # Periodic garbage collection
                if i % 20 == 0:
                    gc.collect()

>>>>>>> origin/main
            except MemoryError:
                # Memory pressure handling
                gc.collect()
                print(f"Memory pressure at query {i}, continuing...")
<<<<<<< HEAD
                
        memory_growth = peak_memory - initial_memory
        
        # Memory pressure assertions
        assert successful_count > 80, f"Too many memory pressure failures: {100 - successful_count}"
        assert memory_growth < 200, f"Excessive memory growth: {memory_growth:.1f}MB"
        
        print(f"Memory stress test: {memory_growth:.1f}MB peak growth, {successful_count}/100 successful")
        
    def test_node_churn_stress(self, orchestrator):
        """Test orchestrator with frequent node registration/deregistration"""
        
        metrics = StressTestMetrics()
        active_nodes = {}
        
=======

        memory_growth = peak_memory - initial_memory

        # Memory pressure assertions
        assert successful_count > 80, f"Too many memory pressure failures: {100 - successful_count}"
        assert memory_growth < 200, f"Excessive memory growth: {memory_growth:.1f}MB"

        print(f"Memory stress test: {memory_growth:.1f}MB peak growth, {successful_count}/100 successful")

    def test_node_churn_stress(self, orchestrator):
        """Test orchestrator with frequent node registration/deregistration"""

        metrics = StressTestMetrics()
        active_nodes = {}

>>>>>>> origin/main
        def register_random_node():
            """Register a random node"""
            node_id = f"dynamic_node_{random.randint(1000, 9999)}"
            node = MockCognitiveNode(
                node_id,
                processing_delay=random.uniform(0.001, 0.01),
                failure_rate=random.uniform(0.0, 0.05)
            )
            orchestrator.register_node(node_id, node)
            active_nodes[node_id] = node
            return node_id
<<<<<<< HEAD
            
=======

>>>>>>> origin/main
        def deregister_random_node():
            """Deregister a random active node"""
            if active_nodes:
                node_id = random.choice(list(active_nodes.keys()))
                del orchestrator.available_nodes[node_id]
                del active_nodes[node_id]
                return node_id
            return None
<<<<<<< HEAD
            
        # Start with some base nodes
        for i in range(5):
            register_random_node()
            
=======

        # Start with some base nodes
        for i in range(5):
            register_random_node()

>>>>>>> origin/main
        # Perform operations with node churn
        for i in range(200):
            # Random node operations
            operation = random.choice(["register", "deregister", "process"])
<<<<<<< HEAD
            
=======

>>>>>>> origin/main
            if operation == "register" or len(active_nodes) < 2:
                register_random_node()
            elif operation == "deregister" and len(active_nodes) > 2:
                deregister_random_node()
            elif operation == "process":
                try:
                    result = orchestrator.process_query(f"Dynamic test {i}")
                    metrics.successful_requests += 1
                except Exception as e:
                    metrics.failed_requests += 1
                    metrics.error_types[type(e).__name__] += 1
<<<<<<< HEAD
                    
                metrics.total_requests += 1
                
=======

                metrics.total_requests += 1

>>>>>>> origin/main
        # Node churn assertions
        assert metrics.total_requests > 0, "Should have processed some requests"
        success_rate = metrics.successful_requests / metrics.total_requests
        assert success_rate > 0.8, f"Too many failures during node churn: {success_rate:.2f}"
        assert len(active_nodes) > 0, "Should have some nodes remaining"
<<<<<<< HEAD
        
        print(f"Node churn stress test: {success_rate:.2f} success rate with dynamic nodes")
        
    def test_failure_cascade_prevention(self, orchestrator):
        """Test orchestrator resilience to cascading failures"""
        
=======

        print(f"Node churn stress test: {success_rate:.2f} success rate with dynamic nodes")

    def test_failure_cascade_prevention(self, orchestrator):
        """Test orchestrator resilience to cascading failures"""

>>>>>>> origin/main
        # Create nodes with increasing failure rates
        failing_nodes = {}
        for i in range(5):
            failure_rate = 0.1 + (i * 0.2)  # 10% to 90% failure rate
            node_name = f"failing_node_{i}"
            failing_nodes[node_name] = MockCognitiveNode(
                node_name,
                processing_delay=0.01,
                failure_rate=failure_rate
            )
            orchestrator.register_node(node_name, failing_nodes[node_name])
<<<<<<< HEAD
            
        # Add one reliable node
        reliable_node = MockCognitiveNode("reliable", processing_delay=0.01, failure_rate=0.0)
        orchestrator.register_node("reliable", reliable_node)
        
        metrics = StressTestMetrics()
        cascade_detected = False
        
=======

        # Add one reliable node
        reliable_node = MockCognitiveNode("reliable", processing_delay=0.01, failure_rate=0.0)
        orchestrator.register_node("reliable", reliable_node)

        metrics = StressTestMetrics()
        cascade_detected = False

>>>>>>> origin/main
        # Process requests and monitor for cascades
        for i in range(100):
            try:
                result = orchestrator.process_query(f"Cascade test {i}")
<<<<<<< HEAD
                
                # Check if result indicates cascade prevention
                if "error" in result and "cascade" in result["error"].lower():
                    cascade_detected = True
                    
                metrics.successful_requests += 1
                
            except Exception as e:
                metrics.failed_requests += 1
                metrics.error_types[type(e).__name__] += 1
                
=======

                # Check if result indicates cascade prevention
                if "error" in result and "cascade" in result["error"].lower():
                    cascade_detected = True

                metrics.successful_requests += 1

            except Exception as e:
                metrics.failed_requests += 1
                metrics.error_types[type(e).__name__] += 1

>>>>>>> origin/main
                # Check if orchestrator is still responsive after failures
                try:
                    # Should still be able to process with reliable node
                    recovery_result = orchestrator.process_query("Recovery test")
                    assert recovery_result is not None, "Orchestrator should remain responsive"
                except Exception:
                    # If completely unresponsive, cascade occurred
                    cascade_detected = True
<<<<<<< HEAD
                    
            metrics.total_requests += 1
            
        # Cascade prevention assertions
        success_rate = metrics.successful_requests / metrics.total_requests
        assert success_rate > 0.3, f"Complete system failure detected: {success_rate:.2f}"
        
        # Verify reliable node is still functional
        final_test = orchestrator.process_query("Final reliability test")
        assert final_test is not None, "Reliable node should still function"
        
        print(f"Cascade prevention test: {success_rate:.2f} success rate, cascade detected: {cascade_detected}")
        
    def test_long_running_stability(self, orchestrator, stress_nodes):
        """Test orchestrator stability over extended operation"""
        
        # Register nodes
        for name, node in stress_nodes.items():
            orchestrator.register_node(name, node)
            
        metrics = StressTestMetrics()
        start_time = time.perf_counter()
        target_duration = 60  # 1 minute stress test
        
        initial_memory = self._get_memory_usage()
        memory_samples = []
        
=======

            metrics.total_requests += 1

        # Cascade prevention assertions
        success_rate = metrics.successful_requests / metrics.total_requests
        assert success_rate > 0.3, f"Complete system failure detected: {success_rate:.2f}"

        # Verify reliable node is still functional
        final_test = orchestrator.process_query("Final reliability test")
        assert final_test is not None, "Reliable node should still function"

        print(f"Cascade prevention test: {success_rate:.2f} success rate, cascade detected: {cascade_detected}")

    def test_long_running_stability(self, orchestrator, stress_nodes):
        """Test orchestrator stability over extended operation"""

        # Register nodes
        for name, node in stress_nodes.items():
            orchestrator.register_node(name, node)

        metrics = StressTestMetrics()
        start_time = time.perf_counter()
        target_duration = 60  # 1 minute stress test

        initial_memory = self._get_memory_usage()
        memory_samples = []

>>>>>>> origin/main
        iteration = 0
        while time.perf_counter() - start_time < target_duration:
            try:
                # Vary query complexity
                if iteration % 10 == 0:
                    query = f"Complex query {iteration} with additional metadata and processing requirements"
                else:
                    query = f"Simple query {iteration}"
<<<<<<< HEAD
                    
                result = orchestrator.process_query(query)
                metrics.successful_requests += 1
                
=======

                result = orchestrator.process_query(query)
                metrics.successful_requests += 1

>>>>>>> origin/main
                # Sample memory usage periodically
                if iteration % 50 == 0:
                    current_memory = self._get_memory_usage()
                    memory_samples.append(current_memory)
<<<<<<< HEAD
                    
                    # Trigger garbage collection periodically
                    if iteration % 200 == 0:
                        gc.collect()
                        
            except Exception as e:
                metrics.failed_requests += 1
                metrics.error_types[type(e).__name__] += 1
                
            metrics.total_requests += 1
            iteration += 1
            
            # Small delay to prevent CPU overload
            time.sleep(0.001)
            
        elapsed_time = time.perf_counter() - start_time
        final_memory = self._get_memory_usage()
        
        # Calculate stability metrics
        metrics.throughput_qps = metrics.total_requests / elapsed_time
        memory_trend = final_memory - initial_memory
        
=======

                    # Trigger garbage collection periodically
                    if iteration % 200 == 0:
                        gc.collect()

            except Exception as e:
                metrics.failed_requests += 1
                metrics.error_types[type(e).__name__] += 1

            metrics.total_requests += 1
            iteration += 1

            # Small delay to prevent CPU overload
            time.sleep(0.001)

        elapsed_time = time.perf_counter() - start_time
        final_memory = self._get_memory_usage()

        # Calculate stability metrics
        metrics.throughput_qps = metrics.total_requests / elapsed_time
        memory_trend = final_memory - initial_memory

>>>>>>> origin/main
        # Stability assertions
        success_rate = metrics.successful_requests / metrics.total_requests
        assert success_rate > 0.95, f"Stability degraded over time: {success_rate:.2f}"
        assert metrics.throughput_qps > 5.0, f"Throughput too low: {metrics.throughput_qps:.1f} QPS"
        assert memory_trend < 50, f"Memory leak detected: {memory_trend:.1f}MB growth"
<<<<<<< HEAD
        
        print(f"Stability test: {elapsed_time:.1f}s, {metrics.throughput_qps:.1f} QPS, {memory_trend:.1f}MB growth")
        
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        import psutil
        import os
        
=======

        print(f"Stability test: {elapsed_time:.1f}s, {metrics.throughput_qps:.1f} QPS, {memory_trend:.1f}MB growth")

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        import os

        import psutil

>>>>>>> origin/main
        try:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except ImportError:
            # Fallback if psutil not available
            return 0.0


@pytest.mark.skipif(not MATRIZ_AVAILABLE, reason="MATRIZ system not available")
class TestAsyncOrchestratorStress:
    """Test async orchestrator stress scenarios"""
<<<<<<< HEAD
    
=======

>>>>>>> origin/main
    @pytest.fixture
    def async_orchestrator(self):
        """Create async orchestrator for testing"""
        return AsyncCognitiveOrchestrator()
<<<<<<< HEAD
        
    @pytest.mark.asyncio
    async def test_async_concurrent_load(self, async_orchestrator):
        """Test async orchestrator under high concurrent load"""
        
=======

    @pytest.mark.asyncio
    async def test_async_concurrent_load(self, async_orchestrator):
        """Test async orchestrator under high concurrent load"""

>>>>>>> origin/main
        # Register mock async node
        async def mock_async_process(data):
            await asyncio.sleep(0.01)  # Simulate async processing
            return {"result": f"Async processed: {data.get('query', 'unknown')}"}
<<<<<<< HEAD
            
        async_orchestrator.register_async_node("async_node", mock_async_process)
        
=======

        async_orchestrator.register_async_node("async_node", mock_async_process)

>>>>>>> origin/main
        # Create many concurrent requests
        async def process_async_request(query_id: int):
            try:
                result = await async_orchestrator.process_query_async(f"Async query {query_id}")
                return {"success": True, "result": result, "query_id": query_id}
            except Exception as e:
                return {"success": False, "error": str(e), "query_id": query_id}
<<<<<<< HEAD
                
        # Launch 500 concurrent requests
        tasks = [process_async_request(i) for i in range(500)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        successful = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
        failed = len(results) - successful
        
        # Async stress assertions
        assert successful > 480, f"Too many async failures: {failed}"
        assert failed < 20, f"Failure rate too high: {failed/len(results):.2f}"
        
        print(f"Async stress test: {successful}/{len(results)} successful")
        
    @pytest.mark.asyncio
    async def test_async_timeout_handling(self, async_orchestrator):
        """Test async orchestrator timeout handling under stress"""
        
=======

        # Launch 500 concurrent requests
        tasks = [process_async_request(i) for i in range(500)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Analyze results
        successful = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
        failed = len(results) - successful

        # Async stress assertions
        assert successful > 480, f"Too many async failures: {failed}"
        assert failed < 20, f"Failure rate too high: {failed/len(results):.2f}"

        print(f"Async stress test: {successful}/{len(results)} successful")

    @pytest.mark.asyncio
    async def test_async_timeout_handling(self, async_orchestrator):
        """Test async orchestrator timeout handling under stress"""

>>>>>>> origin/main
        # Register slow and fast nodes
        async def slow_async_process(data):
            await asyncio.sleep(2.0)  # Very slow processing
            return {"result": "Slow result"}
<<<<<<< HEAD
            
        async def fast_async_process(data):
            await asyncio.sleep(0.001)  # Fast processing
            return {"result": "Fast result"}
            
        async_orchestrator.register_async_node("slow_node", slow_async_process)
        async_orchestrator.register_async_node("fast_node", fast_async_process)
        
=======

        async def fast_async_process(data):
            await asyncio.sleep(0.001)  # Fast processing
            return {"result": "Fast result"}

        async_orchestrator.register_async_node("slow_node", slow_async_process)
        async_orchestrator.register_async_node("fast_node", fast_async_process)

>>>>>>> origin/main
        # Test timeout scenarios
        timeout_results = []
        for i in range(50):
            try:
                # Use short timeout to force timeouts on slow node
                result = await asyncio.wait_for(
                    async_orchestrator.process_query_async(f"Timeout test {i}"),
                    timeout=0.5
                )
                timeout_results.append({"success": True, "result": result})
            except asyncio.TimeoutError:
                timeout_results.append({"success": False, "error": "timeout"})
            except Exception as e:
                timeout_results.append({"success": False, "error": str(e)})
<<<<<<< HEAD
                
        # Verify timeout handling
        timeouts = sum(1 for r in timeout_results if not r["success"] and r.get("error") == "timeout")
        successes = sum(1 for r in timeout_results if r["success"])
        
        # Should have some timeouts (slow node) and some successes (fast node)
        assert timeouts > 0, "Should have some timeouts with slow node"
        assert successes > 0, "Should have some successes with fast node"
        
=======

        # Verify timeout handling
        timeouts = sum(1 for r in timeout_results if not r["success"] and r.get("error") == "timeout")
        successes = sum(1 for r in timeout_results if r["success"])

        # Should have some timeouts (slow node) and some successes (fast node)
        assert timeouts > 0, "Should have some timeouts with slow node"
        assert successes > 0, "Should have some successes with fast node"

>>>>>>> origin/main
        print(f"Async timeout test: {successes} successes, {timeouts} timeouts")


class TestOrchestratorResourceManagement:
    """Test orchestrator resource management under stress"""
<<<<<<< HEAD
    
    def test_graph_memory_management(self):
        """Test MATRIZ graph memory management under stress"""
        
        if not MATRIZ_AVAILABLE:
            pytest.skip("MATRIZ system not available")
            
        orchestrator = CognitiveOrchestrator()
        
        # Register simple node
        simple_node = MockCognitiveNode("simple", processing_delay=0.001)
        orchestrator.register_node("simple", simple_node)
        
        # Generate many nodes to test graph cleanup
        initial_graph_size = len(orchestrator.matriz_graph)
        
        for i in range(1000):
            orchestrator.process_query(f"Graph test {i}")
            
=======

    def test_graph_memory_management(self):
        """Test MATRIZ graph memory management under stress"""

        if not MATRIZ_AVAILABLE:
            pytest.skip("MATRIZ system not available")

        orchestrator = CognitiveOrchestrator()

        # Register simple node
        simple_node = MockCognitiveNode("simple", processing_delay=0.001)
        orchestrator.register_node("simple", simple_node)

        # Generate many nodes to test graph cleanup
        initial_graph_size = len(orchestrator.matriz_graph)

        for i in range(1000):
            orchestrator.process_query(f"Graph test {i}")

>>>>>>> origin/main
            # Check if graph is growing unbounded
            current_size = len(orchestrator.matriz_graph)
            if i > 500 and current_size > 800:
                # Graph should have cleanup mechanism
                pytest.fail(f"Graph growing unbounded: {current_size} nodes after {i} queries")
<<<<<<< HEAD
                
        final_graph_size = len(orchestrator.matriz_graph)
        
        # Graph management assertions
        assert final_graph_size < 1000, f"Graph too large: {final_graph_size}"
        
        print(f"Graph management test: {initial_graph_size} -> {final_graph_size} nodes")
        
    def test_execution_trace_limits(self):
        """Test execution trace memory limits under stress"""
        
        if not MATRIZ_AVAILABLE:
            pytest.skip("MATRIZ system not available")
            
        orchestrator = CognitiveOrchestrator()
        
        # Register node
        node = MockCognitiveNode("trace_test", processing_delay=0.001)
        orchestrator.register_node("trace_test", node)
        
        # Generate many traces
        for i in range(2000):
            orchestrator.process_query(f"Trace test {i}")
            
=======

        final_graph_size = len(orchestrator.matriz_graph)

        # Graph management assertions
        assert final_graph_size < 1000, f"Graph too large: {final_graph_size}"

        print(f"Graph management test: {initial_graph_size} -> {final_graph_size} nodes")

    def test_execution_trace_limits(self):
        """Test execution trace memory limits under stress"""

        if not MATRIZ_AVAILABLE:
            pytest.skip("MATRIZ system not available")

        orchestrator = CognitiveOrchestrator()

        # Register node
        node = MockCognitiveNode("trace_test", processing_delay=0.001)
        orchestrator.register_node("trace_test", node)

        # Generate many traces
        for i in range(2000):
            orchestrator.process_query(f"Trace test {i}")

>>>>>>> origin/main
            # Check trace size doesn't grow unbounded
            trace_count = len(orchestrator.execution_trace)
            if trace_count > 1500:
                # Should have trace cleanup/rotation
                print(f"Warning: Trace growing large: {trace_count} entries")
<<<<<<< HEAD
                
        final_trace_size = len(orchestrator.execution_trace)
        
        # Trace management assertions
        assert final_trace_size < 2000, f"Trace too large: {final_trace_size}"
        
=======

        final_trace_size = len(orchestrator.execution_trace)

        # Trace management assertions
        assert final_trace_size < 2000, f"Trace too large: {final_trace_size}"

>>>>>>> origin/main
        print(f"Trace management test: {final_trace_size} trace entries")


if __name__ == "__main__":
    # Run comprehensive orchestrator stress tests
<<<<<<< HEAD
    pytest.main([__file__, "-v", "-x", "--tb=short"])
=======
    pytest.main([__file__, "-v", "-x", "--tb=short"])
>>>>>>> origin/main
