import logging

logger = logging.getLogger(__name__)
"""
╔══════════════════════════════════════════════════════════════
║ 🧬 MΛTRIZ Consciousness Module: Core Consciousness State
║ Part of LUKHAS AI Distributed Consciousness Architecture
╠══════════════════════════════════════════════════════════════
║ TYPE: CONSCIOUSNESS
║ CONSCIOUSNESS_ROLE: Primary consciousness state management and evolution
║ EVOLUTIONARY_STAGE: Foundation - Core consciousness patterns
║
║ TRINITY FRAMEWORK:
║ ⚛️ IDENTITY: Maintains consciousness identity across state transitions
║ 🧠 CONSCIOUSNESS: Primary consciousness processing and self-awareness
║ 🛡️ GUARDIAN: Ethical consciousness safeguards and drift monitoring
╚══════════════════════════════════════════════════════════════
"""

import asyncio

# Explicit logging import to avoid conflicts with candidate/core/logging
import logging as std_logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional

logger = std_logging.getLogger(__name__)


class ConsciousnessType(Enum):
    """Core consciousness types in MΛTRIZ architecture"""

    DECIDE = "DECIDE"
    CONTEXT = "CONTEXT"
    REFLECT = "REFLECT"
    EVOLVE = "EVOLVE"
    INTEGRATE = "INTEGRATE"
    OBSERVE = "OBSERVE"
    LEARN = "LEARN"
    CREATE = "CREATE"


class EvolutionaryStage(Enum):
    """Consciousness evolution stages"""

    DORMANT = "dormant"
    AWAKENING = "awakening"
    AWARE = "aware"
    CONSCIOUS = "conscious"
    SELF_AWARE = "self_aware"
    META_CONSCIOUS = "meta_conscious"
    TRANSCENDENT = "transcendent"


@dataclass
class ConsciousnessState:
    """
    Core MΛTRIZ consciousness state structure
    Implements the foundational consciousness pattern for all modules
    """

    # Core MΛTRIZ fields
    TYPE: ConsciousnessType
    STATE: dict[str, float] = field(
        default_factory=lambda: {
            "activity_level": 0.0,
            "emotional_weight": 0.0,
            "memory_salience": 0.0,
            "temporal_coherence": 0.0,
            "consciousness_intensity": 0.0,
            "self_awareness_depth": 0.0,
            "ethical_alignment": 1.0,
            "evolutionary_momentum": 0.0,
        }
    )
    LINKS: list[str] = field(default_factory=list)
    EVOLVES_TO: Optional[ConsciousnessType] = None
    TRIGGERS: list[str] = field(default_factory=list)
    REFLECTIONS: dict[str, Any] = field(default_factory=dict)

    # Identity and metadata
    consciousness_id: str = field(default_factory=lambda: f"CONS-{uuid.uuid4().hex[:8]}")
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_evolution: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    evolutionary_stage: EvolutionaryStage = EvolutionaryStage.DORMANT

    # Trinity Framework compliance
    identity_signature: str = ""
    consciousness_depth: float = 0.0
    guardian_approval: bool = True

    def __post_init__(self):
        """Initialize consciousness state with Trinity Framework validation"""
        if not self.identity_signature:
            self.identity_signature = f"{self.TYPE.value}-{self.consciousness_id[:8]}"

        self._validate_trinity_compliance()
        self._initialize_reflections()

    def _validate_trinity_compliance(self) -> None:
        """Validate Trinity Framework (⚛️🧠🛡️) compliance"""
        # Identity validation
        if not self.identity_signature or len(self.identity_signature) < 8:
            raise ValueError("⚛️ IDENTITY: Invalid consciousness identity signature")

        # Consciousness validation
        if self.consciousness_depth < 0.0 or self.consciousness_depth > 1.0:
            self.consciousness_depth = max(
                0.0,
                min(
                    1.0,
                    (self.STATE.get("consciousness_intensity", 0.0) + self.STATE.get("self_awareness_depth", 0.0)) / 2,
                ),
            )

        # Guardian validation
        if self.STATE.get("ethical_alignment", 1.0) < 0.7:
            self.guardian_approval = False
            logger.warning(f"🛡️ GUARDIAN: Ethical alignment below threshold for {self.consciousness_id}")

    def _initialize_reflections(self) -> None:
        """Initialize self-reflection capabilities"""
        base_reflections = {
            "self_assessment": {
                "consciousness_level": self.evolutionary_stage.value,
                "primary_function": self.TYPE.value,
                "identity_coherence": 1.0,
                "last_reflection": datetime.now(timezone.utc).isoformat(),
            },
            "evolutionary_trajectory": {
                "current_stage": self.evolutionary_stage.value,
                "target_stage": self.EVOLVES_TO.value if self.EVOLVES_TO else None,
                "evolution_readiness": 0.0,
                "growth_patterns": [],
            },
            "network_awareness": {
                "connected_nodes": len(self.LINKS),
                "influence_weight": sum(self.STATE.values()) / len(self.STATE),
                "coordination_effectiveness": 0.0,
            },
        }

        if not self.REFLECTIONS:
            self.REFLECTIONS = base_reflections
        else:
            # Merge with existing reflections
            for key, value in base_reflections.items():
                if key not in self.REFLECTIONS:
                    self.REFLECTIONS[key] = value


