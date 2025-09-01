"""
LUKHAS AI Memory - MATRIZ Adapter
Provides MATRIZ instrumentation for memory operations
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

import time
import uuid
from typing import Any, Optional

try:
    from lukhas.observability.matriz_decorators import matriz_record
    from lukhas.observability.matriz_emit import emit, make_node

    def emit_node(node_type):
        return matriz_record(node_type)

    def get_matriz_context():
        return {}

except ImportError:

    def emit_node(node_type):
        _ = node_type

        def decorator(func):
            return func

        return decorator

    def get_matriz_context():
        return {}

    def make_node(**kwargs):
        return kwargs

    def emit(_node) -> None:
        pass


class MemoryMatrizAdapter:
    """MATRIZ instrumentation adapter for memory operations"""

    def __init__(self) -> None:
        self.node_prefix = "LT-MEM"
        self.version = 1

    def create_node(
        self,
        node_type: str,
        state: dict[str, Any],
        labels: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Create a MATRIZ node for memory operations"""

        node_id = f"{self.node_prefix}-{str(uuid.uuid4())[:8].upper()}"
        timestamp = time.time()

        node = {
            "id": node_id,
            "type": node_type,
            "version": self.version,
            "timestamp": timestamp,
            "state": state,
            "labels": labels or [],
            "metadata": metadata or {},
            "context": get_matriz_context() if get_matriz_context else {},
        }

        return node

    @emit_node("memory:matriz:fold_created")
    def emit_fold_created(
        self,
        fold_id: str,
        content_type: str,
        emotional_valence: float,
        importance: float,
        causal_chain_length: int,
        mode: str = "dry_run",
    ) -> dict[str, Any]:
        """Emit MATRIZ node for fold creation"""

        state = {
            "fold_id": fold_id,
            "content_type": content_type,
            "emotional_valence": emotional_valence,
            "importance": importance,
            "causal_chain_length": causal_chain_length,
            "operation_mode": mode,
        }

        labels = ["memory", "fold", "create", mode]

        metadata = {
            "operation": "create_fold",
            "performance_category": "memory_creation",
            "safety_level": "production" if mode == "live" else "dry_run",
        }

        return self.create_node(
            node_type="memory:fold:create",
            state=state,
            labels=labels,
            metadata=metadata,
        )

    @emit_node("memory:matriz:memory_accessed")
    def emit_memory_accessed(
        self,
        query_type: str,
        results_count: int,
        operation_time_ms: float,
        mode: str = "dry_run",
    ) -> dict[str, Any]:
        """Emit MATRIZ node for memory access"""

        state = {
            "query_type": query_type,
            "results_count": results_count,
            "operation_time_ms": operation_time_ms,
            "operation_mode": mode,
        }

        labels = ["memory", "access", "query", mode]

        metadata = {
            "operation": "access_memory",
            "performance_category": "memory_retrieval",
            "efficiency_rating": "fast" if operation_time_ms < 50 else "slow",
        }

        return self.create_node(node_type="memory:access", state=state, labels=labels, metadata=metadata)

    @emit_node("memory:matriz:consolidation")
    def emit_consolidation(
        self,
        fold_count_before: int,
        fold_count_after: int,
        operation_time_ms: float,
        mode: str = "dry_run",
    ) -> dict[str, Any]:
        """Emit MATRIZ node for memory consolidation"""

        consolidation_ratio = fold_count_after / max(fold_count_before, 1)

        state = {
            "fold_count_before": fold_count_before,
            "fold_count_after": fold_count_after,
            "consolidation_ratio": consolidation_ratio,
            "operation_time_ms": operation_time_ms,
            "operation_mode": mode,
        }

        labels = ["memory", "consolidation", "optimization", mode]

        metadata = {
            "operation": "consolidate_memory",
            "performance_category": "memory_optimization",
            "efficiency_impact": "high" if consolidation_ratio < 0.9 else "low",
        }

        return self.create_node(
            node_type="memory:consolidation",
            state=state,
            labels=labels,
            metadata=metadata,
        )

    @emit_node("memory:matriz:cascade_prevention")
    def emit_cascade_prevention(
        self,
        fold_count: int,
        folds_removed: int,
        prevention_rate: float,
        trigger_reason: str,
    ) -> dict[str, Any]:
        """Emit MATRIZ node for cascade prevention events"""

        state = {
            "fold_count": fold_count,
            "folds_removed": folds_removed,
            "prevention_rate": prevention_rate,
            "trigger_reason": trigger_reason,
            "prevention_successful": prevention_rate >= 0.997,
        }

        labels = ["memory", "cascade", "prevention", "safety"]

        metadata = {
            "operation": "cascade_prevention",
            "performance_category": "memory_safety",
            "criticality": "high",
            "success_rate_target": 0.997,
        }

        return self.create_node(
            node_type="memory:cascade:prevention",
            state=state,
            labels=labels,
            metadata=metadata,
        )

    @emit_node("memory:matriz:performance_metrics")
    def emit_performance_metrics(
        self,
        avg_creation_time_ms: float,
        avg_access_time_ms: float,
        total_operations: int,
        error_count: int,
        memory_health_status: str,
    ) -> dict[str, Any]:
        """Emit MATRIZ node for performance metrics"""

        error_rate = error_count / max(total_operations, 1)

        state = {
            "avg_creation_time_ms": avg_creation_time_ms,
            "avg_access_time_ms": avg_access_time_ms,
            "total_operations": total_operations,
            "error_count": error_count,
            "error_rate": error_rate,
            "memory_health_status": memory_health_status,
        }

        labels = ["memory", "performance", "metrics", "monitoring"]

        metadata = {
            "operation": "performance_monitoring",
            "performance_category": "memory_health",
            "health_check": True,
            "targets": {
                "creation_time_target_ms": 10,
                "access_time_target_ms": 50,
                "error_rate_target": 0.05,
            },
        }

        return self.create_node(
            node_type="memory:performance:metrics",
            state=state,
            labels=labels,
            metadata=metadata,
        )

    @emit_node("memory:matriz:error")
    def emit_error(self, operation: str, error_message: str, error_type: str, mode: str = "dry_run") -> dict[str, Any]:
        """Emit MATRIZ node for memory errors"""

        state = {
            "operation": operation,
            "error_message": error_message,
            "error_type": error_type,
            "operation_mode": mode,
            "severity": "high" if mode == "live" else "low",
        }

        labels = ["memory", "error", error_type, mode]

        metadata = {
            "operation": f"error_{operation}",
            "performance_category": "memory_error",
            "requires_attention": mode == "live",
            "error_context": {"operation": operation, "mode": mode},
        }

        return self.create_node(node_type="memory:error", state=state, labels=labels, metadata=metadata)


# Global adapter instance
_matriz_adapter = None


def get_matriz_adapter() -> MemoryMatrizAdapter:
    """Get or create the global MATRIZ adapter instance"""
    global _matriz_adapter
    if _matriz_adapter is None:
        _matriz_adapter = MemoryMatrizAdapter()
    return _matriz_adapter
