"""
Memory Profiler Wrapper
Provides integration layer for memory profiler components
"""

import logging
from datetime import datetime
from typing import Any, Optional

from candidate.core.common import get_logger

try:
    from .memory_profiler import (
        Action,
        Category,
        DataFlowNode,
        OpTree,
        SchemaMatcher,
        SizeMap)

    MEMORY_PROFILER_AVAILABLE = True
except ImportError as e:
    MEMORY_PROFILER_AVAILABLE = False
    logging.warning(f"Memory profiler components not available: {e}")

logger = get_logger(__name__)


class MemoryProfiler:
    """Wrapper for memory profiling functionality"""

    def __init__(self):
        if not MEMORY_PROFILER_AVAILABLE:
            raise ImportError("Memory profiler module not available")

        self.schema_matcher = SchemaMatcher()
        self.op_tree = OpTree()
        self.size_map = SizeMap()
        self.data_flow_nodes: dict[str, DataFlowNode] = {}
        self.memory_events: list[dict[str, Any]] = []
        self.category_stats: dict[Category, dict[str, Any]] = {cat: {"count": 0, "total_size": 0} for cat in Category}

        logger.info("MemoryProfiler initialized")

    def record_allocation(self, tensor_id: str, size: int, category: Optional[Category] = None) -> None:
        """Record a memory allocation event"""
        event = {
            "timestamp": datetime.now(timezone.utc),
            "action": Action.CREATE,
            "tensor_id": tensor_id,
            "size": size,
            "category": category or Category.TEMPORARY,
        }

        self.memory_events.append(event)

        # Update category statistics
        if category:
            self.category_stats[category]["count"] += 1
            self.category_stats[category]["total_size"] += size

        logger.debug(f"Recorded allocation: {tensor_id} ({size} bytes, {category})")

    def record_deallocation(self, tensor_id: str) -> None:
        """Record a memory deallocation event"""
        event = {
            "timestamp": datetime.now(timezone.utc),
            "action": Action.DELETE,
            "tensor_id": tensor_id,
        }

        self.memory_events.append(event)
        logger.debug(f"Recorded deallocation: {tensor_id}")

    def create_data_flow_node(self, node_id: str, operation: str) -> DataFlowNode:
        """Create a data flow node for tracking tensor operations"""
        node = DataFlowNode()
        self.data_flow_nodes[node_id] = node
        logger.debug(f"Created data flow node: {node_id} ({operation})")
        return node

    def get_memory_usage_by_category(self) -> dict[str, dict[str, Any]]:
        """Get memory usage statistics by category"""
        return {
            cat.name: {
                "count": stats["count"],
                "total_size_mb": stats["total_size"] / (1024 * 1024),
                "percentage": 0,  # Will calculate based on total
            }
            for cat, stats in self.category_stats.items()
        }

    def get_memory_timeline(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get timeline of memory events"""
        return self.memory_events[-limit:]

    def analyze_memory_patterns(self) -> dict[str, Any]:
        """Analyze memory usage patterns"""
        analysis = {
            "total_allocations": sum(1 for e in self.memory_events if e.get("action") == Action.CREATE),
            "total_deallocations": sum(1 for e in self.memory_events if e.get("action") == Action.DELETE),
            "peak_memory_usage": 0,
            "fragmentation_score": 0,
            "category_distribution": self.get_memory_usage_by_category(),
            "recommendations": [],
        }

        # Calculate peak memory usage
        current_usage = 0
        peak_usage = 0

        for event in self.memory_events:
            if event.get("action") == Action.CREATE:
                current_usage += event.get("size", 0)
                peak_usage = max(peak_usage, current_usage)
            elif event.get("action") == Action.DELETE:
                # Note: In real implementation, we'd track size of deallocated tensors
                pass

        analysis["peak_memory_usage_mb"] = peak_usage / (1024 * 1024)

        # Generate recommendations
        if analysis["total_deallocations"] < analysis["total_allocations"] * 0.8:
            analysis["recommendations"].append("Consider more aggressive memory cleanup")

        temp_usage = self.category_stats.get(Category.TEMPORARY, {}).get("total_size", 0)
        total_usage = sum(s["total_size"] for s in self.category_stats.values())

        if total_usage > 0 and temp_usage / total_usage > 0.5:
            analysis["recommendations"].append("High temporary memory usage detected - consider optimization")

        logger.info(
            f"Memory analysis complete: {analysis['total_allocations']} allocations, peak {analysis['peak_memory_usage_mb']:.2f} MB"
        )

        return analysis

    def reset_profiler(self) -> None:
        """Reset profiler state"""
        self.memory_events.clear()
        self.data_flow_nodes.clear()
        self.category_stats = {cat: {"count": 0, "total_size": 0} for cat in Category}
        logger.info("Memory profiler reset")


def get_memory_profiler() -> Optional[MemoryProfiler]:
    """Factory function to create memory profiler"""
    if not MEMORY_PROFILER_AVAILABLE:
        logger.warning("Memory profiler not available")
        return None

    try:
        return MemoryProfiler()
    except Exception as e:
        logger.error(f"Failed to create memory profiler: {e}")
        return None