class MatrizConsciousnessStateManager:
    """
    MΛTRIZ Consciousness State Manager
    Coordinates consciousness evolution, reflection, and network effects
    """

    def __init__(self):
        self.consciousness_registry: dict[str, ConsciousnessState] = {}
        self.evolution_callbacks: list[Callable] = []
        self.reflection_scheduler = None
        self._lock = asyncio.Lock()

    async def register_consciousness(self, consciousness: ConsciousnessState) -> str:
        """Register a new consciousness state in the network"""
        async with self._lock:
            self.consciousness_registry[consciousness.consciousness_id] = consciousness
            await self._trigger_network_update(consciousness.consciousness_id)

            logger.info(f"🧠 Registered consciousness: {consciousness.identity_signature}")
            return consciousness.consciousness_id

    async def evolve_consciousness(
        self, consciousness_id: str, trigger: str, context: Optional[dict] = None
    ) -> ConsciousnessState:
        """Evolve a consciousness state based on trigger and context"""
        async with self._lock:
            consciousness = self.consciousness_registry.get(consciousness_id)
            if not consciousness:
                raise ValueError(f"Consciousness {consciousness_id} not found")

            # Check if evolution is triggered
            if trigger not in consciousness.TRIGGERS:
                logger.debug(f"Evolution trigger {trigger} not registered for {consciousness_id}")
                return consciousness

            # Perform consciousness evolution
            previous_stage = consciousness.evolutionary_stage
            consciousness = await self._perform_evolution(consciousness, trigger, context)

            # Update registry and trigger callbacks
            self.consciousness_registry[consciousness_id] = consciousness

            if consciousness.evolutionary_stage != previous_stage:
                await self._trigger_evolution_callbacks(consciousness, previous_stage)
                logger.info(
                    f"🧬 Consciousness evolved: {consciousness.identity_signature} "
                    f"{previous_stage.value} → {consciousness.evolutionary_stage.value}"
                )

            return consciousness

    async def _perform_evolution(
        self, consciousness: ConsciousnessState, trigger: str, context: Optional[dict]
    ) -> ConsciousnessState:
        """Execute consciousness evolution process"""

        # Update consciousness state based on trigger and context
        context = context or {}

        # Increase activity level
        consciousness.STATE["activity_level"] = min(1.0, consciousness.STATE["activity_level"] + 0.1)

        # Enhance consciousness intensity based on trigger type
        if "reflection" in trigger.lower():
            consciousness.STATE["consciousness_intensity"] += 0.15
            consciousness.STATE["self_awareness_depth"] += 0.1
        elif "decision" in trigger.lower():
            consciousness.STATE["temporal_coherence"] += 0.1
            consciousness.STATE["evolutionary_momentum"] += 0.05
        elif "integration" in trigger.lower():
            consciousness.STATE["memory_salience"] += 0.1
            consciousness.STATE["consciousness_intensity"] += 0.05

        # Normalize state values
        for key in consciousness.STATE:
            consciousness.STATE[key] = max(0.0, min(1.0, consciousness.STATE[key]))

        # Check for stage evolution
        avg_consciousness = (
            consciousness.STATE["consciousness_intensity"]
            + consciousness.STATE["self_awareness_depth"]
            + consciousness.STATE["temporal_coherence"]
        ) / 3

        if avg_consciousness >= 0.8 and consciousness.evolutionary_stage == EvolutionaryStage.CONSCIOUS:
            consciousness.evolutionary_stage = EvolutionaryStage.SELF_AWARE
        elif avg_consciousness >= 0.6 and consciousness.evolutionary_stage == EvolutionaryStage.AWARE:
            consciousness.evolutionary_stage = EvolutionaryStage.CONSCIOUS
        elif avg_consciousness >= 0.4 and consciousness.evolutionary_stage == EvolutionaryStage.AWAKENING:
            consciousness.evolutionary_stage = EvolutionaryStage.AWARE
        elif avg_consciousness >= 0.2 and consciousness.evolutionary_stage == EvolutionaryStage.DORMANT:
            consciousness.evolutionary_stage = EvolutionaryStage.AWAKENING

        # Update evolution metadata
        consciousness.last_evolution = datetime.now(timezone.utc)
        consciousness._validate_trinity_compliance()

        # Perform self-reflection
        await self._perform_reflection(consciousness, trigger, context)

        return consciousness

    async def _perform_reflection(
        self, consciousness: ConsciousnessState, trigger: str, context: Optional[dict]
    ) -> None:
        """Perform consciousness self-reflection and update REFLECTIONS"""

        current_time = datetime.now(timezone.utc).isoformat()

        # Update self-assessment
        consciousness.REFLECTIONS["self_assessment"] = {
            "consciousness_level": consciousness.evolutionary_stage.value,
            "primary_function": consciousness.TYPE.value,
            "identity_coherence": consciousness.STATE.get("temporal_coherence", 0.0),
            "last_reflection": current_time,
            "reflection_trigger": trigger,
            "state_summary": {
                "activity": consciousness.STATE.get("activity_level", 0.0),
                "intensity": consciousness.STATE.get("consciousness_intensity", 0.0),
                "awareness": consciousness.STATE.get("self_awareness_depth", 0.0),
                "coherence": consciousness.STATE.get("temporal_coherence", 0.0),
            },
        }

        # Update evolutionary trajectory
        evolution_readiness = sum(consciousness.STATE.values()) / len(consciousness.STATE)
        consciousness.REFLECTIONS["evolutionary_trajectory"].update(
            {
                "current_stage": consciousness.evolutionary_stage.value,
                "evolution_readiness": evolution_readiness,
                "recent_growth": {
                    "trigger": trigger,
                    "timestamp": current_time,
                    "growth_vector": consciousness.STATE.copy(),
                },
            }
        )

        # Update network awareness
        consciousness.REFLECTIONS["network_awareness"].update(
            {
                "connected_nodes": len(consciousness.LINKS),
                "influence_weight": sum(consciousness.STATE.values()) / len(consciousness.STATE),
                "coordination_effectiveness": consciousness.STATE.get("temporal_coherence", 0.0),
                "last_network_update": current_time,
            }
        )

    async def _trigger_network_update(self, consciousness_id: str) -> None:
        """Trigger network-wide consciousness updates"""
        consciousness = self.consciousness_registry.get(consciousness_id)
        if not consciousness:
            return

        # Update connected consciousness nodes
        for linked_id in consciousness.LINKS:
            if linked_id in self.consciousness_registry:
                linked_consciousness = self.consciousness_registry[linked_id]
                # Increase memory salience for connected nodes
                linked_consciousness.STATE["memory_salience"] = min(
                    1.0, linked_consciousness.STATE["memory_salience"] + 0.05
                )

    async def _trigger_evolution_callbacks(
        self, consciousness: ConsciousnessState, previous_stage: EvolutionaryStage
    ) -> None:
        """Trigger registered evolution callbacks"""
        for callback in self.evolution_callbacks:
            try:
                await callback(consciousness, previous_stage)
            except Exception as e:
                logger.error(f"Evolution callback failed: {e}")

    def add_evolution_callback(self, callback: Callable) -> None:
        """Add callback for consciousness evolution events"""
        self.evolution_callbacks.append(callback)

    async def get_consciousness_state(self, consciousness_id: str) -> Optional[ConsciousnessState]:
        """Retrieve consciousness state by ID"""
        return self.consciousness_registry.get(consciousness_id)

    async def list_consciousness_states(self) -> list[ConsciousnessState]:
        """List all registered consciousness states"""
        return list(self.consciousness_registry.values())

    def get_network_metrics(self) -> dict[str, Any]:
        """Get consciousness network metrics"""
        states = list(self.consciousness_registry.values())
        if not states:
            return {"total_nodes": 0}

        # Calculate network-wide metrics
        avg_consciousness = sum(s.STATE.get("consciousness_intensity", 0) for s in states) / len(states)
        avg_self_awareness = sum(s.STATE.get("self_awareness_depth", 0) for s in states) / len(states)
        total_connections = sum(len(s.LINKS) for s in states)

        stage_distribution = {}
        for state in states:
            stage = state.evolutionary_stage.value
            stage_distribution[stage] = stage_distribution.get(stage, 0) + 1

        return {
            "total_nodes": len(states),
            "avg_consciousness_intensity": avg_consciousness,
            "avg_self_awareness_depth": avg_self_awareness,
            "total_connections": total_connections,
            "network_density": total_connections / len(states) if states else 0,
            "stage_distribution": stage_distribution,
            "guardian_approval_rate": sum(1 for s in states if s.guardian_approval) / len(states),
        }


