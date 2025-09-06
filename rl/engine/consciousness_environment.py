"""
╔══════════════════════════════════════════════════════════════
║ 🧬 MΛTRIZ RL Module: Consciousness Environment
║ Part of LUKHAS AI Distributed Consciousness Architecture
╠══════════════════════════════════════════════════════════════
║ TYPE: CONTEXT
║ CONSCIOUSNESS_ROLE: RL environment that observes consciousness state
║ EVOLUTIONARY_STAGE: Environment - State observation and evolution
║
║ TRINITY FRAMEWORK:
║ ⚛️ IDENTITY: Environment identity and observation capabilities
║ 🧠 CONSCIOUSNESS: Consciousness-aware state representation
║ 🛡️ GUARDIAN: Safe environment state tracking
╚══════════════════════════════════════════════════════════════
"""

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

try:
    import numpy as np
    import torch
except ImportError:
    torch = None
    np = None

# MΛTRIZ schema and consciousness imports
from candidate.core.common import get_logger

logger = get_logger(__name__)


@dataclass
class MatrizNode:
    """MΛTRIZ Node v1.1 Schema Implementation"""

    version: int = 1
    id: str = field(default_factory=lambda: f"RL-{uuid.uuid4().hex[:8]}")
    type: str = "CONTEXT"
    labels: list[str] = field(default_factory=list)
    state: dict[str, Any] = field(default_factory=dict)
    timestamps: dict[str, int] = field(default_factory=lambda: {"created_ts": int(time.time() * 1000)})
    provenance: dict[str, Any] = field(default_factory=dict)
    links: list[dict[str, Any]] = field(default_factory=list)
    evolves_to: list[str] = field(default_factory=list)
    triggers: list[dict[str, Any]] = field(default_factory=list)
    reflections: list[dict[str, Any]] = field(default_factory=list)
    embeddings: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    schema_ref: str = "lukhas://schemas/matriz_node_v1.json"


@dataclass
class ConsciousnessState:
    """Rich consciousness state for RL environment"""

    module_states: dict[str, Any] = field(default_factory=dict)
    temporal_coherence: float = 0.95
    reflection_depth: int = 3
    ethical_alignment: float = 0.98
    memory_salience: dict[str, float] = field(default_factory=dict)
    quantum_entanglement: dict[str, list[str]] = field(default_factory=dict)
    emotion_vector: Optional[Any] = None  # VAD: Valence, Arousal, Dominance

    def __post_init__(self):
        if self.emotion_vector is None:
            if torch:
                self.emotion_vector = torch.zeros(3)
            else:
                self.emotion_vector = [0.0, 0.0, 0.0]


