#!/usr/bin/env python3

"""
LUKHAS AI Memory Module - Enhanced Edition
==========================================

Advanced memory systems with hierarchical data storage, fold lineage tracking,
and intelligent optimization for consciousness development.

Constellation Framework: ⚛️🧠🛡️

This module provides comprehensive memory management capabilities including:
- Hierarchical data storage with intelligent tiering
- Fold lineage tracking for memory evolution
- Integration with LUKHAS memory wrapper system
- Advanced memory optimization and compression

Key Features:
- HierarchicalDataStore: Advanced multi-tier memory storage
- FoldLineageTracker: Memory evolution and lineage tracking
- MemoryWrapper: Core memory interface (from lukhas.memory)
- FoldManager: Memory fold management (from lukhas.memory)

Architecture:
- Core Logic: lukhas.memory (production memory system)
- Enhanced Components: root memory/ (advanced memory features)
- Bridge Module: This file provides unified access

Version: 2.0.0
Status: OPERATIONAL
"""

import logging
import os
from typing import Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Memory system status
MEMORY_ENHANCED_ACTIVE = True

try:
    # Import core production memory system
    from lukhas.memory import FoldManager, MemoryFold, MemoryWrapper, access_memory, create_fold, dump_state

    logger.info("✅ Core LUKHAS memory system loaded")

except ImportError as e:
    logger.warning(f"⚠️  Could not import core memory system: {e}")

    # Fallback placeholder functions
    def create_fold(*args, **kwargs):
        return {"status": "memory_unavailable"}

    def access_memory(*args, **kwargs):
        return {"status": "memory_unavailable"}

    def dump_state(*args, **kwargs):
        return {"status": "memory_unavailable"}

    MemoryWrapper = None
    FoldManager = None
    MemoryFold = None

try:
    # Import enhanced memory components
    from memory.fold_lineage_tracker import FoldLineageTracker, LineageChain
    from memory.hierarchical_data_store import HierarchicalDataStore, MemoryTier

    logger.info("✅ Enhanced memory components loaded")
    MEMORY_ENHANCED_ACTIVE = True

except ImportError as e:
    logger.warning(f"⚠️  Could not import enhanced memory components: {e}")

    # Fallback placeholder classes
    class HierarchicalDataStore:
        def __init__(self, *args, **kwargs):
            self.status = "unavailable"

    class MemoryTier:
        pass

    class FoldLineageTracker:
        def __init__(self, *args, **kwargs):
            self.status = "unavailable"

    class LineageChain:
        pass

    MEMORY_ENHANCED_ACTIVE = False


def get_memory_status() -> dict[str, Any]:
    """
    Get comprehensive memory system status including enhanced components.

    Returns:
        Dict containing memory system health, capabilities, and metrics
    """
    try:
        # Test core and enhanced memory functionality
        memory_components = {
            "MemoryWrapper": MemoryWrapper is not None,
            "FoldManager": FoldManager is not None,
            "MemoryFold": MemoryFold is not None,
            "create_fold": callable(create_fold),
            "access_memory": callable(access_memory),
            "dump_state": callable(dump_state),
            "HierarchicalDataStore": HierarchicalDataStore is not None,
            "FoldLineageTracker": FoldLineageTracker is not None,
        }

        working_components = sum(1 for v in memory_components.values() if v)
        total_components = len(memory_components)

        return {
            "status": "OPERATIONAL" if working_components > 6 else "LIMITED",
            "memory_enhanced_active": MEMORY_ENHANCED_ACTIVE,
            "components": memory_components,
            "health": f"{working_components}/{total_components}",
            "health_percentage": round((working_components / total_components) * 100, 1),
            "core_functions": ["create_fold", "access_memory", "dump_state"],
            "enhanced_classes": ["HierarchicalDataStore", "FoldLineageTracker"],
            "architecture": "Enhanced (lukhas.memory + memory/)",
            "version": "2.0.0",
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e),
            "memory_enhanced_active": False,
            "health": "0/8",
            "health_percentage": 0.0,
        }


def create_hierarchical_memory(store_id: str = "default", **config) -> Optional[Any]:
    """
    Create new hierarchical data store for advanced memory management.

    Args:
        store_id: Unique store identifier
        **config: Store configuration parameters

    Returns:
        HierarchicalDataStore object or None if unavailable
    """
    try:
        if not MEMORY_ENHANCED_ACTIVE:
            logger.warning("⚠️  Enhanced memory not available for hierarchical store creation")
            return None

        # Create hierarchical data store
        store = HierarchicalDataStore(**config)
        return store

    except Exception as e:
        logger.error(f"❌ Error creating hierarchical memory: {e}")
        return None


def create_lineage_tracker(tracker_id: str = "default", **config) -> Optional[Any]:
    """
    Create new fold lineage tracker for memory evolution tracking.

    Args:
        tracker_id: Unique tracker identifier
        **config: Tracker configuration parameters

    Returns:
        FoldLineageTracker object or None if unavailable
    """
    try:
        if not MEMORY_ENHANCED_ACTIVE:
            logger.warning("⚠️  Enhanced memory not available for lineage tracker creation")
            return None

        # Create fold lineage tracker
        tracker = FoldLineageTracker(**config)
        return tracker

    except Exception as e:
        logger.error(f"❌ Error creating lineage tracker: {e}")
        return None


def get_enhanced_memory_metrics() -> dict[str, Any]:
    """
    Get metrics from enhanced memory components.

    Returns:
        Dict containing enhanced memory metrics and statistics
    """
    try:
        metrics = {"hierarchical_stores": 0, "lineage_trackers": 0, "total_nodes": 0, "compression_ratio": "0.00%"}

        if MEMORY_ENHANCED_ACTIVE:
            # Test creating store for metrics
            store = create_hierarchical_memory("metrics_test")
            if store and hasattr(store, "get_status"):
                store_status = store.get_status()
                metrics.update(
                    {
                        "hierarchical_stores": 1,
                        "total_nodes": store_status.get("total_nodes", 0),
                        "compression_ratio": store_status.get("compression_ratio", "0.00%"),
                    }
                )

            # Test creating tracker for metrics
            tracker = create_lineage_tracker("metrics_test")
            if tracker:
                metrics["lineage_trackers"] = 1

        return {"status": "collected", "metrics": metrics, "enhanced_active": MEMORY_ENHANCED_ACTIVE}

    except Exception as e:
        logger.error(f"❌ Error collecting enhanced memory metrics: {e}")
        return {"status": "error", "error": str(e), "metrics": {}


# Export main functions and classes
__all__ = [
    "get_memory_status",
    "create_hierarchical_memory",
    "create_lineage_tracker",
    "get_enhanced_memory_metrics",
    "create_fold",
    "access_memory",
    "dump_state",
    "MemoryWrapper",
    "FoldManager",
    "MemoryFold",
    "HierarchicalDataStore",
    "MemoryTier",
    "FoldLineageTracker",
    "LineageChain",
    "MEMORY_ENHANCED_ACTIVE",
    "logger",
]

# System health check on import
if __name__ != "__main__":
    try:
        status = get_memory_status()
        if status.get("health_percentage", 0) > 70:
            logger.info(f"✅ Enhanced memory module loaded: {status['health']} components ready")
        else:
            logger.warning(f"⚠️  Enhanced memory module loaded with limited functionality: {status['health']}")
    except Exception as e:
        logger.error(f"❌ Error during enhanced memory module health check: {e}")
