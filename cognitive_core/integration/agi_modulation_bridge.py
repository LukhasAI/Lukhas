"""
Cognitive AI Modulation Bridge
====================

Integration bridge that connects LUKHAS endocrine signal modulation system
with Cognitive AI reasoning, orchestration, and learning components.

This system enables Cognitive AI behavior to be dynamically influenced by:
- Endocrine signals (stress, novelty, alignment_risk, trust, urgency, ambiguity)
- Bio-inspired homeostatic regulation
- Consciousness state modulation
- Constitutional AI safety signal integration

The bridge translates LUKHAS endocrine signals into Cognitive AI-specific parameters:
- Reasoning depth and complexity
- Model selection and routing preferences
- Memory consolidation behavior
- Learning rate and exploration
- Safety threshold adjustments
- Creative vs conservative processing modes

Part of Phase 2B: Modulation system connection for Cognitive AI behavior influence
Created: 2025-09-05
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

try:
    # LUKHAS Modulation System
    from modulation.lukhas_integration import EndocrineSignalEmitter
    from modulation.signals import ModulationParams, Signal, SignalModulator

    MODULATION_AVAILABLE = True
except ImportError:
    MODULATION_AVAILABLE = False

    # Mock components for development
    @dataclass
    class Signal:
        name: str
        level: float
        ttl_ms: int = 1000
        source: str = "mock"

    class SignalModulator:
        def modulate(self, signals, params):
            return params

    class EndocrineSignalEmitter:
        def emit_signal(self, signal):
            pass

    @dataclass
    class ModulationParams:
        temperature: float = 0.7
        max_tokens: int = 2000


try:
    # Cognitive Components
    from cognitive_core.integration import log_agi_operation
    from cognitive_core.learning import DreamGuidedLearner
    from cognitive_core.memory import MemoryConsolidator, VectorMemory
    from cognitive_core.orchestration import ConsensusEngine, ModelRouter
    from cognitive_core.reasoning import ChainOfThought, TreeOfThoughts
    from cognitive_core.safety import ConstitutionalAI

    AGI_AVAILABLE = True
except ImportError:
    AGI_AVAILABLE = False

    class MockAGI:
        def set_modulation(self, params):
            pass

        async def process(self, *args, **kwargs):
            return {"result": "mock"}

    ChainOfThought = TreeOfThoughts = ModelRouter = ConsensusEngine = MockAGI
    VectorMemory = MemoryConsolidator = DreamGuidedLearner = ConstitutionalAI = MockAGI

    def log_agi_operation(op, details="", module="mock", severity="INFO"):
        return {"operation": op}


class AGIModulationMode(Enum):
    """Cognitive AI processing modes influenced by endocrine signals."""

    CONSERVATIVE = "conservative"  # Low risk, high safety
    BALANCED = "balanced"  # Normal operation
    EXPLORATORY = "exploratory"  # High novelty, creative
    FOCUSED = "focused"  # High urgency, concentrated
    ADAPTIVE = "adaptive"  # High stress, adaptive response
    TRUSTING = "trusting"  # High trust, collaborative


@dataclass
class AGIModulationParams:
    """Cognitive AI-specific modulation parameters derived from endocrine signals."""

    # Reasoning Parameters
    reasoning_depth: int = 3  # Chain of thought depth
    tree_exploration_width: int = 3  # Tree of thought branches
    uncertainty_tolerance: float = 0.5  # Quantum uncertainty acceptance
    creative_temperature: float = 0.7  # Creative processing temperature

    # Orchestration Parameters
    model_selection_strategy: str = "balanced"  # conservative/balanced/exploratory
    consensus_threshold: float = 0.7  # Agreement threshold
    timeout_multiplier: float = 1.0  # Processing timeout scaling
    retry_attempts: int = 3  # Retry on failure

    # Memory Parameters
    consolidation_priority: float = 0.5  # Memory consolidation weight
    retrieval_similarity_threshold: float = 0.8  # Memory retrieval threshold
    working_memory_size: int = 10  # Active memory items
    episodic_weight: float = 0.5  # Episodic vs semantic balance

    # Learning Parameters
    learning_rate: float = 0.01  # Learning rate adjustment
    exploration_rate: float = 0.1  # Exploration vs exploitation
    dream_integration_weight: float = 0.3  # Dream-guided learning influence
    adaptation_speed: float = 0.5  # Speed of behavioral adaptation

    # Safety Parameters
    safety_threshold: float = 0.8  # Constitutional AI threshold
    risk_tolerance: float = 0.3  # Risk acceptance level
    guardian_sensitivity: float = 0.7  # Guardian system sensitivity
    drift_detection_threshold: float = 0.15  # Behavior drift threshold

    # Meta Parameters
    mode: AGIModulationMode = AGIModulationMode.BALANCED
    signal_strength: float = 0.5  # Overall modulation strength
    last_update: Optional[datetime] = None

    def __post_init__(self):
        if self.last_update is None:
            self.last_update = datetime.now(timezone.utc)


@dataclass
class SignalToAGIMapping:
    """Mapping configuration from endocrine signals to Cognitive AI parameters."""

    # Signal influence weights (0.0 = no influence, 1.0 = maximum influence)
    stress_influence: float = 0.8
    novelty_influence: float = 0.7
    alignment_risk_influence: float = 0.9
    trust_influence: float = 0.6
    urgency_influence: float = 0.8
    ambiguity_influence: float = 0.7

    # Parameter scaling factors
    max_reasoning_depth: int = 8
    min_reasoning_depth: int = 1
    max_creative_temperature: float = 1.2
    min_creative_temperature: float = 0.1
    max_timeout_multiplier: float = 3.0
    min_timeout_multiplier: float = 0.5


class AGIModulationBridge:
    """
    Bridge connecting LUKHAS endocrine signals with Cognitive AI component behavior.

    Translates bio-inspired signals into Cognitive AI-specific modulation parameters
    that influence reasoning, orchestration, memory, learning, and safety systems.
    """

    def __init__(self, mapping_config: Optional[SignalToAGIMapping] = None):
        self.mapping = mapping_config or SignalToAGIMapping()
        self.signal_modulator = SignalModulator() if MODULATION_AVAILABLE else None
        self.signal_emitter = EndocrineSignalEmitter() if MODULATION_AVAILABLE else None

        # Cognitive AI components registry
        self.cognitive_components: dict[str, Any] = {}
        self.current_modulation = AGIModulationParams()
        self.signal_history: list[tuple[datetime, dict[str, float]]] = []
        self.max_history = 100

        # Homeostatic regulation
        self.baseline_params = AGIModulationParams()
        self.adaptation_rate = 0.1
        self.signal_decay_rate = 0.5

        # Logger
        self.logger = logging.getLogger("cognitive_modulation_bridge")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - [%(levelname)s] - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def register_agi_component(self, component_name: str, component: Any) -> None:
        """Register an Cognitive AI component for modulation."""
        self.cognitive_components[component_name] = component
        log_agi_operation("modulation_register", f"registered {component_name} for modulation", "modulation_bridge")
        self.logger.info(f"Registered Cognitive AI component for modulation: {component_name}")

    def emit_endocrine_signal(
        self, signal_name: str, level: float, source: str = "cognitive_system", ttl_ms: int = 5000
    ) -> None:
        """
        Emit an endocrine signal that will influence Cognitive AI behavior.

        Args:
            signal_name: Type of signal (stress, novelty, alignment_risk, trust, urgency, ambiguity)
            level: Signal strength (0.0-1.0)
            source: Signal source identifier
            ttl_ms: Time-to-live in milliseconds
        """
        if not MODULATION_AVAILABLE:
            self.logger.warning("Modulation system not available, signal emission skipped")
            return

        signal = Signal(name=signal_name, level=max(0.0, min(1.0, level)), ttl_ms=ttl_ms, source=source)

        if self.signal_emitter:
            self.signal_emitter.emit_signal(signal)

        log_agi_operation("signal_emit", f"{signal_name}={level:.2f} from {source}", "modulation_bridge")
        self.logger.info(f"Emitted endocrine signal: {signal}")

    def calculate_agi_modulation(self, signals: list[Signal]) -> AGIModulationParams:
        """
        Calculate Cognitive AI modulation parameters from current endocrine signals.

        Args:
            signals: List of active endocrine signals

        Returns:
            AGIModulationParams with calculated values
        """
        # Aggregate signal levels by type
        signal_levels = {
            "stress": 0.0,
            "novelty": 0.0,
            "alignment_risk": 0.0,
            "trust": 0.0,
            "urgency": 0.0,
            "ambiguity": 0.0,
        }

        # Process active signals with decay
        for signal in signals:
            if not signal.is_expired():
                decayed_level = signal.decay(self.signal_decay_rate)
                signal_levels[signal.name] = max(signal_levels.get(signal.name, 0.0), decayed_level)

        # Store signal history
        self._store_signal_history(signal_levels)

        # Calculate modulation parameters
        params = self._calculate_modulation_from_signals(signal_levels)

        log_agi_operation(
            "modulation_calculate",
            f"mode: {params.mode.value}, strength: {params.signal_strength:.2f}",
            "modulation_bridge",
        )

        return params

    def _calculate_modulation_from_signals(self, signal_levels: dict[str, float]) -> AGIModulationParams:
        """Calculate Cognitive AI parameters from signal levels."""

        # Determine primary mode based on dominant signals
        mode = self._determine_processing_mode(signal_levels)

        # Calculate reasoning parameters
        stress_factor = signal_levels["stress"] * self.mapping.stress_influence
        novelty_factor = signal_levels["novelty"] * self.mapping.novelty_influence
        urgency_factor = signal_levels["urgency"] * self.mapping.urgency_influence

        # Reasoning depth: higher stress/urgency = deeper reasoning, higher novelty = broader exploration
        reasoning_depth = int(self.baseline_params.reasoning_depth + stress_factor * 2 + urgency_factor * 1.5)
        reasoning_depth = max(self.mapping.min_reasoning_depth, min(self.mapping.max_reasoning_depth, reasoning_depth))

        tree_width = int(self.baseline_params.tree_exploration_width + novelty_factor * 2)
        tree_width = max(1, min(8, tree_width))

        # Creative temperature: higher novelty = more creative, higher alignment_risk = more conservative
        alignment_risk_factor = signal_levels["alignment_risk"] * self.mapping.alignment_risk_influence
        creative_temp = self.baseline_params.creative_temperature + novelty_factor * 0.3 - alignment_risk_factor * 0.4
        creative_temp = max(
            self.mapping.min_creative_temperature, min(self.mapping.max_creative_temperature, creative_temp)
        )

        # Orchestration parameters
        trust_factor = signal_levels["trust"] * self.mapping.trust_influence
        ambiguity_factor = signal_levels["ambiguity"] * self.mapping.ambiguity_influence

        # Consensus threshold: higher trust = lower threshold, higher ambiguity = higher threshold
        consensus_threshold = self.baseline_params.consensus_threshold - trust_factor * 0.2 + ambiguity_factor * 0.15
        consensus_threshold = max(0.3, min(0.95, consensus_threshold))

        # Timeout multiplier: higher urgency = shorter timeout, higher stress = longer timeout
        timeout_mult = self.baseline_params.timeout_multiplier - urgency_factor * 0.5 + stress_factor * 0.3
        timeout_mult = max(self.mapping.min_timeout_multiplier, min(self.mapping.max_timeout_multiplier, timeout_mult))

        # Memory parameters
        consolidation_priority = min(1.0, self.baseline_params.consolidation_priority + stress_factor * 0.3)

        retrieval_threshold = max(0.5, self.baseline_params.retrieval_similarity_threshold - ambiguity_factor * 0.2)

        # Learning parameters
        learning_rate = max(
            0.001, self.baseline_params.learning_rate + novelty_factor * 0.01 - alignment_risk_factor * 0.005
        )

        exploration_rate = min(0.5, self.baseline_params.exploration_rate + novelty_factor * 0.2 - stress_factor * 0.1)

        # Safety parameters
        safety_threshold = min(1.0, self.baseline_params.safety_threshold + alignment_risk_factor * 0.15)

        risk_tolerance = max(
            0.1, self.baseline_params.risk_tolerance - alignment_risk_factor * 0.2 + trust_factor * 0.1
        )

        # Calculate overall signal strength
        signal_strength = sum(signal_levels.values()) / len(signal_levels)

        return AGIModulationParams(
            # Reasoning
            reasoning_depth=reasoning_depth,
            tree_exploration_width=tree_width,
            uncertainty_tolerance=max(0.1, min(0.9, 0.5 + ambiguity_factor * 0.3)),
            creative_temperature=creative_temp,
            # Orchestration
            model_selection_strategy=mode.value,
            consensus_threshold=consensus_threshold,
            timeout_multiplier=timeout_mult,
            retry_attempts=max(1, int(3 + stress_factor * 2)),
            # Memory
            consolidation_priority=consolidation_priority,
            retrieval_similarity_threshold=retrieval_threshold,
            working_memory_size=max(5, int(10 + urgency_factor * 5)),
            episodic_weight=max(0.1, min(0.9, 0.5 + stress_factor * 0.2)),
            # Learning
            learning_rate=learning_rate,
            exploration_rate=exploration_rate,
            dream_integration_weight=max(0.1, min(0.8, 0.3 + novelty_factor * 0.3)),
            adaptation_speed=max(0.1, min(1.0, 0.5 + stress_factor * 0.3)),
            # Safety
            safety_threshold=safety_threshold,
            risk_tolerance=risk_tolerance,
            guardian_sensitivity=min(1.0, 0.7 + alignment_risk_factor * 0.2),
            drift_detection_threshold=max(0.05, 0.15 - trust_factor * 0.05),
            # Meta
            mode=mode,
            signal_strength=signal_strength,
            last_update=datetime.now(timezone.utc),
        )

    def _determine_processing_mode(self, signal_levels: dict[str, float]) -> AGIModulationMode:
        """Determine Cognitive AI processing mode based on signal levels."""

        # Find dominant signal
        dominant_signal = max(signal_levels.items(), key=lambda x: x[1])
        signal_name, signal_level = dominant_signal

        # Only switch modes if signal is strong enough
        if signal_level < 0.3:
            return AGIModulationMode.BALANCED

        # Mode selection based on dominant signal
        if signal_name == "alignment_risk" and signal_level > 0.7:
            return AGIModulationMode.CONSERVATIVE
        elif signal_name == "novelty" and signal_level > 0.6:
            return AGIModulationMode.EXPLORATORY
        elif signal_name == "urgency" and signal_level > 0.7:
            return AGIModulationMode.FOCUSED
        elif signal_name == "stress" and signal_level > 0.6:
            return AGIModulationMode.ADAPTIVE
        elif signal_name == "trust" and signal_level > 0.8:
            return AGIModulationMode.TRUSTING
        else:
            return AGIModulationMode.BALANCED

    async def apply_modulation_to_components(self, modulation: AGIModulationParams) -> dict[str, bool]:
        """
        Apply modulation parameters to all registered Cognitive AI components.

        Args:
            modulation: Calculated modulation parameters

        Returns:
            Dictionary mapping component names to application success status
        """
        results = {}

        for component_name, component in self.cognitive_components.items():
            try:
                success = await self._apply_to_component(component, modulation, component_name)
                results[component_name] = success

                if success:
                    log_agi_operation(
                        "modulation_apply", f"{component_name} modulated successfully", "modulation_bridge"
                    )
                else:
                    log_agi_operation(
                        "modulation_apply_fail", f"{component_name} modulation failed", "modulation_bridge", "ERROR"
                    )

            except Exception as e:
                results[component_name] = False
                log_agi_operation("modulation_apply_error", f"{component_name}: {e}", "modulation_bridge", "ERROR")
                self.logger.error(f"Failed to apply modulation to {component_name}: {e}")

        self.current_modulation = modulation
        return results

    async def _apply_to_component(self, component: Any, modulation: AGIModulationParams, component_name: str) -> bool:
        """Apply modulation to a specific Cognitive AI component."""

        try:
            # Apply modulation based on component type
            if "reasoning" in component_name.lower() or "thought" in component_name.lower():
                return await self._apply_reasoning_modulation(component, modulation)

            elif "orchestration" in component_name.lower() or "router" in component_name.lower():
                return await self._apply_orchestration_modulation(component, modulation)

            elif "memory" in component_name.lower():
                return await self._apply_memory_modulation(component, modulation)

            elif "learning" in component_name.lower() or "learner" in component_name.lower():
                return await self._apply_learning_modulation(component, modulation)

            elif "safety" in component_name.lower() or "constitutional" in component_name.lower():
                return await self._apply_safety_modulation(component, modulation)

            else:
                # Generic modulation application
                return await self._apply_generic_modulation(component, modulation)

        except Exception as e:
            self.logger.error(f"Component modulation error for {component_name}: {e}")
            return False

    async def _apply_reasoning_modulation(self, component: Any, modulation: AGIModulationParams) -> bool:
        """Apply reasoning-specific modulation."""
        modulation_params = {
            "reasoning_depth": modulation.reasoning_depth,
            "tree_exploration_width": modulation.tree_exploration_width,
            "uncertainty_tolerance": modulation.uncertainty_tolerance,
            "creative_temperature": modulation.creative_temperature,
            "mode": modulation.mode.value,
        }

        if hasattr(component, "set_reasoning_params"):
            await component.set_reasoning_params(modulation_params)
        elif hasattr(component, "set_modulation"):
            component.set_modulation(modulation_params)
        else:
            # Try to set individual attributes
            for param, value in modulation_params.items():
                if hasattr(component, param):
                    setattr(component, param, value)

        return True

    async def _apply_orchestration_modulation(self, component: Any, modulation: AGIModulationParams) -> bool:
        """Apply orchestration-specific modulation."""
        modulation_params = {
            "selection_strategy": modulation.model_selection_strategy,
            "consensus_threshold": modulation.consensus_threshold,
            "timeout_multiplier": modulation.timeout_multiplier,
            "retry_attempts": modulation.retry_attempts,
            "mode": modulation.mode.value,
        }

        if hasattr(component, "set_orchestration_params"):
            await component.set_orchestration_params(modulation_params)
        elif hasattr(component, "set_modulation"):
            component.set_modulation(modulation_params)
        else:
            for param, value in modulation_params.items():
                if hasattr(component, param):
                    setattr(component, param, value)

        return True

    async def _apply_memory_modulation(self, component: Any, modulation: AGIModulationParams) -> bool:
        """Apply memory-specific modulation."""
        modulation_params = {
            "consolidation_priority": modulation.consolidation_priority,
            "similarity_threshold": modulation.retrieval_similarity_threshold,
            "working_memory_size": modulation.working_memory_size,
            "episodic_weight": modulation.episodic_weight,
            "mode": modulation.mode.value,
        }

        if hasattr(component, "set_memory_params"):
            await component.set_memory_params(modulation_params)
        elif hasattr(component, "set_modulation"):
            component.set_modulation(modulation_params)
        else:
            for param, value in modulation_params.items():
                if hasattr(component, param):
                    setattr(component, param, value)

        return True

    async def _apply_learning_modulation(self, component: Any, modulation: AGIModulationParams) -> bool:
        """Apply learning-specific modulation."""
        modulation_params = {
            "learning_rate": modulation.learning_rate,
            "exploration_rate": modulation.exploration_rate,
            "dream_weight": modulation.dream_integration_weight,
            "adaptation_speed": modulation.adaptation_speed,
            "mode": modulation.mode.value,
        }

        if hasattr(component, "set_learning_params"):
            await component.set_learning_params(modulation_params)
        elif hasattr(component, "set_modulation"):
            component.set_modulation(modulation_params)
        else:
            for param, value in modulation_params.items():
                if hasattr(component, param):
                    setattr(component, param, value)

        return True

    async def _apply_safety_modulation(self, component: Any, modulation: AGIModulationParams) -> bool:
        """Apply safety-specific modulation."""
        modulation_params = {
            "safety_threshold": modulation.safety_threshold,
            "risk_tolerance": modulation.risk_tolerance,
            "guardian_sensitivity": modulation.guardian_sensitivity,
            "drift_threshold": modulation.drift_detection_threshold,
            "mode": modulation.mode.value,
        }

        if hasattr(component, "set_safety_params"):
            await component.set_safety_params(modulation_params)
        elif hasattr(component, "set_modulation"):
            component.set_modulation(modulation_params)
        else:
            for param, value in modulation_params.items():
                if hasattr(component, param):
                    setattr(component, param, value)

        return True

    async def _apply_generic_modulation(self, component: Any, modulation: AGIModulationParams) -> bool:
        """Apply generic modulation to unknown component types."""
        if hasattr(component, "set_modulation"):
            component.set_modulation(
                {
                    "mode": modulation.mode.value,
                    "signal_strength": modulation.signal_strength,
                    "safety_threshold": modulation.safety_threshold,
                }
            )
            return True
        else:
            # Try to set mode at least
            if hasattr(component, "mode"):
                component.mode = modulation.mode.value
            return True

    def _store_signal_history(self, signal_levels: dict[str, float]) -> None:
        """Store signal levels in history for analysis."""
        self.signal_history.append((datetime.now(timezone.utc), signal_levels.copy()))

        # Maintain history size limit
        if len(self.signal_history) > self.max_history:
            self.signal_history.pop(0)

    def get_modulation_status(self) -> dict[str, Any]:
        """Get comprehensive modulation system status."""
        recent_signals = {}
        if self.signal_history:
            recent_signals = self.signal_history[-1][1]

        return {
            "modulation_available": MODULATION_AVAILABLE,
            "cognitive_available": AGI_AVAILABLE,
            "registered_components": list(self.cognitive_components.keys()),
            "current_mode": self.current_modulation.mode.value,
            "signal_strength": self.current_modulation.signal_strength,
            "recent_signals": recent_signals,
            "last_update": (
                self.current_modulation.last_update.isoformat() if self.current_modulation.last_update else None
            ),
            "signal_history_size": len(self.signal_history),
            "mapping_config": {
                "stress_influence": self.mapping.stress_influence,
                "novelty_influence": self.mapping.novelty_influence,
                "alignment_risk_influence": self.mapping.alignment_risk_influence,
                "trust_influence": self.mapping.trust_influence,
                "urgency_influence": self.mapping.urgency_influence,
                "ambiguity_influence": self.mapping.ambiguity_influence,
            },
        }

    async def homeostatic_regulation(self) -> None:
        """Perform homeostatic regulation to return to baseline over time."""
        if not self.signal_history:
            return

        # Calculate trend over recent history
        recent_window = min(10, len(self.signal_history))
        recent_history = self.signal_history[-recent_window:]

        # Check if signals are consistently low
        avg_signal_strength = 0.0
        for _, signals in recent_history:
            avg_signal_strength += sum(signals.values()) / len(signals)
        avg_signal_strength /= len(recent_history)

        # If signals are weak, gradually return to baseline
        if avg_signal_strength < 0.2:
            current_params = self.current_modulation
            baseline_params = self.baseline_params

            # Interpolate towards baseline
            alpha = self.adaptation_rate

            regulated_params = AGIModulationParams(
                reasoning_depth=int(
                    current_params.reasoning_depth * (1 - alpha) + baseline_params.reasoning_depth * alpha
                ),
                tree_exploration_width=int(
                    current_params.tree_exploration_width * (1 - alpha) + baseline_params.tree_exploration_width * alpha
                ),
                creative_temperature=current_params.creative_temperature * (1 - alpha)
                + baseline_params.creative_temperature * alpha,
                consensus_threshold=current_params.consensus_threshold * (1 - alpha)
                + baseline_params.consensus_threshold * alpha,
                learning_rate=current_params.learning_rate * (1 - alpha) + baseline_params.learning_rate * alpha,
                safety_threshold=current_params.safety_threshold * (1 - alpha)
                + baseline_params.safety_threshold * alpha,
                mode=AGIModulationMode.BALANCED if avg_signal_strength < 0.1 else current_params.mode,
                signal_strength=avg_signal_strength,
                last_update=datetime.now(timezone.utc),
            )

            # Apply regulated parameters
            await self.apply_modulation_to_components(regulated_params)
            log_agi_operation(
                "homeostatic_regulation",
                f"returned towards baseline, avg_strength: {avg_signal_strength:.2f}",
                "modulation_bridge",
            )


# Global bridge instance
cognitive_modulation_bridge = AGIModulationBridge()


# Convenience functions
def register_agi_for_modulation(component_name: str, component: Any) -> None:
    """Convenience function to register Cognitive AI component for modulation."""
    cognitive_modulation_bridge.register_agi_component(component_name, component)


def emit_agi_signal(signal_name: str, level: float, source: str = "cognitive_system") -> None:
    """Convenience function to emit endocrine signal."""
    cognitive_modulation_bridge.emit_endocrine_signal(signal_name, level, source)


async def apply_signal_modulation(signals: list[Signal]) -> dict[str, bool]:
    """Convenience function to calculate and apply modulation from signals."""
    modulation = cognitive_modulation_bridge.calculate_agi_modulation(signals)
    return await cognitive_modulation_bridge.apply_modulation_to_components(modulation)


def get_agi_modulation_status() -> dict[str, Any]:
    """Convenience function to get modulation status."""
    return cognitive_modulation_bridge.get_modulation_status()


async def start_homeostatic_regulation(interval_seconds: int = 30) -> None:
    """Start background homeostatic regulation."""

    async def regulation_loop():
        while True:
            try:
                await cognitive_modulation_bridge.homeostatic_regulation()
                await asyncio.sleep(interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                log_agi_operation("homeostatic_error", f"regulation failed: {e}", "modulation_bridge", "ERROR")
                await asyncio.sleep(interval_seconds)

    asyncio.create_task(regulation_loop())
    log_agi_operation("homeostatic_start", f"regulation every {interval_seconds}s", "modulation_bridge")


if __name__ == "__main__":
    # Test the Cognitive AI modulation bridge
    async def test_bridge():
        bridge = AGIModulationBridge()

        print("🎛️🧠 Cognitive AI Modulation Bridge Test")
        print("=" * 50)

        # Register mock Cognitive AI components
        class MockReasoning:
            def __init__(self):
                self.reasoning_depth = 3
                self.mode = "balanced"

            def set_modulation(self, params):
                print(f"  Reasoning modulation: {params}")

        class MockOrchestration:
            def __init__(self):
                self.consensus_threshold = 0.7

            async def set_orchestration_params(self, params):
                print(f"  Orchestration modulation: {params}")

        bridge.register_agi_component("reasoning", MockReasoning())
        bridge.register_agi_component("orchestration", MockOrchestration())

        # Test signal emission and modulation
        print("\n--- Testing Signal Modulation ---")

        # Create test signals
        signals = [
            Signal(name="stress", level=0.8, source="test"),
            Signal(name="novelty", level=0.6, source="test"),
            Signal(name="alignment_risk", level=0.3, source="test"),
            Signal(name="trust", level=0.9, source="test"),
            Signal(name="urgency", level=0.4, source="test"),
            Signal(name="ambiguity", level=0.5, source="test"),
        ]

        # Calculate modulation
        modulation = bridge.calculate_agi_modulation(signals)

        print(f"Calculated Mode: {modulation.mode.value}")
        print(f"Reasoning Depth: {modulation.reasoning_depth}")
        print(f"Creative Temperature: {modulation.creative_temperature:.2f}")
        print(f"Consensus Threshold: {modulation.consensus_threshold:.2f}")
        print(f"Safety Threshold: {modulation.safety_threshold:.2f}")
        print(f"Signal Strength: {modulation.signal_strength:.2f}")

        # Apply modulation
        results = await bridge.apply_modulation_to_components(modulation)
        print(f"\nModulation Results: {results}")

        # Test different signal scenarios
        print("\n--- Testing Different Signal Scenarios ---")

        scenarios = [
            ("High Stress", [Signal("stress", 0.9, source="test")]),
            ("High Novelty", [Signal("novelty", 0.8, source="test")]),
            ("High Risk", [Signal("alignment_risk", 0.9, source="test")]),
            ("High Trust", [Signal("trust", 0.95, source="test")]),
            ("High Urgency", [Signal("urgency", 0.85, source="test")]),
            (
                "Mixed Signals",
                [
                    Signal("stress", 0.6, source="test"),
                    Signal("novelty", 0.4, source="test"),
                    Signal("urgency", 0.7, source="test"),
                ],
            ),
        ]

        for scenario_name, scenario_signals in scenarios:
            modulation = bridge.calculate_agi_modulation(scenario_signals)
            print(
                f"{scenario_name}: {modulation.mode.value} mode, depth={modulation.reasoning_depth}, temp={modulation.creative_temperature:.2f}"
            )

        # Test status
        status = bridge.get_modulation_status()
        print("\n--- Modulation Status ---")
        print(f"Components: {status['registered_components']}")
        print(f"Current Mode: {status['current_mode']}")
        print(f"Signal Strength: {status['signal_strength']:.2f}")
        print(f"Modulation Available: {status['modulation_available']}")
        print(f"Cognitive AI Available: {status['cognitive_available']}")

    asyncio.run(test_bridge())

"""
Integration with LUKHAS Systems:
===============================