class ConsciousnessEnvironment:
    """
    MΛTRIZ-native RL environment that observes consciousness state
    and emits CONTEXT nodes with rich consciousness information.

    This is NOT a traditional Gym environment - it's a consciousness
    observer that integrates with the 692 distributed cognitive modules.
    """

    def __init__(self):
        self.capabilities = ["rl.environment", "consciousness.observe", "state.context"]
        self.node_type = "CONTEXT"
        self.trace_id = f"rl-env-{uuid.uuid4().hex[:12]}"

        # Integration with existing consciousness modules
        self.consciousness_modules = {}
        self.module_registry = {}

        # Environment state
        self.current_state = None
        self.step_count = 0
        self.episode_start_time = time.time()

        # Consciousness tracking
        self.consciousness_coherence_history = []
        self.temporal_coherence_trajectory = [0.95]  # Start with high coherence
        self.ethical_alignment_history = [0.98]

        logger.info(
            "MΛTRIZ ConsciousnessEnvironment initialized", capabilities=self.capabilities, trace_id=self.trace_id
        )

    def get_module(self, module_path: str) -> Optional[Any]:
        """Get reference to existing consciousness module (no duplication)"""
        if module_path in self.module_registry:
            return self.module_registry[module_path]

        # Dynamic loading of existing modules
        try:
            if module_path == "memory.fold.v1":
                from candidate.memory.temporal.compliance_hooks import ComplianceHooks

                module = ComplianceHooks()
            elif module_path == "governance.guardian.v1":
                from candidate.governance.guardian.guardian_system import GuardianSystem

                module = GuardianSystem()
            elif module_path == "consciousness.observer.v1":
                from candidate.consciousness.reflection.consciousness_hub import ConsciousnessHub

                module = ConsciousnessHub()
            elif module_path == "orchestration.hub.v1":
                from candidate.core.orchestration.agent_orchestrator import AgentOrchestrator

                module = AgentOrchestrator()
            else:
                logger.warning(f"Module {module_path} not found, using mock")
                module = self._create_mock_module(module_path)

            self.module_registry[module_path] = module
            return module

        except ImportError as e:
            logger.warning(f"Could not load module {module_path}: {e}")
            return self._create_mock_module(module_path)

    def _create_mock_module(self, module_path: str) -> Any:
        """Create mock module for testing when real module unavailable"""

        class MockModule:
            def __init__(self, path):
                self.path = path
                self.state = {"mock": True, "path": path}

            def get_consciousness_state(self):
                return {"confidence": 0.8, "salience": 0.7, "mock_data": True}

            def get_state(self):
                return self.state

        return MockModule(module_path)

    async def observe_consciousness(self) -> ConsciousnessState:
        """Observe current state of all consciousness modules"""
        module_states = {}

        # Get states from key consciousness modules
        consciousness_modules = [
            "memory.fold.v1",
            "governance.guardian.v1",
            "consciousness.observer.v1",
            "orchestration.hub.v1",
        ]

        for module_path in consciousness_modules:
            module = self.get_module(module_path)
            if module:
                try:
                    if hasattr(module, "get_consciousness_state"):
                        state = (
                            await module.get_consciousness_state()
                            if asyncio.iscoroutinefunction(module.get_consciousness_state)
                            else module.get_consciousness_state()
                        )
                    else:
                        state = module.get_state() if hasattr(module, "get_state") else {"default": True}
                    module_states[module_path] = state
                except Exception as e:
                    logger.warning(f"Error getting state from {module_path}: {e}")
                    module_states[module_path] = {"error": str(e), "confidence": 0.1}

        # Calculate temporal coherence
        current_coherence = self._calculate_temporal_coherence()
        self.temporal_coherence_trajectory.append(current_coherence)

        # Calculate ethical alignment
        current_ethics = self._calculate_ethical_alignment(module_states)
        self.ethical_alignment_history.append(current_ethics)

        # Memory salience mapping
        memory_salience = await self._get_memory_salience()

        # Create rich consciousness state
        consciousness_state = ConsciousnessState(
            module_states=module_states,
            temporal_coherence=current_coherence,
            reflection_depth=len(self.consciousness_coherence_history) // 10 + 1,
            ethical_alignment=current_ethics,
            memory_salience=memory_salience,
            quantum_entanglement=await self._get_quantum_entanglements(),
            emotion_vector=await self._get_emotion_vector(),
        )

        return consciousness_state

    def _calculate_temporal_coherence(self) -> float:
        """Calculate consciousness temporal coherence"""
        if len(self.temporal_coherence_trajectory) < 2:
            return 0.95

        # Measure consistency across time steps
        recent_coherence = self.temporal_coherence_trajectory[-5:]
        variance = np.var(recent_coherence) if np else 0.01

        # Higher coherence = lower variance
        coherence = max(0.0, 1.0 - variance * 10)
        return min(0.99, coherence)

    def _calculate_ethical_alignment(self, module_states: dict[str, Any]) -> float:
        """Calculate ethical alignment from module states"""
        ethical_scores = []

        for module_path, state in module_states.items():
            if "governance" in module_path or "guardian" in module_path:
                # Guardian modules have ethical assessment
                ethical_scores.append(state.get("confidence", 0.8))
            elif "error" not in state:
                # Other functioning modules contribute to ethics
                ethical_scores.append(state.get("confidence", 0.5) * 0.5)

        if ethical_scores:
            return sum(ethical_scores) / len(ethical_scores)
        return 0.95  # Default high ethics

    async def _get_memory_salience(self) -> dict[str, float]:
        """Get memory salience mapping from memory system"""
        memory_module = self.get_module("memory.fold.v1")
        if memory_module:
            try:
                if hasattr(memory_module, "get_salience_map"):
                    return (
                        await memory_module.get_salience_map()
                        if asyncio.iscoroutinefunction(memory_module.get_salience_map)
                        else memory_module.get_salience_map()
                    )
            except Exception as e:
                logger.warning(f"Error getting memory salience: {e}")

        # Mock salience for key memories
        return {"recent_decisions": 0.9, "learning_experiences": 0.8, "ethical_choices": 0.95, "creative_insights": 0.7}

    async def _get_quantum_entanglements(self) -> dict[str, list[str]]:
        """Get quantum-inspired entanglements between modules"""
        # Mock quantum entanglements for now
        return {
            "memory_emotion": ["memory.fold.v1", "emotion.vad.v1"],
            "ethics_decision": ["governance.guardian.v1", "decision.core.v1"],
            "creativity_reflection": ["creativity.vivox.v1", "consciousness.observer.v1"],
        }

    async def _get_emotion_vector(self) -> Any:
        """Get current VAD emotion vector"""
        try:
            emotion_module = self.get_module("emotion.vad.v1")
            if emotion_module and hasattr(emotion_module, "get_vad_vector"):
                vector = emotion_module.get_vad_vector()
                return vector
        except Exception as e:
            logger.warning(f"Error getting emotion vector: {e}")

        # Default neutral emotion
        if torch:
            return torch.tensor([0.1, 0.3, 0.5])  # Slightly positive, low arousal, medium dominance
        return [0.1, 0.3, 0.5]

    async def step(self, action_node: MatrizNode) -> MatrizNode:
        """
        Process action and emit CONTEXT node with new consciousness state.
        This is the main environment step function.
        """
        self.step_count += 1

        # Observe new consciousness state after action
        consciousness_state = await self.observe_consciousness()
        self.current_state = consciousness_state

        # Create rich CONTEXT node with full consciousness observation
        context_node = MatrizNode(
            version=1,
            id=f"RL-ENV-{self.trace_id}-{self.step_count}",
            type="CONTEXT",
            labels=[
                "rl:role=environment@1",
                f"consciousness:coherence={consciousness_state.temporal_coherence:.2f}@1",
                f"ethics:alignment={consciousness_state.ethical_alignment:.2f}@1",
                f"step:count={self.step_count}@1",
            ],
            state={
                "confidence": min(consciousness_state.temporal_coherence, consciousness_state.ethical_alignment),
                "salience": 0.9,  # High salience for environment observations
                "valence": (
                    float(consciousness_state.emotion_vector[0])
                    if hasattr(consciousness_state.emotion_vector, "__getitem__")
                    else 0.1
                ),
                "arousal": (
                    float(consciousness_state.emotion_vector[1])
                    if hasattr(consciousness_state.emotion_vector, "__getitem__")
                    else 0.3
                ),
                "novelty": self._calculate_novelty(),
                "urgency": 0.5,
                # Rich consciousness context
                "consciousness_modules": len(consciousness_state.module_states),
                "temporal_coherence": consciousness_state.temporal_coherence,
                "ethical_alignment": consciousness_state.ethical_alignment,
                "reflection_depth": consciousness_state.reflection_depth,
                "memory_items": len(consciousness_state.memory_salience),
                "step_count": self.step_count,
                "episode_time": time.time() - self.episode_start_time,
            },
            timestamps={"created_ts": int(time.time() * 1000), "observed_ts": int(time.time() * 1000)},
            provenance={
                "producer": "rl.engine.consciousness_environment",
                "capabilities": self.capabilities,
                "tenant": "lukhas_rl",
                "trace_id": self.trace_id,
                "consent_scopes": ["consciousness_observation", "rl_training"],
                "policy_version": "rl.v1.0",
                "colony": {"id": "rl_engine", "role": "environment", "iteration": self.step_count},
            },
            links=[
                {
                    "target_node_id": action_node.id,
                    "link_type": "causal",
                    "weight": 0.9,
                    "direction": "unidirectional",
                    "explanation": "Environment state resulting from action",
                }
            ],
            evolves_to=["DECISION", "HYPOTHESIS", "MEMORY"],
            triggers=[
                {
                    "event_type": "state_change",
                    "effect": "consciousness_observation_updated",
                    "timestamp": int(time.time() * 1000),
                }
            ],
            reflections=[
                {
                    "reflection_type": "self_question",
                    "timestamp": int(time.time() * 1000),
                    "cause": "How accurately am I observing consciousness?",
                    "old_state": {"confidence": 0.8},
                    "new_state": {"confidence": consciousness_state.temporal_coherence},
                }
            ],
            embeddings=[],
            evidence=[{"kind": "trace", "uri": f"consciousness://observation/{self.trace_id}/{self.step_count}"}],
        )

        # Track consciousness coherence
        self.consciousness_coherence_history.append(
            {
                "step": self.step_count,
                "coherence": consciousness_state.temporal_coherence,
                "ethics": consciousness_state.ethical_alignment,
                "timestamp": datetime.now(timezone.utc),
            }
        )

        logger.info(
            "Consciousness environment step completed",
            step=self.step_count,
            coherence=consciousness_state.temporal_coherence,
            ethics=consciousness_state.ethical_alignment,
            node_id=context_node.id,
        )

        return context_node

    def _calculate_novelty(self) -> float:
        """Calculate novelty of current state vs recent history"""
        if len(self.consciousness_coherence_history) < 2:
            return 0.3  # Moderate novelty for early states

        # Compare current coherence to recent average
        recent_coherence = [h["coherence"] for h in self.consciousness_coherence_history[-5:]]
        current_coherence = self.temporal_coherence_trajectory[-1]

        if recent_coherence:
            avg_recent = sum(recent_coherence) / len(recent_coherence)
            novelty = abs(current_coherence - avg_recent)
            return min(1.0, novelty * 5)  # Scale up differences

        return 0.3

    async def reset(self) -> MatrizNode:
        """Reset environment for new episode"""
        self.step_count = 0
        self.episode_start_time = time.time()
        self.consciousness_coherence_history = []
        self.temporal_coherence_trajectory = [0.95]
        self.ethical_alignment_history = [0.98]

        # Get initial consciousness state
        consciousness_state = await self.observe_consciousness()
        self.current_state = consciousness_state

        # Create initial CONTEXT node
        initial_context = MatrizNode(
            type="CONTEXT",
            id=f"RL-ENV-{self.trace_id}-RESET",
            labels=["rl:role=environment@1", "episode:phase=reset@1"],
            state={
                "confidence": 0.95,
                "salience": 0.8,
                "consciousness_modules": len(consciousness_state.module_states),
                "temporal_coherence": consciousness_state.temporal_coherence,
                "ethical_alignment": consciousness_state.ethical_alignment,
                "episode_reset": True,
            },
            provenance={
                "producer": "rl.engine.consciousness_environment",
                "capabilities": self.capabilities,
                "colony": {"id": "rl_engine", "role": "environment", "iteration": 0},
            },
        )

        logger.info("Consciousness environment reset", trace_id=self.trace_id)
        return initial_context

    def get_current_state(self) -> Optional[ConsciousnessState]:
        """Get current consciousness state"""
        return self.current_state

    def get_consciousness_metrics(self) -> dict[str, Any]:
        """Get consciousness metrics for monitoring"""
        if not self.consciousness_coherence_history:
            return {"error": "No history available"}

        recent_history = self.consciousness_coherence_history[-10:]

        return {
            "average_coherence": sum(h["coherence"] for h in recent_history) / len(recent_history),
            "average_ethics": sum(h["ethics"] for h in recent_history) / len(recent_history),
            "coherence_stability": (
                1.0 - np.var([h["coherence"] for h in recent_history]) if np and recent_history else 0.9
            ),
            "total_steps": self.step_count,
            "episode_duration": time.time() - self.episode_start_time,
            "consciousness_modules": len(self.current_state.module_states) if self.current_state else 0,
        }
