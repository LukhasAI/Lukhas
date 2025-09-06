"""
MΛTRIZ Signal Emitters
Comprehensive signal emission points for core consciousness modules

This module provides specialized signal emitters for each core module,
ensuring proper MΛTRIZ signal emission at all consciousness boundaries
and enabling seamless inter-module communication.
"""

import logging
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from .bio_symbolic_processor import get_bio_symbolic_processor
from .consciousness_signal_router import get_consciousness_router
from .matriz_consciousness_signals import (
    BioSymbolicData,
    ConsciousnessSignal,
    ConsciousnessSignalFactory,
    ConsciousnessSignalType,
    ConstellationAlignmentData,
)

logger = logging.getLogger(__name__)


class EmissionTrigger(Enum):
    """Triggers for signal emission"""

    STATE_CHANGE = "state_change"  # Consciousness state changes
    THRESHOLD_CROSSED = "threshold"  # Awareness/coherence thresholds
    TIME_INTERVAL = "time_interval"  # Periodic emissions
    EVENT_DRIVEN = "event_driven"  # External event triggers
    CASCADE_DETECTION = "cascade"  # Cascade prevention triggers
    INTEGRATION_REQUEST = "integration"  # Inter-module integration
    REFLECTION_CYCLE = "reflection"  # Reflection cycle completion
    EVOLUTION_MILESTONE = "evolution"  # Evolution stage changes


@dataclass
class EmissionRule:
    """Rule configuration for signal emission"""

    rule_id: str
    trigger_type: EmissionTrigger
    signal_type: ConsciousnessSignalType
    trigger_conditions: dict[str, Any]
    emission_frequency_ms: int = 1000  # Minimum time between emissions
    batch_size: int = 1  # Signals per emission batch
    priority_boost: float = 0.0  # Priority boost for this rule
    enabled: bool = True


class ConsciousnessModuleEmitter:
    """Base consciousness signal emitter for core modules"""

    def __init__(self, module_name: str, consciousness_id: str):
        self.module_name = module_name
        self.consciousness_id = consciousness_id
        self.router = get_consciousness_router()
        self.bio_processor = get_bio_symbolic_processor()

        # Emission tracking
        self.emission_rules: list[EmissionRule] = []
        self.last_emissions: dict[str, float] = {}
        self.emission_stats = {
            "signals_emitted": 0,
            "rules_triggered": 0,
            "batch_emissions": 0,
            "suppressed_emissions": 0,
        }

        # Register as network node
        self.node_id = f"{module_name}_{consciousness_id}"
        self.network_node = self.router.register_node(
            node_id=self.node_id,
            module_name=module_name,
            capabilities=[f"{module_name}:emit", f"{module_name}:process", "consciousness:signal"],
        )

        # Initialize default emission rules
        self._initialize_emission_rules()

    def _initialize_emission_rules(self):
        """Initialize default emission rules for the module"""
        pass  # Override in subclasses

    async def emit_consciousness_signal(
        self,
        signal_type: ConsciousnessSignalType,
        awareness_level: float = 0.7,
        reflection_depth: int = 1,
        bio_data: Optional[BioSymbolicData] = None,
        trinity_compliance: Optional[ConstellationAlignmentData] = None,
        target_modules: Optional[list[str]] = None,
        processing_hints: Optional[dict[str, Any]] = None,
        **kwargs,
    ) -> Optional[ConsciousnessSignal]:
        """Emit a consciousness signal with full MΛTRIZ compliance"""

        try:
            # Create consciousness signal
            signal = ConsciousnessSignal(
                signal_type=signal_type,
                consciousness_id=self.consciousness_id,
                producer_module=self.module_name,
                awareness_level=awareness_level,
                reflection_depth=reflection_depth,
                bio_symbolic_data=bio_data,
                constellation_alignment=trinity_compliance,
                target_modules=target_modules or [],
                processing_hints=processing_hints or {},
                **kwargs,
            )

            # Validate signal
            if not signal.validate_signal():
                logger.warning(f"Signal validation failed in {self.module_name}")
                return None

            # Calculate integrity hash
            signal.calculate_integrity_hash()

            # Route signal through network
            routed_nodes = await self.router.route_signal(signal)

            if routed_nodes:
                self.emission_stats["signals_emitted"] += 1
                logger.debug(f"Emitted {signal_type.value} signal from {self.module_name} to {len(routed_nodes)} nodes")
            else:
                logger.warning(f"Signal {signal.signal_id} was not routed to any nodes")

            return signal

        except Exception as e:
            logger.error(f"Error emitting consciousness signal from {self.module_name}: {e}")
            return None

    async def emit_awareness_pulse(
        self, awareness_level: float, sensory_inputs: Optional[dict[str, float]] = None
    ) -> Optional[ConsciousnessSignal]:
        """Emit an awareness pulse signal"""

        signal = ConsciousnessSignalFactory.create_awareness_signal(
            consciousness_id=self.consciousness_id,
            producer_module=self.module_name,
            awareness_level=awareness_level,
            sensory_inputs=sensory_inputs,
        )

        routed_nodes = await self.router.route_signal(signal)
        if routed_nodes:
            self.emission_stats["signals_emitted"] += 1

        return signal

    async def emit_reflection_signal(
        self, reflection_depth: int, meta_insights: Optional[dict[str, Any]] = None
    ) -> Optional[ConsciousnessSignal]:
        """Emit a reflection signal"""

        signal = ConsciousnessSignalFactory.create_reflection_signal(
            consciousness_id=self.consciousness_id,
            producer_module=self.module_name,
            reflection_depth=reflection_depth,
            meta_insights=meta_insights,
        )

        routed_nodes = await self.router.route_signal(signal)
        if routed_nodes:
            self.emission_stats["signals_emitted"] += 1

        return signal

    async def emit_integration_request(
        self, target_modules: list[str], integration_strength: float = 0.8
    ) -> Optional[ConsciousnessSignal]:
        """Emit an integration request signal"""

        signal = ConsciousnessSignalFactory.create_integration_signal(
            consciousness_id=self.consciousness_id,
            producer_module=self.module_name,
            target_modules=target_modules,
            integration_strength=integration_strength,
        )

        routed_nodes = await self.router.route_signal(signal)
        if routed_nodes:
            self.emission_stats["signals_emitted"] += 1

        return signal

    def get_emission_stats(self) -> dict[str, Any]:
        """Get emission statistics for this module"""
        return {
            "module_name": self.module_name,
            "consciousness_id": self.consciousness_id,
            "node_id": self.node_id,
            **self.emission_stats,
        }


