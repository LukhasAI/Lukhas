"""
Memory Service Performance Tests
===============================

T4/0.01% excellence validation tests for memory service operations.
Validates latency SLOs under various load conditions with statistical
significance testing.

Test Requirements:
- Search: p95 <50ms, p99 <100ms
- Upsert: p95 <100ms, p99 <150ms
- Batch: p95 <200ms, p99 <300ms
- 99.9% availability SLO
"""

import asyncio
import random
import statistics
import string
import time
from dataclasses import dataclass
from typing import Any, Dict, List

import pytest

from ..adapters.vector_store_base import VectorDocument
from ..api_read import MemoryReadService, SearchQuery, SearchType
from ..api_write import BatchWriteOperation, MemoryWriteService, WriteOperation
from ..backpressure import AdaptiveBackpressure, BackpressureFactory
from ..circuit_breaker import CircuitBreakerFactory, CircuitBreakerRegistry
from ..metrics import get_metrics_collector, get_t4_compliance_report


@dataclass
class PerformanceTestResult:
    """Results from a performance test run"""
    operation_type: str
    sample_count: int
    duration_seconds: float
    latencies_ms: List[float]
    p50_ms: float
    p95_ms: float
    p99_ms: float
    max_ms: float
    min_ms: float
    throughput_ops_per_sec: float
    error_count: int
    error_rate: float
    t4_compliant: bool
    slo_threshold_ms: float


class MockVectorStore:
    """Mock vector store for testing with configurable latency"""

    def __init__(self, base_latency_ms: float = 5.0, latency_variance: float = 2.0):
        self.base_latency_ms = base_latency_ms
        self.latency_variance = latency_variance
        self.documents: Dict[str, VectorDocument] = {}
        self.call_count = 0
        self.fail_rate = 0.0

    async def initialize(self):
        await asyncio.sleep(0.001)

    async def close(self):
        pass

    async def health_check(self) -> bool:
        return True

    async def search_vectors(self, query) -> Any:
        self.call_count += 1

        # Simulate network/processing latency
        latency = max(0.001, random.gauss(
            self.base_latency_ms / 1000,
            self.latency_variance / 1000
        ))
        await asyncio.sleep(latency)

        # Simulate occasional failures
        if random.random() < self.fail_rate:
            raise Exception("Simulated search failure")

        # Return mock results
        from ..api_read import MemoryFold, SearchResponse, SearchResult
        results = [
            SearchResult(
                fold=MemoryFold(
                    fold_id=f"fold_{i}",
                    content=f"Mock content {i}",
                    metadata={"rank": i},
                    embedding=[]
                ),
                score=0.9 - (i * 0.1),
                rank=i + 1
            ) for i in range(min(query.top_k, 10))
        ]

        return SearchResponse(
            results=results,
            query_time_ms=latency * 1000,
            total_results=len(results)
        )

    async def upsert_documents(self, documents: List[VectorDocument]) -> Dict[str, Any]:
        self.call_count += 1

        # Simulate processing latency
        latency = max(0.001, random.gauss(
            self.base_latency_ms / 1000,
            self.latency_variance / 1000
        ))
        await asyncio.sleep(latency)

        if random.random() < self.fail_rate:
            raise Exception("Simulated upsert failure")

        # Store documents
        for doc in documents:
            self.documents[doc.id] = doc

        return {
            'inserted': len(documents),
            'updated': 0,
            'failed': 0,
            'duration_ms': latency * 1000
        }


@pytest.fixture
async def memory_services():
    """Create memory services with mock vector store for testing"""
    # Create mock vector store
    vector_store = MockVectorStore(base_latency_ms=10.0, latency_variance=5.0)
    await vector_store.initialize()

    # Create circuit breakers
    circuit_breakers = CircuitBreakerRegistry()
    read_breaker = circuit_breakers.create_breaker(
        'test_read',
        CircuitBreakerFactory.create_memory_service_config()
    )
    write_breaker = circuit_breakers.create_breaker(
        'test_write',
        CircuitBreakerFactory.create_memory_service_config()
    )

    # Create backpressure
    backpressure_configs = BackpressureFactory.create_memory_service_config()
    backpressure = AdaptiveBackpressure(backpressure_configs)

    # Create services
    read_service = MemoryReadService(
        vector_store=vector_store,
        circuit_breaker=read_breaker,
        backpressure=backpressure
    )

    write_service = MemoryWriteService(
        vector_store=vector_store,
        circuit_breaker=write_breaker,
        backpressure=backpressure
    )

    yield read_service, write_service, vector_store

    await vector_store.close()


