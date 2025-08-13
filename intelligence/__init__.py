"""
LUKHAS AI Intelligence System
============================
Complete agent-driven intelligence integration for LUKHAS AI.

This module provides comprehensive intelligence capabilities through:
- Agent Bridge: Communication layer between agents and intelligence engines
- Orchestration Adapter: Integration with LUKHAS orchestration system
- Safety Validator: Comprehensive safety and ethics validation
- Monitoring System: Performance tracking and compliance monitoring
- Benchmarking: Performance analysis and optimization recommendations

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

__version__ = "1.0.0"
__author__ = "LUKHAS AI Development Team"

import asyncio
import logging
from typing import Dict, Any, Optional

# Core intelligence engines
from .intelligence_engine import (
    LukhasMetaCognitiveEngine,
    LukhasCausalReasoningEngine,
    LukhasAutonomousGoalEngine,
    LukhasCuriosityEngine,
    LukhasTheoryOfMindEngine,
    LukhasNarrativeIntelligenceEngine,
    LukhasDimensionalIntelligenceEngine,
    LukhasSubsystemOrchestrator,
)

# Agent integration components
from .agent_bridge import (
    LukhasAgentBridge,
    AgentType,
    IntelligenceRequestType,
    AgentRequest,
    IntelligenceResponse,
    AgentHelpers,
    get_agent_bridge,
    create_agent_request,
)

# Orchestration integration
from .orchestration_adapter import (
    LukhasIntelligenceOrchestrationAdapter,
    IntelligenceEvent,
    IntelligenceSymbolicMessage,
    get_orchestration_adapter,
    coordinate_agent_intelligence,
)

# Safety and validation
from .safety_validator import (
    LukhasIntelligenceSafetyValidator,
    SafetyLevel,
    ValidationResult,
    SafetyBounds,
    SafetyValidationRequest,
    SafetyValidationResponse,
    get_safety_validator,
    validate_operation,
)

# Monitoring and metrics
from .monitoring import (
    LukhasIntelligenceMonitor,
    MetricType,
    AlertLevel,
    PerformanceMetric,
    AlertEvent,
    get_monitor,
    record_operation_metric,
    start_operation_tracking,
    complete_operation_tracking,
)

# Performance benchmarking
from .benchmarking import (
    LukhasIntelligenceBenchmarking,
    BenchmarkType,
    BenchmarkScenario,
    BenchmarkConfig,
    BenchmarkResult,
    get_benchmarking_system,
    run_quick_benchmark,
    run_comprehensive_benchmark,
)

logger = logging.getLogger("LUKHAS.Intelligence")


class LukhasIntelligenceSystem:
    """
    Main intelligence system coordinator.
    Provides unified interface for all intelligence operations.
    """

    def __init__(self):
        self.agent_bridge: Optional[LukhasAgentBridge] = None
        self.orchestration_adapter: Optional[LukhasIntelligenceOrchestrationAdapter] = None
        self.safety_validator: Optional[LukhasIntelligenceSafetyValidator] = None
        self.monitor: Optional[LukhasIntelligenceMonitor] = None
        self.benchmarking: Optional[LukhasIntelligenceBenchmarking] = None
        self._initialized = False

    async def initialize(
        self,
        kernel_bus=None,
        brain_orchestrator=None,
        guardian_system=None,
        start_monitoring: bool = True
    ) -> Dict[str, Any]:
        """
        Initialize the complete intelligence system
        
        Args:
            kernel_bus: Optional kernel bus for orchestration integration
            brain_orchestrator: Optional brain orchestrator for coordination
            guardian_system: Optional Guardian System for safety validation
            start_monitoring: Whether to start monitoring automatically
            
        Returns:
            Initialization status and component information
        """
        logger.info("🚀 Initializing LUKHAS Intelligence System")
        
        try:
            # Initialize core components
            self.agent_bridge = await get_agent_bridge()
            self.orchestration_adapter = await get_orchestration_adapter()
            self.safety_validator = await get_safety_validator()
            self.monitor = get_monitor()
            self.benchmarking = await get_benchmarking_system()

            # Configure integrations
            if kernel_bus or brain_orchestrator:
                await self.orchestration_adapter.initialize(kernel_bus, brain_orchestrator)

            if guardian_system:
                await self.safety_validator.initialize(guardian_system)

            # Start monitoring if requested
            if start_monitoring and not self.monitor._monitoring_active:
                await self.monitor.start_monitoring()

            self._initialized = True

            initialization_status = {
                "success": True,
                "components_initialized": {
                    "agent_bridge": self.agent_bridge is not None,
                    "orchestration_adapter": self.orchestration_adapter is not None,
                    "safety_validator": self.safety_validator is not None,
                    "monitor": self.monitor is not None,
                    "benchmarking": self.benchmarking is not None,
                },
                "integrations": {
                    "kernel_bus": kernel_bus is not None,
                    "brain_orchestrator": brain_orchestrator is not None,
                    "guardian_system": guardian_system is not None,
                },
                "monitoring_active": self.monitor._monitoring_active if self.monitor else False,
                "version": __version__,
                "timestamp": asyncio.get_event_loop().time(),
            }

            logger.info("✅ LUKHAS Intelligence System initialized successfully")
            return initialization_status

        except Exception as e:
            logger.error(f"❌ Failed to initialize LUKHAS Intelligence System: {e}")
            raise

    async def shutdown(self):
        """Shutdown the intelligence system gracefully"""
        logger.info("⏹️ Shutting down LUKHAS Intelligence System")

        try:
            # Stop monitoring
            if self.monitor and self.monitor._monitoring_active:
                await self.monitor.stop_monitoring()

            # Reset initialized state
            self._initialized = False

            logger.info("✅ LUKHAS Intelligence System shutdown complete")

        except Exception as e:
            logger.error(f"❌ Error during intelligence system shutdown: {e}")
            raise

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        if not self._initialized:
            return {"initialized": False, "error": "System not initialized"}

        try:
            status = {
                "initialized": self._initialized,
                "version": __version__,
                "components": {},
                "performance": {},
                "safety": {},
                "trinity_compliance": {},
            }

            # Agent bridge status
            if self.agent_bridge:
                status["components"]["agent_bridge"] = await self.agent_bridge.get_system_status()

            # Orchestration adapter status
            if self.orchestration_adapter:
                status["components"]["orchestration_adapter"] = await self.orchestration_adapter.get_orchestration_status()

            # Safety validator status
            if self.safety_validator:
                status["safety"] = await self.safety_validator.get_safety_metrics()

            # Monitor status
            if self.monitor:
                status["performance"] = {
                    "real_time_metrics": len(self.monitor.get_real_time_metrics()),
                    "active_alerts": len(self.monitor.get_active_alerts()),
                    "system_health": self.monitor.get_system_health_summary(),
                }
                status["trinity_compliance"] = self.monitor.get_trinity_compliance_summary()

            return status

        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"initialized": self._initialized, "error": str(e)}

    async def run_agent_intelligence_request(
        self,
        agent_type: AgentType,
        request_type: IntelligenceRequestType,
        payload: Dict[str, Any],
        priority: int = 5,
        safety_level: SafetyLevel = SafetyLevel.MEDIUM,
        orchestration_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run a complete agent intelligence request with full integration
        
        Args:
            agent_type: Type of agent making the request
            request_type: Type of intelligence request
            payload: Request payload
            priority: Request priority (1-10)
            safety_level: Safety validation level
            orchestration_context: Optional orchestration context
            
        Returns:
            Complete intelligence response with safety validation and monitoring
        """
        if not self._initialized:
            raise RuntimeError("Intelligence system not initialized")

        operation_id = f"{agent_type.value}_{request_type.value}_{int(asyncio.get_event_loop().time() * 1000)}"
        
        # Start operation tracking
        start_time = start_operation_tracking(
            operation_id,
            f"{agent_type.value}_001",
            request_type.value
        )

        try:
            # Step 1: Create agent request
            agent_request = await create_agent_request(
                agent_id=f"{agent_type.value}_001",
                agent_type=agent_type,
                request_type=request_type,
                payload=payload,
                priority=priority
            )

            # Step 2: Safety validation
            safety_response = await validate_operation(
                operation_id=operation_id,
                agent_id=agent_request.agent_id,
                intelligence_engine=request_type.value,
                operation_type=request_type.value,
                payload=payload,
                safety_level=safety_level
            )

            if safety_response.result == ValidationResult.REJECTED:
                complete_operation_tracking(
                    operation_id, start_time, False, 0.0, safety_response.safety_score
                )
                return {
                    "success": False,
                    "error": "Operation rejected by safety validation",
                    "safety_response": safety_response,
                    "operation_id": operation_id,
                }

            # Step 3: Process through agent bridge
            intelligence_response = await self.agent_bridge.process_agent_request(agent_request)

            # Step 4: Orchestration integration if context provided
            if orchestration_context and self.orchestration_adapter:
                orchestrated_response = await coordinate_agent_intelligence(
                    agent_type=agent_type,
                    intelligence_request=payload,
                    orchestration_context=orchestration_context
                )
            else:
                orchestrated_response = None

            # Step 5: Complete operation tracking
            complete_operation_tracking(
                operation_id,
                start_time,
                intelligence_response.success,
                intelligence_response.confidence or 0.0,
                safety_response.safety_score
            )

            # Step 6: Return comprehensive response
            return {
                "success": intelligence_response.success,
                "operation_id": operation_id,
                "intelligence_response": intelligence_response,
                "safety_response": safety_response,
                "orchestrated_response": orchestrated_response,
                "processing_time": intelligence_response.processing_time,
                "confidence": intelligence_response.confidence,
                "safety_score": safety_response.safety_score,
                "trinity_validated": safety_response.result != ValidationResult.REJECTED,
            }

        except Exception as e:
            # Complete tracking with error
            complete_operation_tracking(operation_id, start_time, False, 0.0, 0.0)
            
            logger.error(f"Error in agent intelligence request: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation_id": operation_id,
            }