class ConsciousnessEmitter(ConsciousnessModuleEmitter):
    """Signal emitter for consciousness module"""

    def _initialize_emission_rules(self):
        """Initialize consciousness-specific emission rules"""

        # Awareness threshold emissions
        self.emission_rules.append(
            EmissionRule(
                rule_id="awareness_threshold",
                trigger_type=EmissionTrigger.THRESHOLD_CROSSED,
                signal_type=ConsciousnessSignalType.AWARENESS,
                trigger_conditions={"awareness_min": 0.8},
                emission_frequency_ms=2000,
            )
        )

        # Reflection cycle emissions
        self.emission_rules.append(
            EmissionRule(
                rule_id="reflection_cycle",
                trigger_type=EmissionTrigger.REFLECTION_CYCLE,
                signal_type=ConsciousnessSignalType.REFLECTION,
                trigger_conditions={"reflection_depth_min": 3},
                emission_frequency_ms=5000,
            )
        )

        # Consciousness state change emissions
        self.emission_rules.append(
            EmissionRule(
                rule_id="state_change",
                trigger_type=EmissionTrigger.STATE_CHANGE,
                signal_type=ConsciousnessSignalType.EVOLUTION,
                trigger_conditions={"state_change_magnitude": 0.2},
                emission_frequency_ms=3000,
            )
        )

    async def emit_consciousness_state_change(
        self, previous_state: dict[str, Any], current_state: dict[str, Any], change_magnitude: float
    ) -> Optional[ConsciousnessSignal]:
        """Emit consciousness state change signal"""

        from .matriz_consciousness_signals import ConsciousnessStateDelta

        state_delta = ConsciousnessStateDelta(
            previous_state=previous_state,
            current_state=current_state,
            delta_magnitude=change_magnitude,
            transition_type="consciousness_evolution",
            confidence_change=current_state.get("confidence", 0.8) - previous_state.get("confidence", 0.8),
            awareness_level_delta=current_state.get("awareness", 0.7) - previous_state.get("awareness", 0.7),
            reflection_depth_change=current_state.get("reflection_depth", 1)
            - previous_state.get("reflection_depth", 1),
        )

        return await self.emit_consciousness_signal(
            signal_type=ConsciousnessSignalType.EVOLUTION,
            awareness_level=current_state.get("awareness", 0.7),
            reflection_depth=current_state.get("reflection_depth", 1),
            processing_hints={"state_delta": state_delta, "change_magnitude": change_magnitude},
        )


