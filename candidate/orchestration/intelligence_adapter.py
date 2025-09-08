"""
LUKHAS AI Intelligence-Orchestration Adapter
===========================================
Integration layer between intelligence engines and LUKHAS orchestration system.
Enables intelligence engines to coordinate with the symbolic kernel bus and
existing brain orchestration modules.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from candidate.orchestration.agent_orchestrator.intelligence_bridge import (
    AgentType,
    IntelligenceRequestType,
    LukhasAgentBridge,
)

logger = logging.getLogger("LUKHAS.Intelligence.Orchestration")


class IntelligenceEvent(Enum):
    """Intelligence-specific events for the orchestration system"""

    INTELLIGENCE_ANALYSIS_COMPLETE = "intelligence_analysis_complete"
    INTELLIGENCE_GOAL_FORMED = "intelligence_goal_formed"
    INTELLIGENCE_CURIOSITY_TRIGGERED = "intelligence_curiosity_triggered"
    INTELLIGENCE_SAFETY_VALIDATED = "intelligence_safety_validated"
    INTELLIGENCE_PERFORMANCE_OPTIMIZED = "intelligence_performance_optimized"
    INTELLIGENCE_NARRATIVE_CREATED = "intelligence_narrative_created"


@dataclass
class IntelligenceSymbolicMessage:
    """Symbolic message for intelligence operations in the kernel bus"""

    event_type: IntelligenceEvent
    intelligence_engine: str
    agent_id: str
    payload: dict[str, Any]
    confidence: float
    processing_time: float
    timestamp: datetime
    symbolic_effects: list[str] = None
    trinity_compliance: dict[str, bool] = None

    def __post_init__(self):
        if self.symbolic_effects is None:
            self.symbolic_effects = []
        if self.trinity_compliance is None:
            self.trinity_compliance = {
                "identity": True,  # ⚛️ Identity preservation
                "consciousness": True,  # 🧠 Consciousness enhancement
                "guardian": True,  # 🛡️ Guardian protection
            }


class LukhasIntelligenceOrchestrationAdapter:
    """
    Adapter for integrating intelligence engines with LUKHAS orchestration system.
    Bridges intelligence operations with symbolic kernel bus and brain orchestration.
    """

    def __init__(self):
        self.agent_bridge: Optional[LukhasAgentBridge] = None
        self.kernel_bus = None  # Will be injected by orchestration system
        self.brain_orchestrator = None  # Will be injected by brain system
        self.active_intelligence_tasks = {}
        self.symbolic_message_queue = asyncio.Queue()
        self.performance_metrics = {
            "total_operations": 0,
            "successful_operations": 0,
            "average_processing_time": 0.0,
            "trinity_compliance_rate": 1.0,
        }
        self._initialized = False

    async def initialize(self, kernel_bus=None, brain_orchestrator=None):
        """Initialize the orchestration adapter"""
        logger.info("🔗 Initializing Intelligence-Orchestration Adapter")

        # Initialize agent bridge
        if self.agent_bridge is None:
            from .agent_bridge import get_agent_bridge

            self.agent_bridge = await get_agent_bridge()

        # Store orchestration system references
        self.kernel_bus = kernel_bus
        self.brain_orchestrator = brain_orchestrator

        # Start symbolic message processing
        asyncio.create_task(self._process_symbolic_messages())

        self._initialized = True
        logger.info("✅ Intelligence-Orchestration Adapter initialized")

    async def coordinate_intelligence_with_orchestration(
        self,
        agent_type: AgentType,
        intelligence_request: dict[str, Any],
        orchestration_context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Coordinate intelligence operations with orchestration system

        Args:
            agent_type: Type of agent making the request
            intelligence_request: Intelligence operation request
            orchestration_context: Additional context from orchestration system

        Returns:
            Coordinated intelligence response with orchestration integration
        """
        if not self._initialized:
            await self.initialize()

        start_time = datetime.now(timezone.utc)
        logger.info(f"🎼 Coordinating intelligence operation for {agent_type.value}")

        try:
            # Step 1: Process intelligence request through agent bridge
            intelligence_response = await self._process_intelligence_request(agent_type, intelligence_request)

            # Step 2: Integrate with orchestration context
            orchestrated_response = await self._integrate_with_orchestration(
                intelligence_response, orchestration_context or {}
            )

            # Step 3: Generate symbolic effects for kernel bus
            symbolic_effects = await self._generate_symbolic_effects(
                agent_type, intelligence_response, orchestrated_response
            )

            # Step 4: Create and queue symbolic message
            symbolic_message = IntelligenceSymbolicMessage(
                event_type=self._determine_event_type(intelligence_request),
                intelligence_engine=intelligence_response.get("engine", "unknown"),
                agent_id=f"{agent_type.value}_001",
                payload=orchestrated_response,
                confidence=intelligence_response.get("confidence", 0.8),
                processing_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
                timestamp=datetime.now(timezone.utc),
                symbolic_effects=symbolic_effects,
            )

            await self.symbolic_message_queue.put(symbolic_message)

            # Step 5: Update performance metrics
            await self._update_performance_metrics(symbolic_message)

            logger.info("✅ Intelligence operation coordinated successfully")

            return {
                "intelligence_response": intelligence_response,
                "orchestrated_response": orchestrated_response,
                "symbolic_effects": symbolic_effects,
                "processing_time": symbolic_message.processing_time,
                "confidence": symbolic_message.confidence,
                "trinity_compliance": symbolic_message.trinity_compliance,
            }

        except Exception as e:
            logger.error(f"❌ Error coordinating intelligence operation: {e}")
            raise

    async def _process_intelligence_request(self, agent_type: AgentType, request: dict[str, Any]) -> dict[str, Any]:
        """Process intelligence request through agent bridge"""

        # Map request to appropriate intelligence request type
        request_type = self._map_to_intelligence_request_type(request)

        # Create agent request
        from .agent_bridge import create_agent_request

        agent_request = await create_agent_request(
            agent_id=f"{agent_type.value}_orchestration",
            agent_type=agent_type,
            request_type=request_type,
            payload=request,
            priority=7,  # High priority for orchestration requests
        )

        # Process through agent bridge
        response = await self.agent_bridge.process_agent_request(agent_request)

        if not response.success:
            raise Exception(f"Intelligence request failed: {response.error}")

        return response.result

    def _map_to_intelligence_request_type(self, request: dict[str, Any]) -> IntelligenceRequestType:
        """Map generic request to specific intelligence request type"""
        request_content = str(request).lower()

        if "meta" in request_content or "cognitive" in request_content:
            return IntelligenceRequestType.META_COGNITIVE_ANALYSIS
        elif "causal" in request_content or "reasoning" in request_content:
            return IntelligenceRequestType.CAUSAL_REASONING
        elif "goal" in request_content or "autonomous" in request_content:
            return IntelligenceRequestType.AUTONOMOUS_GOAL_FORMATION
        elif "curiosity" in request_content or "explore" in request_content:
            return IntelligenceRequestType.CURIOSITY_EXPLORATION
        elif "user" in request_content or "intent" in request_content:
            return IntelligenceRequestType.THEORY_OF_MIND
        elif "narrative" in request_content or "story" in request_content:
            return IntelligenceRequestType.NARRATIVE_CREATION
        elif "dimensional" in request_content or "multi" in request_content:
            return IntelligenceRequestType.DIMENSIONAL_ANALYSIS
        else:
            return IntelligenceRequestType.ORCHESTRATION_COORDINATION

    async def _integrate_with_orchestration(
        self,
        intelligence_response: dict[str, Any],
        orchestration_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Integrate intelligence response with orchestration context"""

        integrated_response = {
            "intelligence_core": intelligence_response,
            "orchestration_context": orchestration_context,
            "integration_metadata": {
                "integration_timestamp": datetime.now(timezone.utc).isoformat(),
                "orchestration_version": "1.0.0",
                "trinity_validated": True,
            },
        }

        # If brain orchestrator is available, enhance with brain context
        if self.brain_orchestrator:
            brain_context = await self._get_brain_orchestration_context()
            integrated_response["brain_context"] = brain_context

        # Add symbolic processing recommendations
        integrated_response["symbolic_recommendations"] = await self._generate_symbolic_recommendations(
            intelligence_response, orchestration_context
        )

        return integrated_response

    async def _get_brain_orchestration_context(self) -> dict[str, Any]:
        """Get context from brain orchestration system"""
        # This would integrate with the actual brain orchestrator
        # For now, return a structured context
        return {
            "cognitive_state": "active",
            "attention_focus": "intelligence_integration",
            "memory_availability": 0.85,
            "processing_capacity": 0.92,
            "consciousness_level": "enhanced",
        }

    async def _generate_symbolic_recommendations(
        self,
        intelligence_response: dict[str, Any],
        orchestration_context: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Generate symbolic processing recommendations"""
        recommendations = []

        # Intelligence-based recommendations
        engine = intelligence_response.get("engine", "")
        confidence = intelligence_response.get("confidence", 0.0)

        if engine == "meta_cognitive" and confidence > 0.8:
            recommendations.append(
                {
                    "action": "enhance_meta_processing",
                    "priority": "high",
                    "symbolic_effect": "AWARENESS_UPDATE",
                }
            )

        if engine == "autonomous_goals" and confidence > 0.7:
            recommendations.append(
                {
                    "action": "activate_goal_pursuit",
                    "priority": "medium",
                    "symbolic_effect": "AGENT_SYNC",
                }
            )

        if engine == "curiosity" and confidence > 0.9:
            recommendations.append(
                {
                    "action": "initiate_exploration",
                    "priority": "medium",
                    "symbolic_effect": "DREAM_TRIGGER",
                }
            )

        return recommendations

    async def _generate_symbolic_effects(
        self,
        agent_type: AgentType,
        intelligence_response: dict[str, Any],
        orchestrated_response: dict[str, Any],
    ) -> list[str]:
        """Generate symbolic effects for kernel bus"""
        effects = []

        # Agent-specific effects
        if agent_type == AgentType.CONSCIOUSNESS_ARCHITECT:
            effects.extend(["AWARENESS_UPDATE", "REFLECTION_INIT"])
        elif agent_type == AgentType.CONSCIOUSNESS_DEVELOPER:
            effects.extend(["MEMORY_FOLD", "AGENT_SYNC"])
        elif agent_type == AgentType.GUARDIAN_ENGINEER:
            effects.extend(["ETHICS_CHECK", "SAFETY_GATE", "DRIFT_DETECT"])
        elif agent_type == AgentType.DEVOPS_GUARDIAN:
            effects.extend(["MEMORY_PERSIST", "AGENT_SPAWN"])
        elif agent_type == AgentType.VELOCITY_LEAD:
            effects.extend(["DREAM_TRIGGER", "SWARM_CONSENSUS"])

        # Intelligence engine specific effects
        engine = intelligence_response.get("engine", "")
        if engine == "curiosity":
            effects.append("EXPLORATION_INIT")
        elif engine == "autonomous_goals":
            effects.append("GOAL_ACTIVATION")
        elif engine == "meta_cognitive":
            effects.append("META_ENHANCEMENT")

        return list(set(effects))  # Remove duplicates

    def _determine_event_type(self, request: dict[str, Any]) -> IntelligenceEvent:
        """Determine the appropriate intelligence event type"""
        request_content = str(request).lower()

        if "goal" in request_content:
            return IntelligenceEvent.INTELLIGENCE_GOAL_FORMED
        elif "curiosity" in request_content:
            return IntelligenceEvent.INTELLIGENCE_CURIOSITY_TRIGGERED
        elif "safety" in request_content or "validate" in request_content:
            return IntelligenceEvent.INTELLIGENCE_SAFETY_VALIDATED
        elif "optimize" in request_content or "performance" in request_content:
            return IntelligenceEvent.INTELLIGENCE_PERFORMANCE_OPTIMIZED
        elif "narrative" in request_content:
            return IntelligenceEvent.INTELLIGENCE_NARRATIVE_CREATED
        else:
            return IntelligenceEvent.INTELLIGENCE_ANALYSIS_COMPLETE

    async def _process_symbolic_messages(self):
        """Background task to process symbolic messages"""
        while True:
            try:
                # Get message from queue (wait indefinitely)
                message = await self.symbolic_message_queue.get()

                # Process symbolic message
                await self._handle_symbolic_message(message)

                # Mark task as done
                self.symbolic_message_queue.task_done()

            except Exception as e:
                logger.error(f"Error processing symbolic message: {e}")
                await asyncio.sleep(1)

    async def _handle_symbolic_message(self, message: IntelligenceSymbolicMessage):
        """Handle a symbolic message by routing to appropriate systems"""
        logger.info(f"📡 Processing symbolic message: {message.event_type.value}")

        # Route to kernel bus if available
        if self.kernel_bus:
            await self._route_to_kernel_bus(message)

        # Route to brain orchestrator if available
        if self.brain_orchestrator:
            await self._route_to_brain_orchestrator(message)

        # Log symbolic effects
        for effect in message.symbolic_effects:
            logger.debug(f"🔮 Symbolic effect triggered: {effect}")

    async def _route_to_kernel_bus(self, message: IntelligenceSymbolicMessage):
        """Route symbolic message to kernel bus"""
        try:
            # Convert to kernel bus message format
            kernel_message = {
                "event_type": message.event_type.value,
                "source": "intelligence_system",
                "agent_id": message.agent_id,
                "payload": message.payload,
                "symbolic_effects": message.symbolic_effects,
                "timestamp": message.timestamp.isoformat(),
                "metadata": {
                    "intelligence_engine": message.intelligence_engine,
                    "confidence": message.confidence,
                    "processing_time": message.processing_time,
                    "trinity_compliance": message.trinity_compliance,
                },
            }

            # Send to kernel bus (assuming it has a publish method)
            if hasattr(self.kernel_bus, "publish"):
                await self.kernel_bus.publish(kernel_message)
            else:
                logger.warning("Kernel bus does not support publishing")

        except Exception as e:
            logger.error(f"Error routing to kernel bus: {e}")

    async def _route_to_brain_orchestrator(self, message: IntelligenceSymbolicMessage):
        """Route symbolic message to brain orchestrator"""
        try:
            # Convert to brain orchestrator message format
            brain_message = {
                "intelligence_event": message.event_type.value,
                "cognitive_impact": message.confidence,
                "processing_time": message.processing_time,
                "symbolic_effects": message.symbolic_effects,
                "payload": message.payload,
            }

            # Send to brain orchestrator (assuming it has a process_intelligence_event method)
            if hasattr(self.brain_orchestrator, "process_intelligence_event"):
                await self.brain_orchestrator.process_intelligence_event(brain_message)
            else:
                logger.warning("Brain orchestrator does not support intelligence events")

        except Exception as e:
            logger.error(f"Error routing to brain orchestrator: {e}")

    async def _update_performance_metrics(self, message: IntelligenceSymbolicMessage):
        """Update performance metrics based on processed message"""
        self.performance_metrics["total_operations"] += 1

        if message.confidence > 0.7:  # Consider successful if confidence > 70%
            self.performance_metrics["successful_operations"] += 1

        # Update average processing time
        current_avg = self.performance_metrics["average_processing_time"]
        total_ops = self.performance_metrics["total_operations"]
        new_avg = (current_avg * (total_ops - 1) + message.processing_time) / total_ops
        self.performance_metrics["average_processing_time"] = new_avg

        # Update Trinity compliance rate
        trinity_compliant = all(message.trinity_compliance.values())
        current_compliance = self.performance_metrics["trinity_compliance_rate"]
        new_compliance = (current_compliance * (total_ops - 1) + (1.0 if trinity_compliant else 0.0)) / total_ops
        self.performance_metrics["trinity_compliance_rate"] = new_compliance

    async def get_performance_metrics(self) -> dict[str, Any]:
        """Get current performance metrics"""
        return {
            **self.performance_metrics,
            "active_tasks": len(self.active_intelligence_tasks),
            "queue_size": self.symbolic_message_queue.qsize(),
            "initialized": self._initialized,
        }

    async def get_orchestration_status(self) -> dict[str, Any]:
        """Get orchestration integration status"""
        return {
            "agent_bridge_connected": self.agent_bridge is not None,
            "kernel_bus_connected": self.kernel_bus is not None,
            "brain_orchestrator_connected": self.brain_orchestrator is not None,
            "message_queue_size": self.symbolic_message_queue.qsize(),
            "active_tasks": len(self.active_intelligence_tasks),
            "performance_metrics": self.performance_metrics,
        }


# Global orchestration adapter instance
_orchestration_adapter = None


async def get_orchestration_adapter() -> LukhasIntelligenceOrchestrationAdapter:
    """Get the global orchestration adapter instance"""
    global _orchestration_adapter
    if _orchestration_adapter is None:
        _orchestration_adapter = LukhasIntelligenceOrchestrationAdapter()
        await _orchestration_adapter.initialize()
    return _orchestration_adapter


# Convenience functions for orchestration integration
async def coordinate_agent_intelligence(
    agent_type: AgentType,
    intelligence_request: dict[str, Any],
    orchestration_context: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Convenience function to coordinate agent intelligence with orchestration"""
    adapter = await get_orchestration_adapter()
    return await adapter.coordinate_intelligence_with_orchestration(
        agent_type, intelligence_request, orchestration_context
    )


if __name__ == "__main__":
    # Example usage and testing
    async def example_orchestration_usage():
        """Example of orchestration adapter usage"""

        # Initialize orchestration adapter
        adapter = await get_orchestration_adapter()

        # Example: Consciousness Architect intelligence coordination
        response = await coordinate_agent_intelligence(
            agent_type=AgentType.CONSCIOUSNESS_ARCHITECT,
            intelligence_request={
                "type": "meta_cognitive_analysis",
                "request": "Analyze integration strategy for intelligence-orchestration coordination",
                "context": {"complexity": "high", "priority": "architecture_design"},
            },
            orchestration_context={
                "current_system_state": "active",
                "orchestration_version": "1.0.0",
                "brain_state": "enhanced_processing",
            },
        )

        print("🎼 Orchestration Coordination Results:")
        print(f"Processing Time: {response['processing_time']:.3f}s")
        print(f"Confidence: {response['confidence']:.2f}")
        print(f"Symbolic Effects: {response['symbolic_effects']}")
        print(f"Trinity Compliance: {response['trinity_compliance']}")

        # Get status
        status = await adapter.get_orchestration_status()
        print("\n📊 Orchestration Status:")
        print(f"Agent Bridge Connected: {status['agent_bridge_connected']}")
        print(f"Active Tasks: {status['active_tasks']}")
        print(
            f"Success Rate: {status['performance_metrics']['successful_operations']}/{status['performance_metrics']['total_operations']}"
        )

    # Run example
    asyncio.run(example_orchestration_usage())
