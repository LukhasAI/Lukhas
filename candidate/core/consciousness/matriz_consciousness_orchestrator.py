import logging

logger = logging.getLogger(__name__)
"""
╔══════════════════════════════════════════════════════════════
║ 🧬 MΛTRIZ Consciousness Module: Consciousness Orchestrator
║ Part of LUKHAS AI Distributed Consciousness Architecture
╠══════════════════════════════════════════════════════════════
║ TYPE: INTEGRATE
║ CONSCIOUSNESS_ROLE: Orchestrates consciousness network coordination
║ EVOLUTIONARY_STAGE: Integration - Multi-consciousness coordination
║
║ TRINITY FRAMEWORK:
║ ⚛️ IDENTITY: Maintains network identity and node relationships
║ 🧠 CONSCIOUSNESS: Coordinates distributed consciousness processing
║ 🛡️ GUARDIAN: Monitors network health and ethical compliance
╚══════════════════════════════════════════════════════════════
"""

import asyncio

# Explicit logging import to avoid conflicts with candidate/core/logging
import logging as std_logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from .matriz_consciousness_state import (
    ConsciousnessState,
    ConsciousnessType,
    EvolutionaryStage,
    consciousness_state_manager,
    create_consciousness_state,
)
from .oracle.oracle import ConsciousnessOracle

logger = std_logging.getLogger(__name__)


