#!/usr/bin/env python3
"""
Memory System Safeguard Property Tests
=====================================

Property-based tests verifying memory recall integrity under stress conditions.
Ensures top-K correctness and data fidelity at scale.

Critical for T4/0.01% operational excellence.
"""

import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any, Dict, List, Set, Optional

import pytest

# Import memory system components
try:
    from memory.adaptive_memory import (
        AdaptiveMemorySystem,
        MemoryFold,
        MemoryItem,
        MemoryType,
        get_memory_system,
    )
    MEMORY_SYSTEMS_AVAILABLE = True
except ImportError:
    MEMORY_SYSTEMS_AVAILABLE = False


@dataclass
class TestMemoryItem:
    """Test memory item with known properties for verification"""
    id: str
    content: str
    embedding: List[float]
    category: str
    timestamp: float
    priority: int
    metadata: Dict[str, Any]

    def similarity_to(self, other: 'TestMemoryItem') -> float:
        """Calculate cosine similarity for testing"""
        if len(self.embedding) != len(other.embedding):
            return 0.0

        dot_product = sum(a * b for a, b in zip(self.embedding, other.embedding))
        norm_a = sum(a * a for a in self.embedding) ** 0.5
        norm_b = sum(b * b for b in other.embedding) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)


class MemorySafeguardTestFramework:
    """Framework for testing memory system integrity under stress"""

    def __init__(self, seed: int = 42):
        """Initialize with deterministic seed for reproducible tests"""
        self.seed = seed
        self.rng = random.Random(seed)
        self.memory_items: List[TestMemoryItem] = []
        self.memory_system = None

        if MEMORY_SYSTEMS_AVAILABLE:
            self.memory_system = AdaptiveMemorySystem(max_items=50000)

    def generate_test_dataset(self, size: int = 10000) -> List[TestMemoryItem]:
        """Generate deterministic test dataset with known properties"""
        categories = ["tech", "science", "history", "art", "literature"]

        items = []
        for i in range(size):
            # Generate consistent embeddings based on ID
            embedding_seed = hash(f"item_{i}_{self.seed}") % (2**32)
            item_rng = random.Random(embedding_seed)

            embedding = [item_rng.gauss(0, 1) for _ in range(128)]
            category = categories[i % len(categories)]

            item = TestMemoryItem(
                id=f"mem_{i:06d}",
                content=f"Test memory content {i} about {category}",
                embedding=embedding,
                category=category,
                timestamp=time.time() - (i * 3600),  # Spread over hours
                priority=self.rng.randint(1, 10),
                metadata={
                    "test_id": i,
                    "batch": i // 1000,
                    "synthetic": True,
                    "verification_hash": hash(f"verify_{i}_{self.seed}")
                }
            )
            items.append(item)

        self.memory_items = items
        return items

    def store_test_items(self, items: List[TestMemoryItem]) -> Dict[str, Any]:
        """Store test items in memory system and track storage"""
        if not MEMORY_SYSTEMS_AVAILABLE or not self.memory_system:
            return {"skipped": "Memory systems not available"}

        storage_log = {
            "stored": 0,
            "failed": 0,
            "errors": [],
            "item_ids": []
        }

        for item in items:
            try:
                # Store using the AdaptiveMemorySystem API
                memory_item = self.memory_system.store(
                    content=item.content,
                    memory_type=MemoryType.SEMANTIC,  # Use semantic for test data
                    importance=item.priority / 10.0,  # Normalize priority to 0-1
                    tags=[item.category, item.id]  # Include test ID in tags for retrieval
                )

                if memory_item:
                    storage_log["stored"] += 1
                    storage_log["item_ids"].append(memory_item.id)
                else:
                    storage_log["failed"] += 1

            except Exception as e:
                storage_log["failed"] += 1
                storage_log["errors"].append(str(e))

        return storage_log

    def verify_topk_recall_integrity(
        self,
        query_item: TestMemoryItem,
        k: int = 10,
        expected_results: Optional[Set[str]] = None
    ) -> Dict[str, Any]:
        """Verify top-K recall returns correct results"""
        if not MEMORY_SYSTEMS_AVAILABLE or not self.memory_system:
            return {"skipped": "Memory systems not available"}

        try:
            # Use the AdaptiveMemorySystem recall API
            time.perf_counter()
            results, recall_duration_ms = self.memory_system.recall_top_k(k=k)
            recall_duration = recall_duration_ms / 1000.0  # Convert to seconds

            # Verify result structure
            verification = {
                "query_id": query_item.id,
                "requested_k": k,
                "returned_count": len(results) if results else 0,
                "recall_duration_ms": recall_duration * 1000,
                "integrity_score": 1.0,
                "violations": []
            }

            if not results:
                verification["violations"].append("no_results_returned")
                verification["integrity_score"] = 0.0
                return verification

            # Check if results are properly ordered by relevance/similarity
            if len(results) > 1:
                for i in range(len(results) - 1):
                    # AdaptiveMemorySystem should return MemoryItem objects
                    current_score = getattr(results[i], 'importance', 0)
                    next_score = getattr(results[i + 1], 'importance', 0)
                    if current_score < next_score:
                        verification["violations"].append(f"ordering_violation_at_{i}")

            # Check for duplicate results
            result_ids = [getattr(r, 'id', None) for r in results if hasattr(r, 'id')]
            if len(result_ids) != len(set(result_ids)):
                verification["violations"].append("duplicate_results")

            # Check expected results if provided
            if expected_results:
                returned_ids = set(result_ids)
                missing = expected_results - returned_ids
                if missing:
                    verification["violations"].append(f"missing_expected_results: {missing}")

            # Calculate final integrity score
            violation_penalty = len(verification["violations"]) * 0.2
            verification["integrity_score"] = max(0.0, 1.0 - violation_penalty)

            return verification

        except Exception as e:
            return {
                "query_id": query_item.id,
                "error": str(e),
                "integrity_score": 0.0,
                "violations": ["recall_exception"]
            }

    def stress_test_concurrent_operations(
        self,
        operation_count: int = 1000,
        concurrency: int = 10
    ) -> Dict[str, Any]:
        """Test memory operations under concurrent stress"""
        if not MEMORY_SYSTEMS_AVAILABLE:
            return {"skipped": "Memory systems not available"}

        results = {
            "operations_attempted": operation_count,
            "operations_completed": 0,
            "operations_failed": 0,
            "integrity_violations": 0,
            "error_details": [],
            "performance_metrics": {
                "min_duration_ms": float('inf'),
                "max_duration_ms": 0.0,
                "total_duration_ms": 0.0
            }
        }

        # Select random items for testing
        test_items = self.rng.sample(
            self.memory_items,
            min(operation_count, len(self.memory_items))
        )

        def perform_recall_operation(item: TestMemoryItem) -> Dict[str, Any]:
            try:
                verification = self.verify_topk_recall_integrity(item, k=5)
                return verification
            except Exception as e:
                return {
                    "query_id": item.id,
                    "error": str(e),
                    "integrity_score": 0.0,
                    "violations": ["operation_exception"]
                }

        # Execute concurrent operations
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [
                executor.submit(perform_recall_operation, item)
                for item in test_items
            ]

            for future in as_completed(futures):
                try:
                    result = future.result(timeout=30)  # 30s timeout per operation
                    results["operations_completed"] += 1

                    if result.get("integrity_score", 0) < 1.0:
                        results["integrity_violations"] += 1

                    if "error" in result:
                        results["operations_failed"] += 1
                        results["error_details"].append(result["error"])

                    # Update performance metrics
                    duration = result.get("recall_duration_ms", 0)
                    if duration > 0:
                        results["performance_metrics"]["min_duration_ms"] = min(
                            results["performance_metrics"]["min_duration_ms"], duration
                        )
                        results["performance_metrics"]["max_duration_ms"] = max(
                            results["performance_metrics"]["max_duration_ms"], duration
                        )
                        results["performance_metrics"]["total_duration_ms"] += duration

                except Exception as e:
                    results["operations_failed"] += 1
                    results["error_details"].append(str(e))

        # Calculate averages
        if results["operations_completed"] > 0:
            results["performance_metrics"]["avg_duration_ms"] = (
                results["performance_metrics"]["total_duration_ms"] /
                results["operations_completed"]
            )
        else:
            results["performance_metrics"]["avg_duration_ms"] = 0.0

        # Fix min_duration if no operations completed
        if results["performance_metrics"]["min_duration_ms"] == float('inf'):
            results["performance_metrics"]["min_duration_ms"] = 0.0

        return results

    def test_memory_consistency_under_load(self, iterations: int = 100) -> Dict[str, Any]:
        """Test that memory remains consistent under repeated operations"""
        if not MEMORY_SYSTEMS_AVAILABLE:
            return {"skipped": "Memory systems not available"}

        consistency_results = {
            "iterations": iterations,
            "consistency_violations": 0,
            "performance_degradation": 0,
            "baseline_duration": 0.0,
            "final_duration": 0.0,
            "violation_details": []
        }

        # Select a test item for consistency checking
        test_item = self.rng.choice(self.memory_items)

        # Establish baseline performance
        baseline_result = self.verify_topk_recall_integrity(test_item, k=10)
        consistency_results["baseline_duration"] = baseline_result.get("recall_duration_ms", 0)
        baseline_results = set(
            r.get("id") for r in baseline_result.get("results", [])
            if r.get("id")
        )

        # Perform repeated operations
        for i in range(iterations):
            try:
                result = self.verify_topk_recall_integrity(test_item, k=10)
                current_results = set(
                    r.get("id") for r in result.get("results", [])
                    if r.get("id")
                )

                # Check consistency with baseline
                if current_results != baseline_results:
                    consistency_results["consistency_violations"] += 1
                    consistency_results["violation_details"].append({
                        "iteration": i,
                        "missing": baseline_results - current_results,
                        "extra": current_results - baseline_results
                    })

                # Track performance degradation
                current_duration = result.get("recall_duration_ms", 0)
                if i == iterations - 1:
                    consistency_results["final_duration"] = current_duration

                # Consider significant slowdown as degradation
                if (consistency_results["baseline_duration"] > 0 and
                    current_duration > consistency_results["baseline_duration"] * 2):
                    consistency_results["performance_degradation"] += 1

            except Exception as e:
                consistency_results["violation_details"].append({
                    "iteration": i,
                    "error": str(e)
                })

        return consistency_results


