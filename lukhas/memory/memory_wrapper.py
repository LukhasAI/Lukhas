"""
LUKHAS AI Memory Wrapper
Production-safe wrapper for memory operations with feature flag control
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""
import os
import time
from typing import Any, Optional

try:
    from lukhas.observability.matriz_decorators import matriz_record

    def emit_node(node_type):
        return matriz_record(node_type)

except ImportError:

    def emit_node(node_type):
        _ = node_type

        def decorator(func):
            return func

        return decorator


from .fold_system import get_fold_manager


class MemoryWrapper:
    """Production-safe wrapper for memory operations"""

    def __init__(self) -> None:
        self.fold_manager = get_fold_manager()
        self._operation_count = 0
        self._error_count = 0

    def _is_memory_active(self) -> bool:
        """Check if memory system is active via feature flag"""
        # Check environment variable for MEMORY_ACTIVE flag
        return os.getenv("MEMORY_ACTIVE", "false").lower() == "true"

    def _get_mode(self, requested_mode: str = "auto") -> str:
        """Determine operation mode based on feature flags"""
        if requested_mode == "dry_run":
            return "dry_run"
        elif requested_mode == "live" and self._is_memory_active():
            return "live"
        else:
            # Default to dry_run for safety
            return "dry_run"

    @emit_node("memory:wrapper:create_fold")
    def create_fold(
        self,
        content: Any,
        causal_chain: Optional[list[str]] = None,
        emotional_valence: float = 0.0,
        importance: float = 0.5,
        mode: str = "auto",
    ) -> dict[str, Any]:
        """Create a memory fold with comprehensive error handling"""
        start_time = time.time()
        effective_mode = self._get_mode(mode)

        try:
            self._operation_count += 1

            # Validate inputs
            if emotional_valence < -1.0 or emotional_valence > 1.0:
                raise ValueError("emotional_valence must be between -1.0 and 1.0")

            if importance < 0.0 or importance > 1.0:
                raise ValueError("importance must be between 0.0 and 1.0")

            # Create fold through manager
            fold = self.fold_manager.create_fold(
                content=content,
                causal_chain=causal_chain,
                emotional_valence=emotional_valence,
                importance=importance,
                mode=effective_mode,
            )

            operation_time = (time.time() - start_time) * 1000

            return {
                "ok": True,
                "fold_id": fold.id,
                "mode": effective_mode,
                "stored": effective_mode == "live",
                "operation_time_ms": operation_time,
                "fold_data": {
                    "emotional_valence": fold.emotional_valence,
                    "importance": fold.importance,
                    "causal_chain_length": len(fold.causal_chain),
                    "timestamp": fold.timestamp.isoformat(),
                },
            }

        except Exception as e:
            self._error_count += 1
            return {
                "ok": False,
                "error": str(e),
                "mode": effective_mode,
                "operation_time_ms": (time.time() - start_time) * 1000,
            }

    @emit_node("memory:wrapper:consolidate")
    def consolidate_memory(self, threshold: float = 0.5, mode: str = "auto") -> dict[str, Any]:
        """Consolidate memory with safety checks"""
        _ = threshold
        start_time = time.time()
        effective_mode = self._get_mode(mode)

        try:
            self._operation_count += 1

            # Get current status first
            status = self.fold_manager.get_status(mode=effective_mode)

            # Only consolidate if healthy and needed
            if not status.get("memory_healthy", True):
                return {
                    "ok": False,
                    "error": "memory_unhealthy",
                    "mode": effective_mode,
                    "status": status,
                }

            # Perform consolidation
            result = self.fold_manager.consolidate(mode=effective_mode)

            operation_time = (time.time() - start_time) * 1000
            result["operation_time_ms"] = operation_time

            return result

        except Exception as e:
            self._error_count += 1
            return {
                "ok": False,
                "error": str(e),
                "mode": effective_mode,
                "operation_time_ms": (time.time() - start_time) * 1000,
            }

    @emit_node("memory:wrapper:access")
    def access_memory(self, query: dict[str, Any], mode: str = "auto") -> dict[str, Any]:
        """Access memory with query processing"""
        start_time = time.time()
        effective_mode = self._get_mode(mode)

        try:
            self._operation_count += 1

            # Handle different query types
            if "fold_id" in query:
                # Direct fold access
                fold = self.fold_manager.retrieve_fold(query["fold_id"], mode=effective_mode)

                if fold:
                    return {
                        "ok": True,
                        "mode": effective_mode,
                        "results": [fold],
                        "query": query,
                        "operation_time_ms": (time.time() - start_time) * 1000,
                    }
                else:
                    return {
                        "ok": True,
                        "mode": effective_mode,
                        "results": [],
                        "query": query,
                        "message": "fold_not_found",
                        "operation_time_ms": (time.time() - start_time) * 1000,
                    }

            elif "causal_chain" in query:
                # Causal chain query
                if "fold_id" in query["causal_chain"]:
                    chain = self.fold_manager.get_causal_chain(query["causal_chain"]["fold_id"])
                    return {
                        "ok": True,
                        "mode": effective_mode,
                        "results": chain,
                        "query": query,
                        "operation_time_ms": (time.time() - start_time) * 1000,
                    }

            # Default: return empty results for dry_run
            return {
                "ok": True,
                "mode": effective_mode,
                "results": [],
                "query": query,
                "simulated": effective_mode == "dry_run",
                "operation_time_ms": (time.time() - start_time) * 1000,
            }

        except Exception as e:
            self._error_count += 1
            return {
                "ok": False,
                "error": str(e),
                "mode": effective_mode,
                "query": query,
                "operation_time_ms": (time.time() - start_time) * 1000,
            }

    @emit_node("memory:wrapper:status")
    def get_status(self) -> dict[str, Any]:
        """Get comprehensive memory system status"""
        try:
            # Get underlying system status
            system_status = self.fold_manager.get_status()

            # Add wrapper-level metrics
            error_rate = self._error_count / max(self._operation_count, 1)

            return {
                "ok": True,
                "memory_active": self._is_memory_active(),
                "wrapper_metrics": {
                    "total_operations": self._operation_count,
                    "error_count": self._error_count,
                    "error_rate": error_rate,
                    "health_status": "healthy" if error_rate < 0.05 else "degraded",
                },
                "system_status": system_status,
                "feature_flags": {"MEMORY_ACTIVE": self._is_memory_active()},
            }

        except Exception as e:
            return {"ok": False, "error": str(e), "memory_active": False}

    def extend_causal_chain(self, fold_id: str, new_event: str, mode: str = "auto") -> dict[str, Any]:
        """Extend causal chain for a fold"""
        effective_mode = self._get_mode(mode)

        try:
            if effective_mode == "dry_run":
                return {
                    "ok": True,
                    "mode": "dry_run",
                    "extended": False,
                    "simulated": True,
                }

            fold = self.fold_manager.retrieve_fold(fold_id, mode="live")
            if not fold:
                return {"ok": False, "error": "fold_not_found", "mode": effective_mode}

            # Extend chain
            fold.causal_chain.append(new_event)

            return {
                "ok": True,
                "mode": effective_mode,
                "extended": True,
                "new_chain_length": len(fold.causal_chain),
            }

        except Exception as e:
            return {"ok": False, "error": str(e), "mode": effective_mode}

    def update_valence(self, fold_id: str, new_valence: float, mode: str = "auto") -> dict[str, Any]:
        """Update emotional valence for a fold"""
        effective_mode = self._get_mode(mode)

        try:
            # Validate valence range
            if new_valence < -1.0 or new_valence > 1.0:
                return {
                    "ok": False,
                    "error": "valence_out_of_range",
                    "valid_range": [-1.0, 1.0],
                    "mode": effective_mode,
                }

            if effective_mode == "dry_run":
                return {
                    "ok": True,
                    "mode": "dry_run",
                    "updated": False,
                    "simulated": True,
                }

            fold = self.fold_manager.retrieve_fold(fold_id, mode="live")
            if not fold:
                return {"ok": False, "error": "fold_not_found", "mode": effective_mode}

            # Update valence
            old_valence = fold.emotional_valence
            fold.emotional_valence = new_valence

            return {
                "ok": True,
                "mode": effective_mode,
                "updated": True,
                "old_valence": old_valence,
                "new_valence": new_valence,
            }

        except Exception as e:
            return {"ok": False, "error": str(e), "mode": effective_mode}


# Global singleton instance
_memory_wrapper = None


def get_memory_manager() -> MemoryWrapper:
    """Get or create the global memory wrapper instance"""
    global _memory_wrapper
    if _memory_wrapper is None:
        _memory_wrapper = MemoryWrapper()
    return _memory_wrapper