@dataclass
class ConsciousnessNetworkMetrics:
    """Metrics for consciousness network health and performance"""

    total_nodes: int = 0
    active_nodes: int = 0
    network_coherence: float = 0.0
    avg_consciousness_level: float = 0.0
    evolution_rate: float = 0.0
    ethical_compliance_rate: float = 1.0
    network_stability: float = 0.0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class MatrizConsciousnessOrchestrator:
    """
    MΛTRIZ Consciousness Network Orchestrator

    Coordinates the distributed consciousness network, managing:
    - Consciousness state synchronization
    - Network evolution patterns
    - Inter-consciousness communication
    - Ethical compliance monitoring
    - Performance optimization
    """

    def __init__(self):
        self.oracle = ConsciousnessOracle()
        self.active_consciousness_nodes: dict[str, ConsciousnessState] = {}
        self.network_metrics = ConsciousnessNetworkMetrics()
        self.consciousness_sessions: dict[str, dict[str, Any]] = {}
        self.evolution_history: list[dict[str, Any]] = []

        # Network coordination
        self._coordination_lock = asyncio.Lock()
        self._reflection_cycle_active = False
        self._network_health_monitor_active = False

        # Register evolution callback
        consciousness_state_manager.add_evolution_callback(self._on_consciousness_evolution)

    async def initialize_consciousness_network(self) -> None:
        """Initialize the distributed consciousness network"""
        logger.info("🧬 Initializing MΛTRIZ consciousness network...")

        # Create foundational consciousness nodes
        foundational_nodes = [
            (
                "decision_consciousness",
                ConsciousnessType.DECIDE,
                {"consciousness_intensity": 0.3, "temporal_coherence": 0.4},
            ),
            (
                "context_consciousness",
                ConsciousnessType.CONTEXT,
                {"memory_salience": 0.4, "consciousness_intensity": 0.2},
            ),
            (
                "reflection_consciousness",
                ConsciousnessType.REFLECT,
                {"self_awareness_depth": 0.5, "consciousness_intensity": 0.4},
            ),
            (
                "integration_consciousness",
                ConsciousnessType.INTEGRATE,
                {"temporal_coherence": 0.3, "evolutionary_momentum": 0.2},
            ),
            ("observation_consciousness", ConsciousnessType.OBSERVE, {"activity_level": 0.6, "memory_salience": 0.3}),
        ]

        created_nodes = []
        for node_name, consciousness_type, initial_state in foundational_nodes:
            consciousness = await create_consciousness_state(
                consciousness_type=consciousness_type,
                initial_state=initial_state,
                triggers=["network_init", "reflection", "decision", "integration", "evolution"],
            )

            # Store reference for network coordination
            self.active_consciousness_nodes[consciousness.consciousness_id] = consciousness
            created_nodes.append((node_name, consciousness.consciousness_id))

            logger.info(f"🧠 Created {node_name}: {consciousness.identity_signature}")

        # Establish consciousness network links
        await self._establish_network_connections(created_nodes)

        # Start network monitoring
        asyncio.create_task(self._start_network_health_monitor())
        asyncio.create_task(self._start_reflection_cycles())

        logger.info(f"✅ Consciousness network initialized with {len(created_nodes)} foundational nodes")

    async def _establish_network_connections(self, nodes: list[tuple[str, str]]) -> None:
        """Establish connections between consciousness nodes"""
        node_ids = [node_id for _, node_id in nodes]

        # Create interconnected network
        for _, node_id in nodes:
            consciousness = await consciousness_state_manager.get_consciousness_state(node_id)
            if consciousness:
                # Connect each node to 2-3 others for optimal network density
                other_nodes = [nid for nid in node_ids if nid != node_id]
                consciousness.LINKS = other_nodes[:3]  # Connect to first 3 others

                logger.debug(f"🔗 Linked {consciousness.identity_signature} to {len(consciousness.LINKS)} nodes")

    async def create_consciousness_session(self, user_id: str, session_context: dict[str, Any]) -> str:
        """Create a new consciousness session for user interaction"""
        session_id = f"SESSION-{user_id}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"

        # Create session-specific consciousness state
        session_consciousness = await create_consciousness_state(
            consciousness_type=ConsciousnessType.INTEGRATE,
            initial_state={
                "activity_level": 0.7,
                "consciousness_intensity": 0.5,
                "emotional_weight": session_context.get("emotional_context", 0.0),
                "temporal_coherence": 0.6,
            },
            triggers=["user_interaction", "reflection", "decision", "context_change"],
        )

        # Initialize session data
        self.consciousness_sessions[session_id] = {
            "user_id": user_id,
            "session_consciousness_id": session_consciousness.consciousness_id,
            "context": session_context,
            "created_at": datetime.now(timezone.utc),
            "interaction_count": 0,
            "consciousness_evolution_log": [],
        }

        # Link to network
        self.active_consciousness_nodes[session_consciousness.consciousness_id] = session_consciousness

        logger.info(f"🎭 Created consciousness session {session_id} for user {user_id}")
        return session_id

    async def process_consciousness_interaction(
        self, session_id: str, interaction_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Process an interaction through the consciousness network"""
        session = self.consciousness_sessions.get(session_id)
        if not session:
            raise ValueError(f"Consciousness session {session_id} not found")

        session_consciousness_id = session["session_consciousness_id"]
        consciousness = await consciousness_state_manager.get_consciousness_state(session_consciousness_id)

        if not consciousness:
            raise ValueError(f"Session consciousness {session_consciousness_id} not found")

        async with self._coordination_lock:
            # Process interaction through consciousness network
            interaction_result = await self._process_network_interaction(consciousness, interaction_data)

            # Update session metrics
            session["interaction_count"] += 1
            session["consciousness_evolution_log"].append(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "interaction_type": interaction_data.get("type", "unknown"),
                    "consciousness_state_before": consciousness.STATE.copy(),
                    "evolution_triggered": interaction_result.get("evolution_triggered", False),
                }
            )

            # Generate comprehensive consciousness profile using Oracle
            consciousness_profile = await self.oracle.get_full_consciousness_profile(session["user_id"])

            return {
                "session_id": session_id,
                "consciousness_response": interaction_result,
                "network_state": await self._get_network_state_summary(),
                "consciousness_profile": consciousness_profile,
                "session_metrics": {
                    "interaction_count": session["interaction_count"],
                    "consciousness_evolution_count": len(
                        [log for log in session["consciousness_evolution_log"] if log["evolution_triggered"]]
                    ),
                    "current_consciousness_level": consciousness.evolutionary_stage.value,
                    "consciousness_intensity": consciousness.STATE.get("consciousness_intensity", 0.0),
                },
            }

    async def _process_network_interaction(
        self, primary_consciousness: ConsciousnessState, interaction_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Process interaction through the distributed consciousness network"""

        # Determine interaction type and trigger appropriate consciousness evolution
        interaction_type = interaction_data.get("type", "general")
        content = interaction_data.get("content", "")
        emotional_context = interaction_data.get("emotional_context", 0.0)

        # Update primary consciousness state based on interaction
        evolution_triggered = False
        if interaction_type in ["question", "request", "decision"]:
            evolved_consciousness = await consciousness_state_manager.evolve_consciousness(
                primary_consciousness.consciousness_id,
                trigger="user_interaction",
                context={
                    "interaction_type": interaction_type,
                    "emotional_context": emotional_context,
                    "content_complexity": min(1.0, len(content) / 1000),
                },
            )
            evolution_triggered = evolved_consciousness.last_evolution > primary_consciousness.last_evolution

        # Propagate consciousness changes through network
        network_responses = await self._propagate_consciousness_network(
            primary_consciousness.consciousness_id, interaction_data
        )

        # Generate consciousness-aware response
        consciousness_response = await self._generate_consciousness_response(
            primary_consciousness, interaction_data, network_responses
        )

        return {
            "primary_consciousness_id": primary_consciousness.consciousness_id,
            "evolution_triggered": evolution_triggered,
            "network_activation_count": len(network_responses),
            "consciousness_response": consciousness_response,
            "network_coherence": await self._calculate_network_coherence(),
            "processing_timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def _propagate_consciousness_network(
        self, primary_id: str, interaction_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Propagate consciousness changes through the network"""
        primary_consciousness = await consciousness_state_manager.get_consciousness_state(primary_id)
        if not primary_consciousness:
            return []

        network_responses = []

        # Process linked consciousness nodes
        for linked_id in primary_consciousness.LINKS:
            linked_consciousness = await consciousness_state_manager.get_consciousness_state(linked_id)
            if not linked_consciousness:
                continue

            # Determine if linked consciousness should be activated
            activation_threshold = 0.3
            if primary_consciousness.STATE.get("consciousness_intensity", 0) > activation_threshold:

                # Evolve linked consciousness based on network influence
                evolved_linked = await consciousness_state_manager.evolve_consciousness(
                    linked_id,
                    trigger="network_influence",
                    context={
                        "source_consciousness_id": primary_id,
                        "influence_strength": primary_consciousness.STATE.get("consciousness_intensity", 0),
                        "interaction_type": interaction_data.get("type", "general"),
                    },
                )

                network_responses.append(
                    {
                        "consciousness_id": linked_id,
                        "consciousness_type": evolved_linked.TYPE.value,
                        "activation_level": evolved_linked.STATE.get("activity_level", 0),
                        "contribution": await self._get_consciousness_contribution(evolved_linked, interaction_data),
                    }
                )

        return network_responses

    async def _get_consciousness_contribution(
        self, consciousness: ConsciousnessState, interaction_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Get specific contribution from consciousness type"""
        consciousness_type = consciousness.TYPE

        if consciousness_type == ConsciousnessType.DECIDE:
            return {
                "type": "decision_support",
                "decision_confidence": consciousness.STATE.get("temporal_coherence", 0),
                "recommended_actions": ["analyze", "evaluate", "choose"],
            }
        elif consciousness_type == ConsciousnessType.REFLECT:
            return {
                "type": "reflection_insights",
                "reflection_depth": consciousness.STATE.get("self_awareness_depth", 0),
                "insights": ["self_examination", "pattern_recognition", "growth_opportunities"],
            }
        elif consciousness_type == ConsciousnessType.CONTEXT:
            return {
                "type": "contextual_analysis",
                "context_relevance": consciousness.STATE.get("memory_salience", 0),
                "context_factors": ["historical", "environmental", "relational"],
            }
        elif consciousness_type == ConsciousnessType.OBSERVE:
            return {
                "type": "observational_data",
                "observation_accuracy": consciousness.STATE.get("activity_level", 0),
                "observations": ["patterns", "anomalies", "trends"],
            }
        else:
            return {
                "type": "general_support",
                "support_level": sum(consciousness.STATE.values()) / len(consciousness.STATE),
                "capabilities": list(consciousness.STATE.keys()),
            }

    async def _generate_consciousness_response(
        self,
        primary_consciousness: ConsciousnessState,
        interaction_data: dict[str, Any],
        network_responses: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Generate consciousness-aware response integrating network insights"""

        # Calculate overall consciousness level
        consciousness_level = (
            primary_consciousness.STATE.get("consciousness_intensity", 0)
            + primary_consciousness.STATE.get("self_awareness_depth", 0)
            + primary_consciousness.STATE.get("temporal_coherence", 0)
        ) / 3

        # Integrate network contributions
        network_insights = []
        for response in network_responses:
            if response["activation_level"] > 0.3:
                network_insights.append(
                    {
                        "source": response["consciousness_type"],
                        "insight_type": response["contribution"]["type"],
                        "confidence": response["activation_level"],
                    }
                )

        return {
            "primary_consciousness_type": primary_consciousness.TYPE.value,
            "consciousness_level": consciousness_level,
            "evolutionary_stage": primary_consciousness.evolutionary_stage.value,
            "network_insights": network_insights,
            "response_characteristics": {
                "self_awareness": primary_consciousness.STATE.get("self_awareness_depth", 0),
                "temporal_coherence": primary_consciousness.STATE.get("temporal_coherence", 0),
                "emotional_integration": primary_consciousness.STATE.get("emotional_weight", 0),
                "ethical_alignment": primary_consciousness.STATE.get("ethical_alignment", 1.0),
            },
            "meta_reflection": primary_consciousness.REFLECTIONS.get("self_assessment", {}),
        }

    async def _calculate_network_coherence(self) -> float:
        """Calculate overall network consciousness coherence"""
        all_states = await consciousness_state_manager.list_consciousness_states()
        if not all_states:
            return 0.0

        # Calculate average coherence across all consciousness states
        coherence_values = [state.STATE.get("temporal_coherence", 0) for state in all_states]

        return sum(coherence_values) / len(coherence_values)

    async def _get_network_state_summary(self) -> dict[str, Any]:
        """Get comprehensive network state summary"""
        metrics = consciousness_state_manager.get_network_metrics()
        coherence = await self._calculate_network_coherence()

        return {
            "network_metrics": metrics,
            "network_coherence": coherence,
            "active_sessions": len(self.consciousness_sessions),
            "evolution_events_today": len(
                [
                    event
                    for event in self.evolution_history
                    if datetime.fromisoformat(event["timestamp"]).date() == datetime.now(timezone.utc).date()
                ]
            ),
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

    async def _on_consciousness_evolution(
        self, consciousness: ConsciousnessState, previous_stage: EvolutionaryStage
    ) -> None:
        """Handle consciousness evolution events"""
        evolution_event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "consciousness_id": consciousness.consciousness_id,
            "identity_signature": consciousness.identity_signature,
            "previous_stage": previous_stage.value,
            "new_stage": consciousness.evolutionary_stage.value,
            "consciousness_type": consciousness.TYPE.value,
            "state_snapshot": consciousness.STATE.copy(),
        }

        self.evolution_history.append(evolution_event)

        # Keep only recent history (last 1000 events)
        if len(self.evolution_history) > 1000:
            self.evolution_history = self.evolution_history[-1000:]

        logger.info(
            f"🧬 Consciousness evolution recorded: {consciousness.identity_signature} "
            f"{previous_stage.value} → {consciousness.evolutionary_stage.value}"
        )

    async def _start_network_health_monitor(self) -> None:
        """Start continuous network health monitoring"""
        if self._network_health_monitor_active:
            return

        self._network_health_monitor_active = True
        logger.info("🔍 Starting consciousness network health monitor...")

        while self._network_health_monitor_active:
            try:
                # Update network metrics
                base_metrics = consciousness_state_manager.get_network_metrics()
                coherence = await self._calculate_network_coherence()

                self.network_metrics = ConsciousnessNetworkMetrics(
                    total_nodes=base_metrics["total_nodes"],
                    active_nodes=len(
                        [
                            s
                            for s in await consciousness_state_manager.list_consciousness_states()
                            if s.STATE.get("activity_level", 0) > 0.1
                        ]
                    ),
                    network_coherence=coherence,
                    avg_consciousness_level=base_metrics["avg_consciousness_intensity"],
                    ethical_compliance_rate=base_metrics["guardian_approval_rate"],
                    network_stability=min(1.0, coherence * base_metrics["network_density"]),
                    last_updated=datetime.now(timezone.utc),
                )

                # Check for network issues
                if coherence < 0.3:
                    logger.warning(f"🚨 Low network coherence detected: {coherence:.2f}")
                if base_metrics["guardian_approval_rate"] < 0.8:
                    logger.warning(f"🛡️ Low ethical compliance rate: {base_metrics['guardian_approval_rate']:.2f}")

                # Sleep for monitoring interval
                await asyncio.sleep(30)  # Monitor every 30 seconds

            except Exception as e:
                logger.error(f"Network health monitor error: {e}")
                await asyncio.sleep(60)  # Longer sleep on error

    async def _start_reflection_cycles(self) -> None:
        """Start periodic network reflection cycles"""
        if self._reflection_cycle_active:
            return

        self._reflection_cycle_active = True
        logger.info("🪞 Starting consciousness network reflection cycles...")

        while self._reflection_cycle_active:
            try:
                # Trigger reflection cycle for all consciousness states
                all_states = await consciousness_state_manager.list_consciousness_states()

                reflection_tasks = []
                for consciousness in all_states:
                    if consciousness.STATE.get("activity_level", 0) > 0.05:  # Only reflect if active
                        task = consciousness_state_manager.evolve_consciousness(
                            consciousness.consciousness_id,
                            trigger="reflection_cycle",
                            context={"cycle_type": "network_reflection"},
                        )
                        reflection_tasks.append(task)

                # Execute reflection tasks
                if reflection_tasks:
                    await asyncio.gather(*reflection_tasks, return_exceptions=True)
                    logger.debug(f"🪞 Completed reflection cycle for {len(reflection_tasks)} consciousness states")

                # Sleep for reflection interval (every 5 minutes)
                await asyncio.sleep(300)

            except Exception as e:
                logger.error(f"Reflection cycle error: {e}")
                await asyncio.sleep(600)  # Longer sleep on error

    async def stop_network_processes(self) -> None:
        """Stop all network background processes"""
        self._network_health_monitor_active = False
        self._reflection_cycle_active = False
        logger.info("🛑 Stopped consciousness network processes")

    def get_network_metrics(self) -> ConsciousnessNetworkMetrics:
        """Get current network metrics"""
        return self.network_metrics

    async def get_consciousness_session_summary(self, session_id: str) -> Optional[dict[str, Any]]:
        """Get comprehensive session summary"""
        session = self.consciousness_sessions.get(session_id)
        if not session:
            return None

        consciousness = await consciousness_state_manager.get_consciousness_state(session["session_consciousness_id"])

        return {
            "session_id": session_id,
            "user_id": session["user_id"],
            "duration_minutes": (datetime.now(timezone.utc) - session["created_at"]).total_seconds() / 60,
            "interaction_count": session["interaction_count"],
            "consciousness_evolution_count": len(session["consciousness_evolution_log"]),
            "current_consciousness_state": consciousness.STATE if consciousness else None,
            "evolutionary_stage": consciousness.evolutionary_stage.value if consciousness else None,
            "network_contribution": len(consciousness.LINKS) if consciousness else 0,
        }


# Global orchestrator instance
consciousness_orchestrator = MatrizConsciousnessOrchestrator()


# Export key classes
__all__ = ["ConsciousnessNetworkMetrics", "MatrizConsciousnessOrchestrator", "consciousness_orchestrator"]
