#!/usr/bin/env python3
import logging

logger = logging.getLogger(__name__)
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🔌 LUKHAS AI - MEMORY SAFETY INTEGRATION ADAPTERS
║ Connects safety features with existing LUKHAS modules
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: integration_adapters.py
║ Path: memory/systems/integration_adapters.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Integration Team
╠══════════════════════════════════════════════════════════════════════════════════
║ ΛTAG: ΛMEMORY, ΛINTEGRATION, ΛSAFETY, ΛVERIFOLD, ΛDRIFT
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Callable, Optional

import numpy as np

from .hybrid_memory_fold import HybridMemoryFold
from .memory_safety_features import MemorySafetySystem, VerifoldEntry


class VerifoldRegistryAdapter:
    """
    Adapter to integrate Verifold Registry with existing modules.

    Provides trust scoring and verification for all module interactions.
    """

    def __init__(self, safety_system: MemorySafetySystem):
        self.safety = safety_system
        self._trust_callbacks: dict[str, list[Callable]] = {}

    def register_trust_callback(self, module_name: str, callback: Callable):
        """Register a callback for trust score updates"""
        if module_name not in self._trust_callbacks:
            self._trust_callbacks[module_name] = []
        self._trust_callbacks[module_name].append(callback)

    async def verify_for_module(
        self, module_name: str, memory_id: str, memory_data: dict[str, Any]
    ) -> tuple[bool, float, Optional[str]]:
        """
        Verify memory for a specific module.

        Returns: (is_valid, trust_score, error_message)
        """
        # Check if memory is in verifold registry
        if memory_id not in self.safety.verifold_registry:
            return False, 0.0, "Memory not in verifold registry"

        entry = self.safety.verifold_registry[memory_id]

        # Verify integrity
        expected_hash = entry.collapse_hash
        is_valid, error = await self.safety.verify_memory_integrity(memory_id, memory_data, expected_hash)

        if not is_valid:
            # Notify callbacks of failed verification
            await self._notify_trust_update(module_name, memory_id, 0.0)
            return False, 0.0, error

        # Calculate trust score based on verification history
        trust_score = self._calculate_trust_score(entry)

        # Notify callbacks
        await self._notify_trust_update(module_name, memory_id, trust_score)

        return True, trust_score, None

    def _calculate_trust_score(self, entry: VerifoldEntry) -> float:
        """Calculate trust score based on verification history"""
        base_score = entry.integrity_score

        # Boost for frequent successful verifications
        if entry.verification_count > 10:
            base_score *= 1.1

        # Penalty for suspicious modifications
        if entry.suspicious_modifications:
            penalty = 0.9 ** len(entry.suspicious_modifications)
            base_score *= penalty

        # Time decay - newer memories have slightly lower trust
        age = (datetime.now(timezone.utc) - entry.creation_time).total_seconds() / 86400
        if age < 1:  # Less than 1 day old
            base_score *= 0.95

        return min(1.0, base_score)

    async def _notify_trust_update(self, module_name: str, memory_id: str, trust_score: float):
        """Notify registered callbacks of trust updates"""
        if module_name in self._trust_callbacks:
            for callback in self._trust_callbacks[module_name]:
                try:
                    await callback(memory_id, trust_score)
                except Exception as e:
                    logger.error("Trust callback failed", module=module_name, error=str(e))

    def get_module_trust_report(self, module_name: str) -> dict[str, Any]:
        """Get trust statistics for a specific module"""
        # In production, would track per-module verification stats
        return {
            "module": module_name,
            "total_verifications": len(self.safety.verifold_registry),
            "average_trust": (
                np.mean([self._calculate_trust_score(e) for e in self.safety.verifold_registry.values()])
                if self.safety.verifold_registry
                else 1.0
            ),
            "callbacks_registered": len(self._trust_callbacks.get(module_name, [])),
        }