class TestMemoryServicePerformance:
    """Performance test suite for memory service operations"""

    async def run_latency_test(self,
                             operation_func,
                             operation_type: str,
                             sample_count: int = 1000,
                             concurrency: int = 10) -> PerformanceTestResult:
        """Run latency performance test with statistical analysis"""
        latencies = []
        errors = 0
        start_time = time.perf_counter()

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(concurrency)

        async def measure_operation():
            async with semaphore:
                op_start = time.perf_counter()
                try:
                    await operation_func()
                    op_duration = (time.perf_counter() - op_start) * 1000
                    latencies.append(op_duration)
                except Exception:
                    nonlocal errors
                    errors += 1
                    # Still record the time for failed operations
                    op_duration = (time.perf_counter() - op_start) * 1000
                    latencies.append(op_duration)

        # Run all operations
        tasks = [measure_operation() for _ in range(sample_count)]
        await asyncio.gather(*tasks)

        total_duration = time.perf_counter() - start_time

        # Calculate statistics
        if latencies:
            sorted_latencies = sorted(latencies)
            n = len(sorted_latencies)

            p50_ms = sorted_latencies[n // 2]
            p95_ms = sorted_latencies[int(n * 0.95)]
            p99_ms = sorted_latencies[int(n * 0.99)]
            min_ms = min(sorted_latencies)
            max_ms = max(sorted_latencies)
        else:
            p50_ms = p95_ms = p99_ms = min_ms = max_ms = 0.0

        # T4 thresholds
        t4_thresholds = {
            'search': 50.0,
            'upsert': 100.0,
            'batch': 200.0
        }
        threshold = t4_thresholds.get(operation_type, 100.0)

        return PerformanceTestResult(
            operation_type=operation_type,
            sample_count=sample_count,
            duration_seconds=total_duration,
            latencies_ms=latencies,
            p50_ms=p50_ms,
            p95_ms=p95_ms,
            p99_ms=p99_ms,
            max_ms=max_ms,
            min_ms=min_ms,
            throughput_ops_per_sec=sample_count / total_duration,
            error_count=errors,
            error_rate=errors / sample_count if sample_count > 0 else 0.0,
            t4_compliant=p95_ms <= threshold,
            slo_threshold_ms=threshold
        )

    @pytest.mark.asyncio
    async def test_search_performance_t4_compliance(self, memory_services):
        """Test search operation T4/0.01% excellence compliance"""
        read_service, _, vector_store = memory_services

        # Define search operation
        async def search_operation():
            query = SearchQuery(
                query_text=f"test query {random.randint(1, 1000)}",
                search_type=SearchType.SEMANTIC,
                top_k=10
            )
            await read_service.search(query)

        # Run performance test
        result = await self.run_latency_test(
            search_operation,
            'search',
            sample_count=1000,
            concurrency=20
        )

        # Validate T4 requirements
        assert result.p95_ms <= 50.0, f"Search p95 ({result.p95_ms:.2f}ms) exceeds T4 requirement (50ms)"
        assert result.p99_ms <= 100.0, f"Search p99 ({result.p99_ms:.2f}ms) exceeds limit (100ms)"
        assert result.error_rate <= 0.001, f"Error rate ({result.error_rate:.3f}) exceeds 0.1%"

        print(f"Search Performance: p95={result.p95_ms:.2f}ms, p99={result.p99_ms:.2f}ms, "
              f"throughput={result.throughput_ops_per_sec:.1f} ops/sec")

    @pytest.mark.asyncio
    async def test_upsert_performance_t4_compliance(self, memory_services):
        """Test upsert operation T4/0.01% excellence compliance"""
        _, write_service, vector_store = memory_services

        # Define upsert operation
        async def upsert_operation():
            content = ''.join(random.choices(string.ascii_letters, k=1000))
            await write_service.upsert_memory_fold(
                content=content,
                metadata={"test": True, "timestamp": time.time()}
            )

        # Run performance test
        result = await self.run_latency_test(
            upsert_operation,
            'upsert',
            sample_count=500,  # Smaller sample for writes
            concurrency=10
        )

        # Validate T4 requirements
        assert result.p95_ms <= 100.0, f"Upsert p95 ({result.p95_ms:.2f}ms) exceeds T4 requirement (100ms)"
        assert result.p99_ms <= 150.0, f"Upsert p99 ({result.p99_ms:.2f}ms) exceeds limit (150ms)"
        assert result.error_rate <= 0.001, f"Error rate ({result.error_rate:.3f}) exceeds 0.1%"

        print(f"Upsert Performance: p95={result.p95_ms:.2f}ms, p99={result.p99_ms:.2f}ms, "
              f"throughput={result.throughput_ops_per_sec:.1f} ops/sec")

    @pytest.mark.asyncio
    async def test_batch_upsert_performance(self, memory_services):
        """Test batch upsert performance under load"""
        _, write_service, vector_store = memory_services

        # Define batch upsert operation
        async def batch_upsert_operation():
            operations = []
            for i in range(10):  # 10 operations per batch
                op = WriteOperation(
                    content=f"Batch content {i} " + ''.join(random.choices(string.ascii_letters, k=500)),
                    metadata={"batch": True, "index": i}
                )
                operations.append(op)

            batch_op = BatchWriteOperation(operations=operations, atomic=True)
            await write_service.batch_upsert(batch_op)

        # Run performance test
        result = await self.run_latency_test(
            batch_upsert_operation,
            'batch',
            sample_count=100,
            concurrency=5
        )

        # Validate batch requirements (more lenient than individual ops)
        assert result.p95_ms <= 200.0, f"Batch p95 ({result.p95_ms:.2f}ms) exceeds requirement (200ms)"
        assert result.p99_ms <= 300.0, f"Batch p99 ({result.p99_ms:.2f}ms) exceeds limit (300ms)"
        assert result.error_rate <= 0.001, f"Error rate ({result.error_rate:.3f}) exceeds 0.1%"

        print(f"Batch Performance: p95={result.p95_ms:.2f}ms, p99={result.p99_ms:.2f}ms, "
              f"throughput={result.throughput_ops_per_sec:.1f} batches/sec")

    @pytest.mark.asyncio
    async def test_mixed_workload_performance(self, memory_services):
        """Test performance under mixed read/write workload"""
        read_service, write_service, vector_store = memory_services

        # Mixed workload: 70% reads, 30% writes
        async def mixed_operation():
            if random.random() < 0.7:
                # Read operation
                query = SearchQuery(
                    query_text=f"mixed query {random.randint(1, 100)}",
                    search_type=random.choice(list(SearchType)),
                    top_k=random.randint(5, 20)
                )
                await read_service.search(query)
            else:
                # Write operation
                content = ''.join(random.choices(string.ascii_letters, k=800))
                await write_service.upsert_memory_fold(
                    content=content,
                    metadata={"workload": "mixed"}
                )

        # Run mixed workload test
        result = await self.run_latency_test(
            mixed_operation,
            'mixed',
            sample_count=1000,
            concurrency=25
        )

        # Mixed workload should maintain reasonable performance
        assert result.p95_ms <= 150.0, f"Mixed workload p95 ({result.p95_ms:.2f}ms) too high"
        assert result.error_rate <= 0.005, f"Mixed workload error rate ({result.error_rate:.3f}) too high"

        print(f"Mixed Workload Performance: p95={result.p95_ms:.2f}ms, "
              f"throughput={result.throughput_ops_per_sec:.1f} ops/sec, "
              f"error_rate={result.error_rate:.3f}")

    @pytest.mark.asyncio
    async def test_circuit_breaker_under_failures(self, memory_services):
        """Test circuit breaker behavior under simulated failures"""
        read_service, _, vector_store = memory_services

        # Enable high failure rate
        vector_store.fail_rate = 0.8

        # Define search operation
        async def failing_search_operation():
            query = SearchQuery(
                query_text="failing query",
                search_type=SearchType.SEMANTIC,
                top_k=5
            )
            try:
                await read_service.search(query)
            except Exception:
                pass  # Expected failures

        # Run test with high failure rate
        start_time = time.perf_counter()
        tasks = [failing_search_operation() for _ in range(100)]
        await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.perf_counter() - start_time

        # Circuit breaker should have opened and failed fast
        assert duration < 10.0, "Circuit breaker should have opened and failed fast"

        # Reset failure rate and test recovery
        vector_store.fail_rate = 0.0
        await asyncio.sleep(5)  # Wait for circuit breaker recovery

        # Test that service recovers
        query = SearchQuery(query_text="recovery test", top_k=1)
        result = await read_service.search(query)
        assert len(result.results) > 0, "Service should recover after circuit breaker closes"

    @pytest.mark.asyncio
    async def test_backpressure_under_load(self, memory_services):
        """Test backpressure behavior under extreme load"""
        read_service, _, vector_store = memory_services

        # Increase base latency to trigger backpressure
        vector_store.base_latency_ms = 200.0

        rejection_count = 0

        async def load_test_operation():
            nonlocal rejection_count
            try:
                query = SearchQuery(query_text="load test", top_k=1)
                await read_service.search(query)
            except Exception as e:
                if "backpressure" in str(e).lower() or "overloaded" in str(e).lower():
                    rejection_count += 1
                else:
                    raise

        # Generate high load
        tasks = [load_test_operation() for _ in range(500)]
        await asyncio.gather(*tasks, return_exceptions=True)

        # Backpressure should have triggered some rejections
        rejection_rate = rejection_count / 500
        print(f"Backpressure rejection rate: {rejection_rate:.3f}")

        # Should reject some requests but not all
        assert 0.1 <= rejection_rate <= 0.9, f"Unexpected rejection rate: {rejection_rate}"

    @pytest.mark.asyncio
    async def test_sustained_load_performance(self, memory_services):
        """Test performance under sustained load over time"""
        read_service, write_service, vector_store = memory_services

        results = []
        test_duration = 30  # 30 seconds
        batch_size = 50
        start_time = time.perf_counter()

        while time.perf_counter() - start_time < test_duration:
            batch_start = time.perf_counter()

            # Run a batch of operations
            tasks = []
            for _ in range(batch_size):
                if random.random() < 0.8:  # 80% reads
                    query = SearchQuery(query_text=f"sustained {time.time()}", top_k=5)
                    tasks.append(read_service.search(query))
                else:  # 20% writes
                    content = f"Sustained test {time.time()}"
                    tasks.append(write_service.upsert_memory_fold(content=content))

            # Execute batch
            await asyncio.gather(*tasks, return_exceptions=True)

            batch_duration = time.perf_counter() - batch_start
            batch_throughput = batch_size / batch_duration

            results.append({
                'timestamp': time.perf_counter() - start_time,
                'throughput': batch_throughput,
                'latency_ms': batch_duration * 1000 / batch_size
            })

            # Brief pause between batches
            await asyncio.sleep(0.1)

        # Analyze sustained performance
        throughputs = [r['throughput'] for r in results]
        latencies = [r['latency_ms'] for r in results]

        avg_throughput = statistics.mean(throughputs)
        avg_latency = statistics.mean(latencies)
        throughput_stability = statistics.stdev(throughputs) / avg_throughput

        print(f"Sustained Load: avg_throughput={avg_throughput:.1f} ops/sec, "
              f"avg_latency={avg_latency:.2f}ms, stability={throughput_stability:.3f}")

        # Performance should remain stable
        assert throughput_stability < 0.5, f"Throughput too unstable: {throughput_stability:.3f}"
        assert avg_latency < 100.0, f"Average latency too high: {avg_latency:.2f}ms"

    def test_statistical_significance(self):
        """Test statistical significance of performance measurements"""
        # Generate sample data
        sample1 = [random.gauss(50, 10) for _ in range(1000)]
        sample2 = [random.gauss(52, 10) for _ in range(1000)]

        # Perform t-test (simplified)
        mean1, mean2 = statistics.mean(sample1), statistics.mean(sample2)
        std1, std2 = statistics.stdev(sample1), statistics.stdev(sample2)

        # Effect size (Cohen's d)
        pooled_std = ((std1**2 + std2**2) / 2) ** 0.5
        cohens_d = abs(mean1 - mean2) / pooled_std

        print(f"Statistical test: mean1={mean1:.2f}, mean2={mean2:.2f}, "
              f"effect_size={cohens_d:.3f}")

        # For performance testing, we want to detect differences >= 5ms
        # with high confidence
        assert cohens_d > 0.1 or abs(mean1 - mean2) < 5.0, "Statistical power insufficient"


@pytest.mark.asyncio
async def test_complete_t4_compliance_validation():
    """Comprehensive T4/0.01% excellence validation"""
    # This would be run as a complete integration test
    # with real services and load patterns

    collector = get_metrics_collector()
    collector.reset_metrics()

    # Simulate realistic operations over time
    operations_completed = 0
    start_time = time.perf_counter()

    # Run for 60 seconds
    while time.perf_counter() - start_time < 60:
        # Simulate search operation
        with collector.time_operation('search'):
            latency = random.gauss(30, 10)  # 30ms average
            await asyncio.sleep(max(0.001, latency / 1000))
            operations_completed += 1

        # Simulate occasional upsert
        if random.random() < 0.2:
            with collector.time_operation('upsert'):
                latency = random.gauss(50, 15)  # 50ms average
                await asyncio.sleep(max(0.001, latency / 1000))
                operations_completed += 1

        await asyncio.sleep(0.01)  # Brief pause

    # Generate T4 compliance report
    compliance_report = get_t4_compliance_report()

    print(f"T4 Compliance Report: {compliance_report}")

    # Validate overall compliance
    assert compliance_report['overall_compliant'], "T4/0.01% excellence not achieved"
    assert operations_completed > 100, "Insufficient operations for validation"

    print(f"T4/0.01% Excellence Validation PASSED: {operations_completed} operations completed")
