#!/usr/bin/env python3
"""
tests/test_memory_sync.py

Unit tests for Phase 5 memory synchronization implementation.
Tests synchronization safety: fanout/depth/budget trips, idempotency.
"""
import os
import time
import pytest
from uuid import uuid4
from datetime import datetime
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor, as_completed

from lukhas.memory.sync import (
    MemorySynchronizer, SyncResult,
    SyncBudgetConfig, create_memory_synchronizer
)


class TestMemorySynchronizer:
    """Test suite for memory synchronizer functionality."""

    def setup_method(self):
        """Set up test environment."""
        os.environ["LUKHAS_LANE"] = "experimental"
        os.environ["PYTHONHASHSEED"] = "0"
        os.environ["TZ"] = "UTC"

    def test_synchronizer_initialization(self):
        """Test memory synchronizer initializes with correct configuration."""
        # Test default initialization
        syncer = MemorySynchronizer()
        assert syncer.lane == "experimental"
        assert syncer.config.max_fanout == 12
        assert syncer.config.max_fanin == 8

        # Test explicit lane
        syncer = MemorySynchronizer(lane="prod")
        assert syncer.lane == "prod"
        assert syncer.config.max_fanout == 4
        assert syncer.config.max_fanin == 2

    def test_simple_sync_operation(self):
        """Test basic successful synchronization operation."""
        syncer = MemorySynchronizer(lane="experimental")

        fold_data = {
            "fold_id": "test_fold_001",
            "content": {"memories": ["item1", "item2"]},
            "metadata": {"timestamp": datetime.utcnow().isoformat()}
        }

        result = syncer.sync_fold(
            source_lane="experimental",
            target_lane="experimental",
            fold_data=fold_data,
            fold_id="test_fold_001"
        )

        assert result.result == SyncResult.SUCCESS
        assert result.source_lane == "experimental"
        assert result.target_lane == "experimental"
        assert result.fold_id == "test_fold_001"
        assert result.error_message is None
        assert result.duration_ms > 0

    def test_cross_lane_sync_policy(self):
        """Test cross-lane synchronization policy enforcement."""
        exp_syncer = MemorySynchronizer(lane="experimental")
        prod_syncer = MemorySynchronizer(lane="prod")

        fold_data = {"fold_id": "test", "content": {}}

        # Experimental allows cross-lane by default
        result = exp_syncer.sync_fold(
            source_lane="candidate",
            target_lane="experimental",
            fold_data=fold_data
        )
        assert result.result == SyncResult.SUCCESS

        # Production disallows cross-lane by default
        result = prod_syncer.sync_fold(
            source_lane="candidate",
            target_lane="prod",
            fold_data=fold_data
        )
        assert result.result == SyncResult.ERROR_LANE_POLICY
        assert "policy" in result.error_message.lower()

    def test_fanout_budget_enforcement(self):
        """Test fanout budget limit enforcement."""
        # Create syncer with very low fanout limit
        custom_config = {
            "experimental": SyncBudgetConfig(
                max_fanout=2,  # Very low limit
                max_fanin=10,
                ops_budget_per_tick=100
            )
        }
        syncer = MemorySynchronizer(lane="experimental", custom_config=custom_config)

        fold_data = {"fold_id": "test", "content": {}}

        # Simulate concurrent operations by manually reserving resources
        from uuid import uuid4

        # Reserve resources for two concurrent operations
        op1_id = uuid4()
        op2_id = uuid4()
        syncer._reserve_resources(op1_id, "experimental", "candidate", 1, 0, 0)
        syncer._reserve_resources(op2_id, "experimental", "other_lane", 1, 0, 0)

        # Third operation should fail due to fanout limit being exhausted
        result = syncer.sync_fold(
            source_lane="experimental",
            target_lane="third_lane",
            fold_data=fold_data,
            fold_id="test_overflow"
        )
        assert result.result == SyncResult.ERROR_FANOUT
        assert "fanout" in result.error_message.lower()

        # Clean up reserved resources
        syncer._release_resources(op1_id, "experimental", "candidate", 1, 0)
        syncer._release_resources(op2_id, "experimental", "other_lane", 1, 0)

    def test_fanin_budget_enforcement(self):
        """Test fanin budget limit enforcement."""
        # Create syncer with very low fanin limit
        custom_config = {
            "experimental": SyncBudgetConfig(
                max_fanout=10,
                max_fanin=1,  # Very low limit
                ops_budget_per_tick=100
            )
        }
        syncer = MemorySynchronizer(lane="experimental", custom_config=custom_config)

        fold_data = {"fold_id": "test", "content": {}}

        # Simulate concurrent operation by manually reserving fanin resources
        from uuid import uuid4

        # Reserve resources for one concurrent fanin operation
        op1_id = uuid4()
        syncer._reserve_resources(op1_id, "candidate", "experimental", 0, 1, 0)

        # Second operation should fail due to fanin limit being exhausted
        result = syncer.sync_fold(
            source_lane="other_candidate",
            target_lane="experimental",
            fold_data=fold_data,
            fold_id="test_overflow"
        )
        assert result.result == SyncResult.ERROR_FANIN
        assert "fanin" in result.error_message.lower()

        # Clean up reserved resources
        syncer._release_resources(op1_id, "candidate", "experimental", 0, 1)

    def test_depth_limit_enforcement(self):
        """Test operation depth limit enforcement."""
        # Create syncer with very low depth limit
        custom_config = {
            "experimental": SyncBudgetConfig(
                max_depth=1,  # Very low limit
                ops_budget_per_tick=100
            )
        }
        syncer = MemorySynchronizer(lane="experimental", custom_config=custom_config)

        fold_data = {"fold_id": "test", "content": {}}

        # Create parent operation to establish depth
        parent_op_id = uuid4()
        syncer._operation_depth[parent_op_id] = 1

        # Child operation should fail due to depth limit
        result = syncer.sync_fold(
            source_lane="experimental",
            target_lane="experimental",
            fold_data=fold_data,
            fold_id="test_deep",
            parent_op_id=parent_op_id
        )
        assert result.result == SyncResult.ERROR_DEPTH
        assert "depth" in result.error_message.lower()

    def test_operation_budget_enforcement(self):
        """Test per-tick operation budget enforcement."""
        # Create syncer with very low operation budget
        custom_config = {
            "experimental": SyncBudgetConfig(
                ops_budget_per_tick=2,  # Very low limit
                budget_window_seconds=60,  # Long window
                data_budget_per_tick_mb=100  # High data limit
            )
        }
        syncer = MemorySynchronizer(lane="experimental", custom_config=custom_config)

        fold_data = {"fold_id": "test", "content": {}}

        # First two operations should succeed
        for i in range(2):
            result = syncer.sync_fold(
                source_lane="experimental",
                target_lane="experimental",
                fold_data=fold_data,
                fold_id=f"test_{i}"
            )
            assert result.result == SyncResult.SUCCESS

        # Third operation should fail due to budget exhaustion
        result = syncer.sync_fold(
            source_lane="experimental",
            target_lane="experimental",
            fold_data=fold_data,
            fold_id="test_overflow"
        )
        assert result.result == SyncResult.ERROR_BUDGET
        assert "budget" in result.error_message.lower()

    def test_data_budget_enforcement(self):
        """Test data size budget enforcement."""
        # Create syncer with very low data budget
        custom_config = {
            "experimental": SyncBudgetConfig(
                ops_budget_per_tick=100,  # High ops limit
                data_budget_per_tick_mb=0.001,  # Very low data limit (1KB)
                budget_window_seconds=60
            )
        }
        syncer = MemorySynchronizer(lane="experimental", custom_config=custom_config)

        # Create large data payload
        large_data = {
            "fold_id": "test",
            "content": {"large_field": "x" * 5000}  # ~5KB of data
        }

        # Operation should fail due to data budget
        result = syncer.sync_fold(
            source_lane="experimental",
            target_lane="experimental",
            fold_data=large_data,
            fold_id="test_large"
        )
        assert result.result == SyncResult.ERROR_BUDGET
        assert "budget" in result.error_message.lower()

    def test_data_validation(self):
        """Test fold data validation."""
        syncer = MemorySynchronizer(lane="experimental")

        # Invalid data (not a dict)
        result = syncer.sync_fold(
            source_lane="experimental",
            target_lane="experimental",
            fold_data="invalid_data",  # Not a dict
            fold_id="test"
        )
        assert result.result == SyncResult.ERROR_DATA_VALIDATION

        # Missing required fields
        result = syncer.sync_fold(
            source_lane="experimental",
            target_lane="experimental",
            fold_data={},  # Missing fold_id or content
            fold_id="test"
        )
        assert result.result == SyncResult.ERROR_DATA_VALIDATION

    def test_resource_management(self):
        """Test resource reservation and release."""
        # Create syncer with small limits to test resource management
        custom_config = {
            "experimental": SyncBudgetConfig(
                max_fanout=2,
                max_fanin=2,
                ops_budget_per_tick=100
            )
        }
        syncer = MemorySynchronizer(lane="experimental", custom_config=custom_config)

        fold_data = {"fold_id": "test", "content": {}}

        # Start operations that will reserve resources
        results = []
        for i in range(2):
            # Simulate operations in progress by not completing them immediately
            result = syncer.sync_fold(
                source_lane="experimental",
                target_lane="candidate",
                fold_data=fold_data,
                fold_id=f"test_{i}"
            )
            results.append(result)

        # Both should succeed (resources available)
        assert all(r.result == SyncResult.SUCCESS for r in results)

        # Resources should have been released after completion
        stats = syncer.get_sync_stats()
        assert stats["current_fanout"] == 0  # Resources released
        assert stats["current_fanin"] == 0

    def test_sync_statistics(self):
        """Test synchronization statistics collection."""
        syncer = MemorySynchronizer(lane="experimental")

        fold_data = {"fold_id": "test", "content": {}}

        # Perform various operations
        syncer.sync_fold("experimental", "experimental", fold_data, "success_1")
        syncer.sync_fold("experimental", "experimental", fold_data, "success_2")

        # Create operation that will fail
        syncer.sync_fold("experimental", "experimental", {}, "fail_1")  # Invalid data

        stats = syncer.get_sync_stats()

        # Verify stats structure
        expected_keys = {
            "lane", "total_operations", "recent_operations", "successful_operations",
            "success_rate", "current_fanout", "current_fanin", "fanout_capacity",
            "fanin_capacity", "ops_budget_utilization", "max_depth", "active_operations"
        }
        assert set(stats.keys()) == expected_keys

        # Verify stats values
        assert stats["total_operations"] == 3
        assert stats["successful_operations"] == 2
        assert stats["success_rate"] == 2/3

    def test_sync_operation_logging(self):
        """Test synchronization operation logging."""
        syncer = MemorySynchronizer(lane="experimental")

        fold_data = {"fold_id": "test", "content": {}}

        # Perform operation
        result = syncer.sync_fold("experimental", "experimental", fold_data, "test")

        # Check operation log
        log = syncer.get_sync_log()
        assert len(log) == 1
        assert log[0].fold_id == "test"
        assert log[0].result == SyncResult.SUCCESS

        # Test log entry serialization
        log_dict = result.to_dict()
        expected_keys = {
            "op_id", "timestamp", "source_lane", "target_lane", "operation_type",
            "fold_id", "data_size", "fanout_cost", "fanin_cost", "depth_level",
            "result", "duration_ms", "error_message"
        }
        assert set(log_dict.keys()) == expected_keys

    def test_idempotency(self):
        """Test synchronization operation idempotency."""
        syncer = MemorySynchronizer(lane="experimental")

        fold_data = {
            "fold_id": "idempotent_test",
            "content": {"data": "value"},
            "version": 1
        }

        # Perform same operation multiple times
        results = []
        for i in range(3):
            result = syncer.sync_fold(
                source_lane="experimental",
                target_lane="experimental",
                fold_data=fold_data,
                fold_id="idempotent_test"
            )
            results.append(result)

        # All operations should succeed
        assert all(r.result == SyncResult.SUCCESS for r in results)

        # Each should have different operation IDs but same fold_id
        op_ids = {r.op_id for r in results}
        assert len(op_ids) == 3  # Different operation instances
        assert all(r.fold_id == "idempotent_test" for r in results)

    def test_concurrent_sync_operations(self):
        """Test concurrent synchronization safety."""
        syncer = MemorySynchronizer(lane="experimental")

        fold_data = {"fold_id": "concurrent_test", "content": {}}

        def perform_sync(i):
            return syncer.sync_fold(
                source_lane="experimental",
                target_lane="experimental",
                fold_data={**fold_data, "instance": i},
                fold_id=f"concurrent_{i}"
            )

        # Run concurrent operations
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(perform_sync, i) for i in range(10)]
            results = [future.result() for future in as_completed(futures)]

        # All operations should complete successfully
        assert len(results) == 10
        assert all(r.result == SyncResult.SUCCESS for r in results)

        # Check that all operations were logged
        sync_log = syncer.get_sync_log()
        assert len(sync_log) == 10

    def test_lane_configuration_matrix(self):
        """Test synchronization behavior across different lane configurations."""
        test_cases = [
            ("experimental", 12, 8, True),   # High limits, cross-lane allowed
            ("candidate", 8, 4, True),       # Medium limits, cross-lane allowed
            ("prod", 4, 2, False)            # Low limits, cross-lane disallowed
        ]

        fold_data = {"fold_id": "test", "content": {}}

        for lane, expected_fanout, expected_fanin, cross_lane_allowed in test_cases:
            syncer = MemorySynchronizer(lane=lane)

            # Verify configuration
            assert syncer.config.max_fanout == expected_fanout
            assert syncer.config.max_fanin == expected_fanin
            assert syncer.config.allow_cross_lane_sync == cross_lane_allowed

            # Test cross-lane behavior
            result = syncer.sync_fold(
                source_lane="other_lane",
                target_lane=lane,
                fold_data=fold_data
            )

            if cross_lane_allowed:
                assert result.result == SyncResult.SUCCESS
            else:
                assert result.result == SyncResult.ERROR_LANE_POLICY

    def test_custom_configuration(self):
        """Test custom synchronization configuration."""
        custom_config = {
            "experimental": SyncBudgetConfig(
                max_fanout=20,
                max_fanin=15,
                max_depth=5,
                ops_budget_per_tick=200,
                data_budget_per_tick_mb=50.0,
                allow_cross_lane_sync=False
            )
        }

        syncer = MemorySynchronizer(lane="experimental", custom_config=custom_config)

        # Verify custom configuration is applied
        assert syncer.config.max_fanout == 20
        assert syncer.config.max_fanin == 15
        assert syncer.config.max_depth == 5
        assert syncer.config.ops_budget_per_tick == 200
        assert syncer.config.allow_cross_lane_sync == False

    def test_performance_requirements(self):
        """Test synchronization performance requirements."""
        syncer = MemorySynchronizer(lane="experimental")

        fold_data = {"fold_id": "perf_test", "content": {"data": "x" * 100}}

        # Time multiple synchronizations
        start_time = time.perf_counter()
        num_ops = 50

        for i in range(num_ops):
            result = syncer.sync_fold(
                source_lane="experimental",
                target_lane="experimental",
                fold_data={**fold_data, "instance": i},
                fold_id=f"perf_{i}"
            )
            assert result.result == SyncResult.SUCCESS

        duration = time.perf_counter() - start_time

        # Should process operations quickly (< 5ms average)
        avg_duration_ms = (duration / num_ops) * 1000
        assert avg_duration_ms < 5.0, f"Average sync time {avg_duration_ms:.2f}ms exceeds 5ms budget"

    def test_factory_function(self):
        """Test factory function creates synchronizers correctly."""
        syncer = create_memory_synchronizer(lane="candidate")
        assert isinstance(syncer, MemorySynchronizer)
        assert syncer.lane == "candidate"

    def test_reset_stats(self):
        """Test statistics reset functionality."""
        syncer = MemorySynchronizer(lane="experimental")

        fold_data = {"fold_id": "test", "content": {}}

        # Generate some activity
        syncer.sync_fold("experimental", "experimental", fold_data, "test_1")
        syncer.sync_fold("experimental", "experimental", fold_data, "test_2")

        # Verify stats exist
        stats_before = syncer.get_sync_stats()
        assert stats_before["total_operations"] == 2

        # Reset stats
        syncer.reset_stats()

        # Verify stats are cleared
        stats_after = syncer.get_sync_stats()
        assert stats_after["total_operations"] == 0
        assert stats_after["active_operations"] == 0

    def test_budget_window_behavior(self):
        """Test budget window sliding behavior."""
        # Create syncer with tight budget and short window
        custom_config = {
            "experimental": SyncBudgetConfig(
                ops_budget_per_tick=2,
                budget_window_seconds=1  # Very short window
            )
        }
        syncer = MemorySynchronizer(lane="experimental", custom_config=custom_config)

        fold_data = {"fold_id": "test", "content": {}}

        # Fill the budget
        for i in range(2):
            result = syncer.sync_fold("experimental", "experimental", fold_data, f"test_{i}")
            assert result.result == SyncResult.SUCCESS

        # Next operation should fail
        result = syncer.sync_fold("experimental", "experimental", fold_data, "test_fail")
        assert result.result == SyncResult.ERROR_BUDGET

        # Wait for window to slide
        time.sleep(1.1)

        # Operation should succeed again
        result = syncer.sync_fold("experimental", "experimental", fold_data, "test_after_window")
        assert result.result == SyncResult.SUCCESS


class TestMemorySyncIntegration:
    """Integration tests for memory synchronization with other components."""

    def test_prometheus_metrics_integration(self):
        """Test Prometheus metrics are updated correctly."""
        syncer = MemorySynchronizer(lane="experimental")

        fold_data = {"fold_id": "metrics_test", "content": {}}

        # Perform operations that should update metrics
        syncer.sync_fold("experimental", "experimental", fold_data, "success")
        syncer.sync_fold("experimental", "experimental", {}, "failure")  # Invalid data

        # Metrics should be updated (tested via no exceptions)
        # In a real test environment, you'd verify metric values

    def test_environment_variable_integration(self):
        """Test integration with environment variables."""
        # Test LUKHAS_LANE detection
        with patch.dict(os.environ, {"LUKHAS_LANE": "candidate"}):
            syncer = MemorySynchronizer()
            assert syncer.lane == "candidate"

        # Test fallback to experimental
        with patch.dict(os.environ, {}, clear=True):
            if "LUKHAS_LANE" in os.environ:
                del os.environ["LUKHAS_LANE"]
            syncer = MemorySynchronizer()
            assert syncer.lane == "experimental"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])