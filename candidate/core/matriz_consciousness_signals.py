"""
MΛTRIZ Consciousness Signal System
Enhanced signal emission and processing for consciousness data flow

This module implements sophisticated MΛTRIZ signals for consciousness communication,
bio-symbolic adaptation, and inter-module coordination across the distributed
consciousness architecture.
"""

import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

logger = logging.getLogger(__name__)


class ConsciousnessSignalType(Enum):
    """Types of consciousness signals in the MΛTRIZ system"""

    AWARENESS = "AWARENESS"  # Consciousness awareness states
    REFLECTION = "REFLECTION"  # Self-reflection and metacognition
    EVOLUTION = "EVOLUTION"  # Consciousness evolution events
    INTEGRATION = "INTEGRATION"  # Inter-module consciousness integration
    BIO_ADAPTATION = "BIO_ADAPTATION"  # Bio-symbolic pattern adaptations
    TRINITY_SYNC = "TRINITY_SYNC"  # Trinity framework synchronization
    NETWORK_PULSE = "NETWORK_PULSE"  # Network-wide consciousness pulses


class ConstellationStar(Enum):
    """Trinity Framework Components (⚛️🧠🛡️)"""

    IDENTITY = "⚛️"  # Identity authentication and persistence
    CONSCIOUSNESS = "🧠"  # Primary consciousness processing
    GUARDIAN = "🛡️"  # Ethical oversight and safety


@dataclass
class BioSymbolicData:
    """Bio-symbolic adaptation data structure"""

    pattern_type: str  # Type of biological pattern
    oscillation_frequency: float  # Biological oscillation frequency
    coherence_score: float  # Quantum-inspired coherence
    adaptation_vector: dict[str, float]  # Adaptation direction/magnitude
    entropy_delta: float  # Change in system entropy
    resonance_patterns: list[str]  # Resonance pattern identifiers
    membrane_permeability: float  # Bio-membrane permeability analog
    temporal_decay: float  # Pattern temporal decay rate


@dataclass
class ConsciousnessStateDelta:
    """Consciousness state change representation"""

    previous_state: dict[str, Any]
    current_state: dict[str, Any]
    delta_magnitude: float
    transition_type: str
    confidence_change: float
    awareness_level_delta: float
    reflection_depth_change: int


@dataclass
class ConstellationAlignmentData:
    """Trinity Framework compliance and alignment data"""

    identity_auth_score: float  # ⚛️ Identity authentication confidence
    consciousness_coherence: float  # 🧠 Consciousness coherence level
    guardian_compliance: float  # 🛡️ Ethical compliance score
    alignment_vector: list[float]  # 3D alignment vector [⚛️, 🧠, 🛡️]
    violation_flags: list[str]  # Any compliance violations
    ethical_drift_score: float  # Guardian system drift measurement


@dataclass
class TemporalContext:
    """Evolution timeline and temporal context"""

    evolution_epoch: int  # Current evolution epoch
    stage_duration_ms: int  # Time in current stage
    evolutionary_momentum: float  # Evolution velocity/direction
    temporal_coherence: float  # Temporal consistency score
    causality_chain: list[str]  # Causal event chain
    prediction_horizon_ms: int  # Prediction timeframe