class OrchestrationEmitter(ConsciousnessModuleEmitter):
    """Signal emitter for orchestration module"""

    def _initialize_emission_rules(self):
        """Initialize orchestration-specific emission rules"""

        # Integration coordination emissions
        self.emission_rules.append(
            EmissionRule(
                rule_id="integration_coordination",
                trigger_type=EmissionTrigger.INTEGRATION_REQUEST,
                signal_type=ConsciousnessSignalType.INTEGRATION,
                trigger_conditions={"modules_count": 2},
                emission_frequency_ms=1500,
            )
        )

        # System coordination emissions
        self.emission_rules.append(
            EmissionRule(
                rule_id="system_coordination",
                trigger_type=EmissionTrigger.TIME_INTERVAL,
                signal_type=ConsciousnessSignalType.NETWORK_PULSE,
                trigger_conditions={"interval_ms": 10000},
                emission_frequency_ms=10000,
                batch_size=5,
            )
        )

    async def emit_coordination_signal(
        self, coordinated_modules: list[str], coordination_strength: float = 0.8
    ) -> Optional[ConsciousnessSignal]:
        """Emit coordination signal to multiple modules"""

        return await self.emit_consciousness_signal(
            signal_type=ConsciousnessSignalType.INTEGRATION,
            target_modules=coordinated_modules,
            awareness_level=0.8,
            reflection_depth=2,
            processing_hints={
                "coordination_strength": coordination_strength,
                "coordinated_modules": coordinated_modules,
            },
        )

    async def emit_network_health_pulse(self) -> Optional[ConsciousnessSignal]:
        """Emit network health monitoring pulse"""

        network_status = self.router.get_network_status()

        return await self.emit_consciousness_signal(
            signal_type=ConsciousnessSignalType.NETWORK_PULSE,
            awareness_level=network_status["network_metrics"]["network_coherence"],
            reflection_depth=1,
            processing_hints={"network_metrics": network_status["network_metrics"], "health_check": True},
        )


class IdentityEmitter(ConsciousnessModuleEmitter):
    """Signal emitter for identity module"""

    def _initialize_emission_rules(self):
        """Initialize identity-specific emission rules"""

        # Identity authentication emissions
        self.emission_rules.append(
            EmissionRule(
                rule_id="identity_auth",
                trigger_type=EmissionTrigger.STATE_CHANGE,
                signal_type=ConsciousnessSignalType.AWARENESS,
                trigger_conditions={"auth_score_change": 0.1},
                emission_frequency_ms=2500,
            )
        )

        # Identity coherence emissions
        self.emission_rules.append(
            EmissionRule(
                rule_id="identity_coherence",
                trigger_type=EmissionTrigger.THRESHOLD_CROSSED,
                signal_type=ConsciousnessSignalType.TRINITY_SYNC,
                trigger_conditions={"coherence_threshold": 0.9},
                emission_frequency_ms=5000,
            )
        )

    async def emit_identity_authentication(
        self, auth_score: float, identity_context: dict[str, Any]
    ) -> Optional[ConsciousnessSignal]:
        """Emit identity authentication signal"""

        trinity_compliance = ConstellationAlignmentData(
            identity_auth_score=auth_score,
            consciousness_coherence=identity_context.get("coherence", 0.8),
            guardian_compliance=0.95,
            alignment_vector=[auth_score, 0.8, 0.95],
            violation_flags=[],
            ethical_drift_score=0.05,
        )

        return await self.emit_consciousness_signal(
            signal_type=ConsciousnessSignalType.AWARENESS,
            awareness_level=auth_score,
            reflection_depth=1,
            constellation_alignment=trinity_compliance,
            processing_hints=identity_context,
        )

    async def emit_identity_coherence_signal(
        self, coherence_score: float, coherence_factors: dict[str, float]
    ) -> Optional[ConsciousnessSignal]:
        """Emit identity coherence signal"""

        return await self.emit_consciousness_signal(
            signal_type=ConsciousnessSignalType.TRINITY_SYNC,
            awareness_level=coherence_score,
            reflection_depth=2,
            processing_hints={
                "coherence_score": coherence_score,
                "coherence_factors": coherence_factors,
                "trinity_component": "identity",
            },
        )


