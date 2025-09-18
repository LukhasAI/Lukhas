"""
lukhas/memory/sync.py

Phase 5: Memory fold synchronization module with governance guardrails.
Provides bounded fan-in/out and per-tick budgets for safe cross-lane memory operations.

Usage:
    from lukhas.memory.sync import MemorySynchronizer, SyncResult

    syncer = MemorySynchronizer(lane="experimental")
    result = syncer.sync_fold(source_lane="candidate", target_lane="experimental", fold_data=data)
    if result.success:
        # Sync completed safely
        pass
"""
from __future__ import annotations

import os
import logging
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from uuid import UUID, uuid4
from enum import Enum
from collections import defaultdict, deque

# Optional Prometheus metrics
try:
    from prometheus_client import Counter, Histogram, Gauge
    MEMORY_SYNC_OPS_TOTAL = Counter("lukhas_memory_sync_ops_total", "Memory sync operations", ["source_lane", "target_lane", "result"])
    MEMORY_SYNC_DURATION = Histogram("lukhas_memory_sync_duration_seconds", "Memory sync duration", ["operation"])
    MEMORY_FANOUT_GAUGE = Gauge("lukhas_memory_fanout_current", "Current memory fanout", ["lane"])
    MEMORY_BUDGET_UTILIZATION = Gauge("lukhas_memory_budget_utilization", "Budget utilization ratio", ["lane"])
    MEMORY_SYNC_ERRORS_TOTAL = Counter("lukhas_memory_sync_errors_total", "Memory sync errors", ["lane", "error_type"])
    PROM = True
except Exception:
    PROM = False
    class _NoopMetric:
        def labels(self, *_, **__): return self
        def inc(self, *_): pass
        def observe(self, *_): pass
        def set(self, *_): pass
    MEMORY_SYNC_OPS_TOTAL = _NoopMetric()
    MEMORY_SYNC_DURATION = _NoopMetric()
    MEMORY_FANOUT_GAUGE = _NoopMetric()
    MEMORY_BUDGET_UTILIZATION = _NoopMetric()
    MEMORY_SYNC_ERRORS_TOTAL = _NoopMetric()


logger = logging.getLogger(__name__)


class SyncResult(Enum):
    """Memory synchronization operation results."""
    SUCCESS = "success"
    ERROR_FANOUT = "error_fanout"
    ERROR_FANIN = "error_fanin"
    ERROR_DEPTH = "error_depth"
    ERROR_BUDGET = "error_budget"
    ERROR_LANE_POLICY = "error_lane_policy"
    ERROR_DATA_VALIDATION = "error_data_validation"
    ERROR_CONCURRENCY = "error_concurrency"


