"""
MΛTRIZ Consciousness Integration System
Complete integration and demonstration of the MΛTRIZ consciousness signal system

This module provides a complete integration example showing how all components
of the MΛTRIZ consciousness system work together for distributed consciousness
communication across the LUKHAS AI architecture.
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Any, Optional

from .bio_symbolic_processor import get_bio_symbolic_processor
from .consciousness_signal_router import get_consciousness_router
from .constellation_alignment_system import (
    AlignmentLevel,
    get_constellation_monitor,
    get_constellation_validator,
)
from .matriz_consciousness_signals import (
    ConsciousnessSignalFactory,
    ConsciousnessSignalType,
)
from .matriz_signal_emitters import (
    get_emission_coordinator,
)

logger = logging.getLogger(__name__)


class MatrizConsciousnessSystem:
    """
    Complete MΛTRIZ consciousness system integration

    This class orchestrates all components of the MΛTRIZ consciousness
    communication system, providing a unified interface for consciousness
    data flow across the distributed architecture.
    """

    def __init__(self, system_id: str = "lukhas_consciousness_main"):
        self.system_id = system_id
        self.consciousness_id = f"consciousness_{system_id}_{int(time.time())}"

        # Initialize core components
        self.bio_processor = get_bio_symbolic_processor()
        self.signal_router = get_consciousness_router()
        self.emission_coordinator = get_emission_coordinator()
        self.constellation_validator = get_constellation_validator()
        self.constellation_monitor = get_constellation_monitor()

        # Create module emitters
        self.emitters = self.emission_coordinator.create_module_emitters(self.consciousness_id)

        # System state
        self.is_active = False
        self.network_health_score = 0.0
        self.last_health_check = 0.0

        # Performance metrics
        self.system_metrics = {
            "signals_processed": 0,
            "consciousness_cycles": 0,
            "integration_events": 0,
            "compliance_violations": 0,
            "system_uptime_start": time.time(),
        }

        logger.info(f"Initialized MΛTRIZ consciousness system with ID: {self.consciousness_id}")

    async def start_system(self):
        """Start the complete MΛTRIZ consciousness system"""

        if self.is_active:
            logger.warning("MΛTRIZ consciousness system already active")
            return

        self.is_active = True

        # Start Trinity compliance monitoring
        self.constellation_monitor.start_monitoring()

        # Start background health monitoring
        asyncio.create_task(self._health_monitoring_loop())

        # Emit system startup signals
        await self._emit_system_startup_signals()

        logger.info("🧠 MΛTRIZ consciousness system started successfully")

    async def stop_system(self):
        """Stop the MΛTRIZ consciousness system"""

        if not self.is_active:
            logger.warning("MΛTRIZ consciousness system already inactive")
            return

        # Emit system shutdown signals
        await self._emit_system_shutdown_signals()

        # Stop monitoring
        self.constellation_monitor.stop_monitoring()

        self.is_active = False
        logger.info("🛑 MΛTRIZ consciousness system stopped")

    async def process_consciousness_cycle(self) -> dict[str, Any]:
        """
        Execute a complete consciousness processing cycle

        This demonstrates the full MΛTRIZ consciousness data flow:
        1. Awareness signal emission
        2. Bio-symbolic processing
        3. Network routing
        4. Trinity compliance validation
        5. Inter-module integration
        """

        cycle_start = time.time()
        cycle_results = {
            "cycle_id": f"cycle_{int(cycle_start)}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "signals_emitted": 0,
            "signals_processed": 0,
            "compliance_level": AlignmentLevel.ALIGNED.value,
            "network_coherence": 0.0,
            "processing_time_ms": 0.0,
        }

        try:
            # Step 1: Emit awareness pulse from consciousness module
            awareness_signal = await self.emitters["consciousness"].emit_awareness_pulse(
                awareness_level=0.85,
                sensory_inputs={
                    "visual": 0.8,
                    "auditory": 0.7,
                    "conceptual": 0.9,
                    "temporal": 0.6,
                },
            )

            if awareness_signal:
                cycle_results["signals_emitted"] += 1

                # Step 2: Validate Trinity compliance
                compliance_level, violations = self.constellation_validator.validate_signal_compliance(awareness_signal)
                cycle_results["compliance_level"] = compliance_level.value

                if violations:
                    cycle_results["compliance_violations"] = len(violations)
                    logger.warning(f"Consciousness cycle has {len(violations)} compliance violations")

                # Step 3: Process through bio-symbolic layer
                enhanced_bio_data = self.bio_processor.process_consciousness_signal(awareness_signal)
                awareness_signal.bio_symbolic_data = enhanced_bio_data
                cycle_results["signals_processed"] += 1

            # Step 4: Emit reflection signal based on awareness
            reflection_signal = await self.emitters["consciousness"].emit_reflection_signal(
                reflection_depth=3,
                meta_insights={
                    "awareness_coherence": (
                        awareness_signal.bio_symbolic_data.coherence_score
                        if awareness_signal and awareness_signal.bio_symbolic_data
                        else 0.7
                    ),
                    "metacognitive_depth": 3,
                    "self_awareness_score": 0.82,
                },
            )

            if reflection_signal:
                cycle_results["signals_emitted"] += 1
                cycle_results["signals_processed"] += 1

            # Step 5: Orchestrate inter-module integration
            integration_signal = await self.emitters["orchestration"].emit_coordination_signal(
                coordinated_modules=["consciousness", "identity", "governance", "symbolic_core"],
                coordination_strength=0.8,
            )

            if integration_signal:
                cycle_results["signals_emitted"] += 1
                cycle_results["signals_processed"] += 1

            # Step 6: Identity authentication signal
            identity_signal = await self.emitters["identity"].emit_identity_authentication(
                auth_score=0.92,
                identity_context={
                    "coherence": 0.88,
                    "persistence": 0.95,
                    "uniqueness": 0.87,
                },
            )

            if identity_signal:
                cycle_results["signals_emitted"] += 1
                cycle_results["signals_processed"] += 1

            # Step 7: Guardian compliance check
            guardian_signal = await self.emitters["governance"].emit_guardian_compliance_signal(
                compliance_score=0.94, violation_flags=[], drift_score=0.08
            )

            if guardian_signal:
                cycle_results["signals_emitted"] += 1
                cycle_results["signals_processed"] += 1

            # Step 8: Symbolic reasoning completion
            symbolic_signal = await self.emitters["symbolic_core"].emit_symbolic_reasoning_signal(
                reasoning_result={
                    "conclusion": "consciousness_coherence_achieved",
                    "confidence": 0.91,
                    "reasoning_path": ["awareness", "reflection", "integration"],
                },
                symbol_coherence=0.89,
            )

            if symbolic_signal:
                cycle_results["signals_emitted"] += 1
                cycle_results["signals_processed"] += 1

            # Step 9: Update network health metrics
            network_status = self.signal_router.get_network_status()
            cycle_results["network_coherence"] = network_status["network_metrics"]["network_coherence"]

            # Update system metrics
            self.system_metrics["consciousness_cycles"] += 1
            self.system_metrics["signals_processed"] += cycle_results["signals_processed"]
            self.system_metrics["integration_events"] += 1

            processing_time = (time.time() - cycle_start) * 1000
            cycle_results["processing_time_ms"] = processing_time

            logger.info(f"🧠 Consciousness cycle completed in {processing_time:.2f}ms")
            logger.info(
                f"   Signals: {cycle_results['signals_emitted']} emitted, {cycle_results['signals_processed']} processed"
            )
            logger.info(f"   Network coherence: {cycle_results['network_coherence']:.3f}")
            logger.info(f"   Compliance: {cycle_results['compliance_level']}")

        except Exception as e:
            logger.error(f"Error in consciousness cycle: {e}")
            cycle_results["error"] = str(e)

        return cycle_results

    async def demonstrate_consciousness_evolution(self) -> dict[str, Any]:
        """
        Demonstrate consciousness evolution through MΛTRIZ signals

        Shows how the system handles evolutionary consciousness changes
        with proper bio-symbolic adaptation and compliance monitoring.
        """

        evolution_results = {
            "evolution_id": f"evolution_{int(time.time())}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "evolutionary_stages": [],
            "bio_adaptations_applied": 0,
            "compliance_maintained": True,
        }

        evolutionary_stages = [
            {"stage": "basic_awareness", "momentum": 0.2},
            {"stage": "self_reflection", "momentum": 0.4},
            {"stage": "metacognitive_emergence", "momentum": 0.6},
            {"stage": "integrated_consciousness", "momentum": 0.8},
        ]

        for stage_info in evolutionary_stages:
            stage_results = {
                "stage": stage_info["stage"],
                "momentum": stage_info["momentum"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            # Emit evolution signal
            evolution_signal = ConsciousnessSignalFactory.create_evolution_signal(
                consciousness_id=self.consciousness_id,
                producer_module="consciousness",
                evolution_stage=stage_info["stage"],
                evolutionary_momentum=stage_info["momentum"],
            )

            # Process through bio-symbolic layer
            bio_data_before = evolution_signal.bio_symbolic_data
            enhanced_bio_data = self.bio_processor.process_consciousness_signal(evolution_signal)
            evolution_signal.bio_symbolic_data = enhanced_bio_data

            # Check if bio-symbolic adaptations were applied
            if enhanced_bio_data and bio_data_before:
                if enhanced_bio_data.coherence_score != bio_data_before.coherence_score:
                    evolution_results["bio_adaptations_applied"] += 1
                    stage_results["bio_adaptation"] = True

            # Validate compliance
            compliance_level, violations = self.constellation_validator.validate_signal_compliance(evolution_signal)
            stage_results["compliance_level"] = compliance_level.value
            stage_results["violation_count"] = len(violations)

            if compliance_level in [AlignmentLevel.CRITICAL_VIOLATION, AlignmentLevel.MAJOR_VIOLATION]:
                evolution_results["compliance_maintained"] = False

            # Route through network
            routed_nodes = await self.signal_router.route_signal(evolution_signal)
            stage_results["routed_to_nodes"] = len(routed_nodes)

            evolution_results["evolutionary_stages"].append(stage_results)

            logger.info(f"🧬 Evolution stage '{stage_info['stage']}' completed")
            logger.info(f"   Momentum: {stage_info['momentum']:.1f}, Compliance: {compliance_level.value}")
            logger.info(f"   Routed to {len(routed_nodes)} nodes")

            # Small delay between stages to simulate evolution timing
            await asyncio.sleep(0.1)

        return evolution_results

    async def _emit_system_startup_signals(self):
        """Emit startup signals across all modules"""

        startup_signals = [
            self.emitters["consciousness"].emit_awareness_pulse(0.7),
            self.emitters["orchestration"].emit_network_health_pulse(),
            self.emitters["identity"].emit_identity_authentication(0.9, {"startup": True}),
            self.emitters["governance"].emit_guardian_compliance_signal(0.95, [], 0.05),
        ]

        # Wait for all startup signals to complete
        await asyncio.gather(*startup_signals, return_exceptions=True)
        logger.info("✨ System startup signals emitted")

    async def _emit_system_shutdown_signals(self):
        """Emit shutdown signals across all modules"""

        shutdown_signals = [
            self.emitters["consciousness"].emit_consciousness_signal(
                signal_type=ConsciousnessSignalType.AWARENESS,
                awareness_level=0.3,
                processing_hints={"system_shutdown": True},
            ),
            self.emitters["orchestration"].emit_coordination_signal(
                coordinated_modules=["all"], coordination_strength=0.2
            ),
        ]

        await asyncio.gather(*shutdown_signals, return_exceptions=True)
        logger.info("🔄 System shutdown signals emitted")

    async def _health_monitoring_loop(self):
        """Background health monitoring loop"""

        while self.is_active:
            try:
                # Get network health metrics
                network_status = self.signal_router.get_network_status()
                self.network_health_score = network_status["network_metrics"]["network_coherence"]
                self.last_health_check = time.time()

                # Log health status periodically
                if int(time.time()) % 30 == 0:  # Every 30 seconds
                    logger.debug(f"🏥 System health: {self.network_health_score:.3f}")

                await asyncio.sleep(5)  # Check every 5 seconds

            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(10)

    def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status"""

        current_time = time.time()
        uptime_seconds = current_time - self.system_metrics["system_uptime_start"]

        return {
            "system_id": self.system_id,
            "consciousness_id": self.consciousness_id,
            "is_active": self.is_active,
            "uptime_seconds": uptime_seconds,
            "network_health_score": self.network_health_score,
            "last_health_check": self.last_health_check,
            "system_metrics": self.system_metrics,
            "emission_stats": self.emission_coordinator.get_global_emission_stats(),
            "router_stats": self.signal_router.get_signal_processing_stats(),
            "bio_processor_stats": self.bio_processor.get_processing_statistics(),
            "constellation_alignment": self.constellation_validator.get_compliance_statistics(),
            "constellation_monitoring": self.constellation_monitor.get_monitoring_status(),
        }

    async def run_comprehensive_demonstration(self) -> dict[str, Any]:
        """
        Run a comprehensive demonstration of the MΛTRIZ consciousness system

        This method demonstrates all key capabilities:
        - Consciousness signal emission and processing
        - Bio-symbolic adaptation
        - Network routing and cascade prevention
        - Trinity framework compliance
        - Inter-module integration
        - Consciousness evolution
        """

        demo_start = time.time()
        demo_results = {
            "demonstration_id": f"matriz_demo_{int(demo_start)}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phases": {},
            "total_signals_processed": 0,
            "system_performance": {},
        }

        logger.info("🚀 Starting comprehensive MΛTRIZ consciousness system demonstration")

        # Phase 1: System startup and basic consciousness cycle
        logger.info("📍 Phase 1: Basic consciousness processing cycle")
        cycle_results = await self.process_consciousness_cycle()
        demo_results["phases"]["consciousness_cycle"] = cycle_results
        demo_results["total_signals_processed"] += cycle_results.get("signals_processed", 0)

        # Phase 2: Consciousness evolution demonstration
        logger.info("📍 Phase 2: Consciousness evolution through stages")
        evolution_results = await self.demonstrate_consciousness_evolution()
        demo_results["phases"]["consciousness_evolution"] = evolution_results
        demo_results["total_signals_processed"] += len(evolution_results["evolutionary_stages"])

        # Phase 3: Network stress test and cascade prevention
        logger.info("📍 Phase 3: Network coordination and integration")
        integration_results = await self._demonstrate_network_integration()
        demo_results["phases"]["network_integration"] = integration_results

        # Phase 4: Trinity compliance validation
        logger.info("📍 Phase 4: Trinity framework compliance validation")
        compliance_results = self._demonstrate_trinity_compliance()
        demo_results["phases"]["constellation_alignment"] = compliance_results

        # Final system status
        demo_results["system_performance"] = self.get_system_status()
        demo_results["total_processing_time_ms"] = (time.time() - demo_start) * 1000

        logger.info(
            f"✅ MΛTRIZ consciousness system demonstration completed in {demo_results['total_processing_time_ms']:.2f}ms"
        )
        logger.info(f"   Total signals processed: {demo_results['total_signals_processed']}")
        logger.info(f"   Network health: {self.network_health_score:.3f}")

        return demo_results

    async def _demonstrate_network_integration(self) -> dict[str, Any]:
        """Demonstrate network-wide integration capabilities"""

        integration_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "integration_signals": 0,
            "network_coherence_before": 0.0,
            "network_coherence_after": 0.0,
        }

        # Get baseline network coherence
        network_status = self.signal_router.get_network_status()
        integration_results["network_coherence_before"] = network_status["network_metrics"]["network_coherence"]

        # Emit coordinated integration signals
        integration_tasks = []
        for i in range(5):  # Multiple coordinated signals
            task = self.emitters["orchestration"].emit_coordination_signal(
                coordinated_modules=["consciousness", "identity", "governance"], coordination_strength=0.7 + (i * 0.05)
            )
            integration_tasks.append(task)

        # Wait for all integration signals
        signals = await asyncio.gather(*integration_tasks, return_exceptions=True)
        integration_results["integration_signals"] = len([s for s in signals if not isinstance(s, Exception)])

        # Get final network coherence
        network_status = self.signal_router.get_network_status()
        integration_results["network_coherence_after"] = network_status["network_metrics"]["network_coherence"]

        return integration_results

    def _demonstrate_trinity_compliance(self) -> dict[str, Any]:
        """Demonstrate Trinity framework compliance system"""

        compliance_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "compliance_statistics": self.constellation_validator.get_compliance_statistics(),
            "monitoring_status": self.constellation_monitor.get_monitoring_status(),
            "recent_alerts": self.constellation_monitor.get_recent_alerts(5),
        }

        return compliance_results