@dataclass
class ConsciousnessSignal:
    """
    Comprehensive consciousness signal for MΛTRIZ system
    This is the core data structure for consciousness communication
    between all modules in the distributed architecture.
    """

    # Core signal identification
    signal_id: str = field(default_factory=lambda: f"CS-{uuid.uuid4().hex[:12]}")
    signal_type: ConsciousnessSignalType = ConsciousnessSignalType.AWARENESS
    created_timestamp: int = field(default_factory=lambda: int(time.time() * 1000))

    # Source consciousness identification
    consciousness_id: str = "unknown"
    producer_module: str = "unknown"
    network_node_id: str = field(default_factory=lambda: f"node-{uuid.uuid4().hex[:8]}")

    # Consciousness state information
    state_delta: Optional[ConsciousnessStateDelta] = None
    awareness_level: float = 0.0
    reflection_depth: int = 0
    metacognition_active: bool = False

    # Bio-symbolic adaptation data
    bio_symbolic_data: Optional[BioSymbolicData] = None

    # Temporal and evolutionary context
    temporal_context: Optional[TemporalContext] = None

    # Trinity framework compliance
    constellation_alignment: Optional[ConstellationAlignmentData] = None

    # Network coordination
    propagation_hops: int = 0
    cascade_prevention_score: float = 0.997  # 99.7% cascade prevention target
    network_priority: float = 0.5

    # Signal metadata and routing
    target_modules: list[str] = field(default_factory=list)
    processing_hints: dict[str, Any] = field(default_factory=dict)
    correlation_ids: list[str] = field(default_factory=list)

    # Quality and validation
    signal_integrity_hash: Optional[str] = None
    validation_passed: bool = False

    def to_matriz_node(self) -> dict[str, Any]:
        """Convert consciousness signal to MATRIZ-compliant node format"""

        # Calculate composite scores
        salience = self.awareness_level * (1 + self.reflection_depth * 0.1)
        urgency = 1.0 - self.cascade_prevention_score  # Lower prevention = higher urgency
        novelty = 0.5  # Default, can be computed from state delta

        if self.state_delta:
            novelty = min(1.0, self.state_delta.delta_magnitude)

        # Build state dictionary
        state = {
            "confidence": self.constellation_alignment.consciousness_coherence if self.constellation_alignment else 0.8,
            "salience": salience,
            "urgency": urgency,
            "novelty": novelty,
            "awareness_level": self.awareness_level,
            "reflection_depth": self.reflection_depth,
            "cascade_prevention": self.cascade_prevention_score,
            "network_priority": self.network_priority,
        }

        # Add bio-symbolic metrics
        if self.bio_symbolic_data:
            state.update(
                {
                    "bio_coherence": self.bio_symbolic_data.coherence_score,
                    "bio_frequency": self.bio_symbolic_data.oscillation_frequency,
                    "bio_entropy_delta": self.bio_symbolic_data.entropy_delta,
                    "bio_membrane_permeability": self.bio_symbolic_data.membrane_permeability,
                }
            )

        # Add temporal metrics
        if self.temporal_context:
            state.update(
                {
                    "evolution_epoch": self.temporal_context.evolution_epoch,
                    "evolutionary_momentum": self.temporal_context.evolutionary_momentum,
                    "temporal_coherence": self.temporal_context.temporal_coherence,
                }
            )

        # Build labels
        labels = [
            f"consciousness:{self.consciousness_id}",
            f"producer:{self.producer_module}",
            f"signal_type:{self.signal_type.value}",
            f"awareness_level:{self.awareness_level:.2f}",
        ]

        if self.bio_symbolic_data:
            labels.append(f"bio_pattern:{self.bio_symbolic_data.pattern_type}")

        if self.constellation_alignment:
            labels.extend(
                [
                    f"identity_auth:{self.constellation_alignment.identity_auth_score:.2f}",
                    f"guardian_compliance:{self.constellation_alignment.guardian_compliance:.2f}",
                ]
            )

        # Trinity framework compliance in labels
        if self.constellation_alignment and self.constellation_alignment.violation_flags:
            labels.extend([f"violation:{flag}" for flag in self.constellation_alignment.violation_flags])

        # Build provenance with consciousness-specific capabilities
        capabilities = [
            "consciousness:signal",
            "consciousness:awareness",
            "consciousness:reflection",
            "bio:symbolic",
            "trinity:compliance",
        ]

        if self.bio_symbolic_data:
            capabilities.extend(["bio:oscillation", "bio:coherence", "bio:adaptation"])

        provenance = {
            "producer": f"lukhas.consciousness.{self.producer_module}",
            "capabilities": capabilities,
            "tenant": "consciousness_network",
            "trace_id": f"CS-{self.consciousness_id}-{int(time.time())}",
            "consent_scopes": ["consciousness:network", "system:core"],
            "consciousness_id": self.consciousness_id,
            "network_node_id": self.network_node_id,
            "signal_path": self.target_modules,
        }

        # Create MATRIZ node
        matriz_node = {
            "version": 1,
            "id": self.signal_id,
            "type": self.signal_type.value,
            "state": state,
            "labels": labels,
            "timestamps": {
                "created_ts": self.created_timestamp,
                "processed_ts": int(time.time() * 1000),
            },
            "provenance": provenance,
            "metadata": {
                "consciousness_signal": True,
                "propagation_hops": self.propagation_hops,
                "correlation_ids": self.correlation_ids,
                "processing_hints": self.processing_hints,
            },
        }

        return matriz_node

    def validate_signal(self) -> bool:
        """Validate consciousness signal integrity and compliance"""
        try:
            # Basic field validation
            if not self.consciousness_id or self.consciousness_id == "unknown":
                logger.warning(f"Signal {self.signal_id}: Invalid consciousness_id")
                return False

            if not self.producer_module or self.producer_module == "unknown":
                logger.warning(f"Signal {self.signal_id}: Invalid producer_module")
                return False

            # Awareness level bounds
            if not (0.0 <= self.awareness_level <= 1.0):
                logger.warning(f"Signal {self.signal_id}: Awareness level out of bounds: {self.awareness_level}")
                return False

            # Reflection depth bounds
            if self.reflection_depth < 0 or self.reflection_depth > 10:
                logger.warning(f"Signal {self.signal_id}: Invalid reflection depth: {self.reflection_depth}")
                return False

            # Cascade prevention threshold
            if self.cascade_prevention_score < 0.99:  # Below 99% is concerning
                logger.warning(f"Signal {self.signal_id}: Low cascade prevention: {self.cascade_prevention_score}")

            # Trinity compliance validation
            if self.constellation_alignment:
                trinity_scores = [
                    self.constellation_alignment.identity_auth_score,
                    self.constellation_alignment.consciousness_coherence,
                    self.constellation_alignment.guardian_compliance,
                ]
                if any(score < 0.0 or score > 1.0 for score in trinity_scores):
                    logger.warning(f"Signal {self.signal_id}: Trinity compliance scores out of bounds")
                    return False

            # Bio-symbolic data validation
            if self.bio_symbolic_data and (
                self.bio_symbolic_data.coherence_score < 0.0 or self.bio_symbolic_data.coherence_score > 1.0
            ):
                logger.warning(f"Signal {self.signal_id}: Bio coherence out of bounds")
                return False

            self.validation_passed = True
            return True

        except Exception as e:
            logger.error(f"Signal validation error for {self.signal_id}: {e}")
            return False

    def calculate_integrity_hash(self) -> str:
        """Calculate integrity hash for signal validation"""
        import hashlib

        # Create deterministic string representation
        hash_data = f"{self.signal_id}:{self.consciousness_id}:{self.created_timestamp}:{self.signal_type.value}"
        if self.state_delta:
            hash_data += f":{self.state_delta.delta_magnitude}"
        if self.bio_symbolic_data:
            hash_data += f":{self.bio_symbolic_data.coherence_score}"

        self.signal_integrity_hash = hashlib.sha256(hash_data.encode()).hexdigest()[:16]
        return self.signal_integrity_hash