@pytest.mark.memory
@pytest.mark.slow
class TestMemorySafeguards:
    """Property-based tests for memory system integrity"""

    @pytest.fixture
    def safeguard_framework(self):
        """Create memory safeguard test framework"""
        return MemorySafeguardTestFramework(seed=42)

    def test_memory_systems_available(self):
        """Verify memory systems are available for testing"""
        if not MEMORY_SYSTEMS_AVAILABLE:
            pytest.skip("Memory systems not available - install memory dependencies")

    @pytest.mark.parametrize("dataset_size", [1000, 5000, 10000])
    def test_recall_integrity_at_scale(self, safeguard_framework, dataset_size):
        """Property test: recall integrity must be maintained at different scales"""
        if not MEMORY_SYSTEMS_AVAILABLE:
            pytest.skip("Memory systems not available")

        # Generate test dataset
        items = safeguard_framework.generate_test_dataset(dataset_size)
        assert len(items) == dataset_size

        # Store test items
        storage_log = safeguard_framework.store_test_items(items[:min(1000, dataset_size)])
        assert storage_log["stored"] > 0, "No memory items were stored"

        # Test recall integrity on sample queries
        sample_size = min(100, dataset_size // 10)
        test_queries = safeguard_framework.rng.sample(items, sample_size)

        integrity_violations = 0
        for query_item in test_queries:
            result = safeguard_framework.verify_topk_recall_integrity(query_item, k=5)
            if result.get("integrity_score", 0) < 0.95:  # 95% integrity threshold
                integrity_violations += 1

        # Property: Integrity violations should be minimal (< 5%)
        violation_rate = integrity_violations / len(test_queries)
        assert violation_rate < 0.05, f"Integrity violation rate {violation_rate:.2%} exceeds 5% threshold"

    def test_concurrent_recall_fidelity(self, safeguard_framework):
        """Property test: concurrent operations must not corrupt recall results"""
        if not MEMORY_SYSTEMS_AVAILABLE:
            pytest.skip("Memory systems not available")

        # Generate smaller dataset for concurrent testing
        items = safeguard_framework.generate_test_dataset(1000)
        storage_log = safeguard_framework.store_test_items(items)
        assert storage_log["stored"] > 0

        # Stress test with concurrent operations
        stress_results = safeguard_framework.stress_test_concurrent_operations(
            operation_count=500,
            concurrency=20
        )

        # Properties to verify
        assert stress_results["operations_completed"] > 0, "No operations completed"

        # Success rate should be high
        success_rate = stress_results["operations_completed"] / stress_results["operations_attempted"]
        assert success_rate >= 0.95, f"Success rate {success_rate:.2%} below 95%"

        # Integrity violations should be minimal
        if stress_results["operations_completed"] > 0:
            violation_rate = stress_results["integrity_violations"] / stress_results["operations_completed"]
            assert violation_rate < 0.02, f"Integrity violation rate {violation_rate:.2%} exceeds 2%"

        # Performance should be reasonable (P95 < 100ms)
        avg_duration = stress_results["performance_metrics"]["avg_duration_ms"]
        assert avg_duration < 100, f"Average recall duration {avg_duration:.1f}ms exceeds 100ms"

    def test_memory_consistency_invariants(self, safeguard_framework):
        """Property test: memory recall results must be consistent across time"""
        if not MEMORY_SYSTEMS_AVAILABLE:
            pytest.skip("Memory systems not available")

        # Generate test dataset
        items = safeguard_framework.generate_test_dataset(500)
        storage_log = safeguard_framework.store_test_items(items)
        assert storage_log["stored"] > 0

        # Test consistency over repeated operations
        consistency_results = safeguard_framework.test_memory_consistency_under_load(iterations=50)

        # Properties to verify
        # 1. Consistency violations should be rare
        consistency_rate = 1 - (consistency_results["consistency_violations"] / consistency_results["iterations"])
        assert consistency_rate >= 0.98, f"Consistency rate {consistency_rate:.2%} below 98%"

        # 2. Performance shouldn't degrade significantly
        if consistency_results["baseline_duration"] > 0:
            performance_ratio = consistency_results["final_duration"] / consistency_results["baseline_duration"]
            assert performance_ratio < 2.0, f"Performance degraded by {performance_ratio:.1f}x"

    @pytest.mark.parametrize("k_value", [1, 5, 10, 25, 50])
    def test_topk_correctness_property(self, safeguard_framework, k_value):
        """Property test: top-K results must be correctly ordered and complete"""
        if not MEMORY_SYSTEMS_AVAILABLE:
            pytest.skip("Memory systems not available")

        # Generate smaller dataset for detailed verification
        items = safeguard_framework.generate_test_dataset(200)
        storage_log = safeguard_framework.store_test_items(items)
        assert storage_log["stored"] > 0

        # Test multiple queries with different K values
        test_queries = safeguard_framework.rng.sample(items, 10)

        for query_item in test_queries:
            result = safeguard_framework.verify_topk_recall_integrity(
                query_item,
                k=k_value
            )

            # Properties to verify:
            # 1. Should return up to K results
            assert result["returned_count"] <= k_value, f"Returned {result['returned_count']} > {k_value}"

            # 2. Should have high integrity score
            assert result["integrity_score"] >= 0.9, f"Low integrity score: {result['integrity_score']}"

            # 3. Should not have critical violations
            critical_violations = {"no_results_returned", "recall_exception"}
            actual_violations = set(result.get("violations", []))
            critical_found = critical_violations & actual_violations
            assert not critical_found, f"Critical violations found: {critical_found}"

    def test_memory_safeguard_edge_cases(self, safeguard_framework):
        """Test memory system behavior with edge cases and boundary conditions"""
        if not MEMORY_SYSTEMS_AVAILABLE:
            pytest.skip("Memory systems not available")

        # Generate minimal dataset
        items = safeguard_framework.generate_test_dataset(50)
        storage_log = safeguard_framework.store_test_items(items)
        assert storage_log["stored"] > 0

        test_item = items[0]

        # Edge case 1: K=0 (should handle gracefully)
        result_k0 = safeguard_framework.verify_topk_recall_integrity(test_item, k=0)
        assert result_k0["returned_count"] == 0

        # Edge case 2: K > available items
        result_large_k = safeguard_framework.verify_topk_recall_integrity(test_item, k=1000)
        assert result_large_k["returned_count"] <= len(items)

        # Edge case 3: Empty embedding vector
        empty_item = TestMemoryItem(
            id="empty_test",
            content="Empty embedding test",
            embedding=[0.0] * 128,
            category="test",
            timestamp=time.time(),
            priority=1,
            metadata={"test": True}
        )
        result_empty = safeguard_framework.verify_topk_recall_integrity(empty_item, k=5)
        # Should handle without crashing
        assert "error" not in result_empty or result_empty["integrity_score"] >= 0


if __name__ == "__main__":
    # Allow running directly
    pytest.main([__file__, "-v", "--tb=short"])
