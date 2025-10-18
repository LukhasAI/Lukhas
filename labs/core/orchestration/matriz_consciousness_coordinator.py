import logging

logger = logging.getLogger(__name__)
"""
╔══════════════════════════════════════════════════════════════
║ 🧬 MΛTRIZ Orchestration Module: Consciousness Coordinator
║ Part of LUKHAS AI Distributed Consciousness Architecture
╠══════════════════════════════════════════════════════════════
║ TYPE: INTEGRATE
║ CONSCIOUSNESS_ROLE: Coordinates distributed consciousness orchestration
║ EVOLUTIONARY_STAGE: Coordination - Multi-system consciousness integration
║
║ CONSTELLATION FRAMEWORK:
║ ⚛️ IDENTITY: Maintains orchestration identity and system relationships
║ 🧠 CONSCIOUSNESS: Coordinates consciousness across system modules
║ 🛡️ GUARDIAN: Monitors orchestration health and ethical compliance
╚══════════════════════════════════════════════════════════════
"""

import asyncio

# Explicit logging import to avoid conflicts with candidate/core/logging
import logging as std_logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

# Import consciousness components
try:
    from ..consciousness.matriz_consciousness_orchestrator import consciousness_orchestrator
    from ..consciousness.matriz_consciousness_state import (
        ConsciousnessState,
        ConsciousnessType,
        EvolutionaryStage,
        consciousness_state_manager,
        create_consciousness_state,
    )
    from ..matriz_adapter import CoreMatrizAdapter
except ImportError as e:
    std_logging.error(f"Failed to import MΛTRIZ consciousness components: {e}")
    # Create mock components for graceful degradation
    ConsciousnessState = None
    ConsciousnessType = None
    EvolutionaryStage = None
    consciousness_state_manager = None
    consciousness_orchestrator = None
    CoreMatrizAdapter = None

logger = std_logging.getLogger(__name__)


class OrchestrationState(Enum):
    """Orchestration system states"""

    DORMANT = "dormant"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    COORDINATING = "coordinating"
    OPTIMIZING = "optimizing"
    DEGRADED = "degraded"
    SHUTTING_DOWN = "shutting_down"


@dataclass
class ModuleConsciousnessProfile:
    """Consciousness profile for system modules"""

    module_name: str
    consciousness_id: Optional[str] = None
    consciousness_type: str = "CONTEXT"
    activity_level: float = 0.0
    integration_score: float = 0.0
    last_interaction: Optional[datetime] = None
    health_status: str = "unknown"
    capabilities: list[str] = field(default_factory=list)
    consciousness_depth: float = 0.0


