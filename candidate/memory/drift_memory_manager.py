"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - DRIFT MEMORY MANAGER
║ Memory management with symbolic drift tracking and adaptation
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: drift_memory_manager.py
║ Path: lukhas/memory/drift_memory_manager.py
║ Version: 1.0.0 | Created: 2025-07-26
║ Authors: LUKHAS AI Architecture Team
╚══════════════════════════════════════════════════════════════════════════════════
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import numpy as np

from .base_manager import BaseMemoryManager


class DriftMemoryManager(BaseMemoryManager):
    """
    Memory manager with symbolic drift tracking and adaptation.

    Extends BaseMemoryManager with:
    - Symbolic drift detection and tracking
    - Memory evolution monitoring
    - Drift pattern analysis
    - Adaptive memory corrections
    - Temporal drift tracking
    """

    def __init__(self, config: Optional[dict[str, Any]] = None, base_path: Optional[Path] = None):
        """Initialize drift memory manager."""
        super().__init__(config, base_path)

        # Drift configuration
        self.drift_config = {
            "drift_threshold": 0.15,
            "max_drift_rate": 0.05,
            "correction_strength": 0.3,
            "history_window": 10,
            "analysis_interval": timedelta(hours=1),
            **self.config.get("drift", {}),
        }

        # Drift tracking
        self.drift_states: dict[str, dict[str, Any]] = {}
        self.drift_history: dict[str, list[dict[str, Any]]] = {}
        self.reference_states: dict[str, dict[str, Any]] = {}
        self.drift_patterns: dict[str, Any] = {}

        self.logger.info("DriftMemoryManager initialized", drift_config=self.drift_config)

    async def store(
        self,
        memory_data: dict[str, Any],
        memory_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Store memory with drift baseline establishment.

        Creates reference state for future drift detection.
        """
        # Generate ID if not provided
        if not memory_id:
            memory_id = self.generate_memory_id("dmem")

        try:
            # Create symbolic representation for drift tracking
            symbolic_state = self._create_symbolic_state(memory_data)

            # Store as reference state
            self.reference_states[memory_id] = {
                "symbolic": symbolic_state,
                "timestamp": datetime.now(timezone.utc),
                "data_hash": self._compute_data_hash(memory_data),
            }

            # Initialize drift tracking
            self.drift_states[memory_id] = {
                "current_state": symbolic_state.copy(),
                "drift_magnitude": 0.0,
                "drift_vector": np.zeros(len(symbolic_state.get("vector", []))).tolist(),
                "last_checked": datetime.now(timezone.utc),
            }

            self.drift_history[memory_id] = []

            # Prepare enhanced metadata
            enhanced_metadata = {
                **(metadata or {}),
                "drift_tracking": {
                    "enabled": True,
                    "baseline_established": True,
                    "drift_magnitude": 0.0,
                },
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            # Package memory with drift data
            memory_package = {
                "data": memory_data,
                "metadata": enhanced_metadata,
                "drift": {
                    "reference_state": symbolic_state,
                    "current_state": symbolic_state.copy(),
                    "history": [],
                },
            }

            # Save to disk
            self._save_to_disk(memory_id, memory_package)

            # Update index
            self._update_index(memory_id, enhanced_metadata)

            self.logger.info(
                "Drift memory stored with baseline",
                memory_id=memory_id,
                symbolic_dimensions=len(symbolic_state.get("vector", [])),
            )

            return {
                "status": "success",
                "memory_id": memory_id,
                "drift_baseline_established": True,
                "initial_state": symbolic_state,
            }

        except Exception as e:
            self.logger.error("Failed to store drift memory", memory_id=memory_id, error=str(e))
            return {"status": "error", "memory_id": memory_id, "error": str(e)}

    async def retrieve(self, memory_id: str, context: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """
        Retrieve memory with drift analysis.

        Checks for drift and applies corrections if needed.
        """
        try:
            # Load memory package
            memory_package = self._load_from_disk(memory_id)

            # Check for drift
            drift_info = await self._analyze_drift(memory_id)

            # Apply drift correction if needed
            if drift_info["drift_detected"] and context and context.get("apply_correction", False):
                corrected_data = self._apply_drift_correction(memory_package["data"], drift_info)
            else:
                corrected_data = memory_package["data"]

            # Update drift state
            if memory_id in self.drift_states:
                self.drift_states[memory_id]["last_checked"] = datetime.now(timezone.utc)

            self.logger.info(
                "Drift memory retrieved",
                memory_id=memory_id,
                drift_magnitude=drift_info.get("magnitude", 0),
            )

            return {
                "status": "success",
                "data": corrected_data,
                "metadata": {
                    **memory_package["metadata"],
                    "drift_info": drift_info,
                    "correction_applied": drift_info["drift_detected"]
                    and context
                    and context.get("apply_correction", False),
                },
            }

        except FileNotFoundError:
            self.logger.error("Memory not found", memory_id=memory_id)
            return {"status": "error", "error": f"Memory not found: {memory_id}"}
        except Exception as e:
            self.logger.error("Failed to retrieve drift memory", memory_id=memory_id, error=str(e))
            return {"status": "error", "memory_id": memory_id, "error": str(e)}

    async def update(self, memory_id: str, updates: dict[str, Any], merge: bool = True) -> dict[str, Any]:
        """Update memory with drift tracking."""
        try:
            # Retrieve current state
            current = await self.retrieve(memory_id)
            if current["status"] == "error":
                return current

            # Update data
            updated_data = {**current["data"], **updates} if merge else updates

            # Update symbolic state and track drift
            new_symbolic_state = self._create_symbolic_state(updated_data)

            # Calculate drift from reference
            if memory_id in self.reference_states:
                drift_vector = self._calculate_drift_vector(
                    self.reference_states[memory_id]["symbolic"], new_symbolic_state
                )
                drift_magnitude = np.linalg.norm(drift_vector)

                # Update drift state
                self.drift_states[memory_id] = {
                    "current_state": new_symbolic_state,
                    "drift_magnitude": drift_magnitude,
                    "drift_vector": drift_vector.tolist(),
                    "last_checked": datetime.now(timezone.utc),
                }

                # Record drift event
                self._record_drift_event(
                    memory_id,
                    {
                        "timestamp": datetime.now(timezone.utc),
                        "magnitude": drift_magnitude,
                        "vector": drift_vector.tolist(),
                        "trigger": "update",
                    },
                )

            # Store updated memory
            result = await self.store(
                updated_data,
                memory_id,
                {
                    **current["metadata"],
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
            )

            self.logger.info(
                "Drift memory updated",
                memory_id=memory_id,
                drift_change=(drift_magnitude if memory_id in self.reference_states else 0),
            )

            return result

        except Exception as e:
            self.logger.error("Failed to update drift memory", memory_id=memory_id, error=str(e))
            return {"status": "error", "memory_id": memory_id, "error": str(e)}

    async def delete(self, memory_id: str, soft_delete: bool = True) -> dict[str, Any]:
        """Delete memory with drift cleanup."""
        try:
            # Clean up drift tracking
            if memory_id in self.drift_states:
                del self.drift_states[memory_id]
            if memory_id in self.drift_history:
                del self.drift_history[memory_id]
            if memory_id in self.reference_states:
                del self.reference_states[memory_id]

            if soft_delete:
                # Mark as deleted in index
                if memory_id in self._memory_index:
                    self._memory_index[memory_id]["deleted"] = True
                    self._memory_index[memory_id]["deleted_at"] = datetime.now(timezone.utc).isoformat()
                    self._save_index()
            else:
                # Remove from disk
                file_path = self.base_path / f"{memory_id}.json"
                if file_path.exists():
                    file_path.unlink()

                # Remove from index
                if memory_id in self._memory_index:
                    del self._memory_index[memory_id]
                    self._save_index()

            self.logger.info("Drift memory deleted", memory_id=memory_id, soft_delete=soft_delete)

            return {"status": "success"}

        except Exception as e:
            self.logger.error("Failed to delete drift memory", memory_id=memory_id, error=str(e))
            return {"status": "error", "memory_id": memory_id, "error": str(e)}

    async def search(self, criteria: dict[str, Any], limit: Optional[int] = None) -> list[dict[str, Any]]:
        """
        Search memories with drift-aware filtering.

        Supports drift magnitude and pattern searches.
        """
        results = []

        # Extract drift-specific criteria
        max_drift = criteria.pop("max_drift", float("inf"))
        min_drift = criteria.pop("min_drift", 0.0)
        drift_pattern = criteria.pop("drift_pattern", None)

        for memory_id, index_data in self._memory_index.items():
            # Skip deleted memories
            if index_data.get("deleted", False):
                continue

            # Check drift criteria
            drift_state = self.drift_states.get(memory_id, {})
            drift_magnitude = drift_state.get("drift_magnitude", 0.0)

            if not (min_drift <= drift_magnitude <= max_drift):
                continue

            # Check drift pattern if specified
            if drift_pattern and memory_id in self.drift_patterns:
                if not self._matches_drift_pattern(self.drift_patterns[memory_id], drift_pattern):
                    continue

            # Load and check other criteria
            try:
                memory_data = self._load_from_disk(memory_id)
                if self._matches_criteria(memory_data["data"], criteria):
                    results.append(
                        {
                            "memory_id": memory_id,
                            "data": memory_data["data"],
                            "drift_magnitude": drift_magnitude,
                            "metadata": index_data,
                        }
                    )
            except Exception as e:
                self.logger.warning(
                    "Failed to load memory during search",
                    memory_id=memory_id,
                    error=str(e),
                )

        # Sort by drift magnitude if no specific order requested
        results.sort(key=lambda x: x["drift_magnitude"])

        # Apply limit
        if limit and len(results) > limit:
            results = results[:limit]

        return results

    # === Drift-specific methods ===

    async def analyze_drift_patterns(self) -> dict[str, Any]:
        """Analyze drift patterns across all memories."""
        patterns = {
            "total_memories": len(self.drift_states),
            "drifting_memories": 0,
            "average_drift": 0.0,
            "max_drift": 0.0,
            "drift_distribution": {},
            "common_patterns": [],
        }

        total_drift = 0.0
        drift_magnitudes = []

        for drift_state in self.drift_states.values():
            magnitude = drift_state.get("drift_magnitude", 0.0)
            drift_magnitudes.append(magnitude)
            total_drift += magnitude

            if magnitude > self.drift_config["drift_threshold"]:
                patterns["drifting_memories"] += 1

            patterns["max_drift"] = max(patterns["max_drift"], magnitude)

        if drift_magnitudes:
            patterns["average_drift"] = total_drift / len(drift_magnitudes)

            # Calculate drift distribution
            patterns["drift_distribution"] = {
                "minimal": sum(1 for d in drift_magnitudes if d < 0.1),
                "low": sum(1 for d in drift_magnitudes if 0.1 <= d < 0.3),
                "moderate": sum(1 for d in drift_magnitudes if 0.3 <= d < 0.5),
                "high": sum(1 for d in drift_magnitudes if d >= 0.5),
            }

        # Identify common patterns
        patterns["common_patterns"] = self._identify_common_drift_patterns()

        return patterns

    async def get_drift_history(self, memory_id: str) -> dict[str, Any]:
        """Get detailed drift history for a memory."""
        if memory_id not in self.drift_history:
            return {
                "status": "error",
                "error": f"No drift history found for memory: {memory_id}",
            }

        history = self.drift_history[memory_id]

        # Calculate drift statistics
        if history:
            magnitudes = [event["magnitude"] for event in history]
            return {
                "status": "success",
                "memory_id": memory_id,
                "drift_history": history,
                "statistics": {
                    "total_events": len(history),
                    "average_magnitude": np.mean(magnitudes),
                    "max_magnitude": max(magnitudes),
                    "min_magnitude": min(magnitudes),
                    "trend": self._calculate_drift_trend(history),
                },
            }
        else:
            return {
                "status": "success",
                "memory_id": memory_id,
                "drift_history": [],
                "statistics": {
                    "total_events": 0,
                    "message": "No drift events recorded",
                },
            }

    async def correct_drift(self, memory_id: str, correction_strength: Optional[float] = None) -> dict[str, Any]:
        """Manually correct drift for a memory."""
        try:
            # Verify memory exists
            memory = await self.retrieve(memory_id)
            if memory["status"] == "error":
                return memory

            # Get current drift state
            if memory_id not in self.drift_states:
                return {"status": "error", "error": "No drift state found for memory"}

            drift_state = self.drift_states[memory_id]
            reference_state = self.reference_states.get(memory_id)

            if not reference_state:
                return {
                    "status": "error",
                    "error": "No reference state found for drift correction",
                }

            # Apply correction
            strength = correction_strength or self.drift_config["correction_strength"]
            corrected_state = self._apply_state_correction(
                drift_state["current_state"], reference_state["symbolic"], strength
            )

            # Update drift state
            self.drift_states[memory_id]["current_state"] = corrected_state
            self.drift_states[memory_id]["drift_magnitude"] *= 1 - strength

            # Record correction event
            self._record_drift_event(
                memory_id,
                {
                    "timestamp": datetime.now(timezone.utc),
                    "magnitude": self.drift_states[memory_id]["drift_magnitude"],
                    "vector": self.drift_states[memory_id]["drift_vector"],
                    "trigger": "manual_correction",
                    "correction_strength": strength,
                },
            )

            self.logger.info(
                "Drift correction applied",
                memory_id=memory_id,
                correction_strength=strength,
            )

            return {
                "status": "success",
                "memory_id": memory_id,
                "correction_applied": True,
                "new_drift_magnitude": self.drift_states[memory_id]["drift_magnitude"],
            }

        except Exception as e:
            self.logger.error("Failed to correct drift", memory_id=memory_id, error=str(e))
            return {"status": "error", "memory_id": memory_id, "error": str(e)}

    # === Private helper methods ===

    def _create_symbolic_state(self, memory_data: dict[str, Any]) -> dict[str, Any]:
        """Create symbolic representation of memory for drift tracking."""
        # Convert memory data to string for analysis
        data_str = json.dumps(memory_data, sort_keys=True)

        # Create feature vector
        features = []

        # Length feature
        features.append(len(data_str) / 1000.0)  # Normalized

        # Character distribution features
        char_counts = {}
        for char in data_str:
            char_counts[char] = char_counts.get(char, 0) + 1

        # Add top character frequencies as features
        sorted_chars = sorted(char_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for char, count in sorted_chars:
            features.append(count / len(data_str))

        # Pad to fixed length
        while len(features) < 20:
            features.append(0.0)

        return {
            "vector": features[:20],  # Fixed size vector
            "hash": self._compute_data_hash(memory_data),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _compute_data_hash(self, data: dict[str, Any]) -> str:
        """Compute hash of data for change detection."""
        import hashlib

        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]

    def _calculate_drift_vector(self, reference_state: dict[str, Any], current_state: dict[str, Any]) -> np.ndarray:
        """Calculate drift vector between states."""
        ref_vector = np.array(reference_state.get("vector", []))
        curr_vector = np.array(current_state.get("vector", []))

        # Ensure same dimensions
        if len(ref_vector) != len(curr_vector):
            min_len = min(len(ref_vector), len(curr_vector))
            ref_vector = ref_vector[:min_len]
            curr_vector = curr_vector[:min_len]

        return curr_vector - ref_vector

    async def _analyze_drift(self, memory_id: str) -> dict[str, Any]:
        """Analyze drift for a specific memory."""
        drift_info = {
            "drift_detected": False,
            "magnitude": 0.0,
            "direction": None,
            "rate": 0.0,
        }

        if memory_id not in self.drift_states:
            return drift_info

        drift_state = self.drift_states[memory_id]
        drift_info["magnitude"] = drift_state.get("drift_magnitude", 0.0)

        # Check if drift exceeds threshold
        if drift_info["magnitude"] > self.drift_config["drift_threshold"]:
            drift_info["drift_detected"] = True

            # Calculate drift direction
            drift_vector = np.array(drift_state.get("drift_vector", []))
            if drift_vector.size > 0:
                drift_info["direction"] = drift_vector / (np.linalg.norm(drift_vector) + 1e-8)
                drift_info["direction"] = drift_info["direction"].tolist()

            # Calculate drift rate if history available
            if memory_id in self.drift_history and len(self.drift_history[memory_id]) > 1:
                recent_events = self.drift_history[memory_id][-2:]
                time_diff = (recent_events[1]["timestamp"] - recent_events[0]["timestamp"]).total_seconds()
                if time_diff > 0:
                    magnitude_diff = recent_events[1]["magnitude"] - recent_events[0]["magnitude"]
                    drift_info["rate"] = magnitude_diff / time_diff

        return drift_info

    def _apply_drift_correction(self, memory_data: dict[str, Any], drift_info: dict[str, Any]) -> dict[str, Any]:
        """Apply correction to memory data based on drift analysis."""
        # Simple correction - in practice would be more sophisticated
        corrected_data = memory_data.copy()

        # Add correction metadata
        corrected_data["_drift_correction"] = {
            "applied_at": datetime.now(timezone.utc).isoformat(),
            "drift_magnitude": drift_info["magnitude"],
            "correction_type": "standard",
        }

        return corrected_data

    def _apply_state_correction(
        self,
        current_state: dict[str, Any],
        reference_state: dict[str, Any],
        strength: float,
    ) -> dict[str, Any]:
        """Apply correction to symbolic state."""
        curr_vector = np.array(current_state.get("vector", []))
        ref_vector = np.array(reference_state.get("vector", []))

        # Blend vectors based on correction strength
        corrected_vector = curr_vector * (1 - strength) + ref_vector * strength

        return {
            **current_state,
            "vector": corrected_vector.tolist(),
            "corrected": True,
            "correction_strength": strength,
        }

    def _record_drift_event(self, memory_id: str, event: dict[str, Any]) -> None:
        """Record a drift event in history."""
        if memory_id not in self.drift_history:
            self.drift_history[memory_id] = []

        self.drift_history[memory_id].append(event)

        # Keep only recent history
        window_size = self.drift_config["history_window"]
        if len(self.drift_history[memory_id]) > window_size:
            self.drift_history[memory_id] = self.drift_history[memory_id][-window_size:]

    def _identify_common_drift_patterns(self) -> list[dict[str, Any]]:
        """Identify common drift patterns across memories."""
        patterns = []

        # Group memories by similar drift vectors
        drift_groups = {}

        for memory_id, drift_state in self.drift_states.items():
            if drift_state["drift_magnitude"] < self.drift_config["drift_threshold"]:
                continue

            # Find similar drift patterns
            vector = np.array(drift_state.get("drift_vector", []))
            if vector.size == 0:
                continue

            # Normalize vector for comparison
            norm_vector = vector / (np.linalg.norm(vector) + 1e-8)

            # Simple clustering - find similar vectors
            found_group = False
            for group_id, group_data in drift_groups.items():
                group_vector = np.array(group_data["vector"])
                similarity = np.dot(norm_vector, group_vector)

                if similarity > 0.8:  # High similarity threshold
                    group_data["members"].append(memory_id)
                    found_group = True
                    break

            if not found_group:
                drift_groups[len(drift_groups)] = {
                    "vector": norm_vector.tolist(),
                    "members": [memory_id],
                }

        # Convert groups to patterns
        for group_id, group_data in drift_groups.items():
            if len(group_data["members"]) > 1:  # Pattern requires multiple members
                patterns.append(
                    {
                        "pattern_id": f"pattern_{group_id}",
                        "member_count": len(group_data["members"]),
                        "drift_direction": group_data["vector"],
                        "example_memories": group_data["members"][:3],  # First 3 examples
                    }
                )

        return patterns

    def _calculate_drift_trend(self, history: list[dict[str, Any]]) -> str:
        """Calculate drift trend from history."""
        if len(history) < 2:
            return "stable"

        # Get recent magnitudes
        recent_magnitudes = [event["magnitude"] for event in history[-5:]]

        # Calculate trend
        if len(recent_magnitudes) > 1:
            diffs = [recent_magnitudes[i + 1] - recent_magnitudes[i] for i in range(len(recent_magnitudes) - 1)]
            avg_diff = np.mean(diffs)

            if avg_diff > 0.01:
                return "increasing"
            elif avg_diff < -0.01:
                return "decreasing"

        return "stable"

    def _matches_drift_pattern(self, memory_pattern: dict[str, Any], search_pattern: dict[str, Any]) -> bool:
        """Check if memory matches drift pattern criteria."""
        # Simple pattern matching - could be more sophisticated
        for key, value in search_pattern.items():
            if key not in memory_pattern:
                return False
            if memory_pattern[key] != value:
                return False
        return True

    def _matches_criteria(self, data: dict[str, Any], criteria: dict[str, Any]) -> bool:
        """Check if data matches search criteria."""
        for key, value in criteria.items():
            if key not in data:
                return False
            if data[key] != value:
                return False
        return True

    async def get_statistics(self) -> dict[str, Any]:
        """Get drift memory statistics."""
        base_stats = await super().get_statistics()

        # Calculate drift statistics
        drift_magnitudes = [state.get("drift_magnitude", 0.0) for state in self.drift_states.values()]

        drifting_count = sum(1 for mag in drift_magnitudes if mag > self.drift_config["drift_threshold"])

        # Add drift-specific stats
        drift_stats = {
            **base_stats,
            "drift_tracking_enabled": len(self.drift_states),
            "drifting_memories": drifting_count,
            "average_drift": np.mean(drift_magnitudes) if drift_magnitudes else 0.0,
            "max_drift": max(drift_magnitudes) if drift_magnitudes else 0.0,
            "drift_threshold": self.drift_config["drift_threshold"],
            "total_drift_events": sum(len(h) for h in self.drift_history.values()),
        }

        return drift_stats
