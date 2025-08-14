"""
Memory Planning Wrapper
Provides integration layer for memory planning components
"""

import logging
from typing import Any, Optional

from core.common import get_logger

try:
    from .memory_planning import (
        AllocationPool,
        LiveRange,
        LiveRanges,
    )

    MEMORY_PLANNING_AVAILABLE = True
except ImportError as e:
    MEMORY_PLANNING_AVAILABLE = False
    logging.warning(f"Memory planning components not available: {e}")

logger = get_logger(__name__)


class MemoryPlanner:
    """Wrapper for memory planning functionality"""

    def __init__(self):
        if not MEMORY_PLANNING_AVAILABLE:
            raise ImportError("Memory planning module not available")

        self.allocation_pools: dict[str, AllocationPool] = {}
        self.live_ranges: dict[str, LiveRanges] = {}
        logger.info("MemoryPlanner initialized")

    def create_allocation_pool(self, pool_name: str, size: int) -> Any:
        """Create a new allocation pool"""
        pool = AllocationPool()
        self.allocation_pools[pool_name] = pool
        logger.debug(f"Created allocation pool: {pool_name}")
        return pool

    def track_live_range(self, tensor_id: str, begin: float, end: float) -> LiveRange:
        """Track live range for a tensor"""
        live_range = LiveRange(begin, end)

        if tensor_id not in self.live_ranges:
            self.live_ranges[tensor_id] = LiveRanges([live_range])
        else:
            # Add to existing ranges
            existing = self.live_ranges[tensor_id]
            self.live_ranges[tensor_id] = LiveRanges(existing.ranges + [live_range])

        logger.debug(f"Tracked live range for {tensor_id}: [{begin}, {end})")
        return live_range

    def check_overlaps(self, tensor_id1: str, tensor_id2: str) -> bool:
        """Check if two tensors have overlapping live ranges"""
        if tensor_id1 not in self.live_ranges or tensor_id2 not in self.live_ranges:
            return False

        return self.live_ranges[tensor_id1].overlaps(self.live_ranges[tensor_id2])

    def get_allocation_stats(self) -> dict[str, Any]:
        """Get statistics about current allocations"""
        return {
            "allocation_pools": len(self.allocation_pools),
            "tracked_tensors": len(self.live_ranges),
            "pools": {
                name: {"size": len(pool.pools) if hasattr(pool, "pools") else 0}
                for name, pool in self.allocation_pools.items()
            },
        }

    def optimize_memory_layout(self) -> dict[str, Any]:
        """Optimize memory layout based on live ranges"""
        # This is a simplified version - real implementation would do complex
        # optimization
        optimizations = {
            "reuse_opportunities": 0,
            "fragmentation_reduction": 0,
            "suggested_merges": [],
        }

        # Check for non-overlapping tensors that could share memory
        tensor_ids = list(self.live_ranges.keys())
        for i, id1 in enumerate(tensor_ids):
            for id2 in tensor_ids[i + 1 :]:
                if not self.check_overlaps(id1, id2):
                    optimizations["reuse_opportunities"] += 1
                    optimizations["suggested_merges"].append((id1, id2))

        logger.info(
            f"Memory optimization found {optimizations['reuse_opportunities']} reuse opportunities"
        )
        return optimizations


def get_memory_planner() -> Optional[MemoryPlanner]:
    """Factory function to create memory planner"""
    if not MEMORY_PLANNING_AVAILABLE:
        logger.warning("Memory planning not available")
        return None

    try:
        return MemoryPlanner()
    except Exception as e:
        logger.error(f"Failed to create memory planner: {e}")
        return None