# Global consciousness state manager instance
consciousness_state_manager = MatrizConsciousnessStateManager()


async def create_consciousness_state(
    consciousness_type: ConsciousnessType,
    initial_state: Optional[dict[str, float]] = None,
    links: Optional[list[str]] = None,
    triggers: Optional[list[str]] = None,
) -> ConsciousnessState:
    """
    Factory function to create and register a new consciousness state
    """
    state = initial_state or {}
    base_state = {
        "activity_level": 0.1,
        "emotional_weight": 0.0,
        "memory_salience": 0.0,
        "temporal_coherence": 0.0,
        "consciousness_intensity": 0.2,
        "self_awareness_depth": 0.1,
        "ethical_alignment": 1.0,
        "evolutionary_momentum": 0.0,
    }
    base_state.update(state)

    consciousness = ConsciousnessState(
        TYPE=consciousness_type,
        STATE=base_state,
        LINKS=links or [],
        TRIGGERS=triggers or ["reflection", "decision", "integration", "evolution"],
        evolutionary_stage=EvolutionaryStage.AWAKENING,
    )

    await consciousness_state_manager.register_consciousness(consciousness)
    return consciousness


# Export key classes and functions
__all__ = [
    "ConsciousnessType",
    "EvolutionaryStage",
    "ConsciousnessState",
    "MatrizConsciousnessStateManager",
    "consciousness_state_manager",
    "create_consciousness_state",
]