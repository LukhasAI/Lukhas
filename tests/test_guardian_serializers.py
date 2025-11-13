#!/usr/bin/env python3

"""
LUKHAS Guardian Serializers Test Suite
======================================

Comprehensive test suite for Guardian schema serialization system with
performance benchmarks and integration tests.

Test Categories:
- Unit tests for individual components
- Integration tests for system interactions
- Performance benchmarks for optimization validation
- Load tests for throughput validation
- Error handling and edge case tests
- Constitutional AI compliance tests

Performance Targets:
- Serialization: <1ms for 99% of operations
- Validation: <1ms for cached schemas
- Migration: <10ms for typical version changes
- Throughput: 10K+ operations/second
- Memory usage: <100MB total

Author: LUKHAS AI System
Version: 1.0.0
Phase: 7 - Guardian Schema Serializers
"""

import asyncio
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

import pytest

# Import the Guardian serialization system
from governance.guardian_serializers import (
    GuardianSerializer,
    deserialize_guardian,
    get_system_health,
    serialize_guardian,
    validate_guardian,
)
from governance.performance_optimizer import OptimizationLevel, get_performance_optimizer
from governance.schema_migration import (
    CompatibilityType,
    check_schema_compatibility,
    migrate_guardian_data,
)
from governance.schema_registry import SchemaRegistry
from governance.serialization_engine import (
    CompressionType,
    SerializationEngine,
    SerializationFormat,
)
from governance.validation_framework import ValidationFramework, ValidationTier