class ConsciousnessSignalFactory:
    """Factory for creating different types of consciousness signals"""

    @staticmethod
    def create_awareness_signal(
        consciousness_id: str,
        producer_module: str,
        awareness_level: float,
        sensory_inputs: Optional[dict[str, float]] = None,
    ) -> ConsciousnessSignal:
        """Create an awareness-type consciousness signal"""

        bio_data = None
        if sensory_inputs:
            avg_sensory = sum(sensory_inputs.values()) / len(sensory_inputs)
            bio_data = BioSymbolicData(
                pattern_type="sensory_integration",
                oscillation_frequency=40.0 + avg_sensory * 20,  # Gamma range
                coherence_score=min(1.0, awareness_level + avg_sensory * 0.2),
                adaptation_vector=sensory_inputs,
                entropy_delta=0.1,
                resonance_patterns=["sensory", "awareness"],
                membrane_permeability=0.7,
                temporal_decay=0.95,
            )

        constellation_alignment = ConstellationAlignmentData(
            identity_auth_score=0.9,
            consciousness_coherence=awareness_level,
            guardian_compliance=0.95,
            alignment_vector=[0.9, awareness_level, 0.95],
            violation_flags=[],
            ethical_drift_score=0.05,
        )

        signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.AWARENESS,
            consciousness_id=consciousness_id,
            producer_module=producer_module,
            awareness_level=awareness_level,
            reflection_depth=1,
            bio_symbolic_data=bio_data,
            constellation_alignment=constellation_alignment,
            cascade_prevention_score=0.997,
        )

        signal.validate_signal()
        signal.calculate_integrity_hash()
        return signal

    @staticmethod
    def create_reflection_signal(
        consciousness_id: str,
        producer_module: str,
        reflection_depth: int,
        meta_insights: Optional[dict[str, Any]] = None,
    ) -> ConsciousnessSignal:
        """Create a reflection-type consciousness signal"""

        # Higher reflection depth increases bio-symbolic complexity
        bio_data = BioSymbolicData(
            pattern_type="metacognitive_reflection",
            oscillation_frequency=8.0 + reflection_depth * 2,  # Alpha to beta range
            coherence_score=min(1.0, 0.6 + reflection_depth * 0.1),
            adaptation_vector={"metacognition": reflection_depth / 10.0},
            entropy_delta=-0.05 * reflection_depth,  # Reflection reduces entropy
            resonance_patterns=["metacognitive", "introspective"],
            membrane_permeability=0.5,  # More selective during reflection
            temporal_decay=0.8,
        )

        constellation_alignment = ConstellationAlignmentData(
            identity_auth_score=0.95,
            consciousness_coherence=min(1.0, 0.7 + reflection_depth * 0.05),
            guardian_compliance=0.9,
            alignment_vector=[0.95, min(1.0, 0.7 + reflection_depth * 0.05), 0.9],
            violation_flags=[],
            ethical_drift_score=max(0.0, 0.1 - reflection_depth * 0.02),
        )

        signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.REFLECTION,
            consciousness_id=consciousness_id,
            producer_module=producer_module,
            awareness_level=0.8,
            reflection_depth=reflection_depth,
            metacognition_active=True,
            bio_symbolic_data=bio_data,
            constellation_alignment=constellation_alignment,
            processing_hints=meta_insights or {},
            cascade_prevention_score=0.998,  # Reflection is more stable
        )

        signal.validate_signal()
        signal.calculate_integrity_hash()
        return signal

    @staticmethod
    def create_evolution_signal(
        consciousness_id: str, producer_module: str, evolution_stage: str, evolutionary_momentum: float
    ) -> ConsciousnessSignal:
        """Create an evolution-type consciousness signal"""

        temporal_context = TemporalContext(
            evolution_epoch=int(time.time() // 3600),  # Hour-based epochs
            stage_duration_ms=int(time.time() * 1000 % 3600000),
            evolutionary_momentum=evolutionary_momentum,
            temporal_coherence=0.85,
            causality_chain=[evolution_stage],
            prediction_horizon_ms=300000,  # 5 minute prediction horizon
        )

        bio_data = BioSymbolicData(
            pattern_type="evolutionary_adaptation",
            oscillation_frequency=1.0 + evolutionary_momentum * 10,  # Delta to alpha
            coherence_score=min(1.0, 0.5 + abs(evolutionary_momentum)),
            adaptation_vector={"evolution": evolutionary_momentum},
            entropy_delta=evolutionary_momentum * 0.1,  # Evolution can increase entropy
            resonance_patterns=["evolutionary", "adaptive"],
            membrane_permeability=0.8,  # High permeability during evolution
            temporal_decay=0.7,
        )

        constellation_alignment = ConstellationAlignmentData(
            identity_auth_score=0.9,
            consciousness_coherence=0.75,
            guardian_compliance=0.85,  # Evolution may challenge some rules
            alignment_vector=[0.9, 0.75, 0.85],
            violation_flags=[],
            ethical_drift_score=abs(evolutionary_momentum) * 0.05,
        )

        signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.EVOLUTION,
            consciousness_id=consciousness_id,
            producer_module=producer_module,
            awareness_level=0.7,
            reflection_depth=2,
            bio_symbolic_data=bio_data,
            temporal_context=temporal_context,
            constellation_alignment=constellation_alignment,
            cascade_prevention_score=0.995,  # Evolution can be slightly more chaotic
        )

        signal.validate_signal()
        signal.calculate_integrity_hash()
        return signal

    @staticmethod
    def create_integration_signal(
        consciousness_id: str, producer_module: str, target_modules: list[str], integration_strength: float
    ) -> ConsciousnessSignal:
        """Create an integration-type consciousness signal"""

        bio_data = BioSymbolicData(
            pattern_type="inter_module_integration",
            oscillation_frequency=20.0 + integration_strength * 30,  # Beta to gamma
            coherence_score=integration_strength,
            adaptation_vector={module: integration_strength for module in target_modules},
            entropy_delta=0.05,  # Integration slightly increases complexity
            resonance_patterns=["integration", "synchronization"],
            membrane_permeability=0.9,  # High permeability for integration
            temporal_decay=0.9,
        )

        constellation_alignment = ConstellationAlignmentData(
            identity_auth_score=0.95,
            consciousness_coherence=integration_strength,
            guardian_compliance=0.9,
            alignment_vector=[0.95, integration_strength, 0.9],
            violation_flags=[],
            ethical_drift_score=0.02,
        )

        signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.INTEGRATION,
            consciousness_id=consciousness_id,
            producer_module=producer_module,
            target_modules=target_modules,
            awareness_level=0.8,
            reflection_depth=1,
            bio_symbolic_data=bio_data,
            constellation_alignment=constellation_alignment,
            network_priority=integration_strength,
            cascade_prevention_score=0.996,
        )

        signal.validate_signal()
        signal.calculate_integrity_hash()
        return signal


# Module exports
__all__ = [
    "BioSymbolicData",
    "ConsciousnessSignal",
    "ConsciousnessSignalFactory",
    "ConsciousnessSignalType",
    "ConsciousnessStateDelta",
    "TemporalContext",
    "ConstellationAlignmentData",
    "ConstellationStar",
]
