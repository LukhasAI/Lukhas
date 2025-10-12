import logging
from datetime import timezone

logger = logging.getLogger(__name__)
"""
Trauma Repair Wrapper
Integration wrapper for advanced trauma repair system
"""

import logging
from datetime import datetime
from typing import Any, Optional

from lukhas.core.common import get_logger

try:
    from .advanced_trauma_repair import TraumaRepairSystem, TraumaSignature, TraumaType

    TRAUMA_REPAIR_AVAILABLE = True
except ImportError as e:
    TRAUMA_REPAIR_AVAILABLE = False
    logging.warning(f"Advanced trauma repair not available: {e}", timezone)
    # Try mock implementation
    try:
        from .trauma_repair_mock import (
            TraumaRepairSystem,
            TraumaSignature,
            TraumaType,
            get_memory_trauma_repair as get_mock_trauma_repair,
        )

        TRAUMA_REPAIR_AVAILABLE = True
        USING_MOCK = True
        logging.info("Using mock trauma repair implementation")
    except ImportError as e2:
        logging.warning(f"Mock trauma repair also not available: {e2}")
        USING_MOCK = False
else:
    USING_MOCK = False

logger = get_logger(__name__)


class MemoryTraumaRepair:
    """Wrapper for memory trauma repair functionality"""

    def __init__(self):
        if not TRAUMA_REPAIR_AVAILABLE:
            raise ImportError("Trauma repair module not available")

        # Initialize the trauma repair system
        self.repair_system = TraumaRepairSystem(enable_immune_system=True, self_repair_threshold=0.3)

        # Track repair statistics
        self.repair_stats = {
            "total_scans": 0,
            "traumas_detected": 0,
            "repairs_attempted": 0,
            "repairs_successful": 0,
            "repairs_failed": 0,
            "active_traumas": 0,
        }

        logger.info("MemoryTraumaRepair initialized")

    async def initialize(self):
        """Initialize and start the trauma repair system"""
        try:
            await self.repair_system.start()
            logger.info("Trauma repair system started")
            return True
        except Exception as e:
            logger.error(f"Failed to start trauma repair: {e}")
            return False

    async def shutdown(self):
        """Shutdown the trauma repair system"""
        try:
            await self.repair_system.stop()
            logger.info("Trauma repair system stopped")
        except Exception as e:
            logger.error(f"Error stopping trauma repair: {e}")

    async def scan_memory(
        self,
        memory_id: str,
        memory_content: Any,
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Scan a memory for trauma and initiate repair if needed"""
        self.repair_stats["total_scans"] += 1

        result = {
            "memory_id": memory_id,
            "trauma_detected": False,
            "trauma_type": None,
            "severity": 0.0,
            "repair_initiated": False,
            "repair_status": None,
        }

        try:
            # Detect trauma
            trauma = await self.repair_system.detect_trauma(memory_id, memory_content, context)

            if trauma:
                self.repair_stats["traumas_detected"] += 1
                result["trauma_detected"] = True
                result["trauma_type"] = trauma.trauma_type.value if hasattr(trauma, "trauma_type") else "unknown"
                result["severity"] = trauma.severity if hasattr(trauma, "severity") else 0.0

                # Initiate repair if severity exceeds threshold
                if result["severity"] >= self.repair_system.self_repair_threshold:
                    repair_success = await self.repair_system.initiate_repair(memory_id, trauma)
                    result["repair_initiated"] = True
                    result["repair_status"] = "success" if repair_success else "failed"

                    self.repair_stats["repairs_attempted"] += 1
                    if repair_success:
                        self.repair_stats["repairs_successful"] += 1
                    else:
                        self.repair_stats["repairs_failed"] += 1

            logger.debug(f"Memory scan complete: {memory_id}, trauma: {result['trauma_detected']}")

        except Exception as e:
            logger.error(f"Error scanning memory {memory_id}: {e}")
            result["error"] = str(e)

        return result

    async def get_active_traumas(self) -> list[dict[str, Any]]:
        """Get list of currently active traumas"""
        active_traumas = []

        for trauma_id, trauma in self.repair_system.active_traumas.items():
            active_traumas.append(
                {
                    "trauma_id": trauma_id,
                    "memory_id": (trauma.memory_id if hasattr(trauma, "memory_id") else None),
                    "trauma_type": (trauma.trauma_type.value if hasattr(trauma, "trauma_type") else "unknown"),
                    "severity": trauma.severity if hasattr(trauma, "severity") else 0.0,
                    "detected_at": (trauma.detected_at.isoformat() if hasattr(trauma, "detected_at") else None),
                }
            )

        self.repair_stats["active_traumas"] = len(active_traumas)
        return active_traumas

    async def force_repair(self, memory_id: str, repair_strategy: Optional[str] = None) -> dict[str, Any]:
        """Force repair of a specific memory"""
        result = {
            "memory_id": memory_id,
            "repair_initiated": False,
            "repair_status": None,
            "strategy_used": repair_strategy or "auto",
        }

        try:
            # Create a trauma signature for forced repair
            trauma = TraumaSignature(
                trauma_id=f"forced_{memory_id}_{datetime.now(timezone.utc).timestamp()}",
                trauma_type=TraumaType.CORRUPTION,  # Default to corruption
                severity=1.0,  # Max severity to ensure repair
                affected_memories={memory_id},
            )

            # Initiate repair
            repair_success = await self.repair_system.initiate_repair(memory_id, trauma)
            result["repair_initiated"] = True
            result["repair_status"] = "success" if repair_success else "failed"

            logger.info(f"Forced repair on memory {memory_id}: {result['repair_status']}")

        except Exception as e:
            logger.error(f"Error forcing repair on {memory_id}: {e}")
            result["error"] = str(e)

        return result

    def get_repair_statistics(self) -> dict[str, Any]:
        """Get comprehensive repair statistics"""
        stats = self.repair_stats.copy()

        # Add calculated metrics
        if stats["repairs_attempted"] > 0:
            stats["repair_success_rate"] = stats["repairs_successful"] / stats["repairs_attempted"]
        else:
            stats["repair_success_rate"] = 0.0

        if stats["total_scans"] > 0:
            stats["trauma_detection_rate"] = stats["traumas_detected"] / stats["total_scans"]
        else:
            stats["trauma_detection_rate"] = 0.0

        # Add system metrics
        stats["immune_system_enabled"] = self.repair_system.enable_immune_system
        stats["self_repair_threshold"] = self.repair_system.self_repair_threshold
        stats["healing_log_entries"] = len(self.repair_system.healing_log)
        stats["scar_tissue_areas"] = len(self.repair_system.scar_tissue)

        return stats

    async def get_healing_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent healing history"""
        # Return the most recent healing log entries
        return self.repair_system.healing_log[-limit:]

    async def check_memory_health(self, memory_id: str) -> dict[str, Any]:
        """Check the health status of a specific memory"""
        health_status = {
            "memory_id": memory_id,
            "is_healthy": True,
            "has_scar_tissue": False,
            "active_trauma": False,
            "repair_history": [],
        }

        # Check for active trauma
        for trauma in self.repair_system.active_traumas.values():
            if hasattr(trauma, "memory_id") and trauma.memory_id == memory_id:
                health_status["active_trauma"] = True
                health_status["is_healthy"] = False
                break

        # Check for scar tissue
        if memory_id in self.repair_system.scar_tissue:
            health_status["has_scar_tissue"] = True
            health_status["scar_details"] = self.repair_system.scar_tissue[memory_id]

        # Check healing history
        for entry in self.repair_system.healing_log:
            if entry.get("memory_id") == memory_id:
                health_status["repair_history"].append(
                    {
                        "timestamp": entry.get("timestamp"),
                        "repair_type": entry.get("repair_type"),
                        "success": entry.get("success", False),
                    }
                )

        return health_status


def get_memory_trauma_repair() -> Optional[MemoryTraumaRepair]:
    """Factory function to create memory trauma repair"""
    if not TRAUMA_REPAIR_AVAILABLE:
        logger.warning("Trauma repair not available")
        return None

    if USING_MOCK:
        try:
            return get_mock_trauma_repair()
        except Exception as e:
            logger.error(f"Failed to create mock trauma repair: {e}")
            return None
    else:
        try:
            return MemoryTraumaRepair()
        except Exception as e:
            logger.error(f"Failed to create trauma repair: {e}")
            return None