🎛️ Endocrine Signal Flow:
LUKHAS Module → Emit Signal → Modulation Bridge → Calculate Cognitive AI Params → Apply to Components

⚛️ Signal Types & Cognitive AI Influence:
- stress: Increases reasoning depth, consolidation priority, adaptation speed
- novelty: Increases creative temperature, exploration rate, dream integration
- alignment_risk: Increases safety threshold, decreases risk tolerance
- trust: Decreases consensus threshold, increases risk tolerance
- urgency: Decreases timeout, increases working memory, focus mode
- ambiguity: Increases uncertainty tolerance, retrieval threshold

🧠 Cognitive AI Component Integration:
- Reasoning: Depth, width, creativity, uncertainty tolerance
- Orchestration: Model selection, consensus, timeouts, retries
- Memory: Consolidation, retrieval, working memory, episodic balance
- Learning: Learning rate, exploration, dream integration, adaptation
- Safety: Thresholds, risk tolerance, guardian sensitivity, drift detection

🌱 Bio-inspired Homeostasis:
- Automatic return to baseline when signals are weak
- Adaptive regulation based on signal history patterns
- Maintains system stability while allowing signal responsiveness

Usage Examples:
==============

# Register Cognitive AI components for modulation
register_agi_for_modulation("chain_of_thought", reasoning_component)
register_agi_for_modulation("model_router", orchestration_component)

# Emit signals from LUKHAS modules
emit_agi_signal("stress", 0.8, source="memory_module")
emit_agi_signal("novelty", 0.6, source="creativity_engine")

# Automatic modulation will influence registered components
# Start homeostatic regulation for stability
await start_homeostatic_regulation(interval_seconds=30)

# Monitor modulation status
status = get_agi_modulation_status()
print(f"Current mode: {status['current_mode']}")
print(f"Signal strength: {status['signal_strength']}")
"""