class DriftMetricsAdapter:
    """
    Adapter for drift metrics integration with learning and meta modules.

    Provides drift-aware updates and calibration triggers.
    """

    def __init__(self, safety_system: MemorySafetySystem):
        self.safety = safety_system
        self._drift_thresholds: dict[str, float] = {}
        self._calibration_callbacks: dict[str, list[Callable]] = {}

    def set_module_drift_threshold(self, module_name: str, threshold: float):
        """Set custom drift threshold for a module"""
        self._drift_thresholds[module_name] = threshold

    def register_calibration_callback(self, module_name: str, callback: Callable):
        """Register callback for when calibration is needed"""
        if module_name not in self._calibration_callbacks:
            self._calibration_callbacks[module_name] = []
        self._calibration_callbacks[module_name].append(callback)

    async def track_module_usage(
        self, module_name: str, tag: str, embedding: np.ndarray, context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Track drift for module-specific usage.

        Returns drift analysis including recommendations.
        """
        # Add module context
        enriched_context = {
            **context,
            "module": module_name,
            "timestamp": datetime.now(timezone.utc),
        }

        # Track drift
        drift_score = self.safety.track_drift(tag, embedding, enriched_context)

        # Get module threshold
        threshold = self._drift_thresholds.get(module_name, self.safety.max_drift_threshold)

        # Check if calibration needed
        needs_calibration = drift_score > threshold

        if needs_calibration:
            await self._trigger_calibration(module_name, tag, drift_score)

        return {
            "tag": tag,
            "drift_score": drift_score,
            "threshold": threshold,
            "needs_calibration": needs_calibration,
            "recommendation": self._get_drift_recommendation(drift_score, threshold),
        }

    def _get_drift_recommendation(self, drift_score: float, threshold: float) -> str:
        """Get recommendation based on drift score"""
        ratio = drift_score / threshold

        if ratio < 0.5:
            return "stable"
        elif ratio < 0.8:
            return "monitor"
        elif ratio < 1.0:
            return "warning"
        else:
            return "calibrate"

    async def _trigger_calibration(self, module_name: str, tag: str, drift_score: float):
        """Trigger calibration callbacks"""
        if module_name in self._calibration_callbacks:
            for callback in self._calibration_callbacks[module_name]:
                try:
                    await callback(tag, drift_score)
                except Exception as e:
                    logger.error(
                        "Calibration callback failed",
                        module=module_name,
                        tag=tag,
                        error=str(e),
                    )

    def get_module_drift_report(self, module_name: str) -> dict[str, Any]:
        """Get drift analysis for a module"""
        module_tags = []

        # Find tags used by this module
        for tag, metrics in self.safety.drift_metrics.items():
            for usage in metrics.recent_uses:
                if usage.get("context", {}).get("module") == module_name:
                    module_tags.append(tag)
                    break

        module_tags = list(set(module_tags))

        # Calculate module-specific drift stats
        drift_scores = []
        for tag in module_tags:
            if tag in self.safety.drift_metrics:
                metrics = self.safety.drift_metrics[tag]
                if metrics.drift_scores:
                    drift_scores.extend(metrics.drift_scores)

        return {
            "module": module_name,
            "tags_tracked": len(module_tags),
            "average_drift": np.mean(drift_scores) if drift_scores else 0.0,
            "max_drift": max(drift_scores) if drift_scores else 0.0,
            "threshold": self._drift_thresholds.get(module_name, self.safety.max_drift_threshold),
        }


class RealityAnchorsAdapter:
    """
    Adapter for reality anchors integration with creativity and voice modules.

    Ensures outputs remain grounded in verified facts.
    """

    def __init__(self, safety_system: MemorySafetySystem):
        self.safety = safety_system
        self._module_anchors: dict[str, dict[str, str]] = {}
        self._validation_callbacks: dict[str, list[Callable]] = {}

    def add_module_anchor(self, module_name: str, key: str, truth: str):
        """Add module-specific reality anchor"""
        if module_name not in self._module_anchors:
            self._module_anchors[module_name] = {}

        self._module_anchors[module_name][key] = truth
        self.safety.add_reality_anchor(f"{module_name}:{key}", truth)

    def register_validation_callback(self, module_name: str, callback: Callable):
        """Register callback for validation results"""
        if module_name not in self._validation_callbacks:
            self._validation_callbacks[module_name] = []
        self._validation_callbacks[module_name].append(callback)

    async def validate_output(
        self, module_name: str, output_data: dict[str, Any], context: dict[str, Any]
    ) -> tuple[bool, list[str]]:
        """
        Validate module output against reality anchors.

        Returns: (is_valid, violations)
        """
        violations = []

        # Check global anchors
        is_valid, error = await self.safety.prevent_hallucination(output_data, context)

        if not is_valid:
            violations.append(error or "Failed global validation")

        # Check module-specific anchors
        if module_name in self._module_anchors:
            for key, truth in self._module_anchors[module_name].items():
                if key in str(output_data):
                    # Simple check - in production would use NLI
                    if not self._check_consistency(output_data, key, truth):
                        violations.append(f"Violates module anchor: {key} = {truth}")

        # Notify callbacks
        await self._notify_validation(module_name, len(violations) == 0, violations)

        return len(violations) == 0, violations

    def _check_consistency(self, data: dict[str, Any], key: str, truth: str) -> bool:
        """Check if data is consistent with anchor"""
        data_str = str(data).lower()
        key_lower = key.lower()
        truth.lower()

        # Basic consistency check
        if key_lower in data_str:
            # Check for negations near the key
            negations = ["not", "isn't", "wasn't", "never", "false"]
            for neg in negations:
                if neg in data_str and key_lower in data_str:
                    # Found potential contradiction
                    return False

        return True

    async def _notify_validation(self, module_name: str, is_valid: bool, violations: list[str]):
        """Notify registered callbacks"""
        if module_name in self._validation_callbacks:
            for callback in self._validation_callbacks[module_name]:
                try:
                    await callback(is_valid, violations)
                except Exception as e:
                    logger.error("Validation callback failed", module=module_name, error=str(e))

    def get_module_anchors(self, module_name: str) -> dict[str, str]:
        """Get reality anchors for a module"""
        return self._module_anchors.get(module_name, {}).copy()


class ConsensusValidationAdapter:
    """
    Adapter for consensus validation with colony/swarm systems.

    Enables distributed memory verification.
    """

    def __init__(self, safety_system: MemorySafetySystem, memory_fold: HybridMemoryFold):
        self.safety = safety_system
        self.memory = memory_fold
        self._colony_validators: dict[str, Callable] = {}
        self._swarm_consensus_threshold = 0.66  # 2/3 majority

    def register_colony_validator(self, colony_id: str, validator: Callable):
        """Register a colony-specific validator"""
        self._colony_validators[colony_id] = validator

    async def validate_with_colonies(
        self,
        memory_id: str,
        memory_data: dict[str, Any],
        participating_colonies: list[str],
    ) -> tuple[bool, float, dict[str, bool]]:
        """
        Validate memory across multiple colonies.

        Returns: (consensus_reached, agreement_ratio, colony_votes)
        """
        if not participating_colonies:
            return True, 1.0, {}

        colony_votes = {}

        # Get validation from each colony
        for colony_id in participating_colonies:
            if colony_id in self._colony_validators:
                try:
                    validator = self._colony_validators[colony_id]
                    vote = await validator(memory_id, memory_data)
                    colony_votes[colony_id] = bool(vote)
                except Exception as e:
                    logger.error("Colony validation failed", colony=colony_id, error=str(e))
                    colony_votes[colony_id] = False
            else:
                # Default to true if no validator
                colony_votes[colony_id] = True

        # Calculate consensus
        positive_votes = sum(1 for v in colony_votes.values() if v)
        agreement_ratio = positive_votes / len(colony_votes)
        consensus_reached = agreement_ratio >= self._swarm_consensus_threshold

        return consensus_reached, agreement_ratio, colony_votes

    async def distributed_memory_verification(
        self, query: str, colonies: list[str], min_consensus_memories: int = 3
    ) -> list[tuple[Any, float]]:
        """
        Retrieve memories with distributed consensus validation.

        Only returns memories that pass colony consensus.
        """
        # Get candidate memories
        candidates = await self.memory.fold_out_semantic(
            query,
            top_k=min_consensus_memories * 3,  # Get extra for filtering
        )

        verified_results = []

        for memory, base_score in candidates:
            memory_id = memory.item_id
            memory_data = memory.data

            # Get similar memories for consensus
            similar_memories = [(m.item_id, m.data, s) for m, s in candidates if m.item_id != memory_id][
                :min_consensus_memories
            ]

            # Local consensus validation
            is_valid, confidence = await self.safety.consensus_validation(memory_id, memory_data, similar_memories)

            if not is_valid:
                continue

            # Colony consensus validation
            consensus_reached, agreement, votes = await self.validate_with_colonies(memory_id, memory_data, colonies)

            if consensus_reached:
                # Adjust score based on consensus strength
                final_score = base_score * confidence * agreement
                verified_results.append((memory, final_score))

                logger.info(
                    "Memory passed distributed consensus",
                    memory_id=memory_id,
                    confidence=confidence,
                    agreement=agreement,
                    colonies=len(votes),
                )

        # Sort by final score
        verified_results.sort(key=lambda x: x[1], reverse=True)

        return verified_results[:min_consensus_memories]

    def set_swarm_threshold(self, threshold: float):
        """Set consensus threshold for swarm validation"""
        self._swarm_consensus_threshold = max(0.5, min(1.0, threshold))

    def get_consensus_report(self) -> dict[str, Any]:
        """Get consensus validation statistics"""
        return {
            "registered_colonies": len(self._colony_validators),
            "swarm_threshold": self._swarm_consensus_threshold,
            "consensus_mechanism": "distributed_voting",
            "validation_strategy": "memory_similarity_and_colony_agreement",
        }


# Unified integration manager
class MemorySafetyIntegration:
    """
    Central integration point for all safety adapters.

    Coordinates safety features across all LUKHAS modules.
    """

    def __init__(self, safety_system: MemorySafetySystem, memory_fold: HybridMemoryFold):
        self.safety = safety_system
        self.memory = memory_fold

        # Initialize adapters
        self.verifold = VerifoldRegistryAdapter(safety_system)
        self.drift = DriftMetricsAdapter(safety_system)
        self.anchors = RealityAnchorsAdapter(safety_system)
        self.consensus = ConsensusValidationAdapter(safety_system, memory_fold)

        logger.info("Memory safety integration initialized")

    async def register_module(self, module_name: str, config: Optional[dict[str, Any]] = None):
        """Register a module for safety integration"""
        config = config or {}

        # Set module-specific configurations
        if "drift_threshold" in config:
            self.drift.set_module_drift_threshold(module_name, config["drift_threshold"])

        if "reality_anchors" in config:
            for key, truth in config["reality_anchors"].items():
                self.anchors.add_module_anchor(module_name, key, truth)

        if "consensus_threshold" in config:
            self.consensus.set_swarm_threshold(config["consensus_threshold"])

        logger.info(
            "Module registered for safety integration",
            module=module_name,
            config=config,
        )

    def get_integration_status(self) -> dict[str, Any]:
        """Get overall integration status"""
        return {
            "safety_report": self.safety.get_safety_report(),
            "verifold_status": {
                "total_modules": len(self.verifold._trust_callbacks),
                "verifications": len(self.safety.verifold_registry),
            },
            "drift_tracking": {
                "modules_tracked": len(self.drift._drift_thresholds),
                "tags_monitored": len(self.safety.drift_metrics),
            },
            "reality_anchors": {
                "global_anchors": len(self.safety.reality_anchors),
                "module_anchors": sum(len(anchors) for anchors in self.anchors._module_anchors.values()),
            },
            "consensus": self.consensus.get_consensus_report(),
        }


# Example usage
async def demonstrate_integration():
    """Demonstrate safety integration with modules"""
    from .hybrid_memory_fold import create_hybrid_memory_fold

    # Create systems
    memory = create_hybrid_memory_fold()
    safety = MemorySafetySystem()

    # Create integration manager
    integration = MemorySafetyIntegration(safety, memory)

    # Register modules
    await integration.register_module(
        "learning",
        {
            "drift_threshold": 0.3,  # More sensitive for learning
        },
    )

    await integration.register_module(
        "creativity",
        {
            "reality_anchors": {
                "physics": "Objects fall down due to gravity",
                "logic": "Contradictions cannot be true",
            }
        },
    )

    await integration.register_module(
        "voice",
        {
            "drift_threshold": 0.6,  # Less sensitive for voice variation
        },
    )

    print("🔌 SAFETY INTEGRATION DEMONSTRATION")
    print("=" * 60)

    # Test verifold integration
    print("\n1. Verifold Registry Integration:")

    test_memory = {"content": "Learning about safety integration", "module": "learning"}

    mem_id = await memory.fold_in_with_embedding(
        data=test_memory,
        tags=["integration", "test"],
        text_content=test_memory["content"],
    )

    # Register in verifold
    safety.verifold_registry[mem_id] = VerifoldEntry(
        memory_id=mem_id,
        collapse_hash=safety.compute_collapse_hash(test_memory),
        creation_time=datetime.now(timezone.utc),
        last_verified=datetime.now(timezone.utc),
    )

    # Verify for learning module
    is_valid, trust_score, error = await integration.verifold.verify_for_module("learning", mem_id, test_memory)

    print(f"  Verification: {'✅' if is_valid else '❌'}")
    print(f"  Trust score: {trust_score:.3f}")

    # Test drift tracking
    print("\n2. Drift Metrics Integration:")

    embedding = np.random.randn(1024).astype(np.float32)
    drift_result = await integration.drift.track_module_usage("learning", "integration", embedding, {"action": "test"})

    print(f"  Drift score: {drift_result['drift_score']:.3f}")
    print(f"  Recommendation: {drift_result['recommendation']}")

    # Test reality anchors
    print("\n3. Reality Anchors Integration:")

    creative_output = {
        "content": "Imagine objects floating upward naturally",
        "type": "creative_idea",
    }

    is_valid, violations = await integration.anchors.validate_output(
        "creativity", creative_output, {"context": "brainstorming"}
    )

    print(f"  Validation: {'✅' if is_valid else '❌'}")
    if violations:
        print(f"  Violations: {violations}")

    # Get integration status
    print("\n4. Integration Status:")
    status = integration.get_integration_status()
    print(f"  Modules registered: {status['verifold_status']['total_modules']}")
    print(f"  Tags monitored: {status['drift_tracking']['tags_monitored']}")
    print(
        f"  Reality anchors: {status['reality_anchors']['global_anchors'] + status['reality_anchors']['module_anchors']}"
    )

    print("\n✅ Integration demonstration complete!")


if __name__ == "__main__":
    asyncio.run(demonstrate_integration())