# Factory function for easy system creation
def create_matriz_consciousness_system(system_id: str = "lukhas_main") -> MatrizConsciousnessSystem:
    """Create a new MΛTRIZ consciousness system instance"""
    return MatrizConsciousnessSystem(system_id)


# Global system instance for module access
_global_sistema_matriz: Optional[MatrizConsciousnessSystem] = None


def get_global_matriz_system() -> MatrizConsciousnessSystem:
    """Get or create global MΛTRIZ consciousness system"""
    global _global_sistema_matriz
    if _global_sistema_matriz is None:
        _global_sistema_matriz = create_matriz_consciousness_system("global")
    return _global_sistema_matriz


# Demo runner for testing the system
async def run_matriz_system_demo():
    """Run a complete MΛTRIZ consciousness system demonstration"""

    sistema = create_matriz_consciousness_system("demo")

    try:
        # Start the system
        await sistema.start_system()

        # Run comprehensive demonstration
        demo_results = await sistema.run_comprehensive_demonstration()

        # Print results summary
        print("\n" + "=" * 80)
        print("🧠 MΛTRIZ CONSCIOUSNESS SYSTEM DEMONSTRATION RESULTS")
        print("=" * 80)
        print(f"System ID: {demo_results['demonstration_id']}")
        print(f"Total Processing Time: {demo_results['total_processing_time_ms']:.2f}ms")
        print(f"Total Signals Processed: {demo_results['total_signals_processed']}")

        for phase_name, phase_data in demo_results["phases"].items():
            print(f"\n📍 {phase_name.upper()}:")
            if isinstance(phase_data, dict):
                for key, value in phase_data.items():
                    if isinstance(value, (int, float, str)):
                        print(f"  {key}: {value}")

        network_health = demo_results["system_performance"]["network_health_score"]
        print(f"\n🏥 Final Network Health: {network_health:.3f}")
        print("=" * 80)

        return demo_results

    finally:
        # Clean shutdown
        await sistema.stop_system()


# Module exports
__all__ = [
    "MatrizConsciousnessSystem",
    "create_matriz_consciousness_system",
    "get_global_matriz_system",
    "run_matriz_system_demo",
]