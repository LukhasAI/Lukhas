"""
LUKHAS Service Bootstrap
Professional initialization of all services and adapters
"""

import logging
from datetime import datetime
from typing import Any, Optional

from core.adapters.module_service_adapter import register_service_adapters
from core.container.service_container import ServiceContainer, get_container
from core.events.contracts import (
    ConsciousnessStateChanged,
    DreamGenerated,
    MemoryFoldCreated,
    QuantumStateCreated,
    GlyphCreated,
    SymbolTranslated,
    ConsensusReached,
    QuantumStateCollapsed,
)
from core.events.typed_event_bus import EventBusService, get_typed_event_bus
from orchestration.brain.unified_cognitive_orchestrator import UnifiedCognitiveOrchestrator
from core.interfaces.services import (
    IBridgeService,
    IConsciousnessService,
    IDreamService,
    IEmotionService,
    IGovernanceService,
    IMemoryService,
    IQuantumService,
)

logger = logging.getLogger(__name__)


class LUKHASBootstrap:
    """Bootstrap and initialization manager for LUKHAS services"""

    def __init__(self):
        self.container: Optional[ServiceContainer] = None
        self.event_bus: Optional[EventBusService] = None
        self.services: dict[str, Any] = {}
        self.initialized = False
        self.startup_time: Optional[datetime] = None
        self.unified_orchestrator: Optional[UnifiedCognitiveOrchestrator] = None

    async def initialize(self) -> dict[str, Any]:
        """Initialize all LUKHAS services and infrastructure"""
        logger.info("🚀 Starting LUKHAS service bootstrap...")
        self.startup_time = datetime.now()

        try:
            # Step 1: Initialize service container
            logger.info("📦 Initializing service container...")
            self.container = get_container()

            # Step 2: Initialize event bus
            logger.info("📡 Initializing event bus...")
            self.event_bus = get_typed_event_bus()
            await self.event_bus.initialize()

            # Step 3: Register service adapters
            logger.info("🔧 Registering service adapters...")
            register_service_adapters()

            # Step 4: Initialize core services
            logger.info("🧠 Initializing core services...")
            await self._initialize_core_services()

            # Step 5: Initialize Unified Cognitive Orchestrator
            logger.info("🧠 Initializing Unified Cognitive Orchestrator...")
            self.unified_orchestrator = UnifiedCognitiveOrchestrator()
            await self.unified_orchestrator.initialize()

            # Step 6: Set up event subscriptions
            logger.info("📻 Setting up event subscriptions...")
            await self._setup_event_subscriptions()

            # Step 7: Verify system health
            logger.info("🏥 Verifying system health...")
            health_report = await self._check_system_health()

            self.initialized = True
            duration = (datetime.now() - self.startup_time).total_seconds()

            logger.info(f"✅ LUKHAS bootstrap completed in {duration:.2f} seconds")

            return {
                "status": "success",
                "initialized": True,
                "startup_duration": duration,
                "services_loaded": len(self.services),
                "health_report": health_report,
            }

        except Exception as e:
            logger.error(f"❌ Bootstrap failed: {e}")
            return {"status": "failed", "initialized": False, "error": str(e)}

    async def _initialize_core_services(self) -> None:
        """Initialize all core services"""
        service_interfaces = [
            (IMemoryService, "memory"),
            (IConsciousnessService, "consciousness"),
            (IDreamService, "dream"),
            (IQuantumService, "quantum"),
            (IEmotionService, "emotion"),
            (IGovernanceService, "governance"),
            (IBridgeService, "bridge"),
        ]

        for interface, name in service_interfaces:
            try:
                service = self.container.get_service(interface)
                if service:
                    await service.initialize()
                    self.services[name] = service
                    logger.info(f"  ✓ {name} service initialized")
                else:
                    logger.warning(f"  ⚠ {name} service not available")
            except Exception as e:
                logger.error(f"  ✗ {name} service failed: {e}")

    async def _setup_event_subscriptions(self) -> None:
        """Set up cross-module event subscriptions"""

        # Example: Memory events trigger consciousness updates
        async def on_memory_created(event: MemoryFoldCreated):
            consciousness = self.services.get("consciousness")
            if consciousness:
                await consciousness.process_awareness(
                    {
                        "type": "memory_created",
                        "fold_id": event.fold_id,
                        "emotional_context": event.emotional_context,
                    }
                )

        # Example: Dream events create memory folds
        async def on_dream_generated(event: DreamGenerated):
            memory = self.services.get("memory")
            if memory:
                await memory.create_fold(
                    content=event.dream_content,
                    metadata={
                        "type": "dream",
                        "dream_id": event.dream_id,
                        "vividness": event.vividness,
                    },
                )

        # Example: Consciousness state changes trigger emotional analysis
        async def on_consciousness_changed(event: ConsciousnessStateChanged):
            emotion = self.services.get("emotion")
            if emotion:
                await emotion.analyze_emotion(
                    {
                        "consciousness_state": event.new_state,
                        "awareness_level": event.awareness_level,
                    }
                )

        # Example: Ethics checks on quantum operations
        async def on_quantum_state(event: QuantumStateCreated):
            governance = self.services.get("governance")
            if governance:
                await governance.check_ethics(
                    action="quantum_state_created",
                    context={
                        "state_id": event.state_id,
                        "state_type": event.state_type,
                        "coherence": event.coherence,
                    },
                )

        # Register subscriptions
        if self.event_bus:
            self.kernel_bus.subscribe(MemoryFoldCreated, on_memory_created)
            self.kernel_bus.subscribe(DreamGenerated, on_dream_generated)
            self.kernel_bus.subscribe(
                ConsciousnessStateChanged, on_consciousness_changed
            )
            self.kernel_bus.subscribe(QuantumStateCreated, on_quantum_state)

            logger.info("  ✓ Event subscriptions configured")

    async def _check_system_health(self) -> dict[str, Any]:
        """Check health of all services"""
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "services": {},
        }

        for name, service in self.services.items():
            try:
                health = service.get_health()
                health_report["services"][name] = health
            except Exception as e:
                health_report["services"][name] = {
                    "status": "error",
                    "error": str(e),
                }

        # Overall health assessment
        healthy_count = sum(
            1
            for h in health_report["services"].values()
            if h.get("status") == "healthy"
        )
        total_count = len(health_report["services"])

        health_report["overall"] = {
            "healthy_services": healthy_count,
            "total_services": total_count,
            "health_percentage": (
                (healthy_count / total_count * 100) if total_count > 0 else 0
            ),
            "status": ("healthy" if healthy_count == total_count else "degraded"),
        }

        return health_report

    async def demonstrate_integration(self):
        """Demonstrate the fully integrated system"""
        if not self.unified_orchestrator:
            logger.warning("Unified orchestrator not initialized")
            return
        
        logger.info("\n🎭 DEMONSTRATING INTEGRATED LUKHAS SYSTEM")
        logger.info("=" * 60)
        
        # Process various types of thoughts
        test_thoughts = [
            "How should we balance creativity with safety?",
            "Remember the importance of ethical decision-making",
            "Dream about innovative solutions to complex problems",
            "Analyze the quantum entanglement of consciousness",
            "Feel the emotional resonance of our decisions"
        ]
        
        for thought in test_thoughts:
            logger.info(f"\n💭 Processing: '{thought}'")
            result = await self.unified_orchestrator.process_thought(thought)
            logger.info(f"   ✓ Thought ID: {result['thought_id']}")
            logger.info(f"   ✓ Awareness: {result['cognitive_state']['awareness']:.3f}")
            logger.info(f"   ✓ Coherence: {result['cognitive_state']['coherence']:.3f}")
        
        # Get system status
        status = await self.unified_orchestrator.get_system_status()
        
        logger.info("\n📊 SYSTEM STATUS:")
        logger.info(f"   • Active Symbols: {status['cognitive_state']['active_symbols']}")
        logger.info(f"   • Memory Folds: {status['memory']['total_folds']}")
        logger.info(f"   • Cache Hit Rate: {status['memory']['cache_hit_rate']:.1%}")
        logger.info(f"   • Quantum Coherence: {status['cognitive_state']['quantum_coherence']:.3f}")
        logger.info(f"   • Thoughts Processed: {status['metrics']['thoughts_processed']}")
        
        logger.info("\n✅ Integration demonstration complete!")

    async def shutdown(self) -> None:
        """Gracefully shutdown all services"""
        logger.info("🔄 Starting LUKHAS shutdown...")
        
        # Shutdown unified orchestrator
        if self.unified_orchestrator:
            await self.unified_orchestrator.shutdown()

        # Shutdown services in reverse order
        for name in reversed(list(self.services.keys())):
            try:
                service = self.services[name]
                await service.shutdown()
                logger.info(f"  ✓ {name} service shutdown")
            except Exception as e:
                logger.error(f"  ✗ {name} shutdown failed: {e}")

        # Shutdown event bus
        if self.event_bus:
            await self.event_bus.shutdown()
            logger.info("  ✓ Event bus shutdown")

        self.initialized = False
        logger.info("✅ LUKHAS shutdown complete")

    def get_service(self, service_name: str) -> Optional[Any]:
        """Get a service by name"""
        return self.services.get(service_name)

    def get_all_services(self) -> dict[str, Any]:
        """Get all registered services"""
        return self.services.copy()

    async def demonstrate_integration(self) -> None:
        """Demonstrate service integration with a simple workflow"""
        logger.info("\n🎭 Demonstrating service integration...")

        try:
            # 1. Create a memory fold
            memory = self.services.get("memory")
            if memory:
                fold_id = await memory.create_fold(
                    content="Bootstrap demonstration memory",
                    metadata={
                        "type": "demo",
                        "timestamp": datetime.now().isoformat(),
                    },
                )
                logger.info(f"  ✓ Created memory fold: {fold_id}")

            # 2. Process awareness
            consciousness = self.services.get("consciousness")
            if consciousness:
                awareness_result = await consciousness.process_awareness(
                    {
                        "input": "Service integration test",
                        "context": {"demo": True},
                    }
                )
                logger.info(f"  ✓ Processed awareness: {awareness_result}")

            # 3. Generate a dream
            dream = self.services.get("dream")
            if dream:
                dream_result = await dream.generate_dream(
                    seed={"concept": "integration", "emotion": "curiosity"}
                )
                logger.info(f"  ✓ Generated dream: {dream_result.get('dream_id')}")

            # 4. Analyze emotion
            emotion = self.services.get("emotion")
            if emotion:
                emotion_result = await emotion.analyze_emotion(
                    input_data="Service bootstrap successful"
                )
                logger.info(f"  ✓ Analyzed emotion: VAD={emotion_result}")

            # 5. Check ethics
            governance = self.services.get("governance")
            if governance:
                ethics_result = await governance.check_ethics(
                    action="bootstrap_demo", context={"purpose": "testing"}
                )
                logger.info(
                    f"  ✓ Ethics check: {'Permitted' if ethics_result else 'Denied'}"
                )

            logger.info("✅ Integration demonstration complete")

        except Exception as e:
            logger.error(f"❌ Integration demonstration failed: {e}")


# Global bootstrap instance
_bootstrap: Optional[LUKHASBootstrap] = None


async def get_bootstrap() -> LUKHASBootstrap:
    """Get or create the global bootstrap instance"""
    global _bootstrap
    if _bootstrap is None:
        _bootstrap = LUKHASBootstrap()
    return _bootstrap


async def initialize_lukhas() -> dict[str, Any]:
    """Initialize LUKHAS system using bootstrap"""
    bootstrap = await get_bootstrap()
    return await bootstrap.initialize()


async def shutdown_lukhas() -> None:
    """Shutdown LUKHAS system"""
    bootstrap = await get_bootstrap()
    await bootstrap.shutdown()


# Neuroplastic tags
# TAG:core
# TAG:bootstrap
# TAG:initialization
# TAG:professional_architecture