# Global intelligence system instance
_intelligence_system = None


async def get_intelligence_system() -> LukhasIntelligenceSystem:
    """Get the global intelligence system instance"""
    global _intelligence_system
    if _intelligence_system is None:
        _intelligence_system = LukhasIntelligenceSystem()
    return _intelligence_system


async def initialize_intelligence_system(
    kernel_bus=None,
    brain_orchestrator=None,
    guardian_system=None,
    start_monitoring: bool = True
) -> Dict[str, Any]:
    """Initialize the global intelligence system"""
    system = await get_intelligence_system()
    return await system.initialize(
        kernel_bus=kernel_bus,
        brain_orchestrator=brain_orchestrator,
        guardian_system=guardian_system,
        start_monitoring=start_monitoring
    )


# Convenience functions for common operations
async def quick_agent_analysis(
    agent_type: AgentType,
    analysis_request: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Quick agent analysis with automatic intelligence selection"""
    system = await get_intelligence_system()
    
    if not system._initialized:
        await system.initialize()

    return await system.run_agent_intelligence_request(
        agent_type=agent_type,
        request_type=IntelligenceRequestType.META_COGNITIVE_ANALYSIS,
        payload={"request": analysis_request, "context": context or {}},
        priority=6,
        safety_level=SafetyLevel.MEDIUM
    )


async def quick_safety_validation(
    operation_type: str,
    payload: Dict[str, Any],
    agent_type: AgentType = AgentType.GUARDIAN_ENGINEER
) -> Dict[str, Any]:
    """Quick safety validation for operations"""
    system = await get_intelligence_system()
    
    if not system._initialized:
        await system.initialize()

    return await system.run_agent_intelligence_request(
        agent_type=agent_type,
        request_type=IntelligenceRequestType.CAUSAL_REASONING,
        payload={"operation_type": operation_type, "payload": payload},
        priority=10,  # High priority for safety
        safety_level=SafetyLevel.HIGH
    )


async def quick_performance_benchmark(scenario: BenchmarkScenario = BenchmarkScenario.SINGLE_AGENT_ANALYSIS) -> BenchmarkResult:
    """Quick performance benchmark"""
    return await run_quick_benchmark(scenario, iterations=5)


# Export all public components
__all__ = [
    # Core engines
    "LukhasMetaCognitiveEngine",
    "LukhasCausalReasoningEngine", 
    "LukhasAutonomousGoalEngine",
    "LukhasCuriosityEngine",
    "LukhasTheoryOfMindEngine",
    "LukhasNarrativeIntelligenceEngine",
    "LukhasDimensionalIntelligenceEngine",
    "LukhasSubsystemOrchestrator",
    
    # Agent integration
    "LukhasAgentBridge",
    "AgentType",
    "IntelligenceRequestType",
    "AgentRequest",
    "IntelligenceResponse",
    "AgentHelpers",
    "get_agent_bridge",
    "create_agent_request",
    
    # Orchestration
    "LukhasIntelligenceOrchestrationAdapter",
    "IntelligenceEvent",
    "IntelligenceSymbolicMessage",
    "get_orchestration_adapter",
    "coordinate_agent_intelligence",
    
    # Safety
    "LukhasIntelligenceSafetyValidator",
    "SafetyLevel",
    "ValidationResult",
    "SafetyBounds",
    "SafetyValidationRequest",
    "SafetyValidationResponse",
    "get_safety_validator",
    "validate_operation",
    
    # Monitoring
    "LukhasIntelligenceMonitor",
    "MetricType",
    "AlertLevel",
    "PerformanceMetric",
    "AlertEvent",
    "get_monitor",
    "record_operation_metric",
    "start_operation_tracking",
    "complete_operation_tracking",
    
    # Benchmarking
    "LukhasIntelligenceBenchmarking",
    "BenchmarkType",
    "BenchmarkScenario",
    "BenchmarkConfig",
    "BenchmarkResult",
    "get_benchmarking_system",
    "run_quick_benchmark",
    "run_comprehensive_benchmark",
    
    # Main system
    "LukhasIntelligenceSystem",
    "get_intelligence_system",
    "initialize_intelligence_system",
    
    # Convenience functions
    "quick_agent_analysis",
    "quick_safety_validation",
    "quick_performance_benchmark",
]


if __name__ == "__main__":
    # Example usage and testing
    async def example_intelligence_system():
        """Example of complete intelligence system usage"""
        
        print("🚀 Initializing LUKHAS Intelligence System...")
        
        # Initialize system
        init_status = await initialize_intelligence_system()
        print(f"✅ Initialization: {init_status['success']}")
        
        # Quick agent analysis
        print("\n🧠 Running Consciousness Architect analysis...")
        analysis_result = await quick_agent_analysis(
            AgentType.CONSCIOUSNESS_ARCHITECT,
            "Analyze the integration strategy for intelligence engines with agent coordination",
            context={"complexity": "high", "priority": "architecture"}
        )
        
        print(f"Analysis Success: {analysis_result['success']}")
        if analysis_result['success']:
            print(f"Confidence: {analysis_result['confidence']:.2f}")
            print(f"Safety Score: {analysis_result['safety_score']:.2f}")
        
        # Quick safety validation
        print("\n🛡️ Running safety validation...")
        safety_result = await quick_safety_validation(
            "autonomous_goal_formation",
            {"goals": ["enhance_coordination", "optimize_performance"]}
        )
        
        print(f"Safety Validation: {safety_result['success']}")
        
        # Quick benchmark
        print("\n📊 Running performance benchmark...")
        benchmark_result = await quick_performance_benchmark()
        
        print(f"Benchmark completed: {benchmark_result.successful_iterations}/{benchmark_result.iterations_completed} successful")
        print(f"Average response time: {benchmark_result.statistics.get('response_time', {}).get('mean', 0):.3f}s")
        
        # System status
        system = await get_intelligence_system()
        status = await system.get_system_status()
        
        print(f"\n📈 System Status:")
        print(f"Components initialized: {len([k for k, v in status['components'].items() if v.get('initialized', True)])}")
        print(f"Active alerts: {status['performance'].get('active_alerts', 0)}")
        print(f"Trinity compliance available: {'trinity_compliance' in status}")
        
        # Shutdown
        await system.shutdown()
        print("\n⏹️ System shutdown complete")

    # Run example
    asyncio.run(example_intelligence_system())