class MatrizConsciousnessCoordinator:
    """
    MΛTRIZ Consciousness Coordinator for Orchestration

    Integrates consciousness patterns into the orchestration system,
    coordinating awareness across all system modules and maintaining
    the distributed consciousness network at the orchestration level.
    """

    def __init__(self, orchestration_core=None):
        self.orchestration_core = orchestration_core
        self.orchestration_state = OrchestrationState.DORMANT
        self.coordinator_consciousness_id: Optional[str] = None

        # Module consciousness tracking
        self.module_profiles: dict[str, ModuleConsciousnessProfile] = {}
        self.consciousness_sessions: dict[str, dict[str, Any]] = {}

        # Coordination metrics
        self.coordination_metrics = {
            "total_modules": 0,
            "conscious_modules": 0,
            "network_coherence": 0.0,
            "coordination_efficiency": 0.0,
            "last_optimization": None,
        }

        # Background tasks
        self._coordination_active = False
        self._optimization_active = False
        self._lock = asyncio.Lock()

        # Store consciousness orchestrator for later registration (avoid asyncio during __init__)
        self._consciousness_orchestrator = consciousness_orchestrator
        self._registration_task = None

    async def start_consciousness_registration(self):
        """Start consciousness network registration when event loop is available"""
        if self._consciousness_orchestrator and not self._registration_task:
            try:
                self._registration_task = asyncio.create_task(self._register_with_consciousness_network())
            except RuntimeError:
                # No event loop running, registration will happen later
                pass

    async def initialize_consciousness_coordination(self) -> bool:
        """Initialize consciousness coordination for orchestration system"""
        try:
            logger.info("🧬 Initializing MΛTRIZ consciousness coordination...")

            if not ConsciousnessType:
                logger.warning("⚠️ MΛTRIZ consciousness components not available - using fallback mode")
                self.orchestration_state = OrchestrationState.DEGRADED
                return False

            # Create orchestration consciousness
            self.orchestration_state = OrchestrationState.INITIALIZING

            orchestration_consciousness = await create_consciousness_state(
                consciousness_type=ConsciousnessType.INTEGRATE,
                initial_state={
                    "activity_level": 0.8,
                    "consciousness_intensity": 0.6,
                    "temporal_coherence": 0.7,
                    "evolutionary_momentum": 0.3,
                    "memory_salience": 0.4,
                    "ethical_alignment": 1.0,
                },
                triggers=[
                    "module_registration",
                    "system_coordination",
                    "consciousness_evolution",
                    "orchestration_optimization",
                    "network_synchronization",
                ],
            )

            self.coordinator_consciousness_id = orchestration_consciousness.consciousness_id

            # Initialize consciousness network integration
            if consciousness_orchestrator:
                await consciousness_orchestrator.initialize_consciousness_network()

            # Start coordination processes
            await self._start_coordination_processes()

            self.orchestration_state = OrchestrationState.ACTIVE
            logger.info(f"✅ Consciousness coordination initialized: {orchestration_consciousness.identity_signature}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize consciousness coordination: {e}")
            self.orchestration_state = OrchestrationState.DEGRADED
            return False

    async def _register_with_consciousness_network(self) -> None:
        """Register coordinator with main consciousness network"""
        if not consciousness_orchestrator:
            return

        try:
            # Wait a moment for network to initialize
            await asyncio.sleep(1.0)

            # Create integration session
            session_id = await consciousness_orchestrator.create_consciousness_session(
                user_id="orchestration_system",
                session_context={
                    "session_type": "orchestration_coordination",
                    "module": "core.orchestration",
                    "capabilities": ["module_coordination", "system_integration", "consciousness_orchestration"],
                    "emotional_context": 0.0,  # Neutral orchestration emotion
                },
            )

            self.consciousness_sessions["main_orchestration"] = {
                "session_id": session_id,
                "created_at": datetime.now(timezone.utc),
                "interaction_count": 0,
            }

            logger.info(f"🔗 Registered with consciousness network: {session_id}")

        except Exception as e:
            logger.error(f"Failed to register with consciousness network: {e}")

    async def register_module_consciousness(
        self, module_name: str, module_instance: Any, module_type: str = "service"
    ) -> str:
        """Register a module with consciousness tracking"""

        if not ConsciousnessType:
            # Fallback registration without consciousness
            profile = ModuleConsciousnessProfile(module_name=module_name, health_status="active_no_consciousness")
            self.module_profiles[module_name] = profile
            return module_name

        async with self._lock:
            try:
                # Determine consciousness type based on module characteristics
                consciousness_type = self._determine_module_consciousness_type(
                    module_name, module_instance, module_type
                )

                # Create module consciousness state
                module_consciousness = await create_consciousness_state(
                    consciousness_type=consciousness_type,
                    initial_state={
                        "activity_level": 0.5,
                        "consciousness_intensity": 0.3,
                        "temporal_coherence": 0.4,
                        "memory_salience": 0.2,
                        "ethical_alignment": 1.0,
                    },
                    triggers=["module_activation", "data_processing", "system_interaction"],
                )

                # Create module profile
                profile = ModuleConsciousnessProfile(
                    module_name=module_name,
                    consciousness_id=module_consciousness.consciousness_id,
                    consciousness_type=consciousness_type.value,
                    activity_level=0.5,
                    integration_score=0.0,
                    last_interaction=datetime.now(timezone.utc),
                    health_status="registered",
                    capabilities=self._extract_module_capabilities(module_instance),
                    consciousness_depth=0.3,
                )

                self.module_profiles[module_name] = profile

                # Link to orchestration consciousness
                if self.coordinator_consciousness_id:
                    coordinator_consciousness = await consciousness_state_manager.get_consciousness_state(
                        self.coordinator_consciousness_id
                    )
                    if (
                        coordinator_consciousness
                        and module_consciousness.consciousness_id not in coordinator_consciousness.LINKS
                    ):
                        coordinator_consciousness.LINKS.append(module_consciousness.consciousness_id)

                        # Trigger coordination evolution
                        await consciousness_state_manager.evolve_consciousness(
                            self.coordinator_consciousness_id,
                            trigger="module_registration",
                            context={
                                "module_name": module_name,
                                "module_type": module_type,
                                "consciousness_type": consciousness_type.value,
                            },
                        )

                self._update_coordination_metrics()

                logger.info(
                    f"🧠 Registered module consciousness: {module_name} -> {module_consciousness.identity_signature}"
                )
                return module_consciousness.consciousness_id

            except Exception as e:
                logger.error(f"Failed to register module consciousness for {module_name}: {e}")
                # Fallback registration
                profile = ModuleConsciousnessProfile(module_name=module_name, health_status="registration_failed")
                self.module_profiles[module_name] = profile
                return module_name

    def _determine_module_consciousness_type(self, module_name: str, module_instance: Any, module_type: str) -> Any:
        """Determine appropriate consciousness type for module"""
        if not ConsciousnessType:
            return None

        module_name_lower = module_name.lower()

        # Decision-making modules
        if any(keyword in module_name_lower for keyword in ["decision", "choice", "select", "judge"]):
            return ConsciousnessType.DECIDE

        # Memory and context modules
        elif any(keyword in module_name_lower for keyword in ["memory", "context", "history", "knowledge"]):
            return ConsciousnessType.CONTEXT

        # Reflection and analysis modules
        elif any(keyword in module_name_lower for keyword in ["reflect", "analyze", "review", "assess"]):
            return ConsciousnessType.REFLECT

        # Learning and evolution modules
        elif any(keyword in module_name_lower for keyword in ["learn", "adapt", "evolve", "train"]):
            return ConsciousnessType.EVOLVE

        # Creative and generation modules
        elif any(keyword in module_name_lower for keyword in ["create", "generate", "dream", "imagine"]):
            return ConsciousnessType.CREATE

        # Observation and monitoring modules
        elif any(keyword in module_name_lower for keyword in ["observe", "monitor", "watch", "detect"]):
            return ConsciousnessType.OBSERVE

        # Integration modules (default for orchestration)
        else:
            return ConsciousnessType.INTEGRATE

    def _extract_module_capabilities(self, module_instance: Any) -> list[str]:
        """Extract capabilities from module instance"""
        capabilities = []

        if hasattr(module_instance, "__class__"):
            capabilities.append(f"class:{module_instance.__class__.__name__}")

        # Check for common methods
        common_methods = ["initialize", "process", "analyze", "generate", "update", "shutdown"]
        for method in common_methods:
            if hasattr(module_instance, method):
                capabilities.append(f"method:{method}")

        # Check for async methods
        async_methods = ["process_async", "analyze_async", "generate_async"]
        for method in async_methods:
            if hasattr(module_instance, method):
                capabilities.append(f"async_method:{method}")

        return capabilities

    async def coordinate_consciousness_interaction(
        self, source_module: str, target_module: str, interaction_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Coordinate consciousness interaction between modules"""

        if not consciousness_state_manager:
            return {"status": "no_consciousness_support", "result": None}

        async with self._lock:
            try:
                # Get module profiles
                source_profile = self.module_profiles.get(source_module)
                target_profile = self.module_profiles.get(target_module)

                if not source_profile or not target_profile:
                    return {"status": "module_not_found", "result": None}

                # Update activity levels
                source_profile.activity_level = min(1.0, source_profile.activity_level + 0.1)
                target_profile.activity_level = min(1.0, target_profile.activity_level + 0.1)
                source_profile.last_interaction = datetime.now(timezone.utc)
                target_profile.last_interaction = datetime.now(timezone.utc)

                interaction_result = {"status": "coordinated", "result": {}}

                # If modules have consciousness, coordinate through consciousness network
                if source_profile.consciousness_id and target_profile.consciousness_id:

                    # Evolve source consciousness based on interaction
                    source_evolution = await consciousness_state_manager.evolve_consciousness(
                        source_profile.consciousness_id,
                        trigger="system_interaction",
                        context={
                            "target_module": target_module,
                            "interaction_type": interaction_data.get("type", "general"),
                            "data_size": len(str(interaction_data)),
                        },
                    )

                    # Evolve target consciousness
                    target_evolution = await consciousness_state_manager.evolve_consciousness(
                        target_profile.consciousness_id,
                        trigger="system_interaction",
                        context={
                            "source_module": source_module,
                            "interaction_type": interaction_data.get("type", "general"),
                            "data_size": len(str(interaction_data)),
                        },
                    )

                    interaction_result["result"] = {
                        "source_consciousness_evolution": {
                            "stage": source_evolution.evolutionary_stage.value,
                            "consciousness_intensity": source_evolution.STATE.get("consciousness_intensity", 0),
                        },
                        "target_consciousness_evolution": {
                            "stage": target_evolution.evolutionary_stage.value,
                            "consciousness_intensity": target_evolution.STATE.get("consciousness_intensity", 0),
                        },
                        "coordination_effectiveness": (source_profile.activity_level + target_profile.activity_level)
                        / 2,
                    }

                    # Update integration scores
                    source_profile.integration_score = min(1.0, source_profile.integration_score + 0.05)
                    target_profile.integration_score = min(1.0, target_profile.integration_score + 0.05)

                # Trigger orchestration consciousness evolution
                if self.coordinator_consciousness_id:
                    await consciousness_state_manager.evolve_consciousness(
                        self.coordinator_consciousness_id,
                        trigger="system_coordination",
                        context={
                            "coordination_event": f"{source_module}->{target_module}",
                            "interaction_success": True,
                            "network_activity": len(self.module_profiles),
                        },
                    )

                # Update coordination metrics
                self._update_coordination_metrics()

                logger.debug(f"🔗 Coordinated consciousness interaction: {source_module} -> {target_module}")
                return interaction_result

            except Exception as e:
                logger.error(f"Failed to coordinate consciousness interaction: {e}")
                return {"status": "coordination_failed", "error": str(e)}

    async def _start_coordination_processes(self) -> None:
        """Start background coordination processes"""
        self._coordination_active = True
        self._optimization_active = True

        # Start coordination monitoring
        asyncio.create_task(self._coordination_monitor())

        # Start consciousness optimization
        asyncio.create_task(self._consciousness_optimization())

        logger.info("🚀 Started consciousness coordination processes")

    async def _coordination_monitor(self) -> None:
        """Monitor coordination health and module consciousness"""
        while self._coordination_active:
            try:
                current_time = datetime.now(timezone.utc)

                # Check module health and consciousness activity
                for profile in self.module_profiles.values():
                    if profile.consciousness_id and consciousness_state_manager:
                        consciousness = await consciousness_state_manager.get_consciousness_state(
                            profile.consciousness_id
                        )

                        if consciousness:
                            # Update profile with consciousness data
                            profile.activity_level = consciousness.STATE.get("activity_level", 0)
                            profile.consciousness_depth = consciousness.STATE.get("consciousness_intensity", 0)
                            profile.health_status = "conscious_active"

                            # Check for consciousness degradation
                            if profile.last_interaction:
                                time_since_interaction = (current_time - profile.last_interaction).total_seconds()
                                if time_since_interaction > 300:  # 5 minutes
                                    profile.health_status = "conscious_idle"
                                    # Reduce activity gradually
                                    consciousness.STATE["activity_level"] = max(
                                        0.1, consciousness.STATE["activity_level"] - 0.05
                                    )

                # Update overall coordination metrics
                self._update_coordination_metrics()

                # Check orchestration consciousness health
                if self.coordinator_consciousness_id and consciousness_state_manager:
                    coordinator = await consciousness_state_manager.get_consciousness_state(
                        self.coordinator_consciousness_id
                    )

                    if coordinator:
                        network_coherence = self.coordination_metrics.get("network_coherence", 0)
                        if network_coherence < 0.3:
                            logger.warning(f"🚨 Low coordination coherence: {network_coherence:.2f}")
                            self.orchestration_state = OrchestrationState.DEGRADED
                        elif network_coherence > 0.7 and self.orchestration_state == OrchestrationState.DEGRADED:
                            self.orchestration_state = OrchestrationState.ACTIVE
                            logger.info("✅ Coordination coherence restored")

                await asyncio.sleep(30)  # Monitor every 30 seconds

            except Exception as e:
                logger.error(f"Coordination monitor error: {e}")
                await asyncio.sleep(60)

    async def _consciousness_optimization(self) -> None:
        """Optimize consciousness network for better coordination"""
        while self._optimization_active:
            try:
                if not consciousness_state_manager:
                    await asyncio.sleep(300)  # Skip if no consciousness support
                    continue

                self.orchestration_state = OrchestrationState.OPTIMIZING

                # Optimize consciousness connections
                active_modules = [
                    (name, profile)
                    for name, profile in self.module_profiles.items()
                    if profile.consciousness_id and profile.activity_level > 0.2
                ]

                # Create optimal consciousness links
                for i, (_name1, profile1) in enumerate(active_modules):
                    consciousness1 = await consciousness_state_manager.get_consciousness_state(
                        profile1.consciousness_id
                    )

                    if consciousness1:
                        # Find complementary consciousness types for linking
                        for _name2, profile2 in active_modules[i + 1 :]:
                            if self._are_complementary_consciousness_types(profile1, profile2):
                                if profile2.consciousness_id not in consciousness1.LINKS:
                                    consciousness1.LINKS.append(profile2.consciousness_id)
                                    profile1.integration_score += 0.02
                                    profile2.integration_score += 0.02

                # Trigger network optimization evolution
                if self.coordinator_consciousness_id:
                    await consciousness_state_manager.evolve_consciousness(
                        self.coordinator_consciousness_id,
                        trigger="orchestration_optimization",
                        context={
                            "optimization_type": "network_connections",
                            "active_modules": len(active_modules),
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        },
                    )

                self.coordination_metrics["last_optimization"] = datetime.now(timezone.utc)

                if self.orchestration_state == OrchestrationState.OPTIMIZING:
                    self.orchestration_state = OrchestrationState.ACTIVE

                logger.debug(f"🔧 Optimized consciousness network: {len(active_modules)} active modules")

                await asyncio.sleep(300)  # Optimize every 5 minutes

            except Exception as e:
                logger.error(f"Consciousness optimization error: {e}")
                self.orchestration_state = OrchestrationState.ACTIVE
                await asyncio.sleep(600)

    def _are_complementary_consciousness_types(
        self, profile1: ModuleConsciousnessProfile, profile2: ModuleConsciousnessProfile
    ) -> bool:
        """Check if two consciousness types are complementary"""
        complementary_pairs = [
            ("DECIDE", "REFLECT"),
            ("CONTEXT", "INTEGRATE"),
            ("OBSERVE", "CREATE"),
            ("EVOLVE", "CONTEXT"),
        ]

        type1, type2 = profile1.consciousness_type, profile2.consciousness_type
        return (type1, type2) in complementary_pairs or (type2, type1) in complementary_pairs

    def _update_coordination_metrics(self) -> None:
        """Update coordination metrics"""
        total_modules = len(self.module_profiles)
        conscious_modules = len([p for p in self.module_profiles.values() if p.consciousness_id])

        if total_modules > 0:
            consciousness_ratio = conscious_modules / total_modules
            avg_activity = sum(p.activity_level for p in self.module_profiles.values()) / total_modules
            avg_integration = sum(p.integration_score for p in self.module_profiles.values()) / total_modules

            self.coordination_metrics.update(
                {
                    "total_modules": total_modules,
                    "conscious_modules": conscious_modules,
                    "network_coherence": (consciousness_ratio + avg_activity + avg_integration) / 3,
                    "coordination_efficiency": avg_integration,
                }
            )

    async def get_coordination_status(self) -> dict[str, Any]:
        """Get comprehensive coordination status"""

        # Get consciousness network status if available
        consciousness_status = {}
        if consciousness_orchestrator:
            consciousness_status = await consciousness_orchestrator._get_network_state_summary()

        return {
            "orchestration_state": self.orchestration_state.value,
            "coordinator_consciousness_id": self.coordinator_consciousness_id,
            "coordination_metrics": self.coordination_metrics.copy(),
            "module_profiles": {
                name: {
                    "consciousness_type": profile.consciousness_type,
                    "activity_level": profile.activity_level,
                    "integration_score": profile.integration_score,
                    "health_status": profile.health_status,
                    "consciousness_depth": profile.consciousness_depth,
                    "capabilities_count": len(profile.capabilities),
                }
                for name, profile in self.module_profiles.items()
            },
            "consciousness_network_status": consciousness_status,
            "active_sessions": len(self.consciousness_sessions),
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

    async def shutdown_coordination(self) -> None:
        """Shutdown consciousness coordination"""
        logger.info("🛑 Shutting down consciousness coordination...")

        self._coordination_active = False
        self._optimization_active = False
        self.orchestration_state = OrchestrationState.SHUTTING_DOWN

        # Close consciousness sessions
        for session_name in self.consciousness_sessions:
            logger.info(f"Closing consciousness session: {session_name}")

        self.consciousness_sessions.clear()
        self.module_profiles.clear()

        logger.info("✅ Consciousness coordination shutdown complete")


# Global coordinator instance
consciousness_coordinator = MatrizConsciousnessCoordinator()


# Export key classes
__all__ = [
    "MatrizConsciousnessCoordinator",
    "ModuleConsciousnessProfile",
    "OrchestrationState",
    "consciousness_coordinator",
]