class GovernanceEmitter(ConsciousnessModuleEmitter):
    """Signal emitter for governance module"""

    def _initialize_emission_rules(self):
        """Initialize governance-specific emission rules"""

        # Guardian compliance emissions
        self.emission_rules.append(
            EmissionRule(
                rule_id="guardian_compliance",
                trigger_type=EmissionTrigger.EVENT_DRIVEN,
                signal_type=ConsciousnessSignalType.TRINITY_SYNC,
                trigger_conditions={"compliance_violation": True},
                emission_frequency_ms=1000,
                priority_boost=0.3,
            )
        )

        # Ethical drift monitoring
        self.emission_rules.append(
            EmissionRule(
                rule_id="ethical_drift",
                trigger_type=EmissionTrigger.THRESHOLD_CROSSED,
                signal_type=ConsciousnessSignalType.AWARENESS,
                trigger_conditions={"drift_threshold": 0.15},
                emission_frequency_ms=3000,
                priority_boost=0.2,
            )
        )

    async def emit_guardian_compliance_signal(
        self, compliance_score: float, violation_flags: list[str], drift_score: float
    ) -> Optional[ConsciousnessSignal]:
        """Emit guardian compliance signal"""

        trinity_compliance = ConstellationAlignmentData(
            identity_auth_score=0.9,
            consciousness_coherence=0.8,
            guardian_compliance=compliance_score,
            alignment_vector=[0.9, 0.8, compliance_score],
            violation_flags=violation_flags,
            ethical_drift_score=drift_score,
        )

        urgency_level = 1.0 - compliance_score  # Lower compliance = higher urgency

        return await self.emit_consciousness_signal(
            signal_type=ConsciousnessSignalType.TRINITY_SYNC,
            awareness_level=min(1.0, 0.5 + compliance_score * 0.5),
            reflection_depth=3,
            constellation_alignment=trinity_compliance,
            processing_hints={
                "guardian_alert": len(violation_flags) > 0,
                "urgency_level": urgency_level,
                "drift_score": drift_score,
            },
        )

    async def emit_ethical_drift_alert(
        self, drift_score: float, drift_factors: dict[str, float]
    ) -> Optional[ConsciousnessSignal]:
        """Emit ethical drift alert signal"""

        return await self.emit_consciousness_signal(
            signal_type=ConsciousnessSignalType.AWARENESS,
            awareness_level=max(0.3, 1.0 - drift_score),  # Higher drift = lower awareness
            reflection_depth=4,  # Deep reflection for ethical concerns
            processing_hints={
                "ethical_alert": True,
                "drift_score": drift_score,
                "drift_factors": drift_factors,
                "priority": "high",
            },
        )


class SymbolicCoreEmitter(ConsciousnessModuleEmitter):
    """Signal emitter for symbolic_core module"""

    def _initialize_emission_rules(self):
        """Initialize symbolic core emission rules"""

        # Symbolic reasoning emissions
        self.emission_rules.append(
            EmissionRule(
                rule_id="symbolic_reasoning",
                trigger_type=EmissionTrigger.EVENT_DRIVEN,
                signal_type=ConsciousnessSignalType.REFLECTION,
                trigger_conditions={"reasoning_completed": True},
                emission_frequency_ms=1500,
            )
        )

        # Symbol coherence emissions
        self.emission_rules.append(
            EmissionRule(
                rule_id="symbol_coherence",
                trigger_type=EmissionTrigger.THRESHOLD_CROSSED,
                signal_type=ConsciousnessSignalType.BIO_ADAPTATION,
                trigger_conditions={"coherence_threshold": 0.75},
                emission_frequency_ms=4000,
            )
        )

    async def emit_symbolic_reasoning_signal(
        self, reasoning_result: dict[str, Any], symbol_coherence: float
    ) -> Optional[ConsciousnessSignal]:
        """Emit symbolic reasoning completion signal"""

        # Create bio-symbolic data representing reasoning patterns
        bio_data = BioSymbolicData(
            pattern_type="symbolic_reasoning",
            oscillation_frequency=15.0 + symbol_coherence * 25,  # Beta-gamma range
            coherence_score=symbol_coherence,
            adaptation_vector={"symbolic_strength": symbol_coherence},
            entropy_delta=0.05,
            resonance_patterns=["symbolic", "reasoning"],
            membrane_permeability=0.8,
            temporal_decay=0.9,
        )

        return await self.emit_consciousness_signal(
            signal_type=ConsciousnessSignalType.REFLECTION,
            awareness_level=0.7,
            reflection_depth=3,
            bio_symbolic_data=bio_data,
            processing_hints={"reasoning_result": reasoning_result, "symbol_coherence": symbol_coherence},
        )

    async def emit_symbol_evolution_signal(
        self, evolved_symbols: list[str], evolution_strength: float
    ) -> Optional[ConsciousnessSignal]:
        """Emit symbol evolution signal"""

        return await self.emit_consciousness_signal(
            signal_type=ConsciousnessSignalType.BIO_ADAPTATION,
            awareness_level=0.6,
            reflection_depth=2,
            processing_hints={
                "evolved_symbols": evolved_symbols,
                "evolution_strength": evolution_strength,
                "adaptation_type": "symbolic",
            },
        )