@dataclass(frozen=True)
class SyncOperation:
    """Memory synchronization operation record."""
    op_id: UUID
    timestamp: datetime
    source_lane: str
    target_lane: str
    operation_type: str  # "fold_sync", "promote", "replicate"
    fold_id: Optional[str]
    data_size: int
    fanout_cost: int
    fanin_cost: int
    depth_level: int
    result: SyncResult
    duration_ms: float
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/serialization."""
        return {
            "op_id": str(self.op_id),
            "timestamp": self.timestamp.isoformat(),
            "source_lane": self.source_lane,
            "target_lane": self.target_lane,
            "operation_type": self.operation_type,
            "fold_id": self.fold_id,
            "data_size": self.data_size,
            "fanout_cost": self.fanout_cost,
            "fanin_cost": self.fanin_cost,
            "depth_level": self.depth_level,
            "result": self.result.value,
            "duration_ms": self.duration_ms,
            "error_message": self.error_message
        }


@dataclass
class SyncBudgetConfig:
    """Configuration for synchronization budgets and limits."""
    # Fanout limits (number of concurrent outbound sync operations)
    max_fanout: int = 8

    # Fan-in limits (number of concurrent inbound sync operations)
    max_fanin: int = 4

    # Operation depth limits (nested sync operations)
    max_depth: int = 3

    # Per-tick operation budgets
    ops_budget_per_tick: int = 50
    data_budget_per_tick_mb: float = 10.0

    # Time windows for budget calculation
    budget_window_seconds: int = 30

    # Lane-specific sync policies
    allow_cross_lane_sync: bool = True
    require_governance_approval: bool = False


# Default configurations per lane
DEFAULT_SYNC_CONFIGS: Dict[str, SyncBudgetConfig] = {
    "experimental": SyncBudgetConfig(
        max_fanout=12,
        max_fanin=8,
        max_depth=4,
        ops_budget_per_tick=100,
        data_budget_per_tick_mb=20.0,
        allow_cross_lane_sync=True,
        require_governance_approval=False
    ),
    "candidate": SyncBudgetConfig(
        max_fanout=8,
        max_fanin=4,
        max_depth=3,
        ops_budget_per_tick=50,
        data_budget_per_tick_mb=10.0,
        allow_cross_lane_sync=True,
        require_governance_approval=True
    ),
    "prod": SyncBudgetConfig(
        max_fanout=4,
        max_fanin=2,
        max_depth=2,
        ops_budget_per_tick=25,
        data_budget_per_tick_mb=5.0,
        allow_cross_lane_sync=False,
        require_governance_approval=True
    )
}


class MemorySynchronizer:
    """
    Memory fold synchronization coordinator with governance guardrails.

    Provides bounded fan-in/out, depth controls, and per-tick budgets
    to ensure safe memory synchronization across lanes.
    """

    def __init__(self, lane: Optional[str] = None, custom_config: Optional[Dict[str, SyncBudgetConfig]] = None):
        """
        Initialize memory synchronizer.

        Args:
            lane: Target lane (defaults to LUKHAS_LANE env var)
            custom_config: Custom configuration overrides
        """
        self.lane = (lane or os.getenv("LUKHAS_LANE", "experimental")).lower()

        # Load configurations
        self.sync_configs = custom_config or DEFAULT_SYNC_CONFIGS.copy()
        self.config = self.sync_configs.get(self.lane, DEFAULT_SYNC_CONFIGS["experimental"])

        # Synchronization state tracking
        self._active_fanout: Dict[str, Set[UUID]] = defaultdict(set)  # lane -> operation_ids
        self._active_fanin: Dict[str, Set[UUID]] = defaultdict(set)   # lane -> operation_ids
        self._operation_depth: Dict[UUID, int] = {}                   # op_id -> depth

        # Budget tracking
        self._ops_history: deque = deque(maxlen=1000)  # Recent operations for budget calculation
        self._data_usage_history: deque = deque(maxlen=1000)  # Recent data usage

        # Operation log
        self._sync_log: List[SyncOperation] = []

        # Thread safety
        self._lock = threading.RLock()

        logger.info(f"MemorySynchronizer initialized: lane={self.lane}, config={self.config}")

    def sync_fold(
        self,
        source_lane: str,
        target_lane: str,
        fold_data: Dict[str, Any],
        fold_id: Optional[str] = None,
        operation_type: str = "fold_sync",
        parent_op_id: Optional[UUID] = None
    ) -> SyncOperation:
        """
        Synchronize memory fold between lanes with governance checks.

        Args:
            source_lane: Source lane for the fold data
            target_lane: Target lane to sync to
            fold_data: Memory fold data to synchronize
            fold_id: Optional fold identifier
            operation_type: Type of sync operation
            parent_op_id: Parent operation ID (for depth tracking)

        Returns:
            SyncOperation with result and metrics
        """
        op_id = uuid4()
        start_time = datetime.utcnow()

        with self._lock:
            try:
                # Calculate operation costs
                data_size = self._calculate_data_size(fold_data)
                fanout_cost = 1 if target_lane != self.lane else 0
                fanin_cost = 1 if source_lane != self.lane else 0
                depth_level = self._calculate_depth(parent_op_id)

                # 1. Check lane policy
                if not self._check_lane_policy(source_lane, target_lane):
                    result = self._create_sync_operation(
                        op_id, start_time, source_lane, target_lane, operation_type,
                        fold_id, data_size, fanout_cost, fanin_cost, depth_level,
                        SyncResult.ERROR_LANE_POLICY,
                        "Cross-lane sync not permitted by policy"
                    )
                    self._log_operation(result)
                    return result

                # 2. Check fanout limits
                if fanout_cost > 0 and not self._check_fanout_budget(target_lane, fanout_cost):
                    result = self._create_sync_operation(
                        op_id, start_time, source_lane, target_lane, operation_type,
                        fold_id, data_size, fanout_cost, fanin_cost, depth_level,
                        SyncResult.ERROR_FANOUT,
                        f"Fanout limit {self.config.max_fanout} exceeded"
                    )
                    self._log_operation(result)
                    return result

                # 3. Check fanin limits
                if fanin_cost > 0 and not self._check_fanin_budget(source_lane, fanin_cost):
                    result = self._create_sync_operation(
                        op_id, start_time, source_lane, target_lane, operation_type,
                        fold_id, data_size, fanout_cost, fanin_cost, depth_level,
                        SyncResult.ERROR_FANIN,
                        f"Fanin limit {self.config.max_fanin} exceeded"
                    )
                    self._log_operation(result)
                    return result

                # 4. Check depth limits
                if depth_level > self.config.max_depth:
                    result = self._create_sync_operation(
                        op_id, start_time, source_lane, target_lane, operation_type,
                        fold_id, data_size, fanout_cost, fanin_cost, depth_level,
                        SyncResult.ERROR_DEPTH,
                        f"Depth limit {self.config.max_depth} exceeded"
                    )
                    self._log_operation(result)
                    return result

                # 5. Check operation budget
                if not self._check_ops_budget():
                    result = self._create_sync_operation(
                        op_id, start_time, source_lane, target_lane, operation_type,
                        fold_id, data_size, fanout_cost, fanin_cost, depth_level,
                        SyncResult.ERROR_BUDGET,
                        f"Operation budget {self.config.ops_budget_per_tick} exceeded"
                    )
                    self._log_operation(result)
                    return result

                # 6. Check data budget
                if not self._check_data_budget(data_size):
                    result = self._create_sync_operation(
                        op_id, start_time, source_lane, target_lane, operation_type,
                        fold_id, data_size, fanout_cost, fanin_cost, depth_level,
                        SyncResult.ERROR_BUDGET,
                        f"Data budget {self.config.data_budget_per_tick_mb}MB exceeded"
                    )
                    self._log_operation(result)
                    return result

                # 7. Validate fold data
                if not self._validate_fold_data(fold_data):
                    result = self._create_sync_operation(
                        op_id, start_time, source_lane, target_lane, operation_type,
                        fold_id, data_size, fanout_cost, fanin_cost, depth_level,
                        SyncResult.ERROR_DATA_VALIDATION,
                        "Fold data validation failed"
                    )
                    self._log_operation(result)
                    return result

                # All checks passed - proceed with sync
                self._reserve_resources(op_id, source_lane, target_lane, fanout_cost, fanin_cost, depth_level)

                try:
                    # Perform the actual synchronization
                    self._perform_sync(source_lane, target_lane, fold_data, fold_id)

                    # Sync successful
                    duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                    result = self._create_sync_operation(
                        op_id, start_time, source_lane, target_lane, operation_type,
                        fold_id, data_size, fanout_cost, fanin_cost, depth_level,
                        SyncResult.SUCCESS, None, duration_ms
                    )

                    # Update budgets
                    self._record_operation(result)

                finally:
                    # Release resources
                    self._release_resources(op_id, source_lane, target_lane, fanout_cost, fanin_cost)

            except Exception as e:
                duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                result = self._create_sync_operation(
                    op_id, start_time, source_lane, target_lane, operation_type,
                    fold_id, 0, fanout_cost, fanin_cost, depth_level,
                    SyncResult.ERROR_CONCURRENCY, str(e), duration_ms
                )
                logger.exception(f"Memory sync operation {op_id} failed: {e}")

            self._log_operation(result)
            return result

    def _calculate_data_size(self, data: Dict[str, Any]) -> int:
        """Estimate data size in bytes (simplified implementation)."""
        try:
            import json
            return len(json.dumps(data).encode('utf-8'))
        except Exception:
            # Fallback estimation
            return len(str(data).encode('utf-8'))

    def _calculate_depth(self, parent_op_id: Optional[UUID]) -> int:
        """Calculate operation depth based on parent operation."""
        if parent_op_id is None:
            return 0
        return self._operation_depth.get(parent_op_id, 0) + 1

    def _check_lane_policy(self, source_lane: str, target_lane: str) -> bool:
        """Check if cross-lane sync is allowed by policy."""
        if source_lane == target_lane:
            return True  # Same-lane sync always allowed

        return self.config.allow_cross_lane_sync

    def _check_fanout_budget(self, target_lane: str, cost: int) -> bool:
        """Check if fanout budget allows the operation."""
        # Total fanout from this synchronizer
        current_fanout = sum(len(ops) for ops in self._active_fanout.values())
        return current_fanout + cost <= self.config.max_fanout

    def _check_fanin_budget(self, source_lane: str, cost: int) -> bool:
        """Check if fanin budget allows the operation."""
        # Total fanin to this synchronizer
        current_fanin = sum(len(ops) for ops in self._active_fanin.values())
        return current_fanin + cost <= self.config.max_fanin

    def _check_ops_budget(self) -> bool:
        """Check if operation budget allows new operation."""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.config.budget_window_seconds)

        # Count recent operations
        recent_ops = [
            op for op in self._ops_history
            if op.timestamp >= window_start
        ]

        return len(recent_ops) < self.config.ops_budget_per_tick

    def _check_data_budget(self, data_size: int) -> bool:
        """Check if data budget allows the operation."""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.config.budget_window_seconds)

        # Calculate recent data usage
        recent_data_mb = sum(
            op.data_size / (1024 * 1024) for op in self._data_usage_history
            if op.timestamp >= window_start
        )

        data_size_mb = data_size / (1024 * 1024)
        return recent_data_mb + data_size_mb <= self.config.data_budget_per_tick_mb

    def _validate_fold_data(self, data: Dict[str, Any]) -> bool:
        """Validate fold data structure and content."""
        if not isinstance(data, dict):
            return False

        # Check for required fields (simplified validation)
        if "fold_id" not in data and "content" not in data:
            return False

        return True

    def _reserve_resources(self, op_id: UUID, source_lane: str, target_lane: str,
                          fanout_cost: int, fanin_cost: int, depth_level: int):
        """Reserve synchronization resources."""
        if fanout_cost > 0:
            self._active_fanout[target_lane].add(op_id)

        if fanin_cost > 0:
            self._active_fanin[source_lane].add(op_id)

        self._operation_depth[op_id] = depth_level

    def _release_resources(self, op_id: UUID, source_lane: str, target_lane: str,
                          fanout_cost: int, fanin_cost: int):
        """Release synchronization resources."""
        if fanout_cost > 0:
            self._active_fanout[target_lane].discard(op_id)

        if fanin_cost > 0:
            self._active_fanin[source_lane].discard(op_id)

        self._operation_depth.pop(op_id, None)

    def _perform_sync(self, source_lane: str, target_lane: str, data: Dict[str, Any], fold_id: Optional[str]):
        """Perform the actual memory synchronization (implementation placeholder)."""
        # This would contain the actual sync logic
        # For now, we simulate the sync operation
        logger.debug(f"Syncing fold {fold_id} from {source_lane} to {target_lane}")

        # Simulate some processing time
        import time
        time.sleep(0.001)  # 1ms simulated sync time

    def _create_sync_operation(self, op_id: UUID, start_time: datetime,
                              source_lane: str, target_lane: str, operation_type: str,
                              fold_id: Optional[str], data_size: int,
                              fanout_cost: int, fanin_cost: int, depth_level: int,
                              result: SyncResult, error_message: Optional[str] = None,
                              duration_ms: Optional[float] = None) -> SyncOperation:
        """Create sync operation record."""
        if duration_ms is None:
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

        return SyncOperation(
            op_id=op_id,
            timestamp=start_time,
            source_lane=source_lane,
            target_lane=target_lane,
            operation_type=operation_type,
            fold_id=fold_id,
            data_size=data_size,
            fanout_cost=fanout_cost,
            fanin_cost=fanin_cost,
            depth_level=depth_level,
            result=result,
            duration_ms=duration_ms,
            error_message=error_message
        )

    def _record_operation(self, operation: SyncOperation):
        """Record operation for budget tracking."""
        self._ops_history.append(operation)
        self._data_usage_history.append(operation)

    def _log_operation(self, operation: SyncOperation):
        """Log synchronization operation."""
        self._sync_log.append(operation)

        # Log to standard logging
        log_entry = operation.to_dict()
        if operation.result == SyncResult.SUCCESS:
            logger.info(f"Memory sync SUCCESS: {log_entry}")
        else:
            logger.warning(f"Memory sync FAILED: {log_entry}")

        # Update Prometheus metrics
        if PROM:
            MEMORY_SYNC_OPS_TOTAL.labels(
                source_lane=operation.source_lane,
                target_lane=operation.target_lane,
                result=operation.result.value
            ).inc()

            MEMORY_SYNC_DURATION.labels(operation=operation.operation_type).observe(
                operation.duration_ms / 1000.0
            )

            if operation.result != SyncResult.SUCCESS:
                MEMORY_SYNC_ERRORS_TOTAL.labels(
                    lane=self.lane,
                    error_type=operation.result.value
                ).inc()

    def get_sync_stats(self) -> Dict[str, Any]:
        """Get current synchronization statistics."""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.config.budget_window_seconds)

        # Calculate recent metrics
        recent_ops = [op for op in self._sync_log if op.timestamp >= window_start]
        successful_ops = [op for op in recent_ops if op.result == SyncResult.SUCCESS]

        # Calculate current resource usage
        total_fanout = sum(len(ops) for ops in self._active_fanout.values())
        total_fanin = sum(len(ops) for ops in self._active_fanin.values())

        # Budget utilization
        ops_utilization = len(recent_ops) / max(1, self.config.ops_budget_per_tick)

        return {
            "lane": self.lane,
            "total_operations": len(self._sync_log),
            "recent_operations": len(recent_ops),
            "successful_operations": len(successful_ops),
            "success_rate": len(successful_ops) / max(1, len(recent_ops)),
            "current_fanout": total_fanout,
            "current_fanin": total_fanin,
            "fanout_capacity": self.config.max_fanout,
            "fanin_capacity": self.config.max_fanin,
            "ops_budget_utilization": min(1.0, ops_utilization),
            "max_depth": self.config.max_depth,
            "active_operations": len(self._operation_depth)
        }

    def get_sync_log(self, limit: Optional[int] = None) -> List[SyncOperation]:
        """Get recent sync operations for audit/debugging."""
        if limit is None:
            return self._sync_log.copy()
        return self._sync_log[-limit:]

    def reset_stats(self):
        """Reset synchronization statistics (for testing)."""
        with self._lock:
            self._sync_log.clear()
            self._ops_history.clear()
            self._data_usage_history.clear()
            self._active_fanout.clear()
            self._active_fanin.clear()
            self._operation_depth.clear()


def create_memory_synchronizer(lane: Optional[str] = None, **config_overrides) -> MemorySynchronizer:
    """Factory function for creating memory synchronizers."""
    return MemorySynchronizer(lane=lane)