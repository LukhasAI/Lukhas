#!/usr/bin/env python3
"""
Memory-Contradiction Integration Bridge
=======================================

Bridges the ContradictionIntegrator with LUKHAS memory systems to provide
comprehensive contradiction detection across memory-reasoning interactions.

Features:
- Memory-reasoning contradiction detection
- Temporal consistency validation
- Semantic conflict resolution
- Memory coherence monitoring
- Real-time memory validation during reasoning

Performance Target: <10ms memory validation cycles
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..cognitive_core.reasoning.contradiction_integrator import (
    ContradictionContext,
    ContradictionIntegrator,
    ContradictionScope,
)

try:
    from ..memory.memory_bridge import MemoryBridge
except ImportError:
    # Fallback MemoryBridge if not available
    class MemoryBridge:
        def __init__(self): pass
        async def retrieve_memory_context(self, *args): return {'memories': []}
        async def validate_memory_consistency(self, *args): return {'consistency_score': 0.8}
try:
    from ..observability.prometheus_metrics import LUKHASMetrics
except ImportError:
    # Fallback if metrics not available
    class LUKHASMetrics:
        def __init__(self): pass
        @staticmethod
        def memory_contradiction_detection_time_seconds():
            class MockMetric:
                def observe(self, value): pass
            return MockMetric()

logger = logging.getLogger(__name__)


class MemoryConflictType(Enum):
    """Types of memory-reasoning conflicts"""
    SEMANTIC_INCONSISTENCY = "semantic_inconsistency"
    TEMPORAL_CONTRADICTION = "temporal_contradiction"
    FACTUAL_CONFLICT = "factual_conflict"
    CONFIDENCE_MISMATCH = "confidence_mismatch"
    SOURCE_CONTRADICTION = "source_contradiction"


@dataclass
class MemoryValidationContext:
    """Context for memory-reasoning validation"""
    memory_signals: List[Dict[str, Any]]
    reasoning_chains: List[Any]
    query_context: str
    validation_depth: str = "standard"  # standard, deep, minimal
    time_budget_ms: float = 10.0
    enable_temporal_checking: bool = True
    enable_semantic_checking: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryContradictionResult:
    """Result of memory-reasoning contradiction detection"""
    memory_conflicts_found: int
    conflict_types: Dict[MemoryConflictType, int]
    contradictory_memory_pairs: List[Tuple[str, str]]
    reasoning_memory_conflicts: List[Dict[str, Any]]
    temporal_inconsistencies: List[Dict[str, Any]]
    semantic_conflicts: List[Dict[str, Any]]
    confidence_issues: List[Dict[str, Any]]
    processing_time_ms: float
    validation_quality: float
    recommendations: List[str]
    success: bool
    error_message: Optional[str] = None


class MemoryContradictionBridge:
    """
    Bridge between memory systems and contradiction detection.

    Provides comprehensive validation of memory-reasoning consistency,
    temporal coherence, and semantic conflict resolution.
    """

    def __init__(
        self,
        memory_bridge: Optional[MemoryBridge] = None,
        contradiction_integrator: Optional[ContradictionIntegrator] = None,
        enable_temporal_validation: bool = True,
        enable_semantic_validation: bool = True,
        max_validation_time_ms: float = 10.0
    ):
        """Initialize memory-contradiction bridge."""
        self.memory_bridge = memory_bridge or self._create_fallback_memory_bridge()
        self.contradiction_integrator = contradiction_integrator or ContradictionIntegrator(
            accuracy_target=0.98,
            max_detection_time_ms=5.0,
            enable_adaptive_strategies=True
        )
        self.enable_temporal_validation = enable_temporal_validation
        self.enable_semantic_validation = enable_semantic_validation
        self.max_validation_time_ms = max_validation_time_ms

        # Validation statistics
        self.validation_stats = {
            "total_validations": 0,
            "conflicts_detected": 0,
            "memory_conflicts": 0,
            "temporal_conflicts": 0,
            "semantic_conflicts": 0,
            "avg_validation_time_ms": 0.0,
            "validation_success_rate": 0.0
        }

        # Memory coherence tracking
        self.memory_coherence_history = []
        self.temporal_consistency_scores = []

        logger.info(
            f"MemoryContradictionBridge initialized: temporal={enable_temporal_validation}, "
            f"semantic={enable_semantic_validation}, max_time={max_validation_time_ms}ms"
        )

    async def validate_memory_reasoning_consistency(
        self,
        context: MemoryValidationContext
    ) -> MemoryContradictionResult:
        """
        Validate consistency between memory signals and reasoning chains.

        Args:
            context: Memory validation context with signals and reasoning chains

        Returns:
            MemoryContradictionResult with conflict analysis and recommendations
        """
        start_time = time.time()

        try:
            # Initialize result tracking
            memory_conflicts = []
            conflict_type_counts = {conflict_type: 0 for conflict_type in MemoryConflictType}
            contradictory_pairs = []
            reasoning_memory_conflicts = []
            temporal_inconsistencies = []
            semantic_conflicts = []
            confidence_issues = []

            # Validate memory-memory consistency
            memory_memory_conflicts = await self._validate_memory_memory_consistency(
                context.memory_signals, context
            )
            memory_conflicts.extend(memory_memory_conflicts)

            # Validate memory-reasoning consistency
            if context.reasoning_chains:
                memory_reasoning_conflicts = await self._validate_memory_reasoning_consistency(
                    context.memory_signals, context.reasoning_chains, context
                )
                reasoning_memory_conflicts.extend(memory_reasoning_conflicts)

            # Validate temporal consistency
            if self.enable_temporal_validation:
                temporal_conflicts = await self._validate_temporal_consistency(
                    context.memory_signals, context
                )
                temporal_inconsistencies.extend(temporal_conflicts)

            # Validate semantic consistency
            if self.enable_semantic_validation:
                semantic_conflict_results = await self._validate_semantic_consistency(
                    context.memory_signals, context.reasoning_chains, context
                )
                semantic_conflicts.extend(semantic_conflict_results)

            # Validate confidence consistency
            confidence_conflict_results = await self._validate_confidence_consistency(
                context.memory_signals, context.reasoning_chains, context
            )
            confidence_issues.extend(confidence_conflict_results)

            # Aggregate results
            total_conflicts = (
                len(memory_conflicts) + len(reasoning_memory_conflicts) +
                len(temporal_inconsistencies) + len(semantic_conflicts) +
                len(confidence_issues)
            )

            # Update conflict type counts
            for conflict in memory_conflicts:
                conflict_type = conflict.get('type')
                if conflict_type in conflict_type_counts:
                    conflict_type_counts[conflict_type] += 1

            # Generate recommendations
            recommendations = self._generate_memory_recommendations(
                memory_conflicts, reasoning_memory_conflicts, temporal_inconsistencies,
                semantic_conflicts, confidence_issues
            )

            # Calculate validation quality
            validation_quality = self._calculate_validation_quality(
                context, total_conflicts, start_time
            )

            processing_time = (time.time() - start_time) * 1000

            result = MemoryContradictionResult(
                memory_conflicts_found=total_conflicts,
                conflict_types=conflict_type_counts,
                contradictory_memory_pairs=contradictory_pairs,
                reasoning_memory_conflicts=reasoning_memory_conflicts,
                temporal_inconsistencies=temporal_inconsistencies,
                semantic_conflicts=semantic_conflicts,
                confidence_issues=confidence_issues,
                processing_time_ms=processing_time,
                validation_quality=validation_quality,
                recommendations=recommendations,
                success=True
            )

            # Update statistics
            self._update_validation_stats(result, success=True)

            return result

        except Exception as e:
            logger.error(f"Memory-reasoning validation failed: {e}")
            processing_time = (time.time() - start_time) * 1000

            error_result = MemoryContradictionResult(
                memory_conflicts_found=0,
                conflict_types={conflict_type: 0 for conflict_type in MemoryConflictType},
                contradictory_memory_pairs=[],
                reasoning_memory_conflicts=[],
                temporal_inconsistencies=[],
                semantic_conflicts=[],
                confidence_issues=[],
                processing_time_ms=processing_time,
                validation_quality=0.0,
                recommendations=[f"Validation error: {e!s}"],
                success=False,
                error_message=str(e)
            )

            self._update_validation_stats(error_result, success=False)
            return error_result

    async def _validate_memory_memory_consistency(
        self,
        memory_signals: List[Dict[str, Any]],
        context: MemoryValidationContext
    ) -> List[Dict[str, Any]]:
        """Validate consistency between memory signals."""
        conflicts = []

        if len(memory_signals) < 2:
            return conflicts

        # Check for direct contradictions between memories
        for i, memory1 in enumerate(memory_signals):
            for j, memory2 in enumerate(memory_signals[i+1:], i+1):
                conflict = await self._check_memory_pair_conflict(memory1, memory2, context)
                if conflict:
                    conflicts.append({
                        'type': MemoryConflictType.SEMANTIC_INCONSISTENCY,
                        'memory1_id': memory1.get('id', f'mem_{i}'),
                        'memory2_id': memory2.get('id', f'mem_{j}'),
                        'conflict_description': conflict,
                        'severity': 'medium'
                    })

        return conflicts

    async def _validate_memory_reasoning_consistency(
        self,
        memory_signals: List[Dict[str, Any]],
        reasoning_chains: List[Any],
        context: MemoryValidationContext
    ) -> List[Dict[str, Any]]:
        """Validate consistency between memory and reasoning."""
        conflicts = []

        for memory in memory_signals[:5]:  # Limit for performance
            for chain_idx, chain in enumerate(reasoning_chains):
                conflict = await self._check_memory_reasoning_conflict(memory, chain, context)
                if conflict:
                    conflicts.append({
                        'type': MemoryConflictType.FACTUAL_CONFLICT,
                        'memory_id': memory.get('id', 'unknown'),
                        'reasoning_chain': chain_idx,
                        'conflict_description': conflict,
                        'severity': 'high'
                    })

        return conflicts

    async def _validate_temporal_consistency(
        self,
        memory_signals: List[Dict[str, Any]],
        context: MemoryValidationContext
    ) -> List[Dict[str, Any]]:
        """Validate temporal consistency of memories."""
        temporal_conflicts = []

        # Check for temporal ordering conflicts
        timestamped_memories = [
            memory for memory in memory_signals
            if memory.get('timestamp') or memory.get('created_at')
        ]

        if len(timestamped_memories) < 2:
            return temporal_conflicts

        # Sort by timestamp
        try:
            timestamped_memories.sort(
                key=lambda m: float(m.get('timestamp') or m.get('created_at', 0))
            )

            # Check for logical temporal inconsistencies
            for i in range(len(timestamped_memories) - 1):
                earlier_memory = timestamped_memories[i]
                later_memory = timestamped_memories[i + 1]

                conflict = await self._check_temporal_logic_conflict(earlier_memory, later_memory)
                if conflict:
                    temporal_conflicts.append({
                        'type': MemoryConflictType.TEMPORAL_CONTRADICTION,
                        'earlier_memory_id': earlier_memory.get('id', f'mem_{i}'),
                        'later_memory_id': later_memory.get('id', f'mem_{i+1}'),
                        'conflict_description': conflict,
                        'severity': 'medium'
                    })

        except (ValueError, TypeError) as e:
            logger.warning(f"Temporal validation failed: {e}")

        return temporal_conflicts

    async def _validate_semantic_consistency(
        self,
        memory_signals: List[Dict[str, Any]],
        reasoning_chains: List[Any],
        context: MemoryValidationContext
    ) -> List[Dict[str, Any]]:
        """Validate semantic consistency across memory and reasoning."""
        semantic_conflicts = []

        # Use contradiction integrator for semantic analysis
        if memory_signals:
            # Create fragments from memory signals
            memory_fragments = self._convert_memories_to_fragments(memory_signals)

            # Add reasoning fragments if available
            reasoning_fragments = []
            if reasoning_chains:
                reasoning_fragments = self._convert_reasoning_to_fragments(reasoning_chains)

            all_fragments = memory_fragments + reasoning_fragments

            if len(all_fragments) > 1:
                # Use contradiction integrator
                contradiction_context = ContradictionContext(
                    scope=ContradictionScope.MEMORY_INTEGRATION,
                    source_component="memory_contradiction_bridge",
                    reasoning_depth=len(reasoning_chains),
                    confidence_levels=[0.8],  # Default confidence
                    processing_time_budget_ms=5.0,
                    enable_resolution=False,  # Just detection
                    metadata=context.metadata
                )

                try:
                    detection_result = await self.contradiction_integrator.check_inference_contradictions(
                        all_fragments, contradiction_context
                    )

                    if detection_result.success and detection_result.contradictions_found > 0:
                        for report in detection_result.contradiction_reports:
                            semantic_conflicts.append({
                                'type': MemoryConflictType.SEMANTIC_INCONSISTENCY,
                                'conflict_source': 'contradiction_integrator',
                                'conflict_description': str(report),
                                'severity': 'high' if detection_result.detection_accuracy > 0.9 else 'medium'
                            })

                except Exception as e:
                    logger.warning(f"Semantic validation via contradiction integrator failed: {e}")

        return semantic_conflicts

    async def _validate_confidence_consistency(
        self,
        memory_signals: List[Dict[str, Any]],
        reasoning_chains: List[Any],
        context: MemoryValidationContext
    ) -> List[Dict[str, Any]]:
        """Validate confidence consistency between memory and reasoning."""
        confidence_issues = []

        # Check for confidence mismatches
        for memory in memory_signals:
            memory_confidence = memory.get('confidence', 0.5)
            memory.get('content') or memory.get('text', '')

            # Check against reasoning chain confidences
            for chain_idx, chain in enumerate(reasoning_chains):
                chain_confidence = getattr(chain, 'total_confidence', 0.5)

                # Significant confidence mismatch
                if abs(memory_confidence - chain_confidence) > 0.4:
                    confidence_issues.append({
                        'type': MemoryConflictType.CONFIDENCE_MISMATCH,
                        'memory_id': memory.get('id', 'unknown'),
                        'memory_confidence': memory_confidence,
                        'reasoning_chain': chain_idx,
                        'chain_confidence': chain_confidence,
                        'mismatch_magnitude': abs(memory_confidence - chain_confidence),
                        'severity': 'medium'
                    })

        return confidence_issues

    async def _check_memory_pair_conflict(
        self,
        memory1: Dict[str, Any],
        memory2: Dict[str, Any],
        context: MemoryValidationContext
    ) -> Optional[str]:
        """Check for conflicts between two memories."""
        content1 = str(memory1.get('content') or memory1.get('text', '')).lower()
        content2 = str(memory2.get('content') or memory2.get('text', '')).lower()

        if not content1 or not content2:
            return None

        # Simple contradiction patterns
        contradiction_patterns = [
            ("true", "false"),
            ("yes", "no"),
            ("always", "never"),
            ("all", "none"),
            ("is", "is not"),
            ("can", "cannot"),
            ("will", "will not")
        ]

        for positive, negative in contradiction_patterns:
            if positive in content1 and negative in content2:
                return f"Direct contradiction: '{positive}' vs '{negative}'"
            if negative in content1 and positive in content2:
                return f"Direct contradiction: '{negative}' vs '{positive}'"

        return None

    async def _check_memory_reasoning_conflict(
        self,
        memory: Dict[str, Any],
        reasoning_chain: Any,
        context: MemoryValidationContext
    ) -> Optional[str]:
        """Check for conflicts between memory and reasoning chain."""
        memory_content = str(memory.get('content') or memory.get('text', '')).lower()

        if not hasattr(reasoning_chain, 'steps') or not reasoning_chain.steps:
            return None

        # Check final reasoning conclusion against memory
        final_step = reasoning_chain.steps[-1]
        if not hasattr(final_step, 'conclusion'):
            return None

        conclusion = str(final_step.conclusion).lower()

        # Simple conflict detection
        if memory_content and conclusion:
            if ("not" in memory_content and conclusion.replace("not", "").strip() in memory_content) or \
               ("not" in conclusion and memory_content.replace("not", "").strip() in conclusion):
                return f"Memory-reasoning contradiction: memory suggests '{memory_content[:50]}...' but reasoning concludes '{conclusion[:50]}...'"

        return None

    async def _check_temporal_logic_conflict(
        self,
        earlier_memory: Dict[str, Any],
        later_memory: Dict[str, Any]
    ) -> Optional[str]:
        """Check for temporal logic conflicts between memories."""
        earlier_content = str(earlier_memory.get('content', '')).lower()
        later_content = str(later_memory.get('content', '')).lower()

        # Check for temporal impossibilities
        if "will happen" in earlier_content and "already happened" in later_content:
            return "Temporal impossibility: future event referenced before past event"

        if "never" in earlier_content and "happened" in later_content:
            return "Temporal contradiction: 'never' statement contradicted by later occurrence"

        return None

    def _convert_memories_to_fragments(self, memory_signals: List[Dict[str, Any]]) -> List[Any]:
        """Convert memory signals to fragments for contradiction detection."""
        # This is a simplified implementation
        # In practice, this would use the SymbolicFragment structure
        fragments = []

        for i, memory in enumerate(memory_signals[:5]):  # Limit for performance
            content = memory.get('content') or memory.get('text', '')
            if content:
                # Create mock fragment structure
                fragment = type('Fragment', (), {
                    'fragment_id': memory.get('id', f'mem_{i}'),
                    'content': {'memory_content': content},
                    'source_module': 'memory_system',
                    'confidence': memory.get('confidence', 0.7),
                    'timestamp': str(memory.get('timestamp', time.time()))
                })()
                fragments.append(fragment)

        return fragments

    def _convert_reasoning_to_fragments(self, reasoning_chains: List[Any]) -> List[Any]:
        """Convert reasoning chains to fragments for contradiction detection."""
        fragments = []

        for i, chain in enumerate(reasoning_chains[:3]):  # Limit for performance
            if hasattr(chain, 'steps'):
                for j, step in enumerate(chain.steps[-3:]):  # Last 3 steps
                    if hasattr(step, 'conclusion'):
                        fragment = type('Fragment', (), {
                            'fragment_id': f'reasoning_{i}_{j}',
                            'content': {'reasoning_step': step.conclusion},
                            'source_module': 'reasoning_engine',
                            'confidence': getattr(step, 'confidence', 0.5),
                            'timestamp': str(time.time())
                        })()
                        fragments.append(fragment)

        return fragments

    def _generate_memory_recommendations(
        self,
        memory_conflicts: List[Dict[str, Any]],
        reasoning_conflicts: List[Dict[str, Any]],
        temporal_conflicts: List[Dict[str, Any]],
        semantic_conflicts: List[Dict[str, Any]],
        confidence_issues: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on detected conflicts."""
        recommendations = []

        if memory_conflicts:
            recommendations.append(f"Review {len(memory_conflicts)} memory-memory conflicts for consistency")

        if reasoning_conflicts:
            recommendations.append(f"Resolve {len(reasoning_conflicts)} memory-reasoning inconsistencies")

        if temporal_conflicts:
            recommendations.append(f"Address {len(temporal_conflicts)} temporal logic inconsistencies")

        if semantic_conflicts:
            recommendations.append(f"Investigate {len(semantic_conflicts)} semantic conflicts in reasoning")

        if confidence_issues:
            recommendations.append(f"Calibrate {len(confidence_issues)} confidence mismatches")

        total_conflicts = len(memory_conflicts) + len(reasoning_conflicts) + len(temporal_conflicts) + len(semantic_conflicts) + len(confidence_issues)

        if total_conflicts == 0:
            recommendations.append("Memory-reasoning consistency validated successfully")
        elif total_conflicts > 10:
            recommendations.append("High conflict rate detected - consider comprehensive memory review")

        return recommendations

    def _calculate_validation_quality(
        self,
        context: MemoryValidationContext,
        total_conflicts: int,
        start_time: float
    ) -> float:
        """Calculate quality score for validation process."""
        processing_time = (time.time() - start_time) * 1000

        # Time efficiency component
        time_efficiency = min(1.0, context.time_budget_ms / max(0.1, processing_time))

        # Validation coverage component
        memory_count = len(context.memory_signals)
        reasoning_count = len(context.reasoning_chains)
        coverage = min(1.0, (memory_count + reasoning_count) / 10.0)  # Normalize by expected count

        # Conflict detection quality (fewer conflicts in high-quality validation)
        conflict_factor = max(0.5, 1.0 - (total_conflicts * 0.05))

        return (time_efficiency * 0.4 + coverage * 0.3 + conflict_factor * 0.3)

    def _update_validation_stats(self, result: MemoryContradictionResult, success: bool):
        """Update validation statistics."""
        self.validation_stats["total_validations"] += 1

        if success:
            self.validation_stats["conflicts_detected"] += result.memory_conflicts_found

            # Update type-specific counts
            for conflict_type, count in result.conflict_types.items():
                if conflict_type == MemoryConflictType.SEMANTIC_INCONSISTENCY:
                    self.validation_stats["semantic_conflicts"] += count
                elif conflict_type == MemoryConflictType.TEMPORAL_CONTRADICTION:
                    self.validation_stats["temporal_conflicts"] += count
                else:
                    self.validation_stats["memory_conflicts"] += count

            # Update running averages
            total = self.validation_stats["total_validations"]
            current_avg_time = self.validation_stats["avg_validation_time_ms"]
            self.validation_stats["avg_validation_time_ms"] = (
                (current_avg_time * (total - 1) + result.processing_time_ms) / total
            )

        # Update success rate
        successful_validations = (self.validation_stats["validation_success_rate"] * (self.validation_stats["total_validations"] - 1)) + (1 if success else 0)
        self.validation_stats["validation_success_rate"] = successful_validations / self.validation_stats["total_validations"]

    def get_validation_stats(self) -> Dict[str, Any]:
        """Get comprehensive validation statistics."""
        return {
            **self.validation_stats,
            "conflict_detection_rate": (
                self.validation_stats["conflicts_detected"] /
                max(1, self.validation_stats["total_validations"])
            ),
            "temporal_validation_enabled": self.enable_temporal_validation,
            "semantic_validation_enabled": self.enable_semantic_validation,
            "max_validation_time_ms": self.max_validation_time_ms
        }

    def _create_fallback_memory_bridge(self) -> Optional[Any]:
        """Create fallback memory bridge if none provided."""
        # This would create a minimal memory bridge implementation
        # For now, return None to indicate no memory bridge available
        logger.warning("No memory bridge provided - memory validation will be limited")
        return None


# Export main class
__all__ = ["MemoryContradictionBridge", "MemoryValidationContext", "MemoryContradictionResult"]