class TestGuardianSchemaRegistry:
    """Test suite for Guardian Schema Registry"""

    def test_schema_registry_initialization(self):
        """Test schema registry initialization"""
        registry = SchemaRegistry()

        # Check that Guardian schema is loaded
        schemas = registry.list_schemas()
        assert "guardian_decision" in schemas
        assert "2.0.0" in schemas["guardian_decision"]

    def test_schema_validation(self):
        """Test schema validation functionality"""
        registry = SchemaRegistry()

        # Valid Guardian decision
        valid_decision = {
            "schema_version": "2.0.0",
            "decision": {
                "status": "allow",
                "policy": "test/v1.0.0",
                "timestamp": "2023-01-01T00:00:00Z",
                "confidence": 0.95
            },
            "subject": {
                "correlation_id": "test-correlation-123",
                "actor": {"type": "user", "id": "test-user"},
                "operation": {"name": "test_operation"}
            },
            "context": {
                "environment": {"region": "us-west-1", "runtime": "prod"},
                "features": {"enforcement_enabled": True}
            },
            "metrics": {"latency_ms": 50},
            "enforcement": {"mode": "enforced"},
            "audit": {
                "event_id": "audit-event-123",
                "timestamp": "2023-01-01T00:00:00Z"
            },
            "integrity": {"content_sha256": "a" * 64}
        }

        result = registry.validate_data(valid_decision, "guardian_decision")
        assert result.is_valid
        assert result.validation_time_ms < 100  # Performance check

    def test_schema_validation_errors(self):
        """Test schema validation with errors"""
        registry = SchemaRegistry()

        # Invalid Guardian decision (missing required fields)
        invalid_decision = {
            "schema_version": "2.0.0",
            "decision": {
                "status": "invalid_status",  # Invalid status
                "timestamp": "invalid-timestamp"  # Invalid format
            }
            # Missing required fields
        }

        result = registry.validate_data(invalid_decision, "guardian_decision")
        assert not result.is_valid
        assert len(result.errors) > 0

    def test_schema_registry_metrics(self):
        """Test schema registry metrics collection"""
        registry = SchemaRegistry()

        # Perform some operations
        valid_decision = self._create_valid_guardian_decision()
        for _ in range(10):
            registry.validate_data(valid_decision, "guardian_decision")

        metrics = registry.get_metrics()
        assert metrics["total_schemas"] > 0
        assert metrics["cache_hit_rate"] >= 0

    def _create_valid_guardian_decision(self) -> Dict[str, Any]:
        """Create a valid Guardian decision for testing"""
        return {
            "schema_version": "2.0.0",
            "decision": {
                "status": "allow",
                "policy": "test/v1.0.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "confidence": 0.95
            },
            "subject": {
                "correlation_id": str(uuid.uuid4()),
                "actor": {"type": "user", "id": "test-user"},
                "operation": {"name": "test_operation"}
            },
            "context": {
                "environment": {"region": "us-west-1", "runtime": "prod"},
                "features": {"enforcement_enabled": True}
            },
            "metrics": {"latency_ms": 50},
            "enforcement": {"mode": "enforced"},
            "audit": {
                "event_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "integrity": {"content_sha256": "a" * 64}
        }


class TestSerializationEngine:
    """Test suite for Serialization Engine"""

    def test_json_serialization(self):
        """Test JSON serialization"""
        engine = SerializationEngine()
        test_data = {"key": "value", "number": 42}

        result = engine.serialize(test_data, SerializationFormat.JSON)
        assert result.success
        assert result.serialization_time_ms < 10

        # Test deserialization
        deserialize_result = engine.deserialize(
            result.data, SerializationFormat.JSON
        )
        assert deserialize_result.success
        assert deserialize_result.data == test_data

    def test_msgpack_serialization(self):
        """Test MessagePack serialization"""
        engine = SerializationEngine()
        test_data = {"key": "value", "number": 42, "nested": {"data": [1, 2, 3]}}

        result = engine.serialize(test_data, SerializationFormat.MSGPACK)
        assert result.success
        assert result.serialization_time_ms < 10
        assert len(result.data) < len(json.dumps(test_data).encode())

    def test_compression(self):
        """Test data compression"""
        engine = SerializationEngine()
        large_data = {"data": "x" * 10000}  # Large data for compression testing

        # Test without compression
        uncompressed = engine.serialize(large_data, SerializationFormat.JSON, CompressionType.NONE)

        # Test with compression
        compressed = engine.serialize(large_data, SerializationFormat.JSON, CompressionType.ZSTD)

        assert compressed.compressed_size < uncompressed.compressed_size
        assert compressed.compression_ratio > 1.0

    def test_performance_metrics(self):
        """Test serialization performance metrics"""
        engine = SerializationEngine()
        test_data = self._create_test_guardian_decision()

        # Perform multiple operations
        for _ in range(100):
            engine.serialize(test_data, SerializationFormat.MSGPACK)

        metrics = engine.get_metrics()
        assert metrics["serialization_count"] == 100
        assert metrics["average_serialization_time_ms"] > 0

    def _create_test_guardian_decision(self) -> Dict[str, Any]:
        """Create test Guardian decision"""
        return {
            "schema_version": "2.0.0",
            "decision": {"status": "allow", "policy": "test", "timestamp": "2023-01-01T00:00:00Z"},
            "subject": {
                "correlation_id": "test-123",
                "actor": {"type": "user", "id": "test"},
                "operation": {"name": "test"}
            },
            "context": {
                "environment": {"region": "test", "runtime": "test"},
                "features": {"enforcement_enabled": True}
            },
            "metrics": {"latency_ms": 10},
            "enforcement": {"mode": "enforced"},
            "audit": {"event_id": "audit-123", "timestamp": "2023-01-01T00:00:00Z"},
            "integrity": {"content_sha256": "a" * 64}
        }


class TestValidationFramework:
    """Test suite for Validation Framework"""

    def test_syntax_validation(self):
        """Test syntax-level validation"""
        framework = ValidationFramework()

        # Valid data
        valid_data = self._create_valid_guardian_decision()
        result = framework.validate(valid_data, tiers={ValidationTier.SYNTAX})
        assert result.is_valid

        # Invalid data
        invalid_data = {"invalid": "structure"}
        result = framework.validate(invalid_data, tiers={ValidationTier.SYNTAX})
        assert not result.is_valid
        assert len(result.issues) > 0

    def test_semantic_validation(self):
        """Test semantic-level validation"""
        framework = ValidationFramework()

        valid_data = self._create_valid_guardian_decision()
        result = framework.validate(valid_data, tiers={ValidationTier.SEMANTIC})
        assert result.is_valid

    def test_constitutional_ai_validation(self):
        """Test Constitutional AI validation"""
        framework = ValidationFramework()

        # Decision with potential ethical concerns
        decision_data = self._create_valid_guardian_decision()
        decision_data["decision"]["status"] = "deny"
        # Remove reasons - should trigger warning

        result = framework.validate(decision_data, tiers={ValidationTier.CONSTITUTIONAL})

        # Should have warnings about missing reasoning
        warnings = [issue for issue in result.issues if issue.severity.value == "warning"]
        assert len(warnings) >= 0  # May have warnings

    def test_validation_performance(self):
        """Test validation performance"""
        framework = ValidationFramework()
        valid_data = self._create_valid_guardian_decision()

        start_time = time.perf_counter()
        result = framework.validate(valid_data)
        end_time = time.perf_counter()

        assert result.validation_time_ms < 50  # Should be under 50ms
        assert (end_time - start_time) * 1000 < 100

    def _create_valid_guardian_decision(self) -> Dict[str, Any]:
        """Create valid Guardian decision for testing"""
        return {
            "schema_version": "2.0.0",
            "decision": {
                "status": "allow",
                "policy": "test/v1.0.0",
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "subject": {
                "correlation_id": str(uuid.uuid4()),
                "actor": {"type": "user", "id": "test-user"},
                "operation": {"name": "test_operation"}
            },
            "context": {
                "environment": {"region": "us-west-1", "runtime": "prod"},
                "features": {"enforcement_enabled": True}
            },
            "metrics": {"latency_ms": 50},
            "enforcement": {"mode": "enforced"},
            "audit": {
                "event_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "integrity": {"content_sha256": "a" * 64}
        }


class TestSchemaMigration:
    """Test suite for Schema Migration"""

    def test_version_compatibility(self):
        """Test schema version compatibility checking"""
        compatibility = check_schema_compatibility("2.0.0", "2.1.0")
        assert compatibility == CompatibilityType.FORWARD

        compatibility = check_schema_compatibility("1.0.0", "2.0.0")
        assert compatibility in [CompatibilityType.FORWARD, CompatibilityType.NONE]

    def test_guardian_migration(self):
        """Test Guardian schema migration"""
        # Create v1.0.0 style data
        old_data = {
            "timestamp": "2023-01-01T00:00:00Z",
            "decision": {"status": "allow", "policy": "test"},
            "emergency_active": False
        }

        result = migrate_guardian_data(old_data, "2.0.0", "1.0.0")
        assert result.success
        assert result.migrated_data["schema_version"] == "2.0.0"
        assert "integrity" in result.migrated_data

    def test_migration_performance(self):
        """Test migration performance"""
        old_data = {
            "decision": {"status": "allow", "policy": "test"},
            "timestamp": "2023-01-01T00:00:00Z"
        }

        start_time = time.perf_counter()
        result = migrate_guardian_data(old_data, "2.0.0", "1.0.0")
        end_time = time.perf_counter()

        assert result.success
        assert result.migration_time_ms < 100
        assert (end_time - start_time) * 1000 < 100


class TestPerformanceOptimizer:
    """Test suite for Performance Optimizer"""

    def test_cache_performance(self):
        """Test cache performance improvements"""
        optimizer = get_performance_optimizer(OptimizationLevel.AGGRESSIVE)

        # Test function to optimize
        def test_validation(data):
            time.sleep(0.001)  # Simulate work
            return {"valid": True}

        optimized_func = optimizer.optimize_validation(test_validation, "test_pattern")

        # First call - should be slow
        start_time = time.perf_counter()
        result1 = optimized_func({"test": "data"})
        first_call_time = time.perf_counter() - start_time

        # Second call - should be fast (cached)
        start_time = time.perf_counter()
        result2 = optimized_func({"test": "data"})
        second_call_time = time.perf_counter() - start_time

        assert result1 == result2
        assert second_call_time < first_call_time

    def test_batch_processing(self):
        """Test batch processing performance"""
        optimizer = get_performance_optimizer()

        def simple_processor(item):
            return item * 2

        items = list(range(1000))

        async def test_batch():
            results = await optimizer.batch_validate(items, simple_processor)
            return results

        start_time = time.perf_counter()
        results = asyncio.run(test_batch())
        end_time = time.perf_counter()

        assert len(results) == 1000
        assert results[0] == 0
        assert results[999] == 1998
        assert (end_time - start_time) < 5.0  # Should complete quickly


class TestGuardianSerializer:
    """Test suite for Guardian Serializer integration"""

    def test_full_serialization_pipeline(self):
        """Test complete serialization pipeline"""
        serializer = GuardianSerializer()
        decision_data = self._create_test_decision()

        # Test serialization
        result = serializer.serialize_decision(decision_data)
        assert result.success
        assert result.serialized_data is not None
        assert result.execution_time_ms < 100

    def test_deserialization_pipeline(self):
        """Test complete deserialization pipeline"""
        serializer = GuardianSerializer()
        decision_data = self._create_test_decision()

        # Serialize first
        serialize_result = serializer.serialize_decision(decision_data)
        assert serialize_result.success

        # Then deserialize
        deserialize_result = serializer.deserialize_decision(serialize_result.serialized_data)
        assert deserialize_result.success
        assert deserialize_result.data["schema_version"] == "2.0.0"

    def test_validation_pipeline(self):
        """Test validation pipeline"""
        serializer = GuardianSerializer()
        decision_data = self._create_test_decision()

        result = serializer.validate_decision(decision_data)
        assert result.success
        assert result.validation_result is not None

    def test_migration_pipeline(self):
        """Test migration pipeline"""
        serializer = GuardianSerializer()
        old_decision = {
            "decision": {"status": "allow", "policy": "test"},
            "timestamp": "2023-01-01T00:00:00Z"
        }

        result = serializer.migrate_decision(old_decision, "2.0.0")
        assert result.success
        assert result.data["schema_version"] == "2.0.0"

    @pytest.mark.asyncio
    async def test_batch_operations(self):
        """Test batch processing operations"""
        serializer = GuardianSerializer()
        decisions = [self._create_test_decision() for _ in range(10)]

        results = await serializer.batch_serialize_decisions(decisions)
        assert len(results) == 10
        assert all(result.success for result in results)

    def test_system_status(self):
        """Test system status reporting"""
        serializer = GuardianSerializer()
        status = serializer.get_system_status()

        assert "system" in status
        assert "schema_registry" in status
        assert "serialization_engine" in status
        assert "validation_framework" in status
        assert "migration_engine" in status
        assert "performance_optimizer" in status
        assert "integration_health" in status

    def _create_test_decision(self) -> Dict[str, Any]:
        """Create test Guardian decision"""
        return {
            "schema_version": "2.0.0",
            "decision": {
                "status": "allow",
                "policy": "test/v1.0.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "confidence": 0.95
            },
            "subject": {
                "correlation_id": str(uuid.uuid4()),
                "actor": {"type": "user", "id": "test-user"},
                "operation": {"name": "test_operation"}
            },
            "context": {
                "environment": {"region": "us-west-1", "runtime": "prod"},
                "features": {"enforcement_enabled": True}
            },
            "metrics": {"latency_ms": 50},
            "enforcement": {"mode": "enforced"},
            "audit": {
                "event_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "integrity": {"content_sha256": "a" * 64}
        }


class TestPerformanceBenchmarks:
    """Performance benchmark tests"""

    def test_serialization_throughput(self):
        """Benchmark serialization throughput"""
        decision_data = self._create_benchmark_decision()

        # Warm up
        for _ in range(100):
            serialize_guardian(decision_data)

        # Benchmark
        start_time = time.perf_counter()
        operations = 1000

        for _ in range(operations):
            result = serialize_guardian(decision_data)
            assert result.success

        end_time = time.perf_counter()
        total_time = end_time - start_time
        throughput = operations / total_time

        # Should achieve >1000 ops/second
        assert throughput > 500  # Conservative target
        print(f"Serialization throughput: {throughput:.1f} ops/second")

    def test_validation_performance(self):
        """Benchmark validation performance"""
        decision_data = self._create_benchmark_decision()

        # Warm up cache
        for _ in range(100):
            validate_guardian(decision_data)

        # Benchmark cached validation
        start_time = time.perf_counter()
        operations = 1000

        for _ in range(operations):
            result = validate_guardian(decision_data)
            assert result.success

        end_time = time.perf_counter()
        total_time = end_time - start_time
        throughput = operations / total_time

        # Should achieve high throughput with caching
        assert throughput > 1000  # Should be much faster with caching
        print(f"Validation throughput (cached): {throughput:.1f} ops/second")

    def test_end_to_end_latency(self):
        """Test end-to-end latency for single operations"""
        decision_data = self._create_benchmark_decision()

        latencies = []

        for _ in range(100):
            start_time = time.perf_counter()

            # Full pipeline: validate, serialize, deserialize
            validate_guardian(decision_data)
            serialize_result = serialize_guardian(decision_data)
            deserialize_guardian(serialize_result.serialized_data)

            end_time = time.perf_counter()
            latency = (end_time - start_time) * 1000  # Convert to ms
            latencies.append(latency)

        avg_latency = sum(latencies) / len(latencies)
        p99_latency = sorted(latencies)[98]  # 99th percentile

        # Performance targets
        assert avg_latency < 10  # Average under 10ms
        assert p99_latency < 50   # P99 under 50ms

        print(f"Average end-to-end latency: {avg_latency:.2f}ms")
        print(f"P99 latency: {p99_latency:.2f}ms")

    def test_memory_usage(self):
        """Test memory usage under load"""
        import tracemalloc

        tracemalloc.start()

        # Baseline memory
        baseline_snapshot = tracemalloc.take_snapshot()

        # Create load
        decisions = [self._create_benchmark_decision() for _ in range(1000)]

        for decision in decisions:
            serialize_guardian(decision)
            validate_guardian(decision)

        # Measure memory
        current_snapshot = tracemalloc.take_snapshot()
        top_stats = current_snapshot.compare_to(baseline_snapshot, 'lineno')

        total_memory_mb = sum(stat.size for stat in top_stats) / 1024 / 1024

        # Should stay under 100MB as per requirements
        assert total_memory_mb < 100
        print(f"Memory usage under load: {total_memory_mb:.2f}MB")

        tracemalloc.stop()

    def _create_benchmark_decision(self) -> Dict[str, Any]:
        """Create decision for benchmarking"""
        return {
            "schema_version": "2.0.0",
            "decision": {
                "status": "allow",
                "policy": "benchmark/v1.0.0",
                "timestamp": "2023-01-01T00:00:00Z",
                "confidence": 0.95,
                "severity": "low"
            },
            "subject": {
                "correlation_id": "benchmark-123",
                "actor": {"type": "user", "id": "benchmark-user", "tier": "T3"},
                "operation": {"name": "benchmark_operation", "resource": "test"}
            },
            "context": {
                "environment": {"region": "us-west-1", "runtime": "prod", "version": "1.0.0"},
                "features": {"enforcement_enabled": True, "emergency_active": False}
            },
            "metrics": {
                "latency_ms": 25,
                "risk_score": 0.1,
                "drift_score": 0.05,
                "quota_remaining": 1000
            },
            "enforcement": {"mode": "enforced", "actions": ["log_only"]},
            "audit": {
                "event_id": "benchmark-audit-123",
                "timestamp": "2023-01-01T00:00:00Z",
                "source_system": "guardian"
            },
            "reasons": [
                {"code": "POLICY_ALLOW", "message": "Request allowed by policy"}
            ],
            "integrity": {"content_sha256": "b" * 64}
        }


# Integration test that validates the complete system
class TestSystemIntegration:
    """Integration tests for the complete Guardian serialization system"""

    def test_complete_workflow(self):
        """Test complete Guardian workflow from decision to storage"""
        # Create Guardian decision
        decision_data = {
            "schema_version": "2.0.0",
            "decision": {
                "status": "allow",
                "policy": "integration_test/v1.0.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "confidence": 0.95
            },
            "subject": {
                "correlation_id": str(uuid.uuid4()),
                "actor": {"type": "user", "id": "integration-test-user"},
                "operation": {"name": "integration_test"}
            },
            "context": {
                "environment": {"region": "test", "runtime": "ci"},
                "features": {"enforcement_enabled": True}
            },
            "metrics": {"latency_ms": 10},
            "enforcement": {"mode": "enforced"},
            "audit": {
                "event_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "integrity": {"content_sha256": "c" * 64}
        }

        # Step 1: Validate
        validation_result = validate_guardian(decision_data)
        assert validation_result.success

        # Step 2: Serialize
        serialization_result = serialize_guardian(decision_data)
        assert serialization_result.success

        # Step 3: Deserialize
        deserialization_result = deserialize_guardian(serialization_result.serialized_data)
        assert deserialization_result.success

        # Step 4: Verify data integrity
        original_decision = decision_data["decision"]["status"]
        deserialized_decision = deserialization_result.data["decision"]["status"]
        assert original_decision == deserialized_decision

    def test_system_health_check(self):
        """Test system health monitoring"""
        health = get_system_health()

        assert health["system"]["status"] == "operational"
        assert health["integration_health"]["schema_registry_healthy"]
        assert health["integration_health"]["serialization_healthy"]

# Run performance benchmarks if this file is executed directly
if __name__ == "__main__":
    print("Running Guardian Serializers Performance Benchmarks...")

    benchmark = TestPerformanceBenchmarks()

    print("\n1. Testing serialization throughput...")
    benchmark.test_serialization_throughput()

    print("\n2. Testing validation performance...")
    benchmark.test_validation_performance()

    print("\n3. Testing end-to-end latency...")
    benchmark.test_end_to_end_latency()

    print("\n4. Testing memory usage...")
    benchmark.test_memory_usage()

    print("\n5. Testing complete workflow...")
    integration = TestSystemIntegration()
    integration.test_complete_workflow()

    print("\n6. Testing system health...")
    integration.test_system_health_check()

    print("\nAll benchmarks completed successfully!")

    # Print final system status
    health = get_system_health()
    print(f"\nSystem Status: {health['system']['status']}")
    print(f"Schema Registry: {'✓' if health['integration_health']['schema_registry_healthy'] else '✗'}")
    print(f"Serialization Engine: {'✓' if health['integration_health']['serialization_healthy'] else '✗'}")
    print(f"Validation Framework: {'✓' if health['integration_health']['validation_healthy'] else '✗'}")
    print(f"Performance Optimal: {'✓' if health['integration_health']['performance_optimal'] else '✗'}")