class MatrizSignalEmissionCoordinator:
    """Coordinates signal emissions across all core modules"""

    def __init__(self):
        self.emitters: dict[str, ConsciousnessModuleEmitter] = {}
        self.router = get_consciousness_router()
        self.emission_history: deque = deque(maxlen=1000)

        # Global emission metrics
        self.global_stats = {
            "total_signals_emitted": 0,
            "signals_per_module": defaultdict(int),
            "signal_types_emitted": defaultdict(int),
            "average_emission_rate": 0.0,
        }

    def register_emitter(self, module_name: str, emitter: ConsciousnessModuleEmitter):
        """Register a module emitter"""
        self.emitters[module_name] = emitter
        logger.info(f"Registered emitter for module: {module_name}")

    def create_module_emitters(self, consciousness_id: str) -> dict[str, ConsciousnessModuleEmitter]:
        """Create all core module emitters"""

        emitters = {
            "consciousness": ConsciousnessEmitter("consciousness", consciousness_id),
            "orchestration": OrchestrationEmitter("orchestration", consciousness_id),
            "identity": IdentityEmitter("identity", consciousness_id),
            "governance": GovernanceEmitter("governance", consciousness_id),
            "symbolic_core": SymbolicCoreEmitter("symbolic_core", consciousness_id),
        }

        # Register all emitters
        for module_name, emitter in emitters.items():
            self.register_emitter(module_name, emitter)

        return emitters

    async def broadcast_network_sync(self, sync_data: dict[str, Any]) -> list[ConsciousnessSignal]:
        """Broadcast synchronization signal to all modules"""

        signals = []
        for emitter in self.emitters.values():
            signal = await emitter.emit_consciousness_signal(
                signal_type=ConsciousnessSignalType.NETWORK_PULSE,
                awareness_level=0.8,
                reflection_depth=1,
                processing_hints={"sync_data": sync_data, "broadcast": True, "source": "coordinator"},
            )
            if signal:
                signals.append(signal)

        return signals

    def get_global_emission_stats(self) -> dict[str, Any]:
        """Get global emission statistics"""

        # Aggregate stats from all emitters
        total_emissions = 0
        for emitter in self.emitters.values():
            stats = emitter.get_emission_stats()
            total_emissions += stats["signals_emitted"]
            self.global_stats["signals_per_module"][stats["module_name"]] = stats["signals_emitted"]

        self.global_stats["total_signals_emitted"] = total_emissions

        return {
            "global_stats": self.global_stats,
            "module_stats": {name: emitter.get_emission_stats() for name, emitter in self.emitters.items()},
            "network_status": self.router.get_network_status(),
        }


# Global coordinator instance
_global_coordinator: Optional[MatrizSignalEmissionCoordinator] = None


def get_emission_coordinator() -> MatrizSignalEmissionCoordinator:
    """Get or create global emission coordinator"""
    global _global_coordinator
    if _global_coordinator is None:
        _global_coordinator = MatrizSignalEmissionCoordinator()
    return _global_coordinator


# Factory functions for creating specific emitters
def create_consciousness_emitter(consciousness_id: str) -> ConsciousnessEmitter:
    """Create consciousness module emitter"""
    return ConsciousnessEmitter("consciousness", consciousness_id)


def create_orchestration_emitter(consciousness_id: str) -> OrchestrationEmitter:
    """Create orchestration module emitter"""
    return OrchestrationEmitter("orchestration", consciousness_id)


def create_identity_emitter(consciousness_id: str) -> IdentityEmitter:
    """Create identity module emitter"""
    return IdentityEmitter("identity", consciousness_id)


def create_governance_emitter(consciousness_id: str) -> GovernanceEmitter:
    """Create governance module emitter"""
    return GovernanceEmitter("governance", consciousness_id)


def create_symbolic_emitter(consciousness_id: str) -> SymbolicCoreEmitter:
    """Create symbolic core emitter"""
    return SymbolicCoreEmitter("symbolic_core", consciousness_id)


# Module exports
__all__ = [
    "EmissionTrigger",
    "EmissionRule",
    "ConsciousnessModuleEmitter",
    "ConsciousnessEmitter",
    "OrchestrationEmitter",
    "IdentityEmitter",
    "GovernanceEmitter",
    "SymbolicCoreEmitter",
    "MatrizSignalEmissionCoordinator",
    "get_emission_coordinator",
    "create_consciousness_emitter",
    "create_orchestration_emitter",
    "create_identity_emitter",
    "create_governance_emitter",
    "create_symbolic_emitter",
]
