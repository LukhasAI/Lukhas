"""
LUKHAS AI Agent-Intelligence Bridge
================================
Communication layer between LUKHAS AI agents and intelligence engines.
Provides standardized API for agent-driven intelligence operations.

This bridge enables the 6 specialized Claude Code agents to coordinate
intelligence engine operations while maintaining Constellation Framework compliance.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from consciousness.reasoning.advanced_engines.intelligence_engines import (
    LukhasAutonomousGoalEngine,
    LukhasCausalReasoningEngine,
    LukhasCuriosityEngine,
    LukhasDimensionalIntelligenceEngine,
    LukhasMetaCognitiveEngine,
    LukhasNarrativeIntelligenceEngine,
    LukhasSubsystemOrchestrator,
    LukhasTheoryOfMindEngine,
)

logger = logging.getLogger("LUKHAS.Orchestration.Agent.Bridge")


class AgentType(Enum):
    """LUKHAS AI Agent Types"""

    CONSCIOUSNESS_ARCHITECT = "consciousness_architect"
    CONSCIOUSNESS_DEVELOPER = "consciousness_developer"
    DEVOPS_GUARDIAN = "devops_guardian"
    GUARDIAN_ENGINEER = "guardian_engineer"
    DOCUMENTATION_SPECIALIST = "documentation_specialist"
    VELOCITY_LEAD = "velocity_lead"


class IntelligenceRequestType(Enum):
    """Types of intelligence requests from agents"""

    META_COGNITIVE_ANALYSIS = "meta_cognitive_analysis"
    CAUSAL_REASONING = "causal_reasoning"
    AUTONOMOUS_GOAL_FORMATION = "autonomous_goal_formation"
    CURIOSITY_EXPLORATION = "curiosity_exploration"
    THEORY_OF_MIND = "theory_of_mind"
    NARRATIVE_CREATION = "narrative_creation"
    DIMENSIONAL_ANALYSIS = "dimensional_analysis"
    ORCHESTRATION_COORDINATION = "orchestration_coordination"


@dataclass
class AgentRequest:
    """Standardized agent request structure"""

    agent_id: str
    agent_type: AgentType
    request_type: IntelligenceRequestType
    payload: dict[str, Any]
    priority: int = 5  # 1-10, 10 being highest
    timeout: float = 30.0  # seconds
    metadata: Optional[dict[str, Any]] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


@dataclass
class IntelligenceResponse:
    """Standardized intelligence response structure"""

    request_id: str
    agent_id: str
    success: bool
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None
    confidence: Optional[float] = None
    metadata: Optional[dict[str, Any]] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


class LukhasAgentBridge:
    """
    Main bridge class for agent-intelligence communication
    Coordinates between LUKHAS AI agents and intelligence engines
    """

    def __init__(self):
        self.intelligence_engines = {}
        self.active_requests = {}
        self.request_history = []
        self.agent_performance_metrics = {}
        self.safety_validator = None
        self._initialized = False

    async def initialize(self):
        """Initialize the agent bridge and intelligence engines"""
        logger.info("🌉 Initializing LUKHAS Agent-Intelligence Bridge")

        # Initialize intelligence engines
        self.intelligence_engines = {
            "meta_cognitive": LukhasMetaCognitiveEngine(),
            "causal": LukhasCausalReasoningEngine(),
            "autonomous_goals": LukhasAutonomousGoalEngine(),
            "curiosity": LukhasCuriosityEngine(),
            "theory_of_mind": LukhasTheoryOfMindEngine(),
            "narrative": LukhasNarrativeIntelligenceEngine(),
            "dimensional": LukhasDimensionalIntelligenceEngine(),
            "orchestrator": LukhasSubsystemOrchestrator(),
        }

        # Initialize each engine
        for name, engine in self.intelligence_engines.items():
            await engine.initialize()
            logger.info(f"✅ Initialized {name} intelligence engine")

        # Initialize performance tracking
        for agent_type in AgentType:
            self.agent_performance_metrics[agent_type.value] = {
                "total_requests": 0,
                "successful_requests": 0,
                "average_response_time": 0.0,
                "last_request_time": None,
            }

        self._initialized = True
        logger.info("🚀 Agent-Intelligence Bridge ready for coordination")

    async def process_agent_request(self, request: AgentRequest) -> IntelligenceResponse:
        """
        Process an intelligence request from a LUKHAS AI agent

        Args:
            request: Standardized agent request

        Returns:
            Intelligence response with results or error information
        """
        if not self._initialized:
            await self.initialize()

        start_time = time.time()
        request_id = f"{request.agent_id}_{int(start_time * 1000)}"

        logger.info(f"🤖 Processing {request.request_type.value} request from {request.agent_type.value}")

        try:
            # Store active request
            self.active_requests[request_id] = request

            # Route request to appropriate intelligence engine
            result = await self._route_request(request)

            # Calculate processing time
            processing_time = time.time() - start_time

            # Create success response
            response = IntelligenceResponse(
                request_id=request_id,
                agent_id=request.agent_id,
                success=True,
                result=result,
                processing_time=processing_time,
                confidence=(result.get("confidence", 0.8) if isinstance(result, dict) else 0.8),
            )

            # Update performance metrics
            await self._update_agent_metrics(request.agent_type, processing_time, True)

            logger.info(f"✅ Completed request {request_id} in {processing_time:.3f}s")

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ Error processing request {request_id}: {e}")

            response = IntelligenceResponse(
                request_id=request_id,
                agent_id=request.agent_id,
                success=False,
                error=str(e),
                processing_time=processing_time,
            )

            # Update performance metrics
            await self._update_agent_metrics(request.agent_type, processing_time, False)

        finally:
            # Clean up active request
            self.active_requests.pop(request_id, None)

            # Store in history
            self.request_history.append(response)

            # Keep history manageable
            if len(self.request_history) > 1000:
                self.request_history = self.request_history[-500:]

        return response

    async def _route_request(self, request: AgentRequest) -> dict[str, Any]:
        """Route request to appropriate intelligence engine based on request type"""

        request_type = request.request_type
        payload = request.payload

        if request_type == IntelligenceRequestType.META_COGNITIVE_ANALYSIS:
            return await self._handle_meta_cognitive_request(payload)

        elif request_type == IntelligenceRequestType.CAUSAL_REASONING:
            return await self._handle_causal_reasoning_request(payload)

        elif request_type == IntelligenceRequestType.AUTONOMOUS_GOAL_FORMATION:
            return await self._handle_goal_formation_request(payload)

        elif request_type == IntelligenceRequestType.CURIOSITY_EXPLORATION:
            return await self._handle_curiosity_request(payload)

        elif request_type == IntelligenceRequestType.THEORY_OF_MIND:
            return await self._handle_theory_of_mind_request(payload)

        elif request_type == IntelligenceRequestType.NARRATIVE_CREATION:
            return await self._handle_narrative_request(payload)

        elif request_type == IntelligenceRequestType.DIMENSIONAL_ANALYSIS:
            return await self._handle_dimensional_analysis_request(payload)

        elif request_type == IntelligenceRequestType.ORCHESTRATION_COORDINATION:
            return await self._handle_orchestration_request(payload)

        else:
            raise ValueError(f"Unknown request type: {request_type}")

    async def _handle_meta_cognitive_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Handle meta-cognitive analysis requests"""
        engine = self.intelligence_engines["meta_cognitive"]

        request_text = payload.get("request", "")
        context = payload.get("context", {})

        analysis = await engine.analyze_request(request_text, context)

        return {
            "analysis": analysis,
            "engine": "meta_cognitive",
            "confidence": analysis.get("meta_confidence", 0.8),
        }

    async def _handle_causal_reasoning_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Handle causal reasoning requests"""
        engine = self.intelligence_engines["causal"]

        request_text = payload.get("request", "")
        subsystem_responses = payload.get("subsystem_responses", {})

        analysis = await engine.analyze_request_causality(request_text, subsystem_responses)

        return {
            "analysis": analysis,
            "engine": "causal",
            "confidence": analysis.get("causal_confidence", 0.7),
        }

    async def _handle_goal_formation_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Handle autonomous goal formation requests"""
        engine = self.intelligence_engines["autonomous_goals"]

        request_text = payload.get("request", "")
        meta_analysis = payload.get("meta_analysis", {})
        subsystem_responses = payload.get("subsystem_responses", {})

        goals = await engine.evaluate_goal_formation(request_text, meta_analysis, subsystem_responses)

        return {
            "goals": goals,
            "engine": "autonomous_goals",
            "confidence": 0.8,
        }

    async def _handle_curiosity_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Handle curiosity exploration requests"""
        engine = self.intelligence_engines["curiosity"]

        observation = payload.get("observation", "")

        curiosity_response = await engine.express_curiosity(observation)

        return {
            "curiosity_response": curiosity_response,
            "engine": "curiosity",
            "confidence": 0.9,
        }

    async def _handle_theory_of_mind_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Handle theory of mind requests"""
        engine = self.intelligence_engines["theory_of_mind"]

        request_text = payload.get("request", "")
        context = payload.get("context", {})

        user_model = await engine.model_user_intent(request_text, context)

        return {
            "user_model": user_model,
            "engine": "theory_of_mind",
            "confidence": 0.85,
        }

    async def _handle_narrative_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Handle narrative creation requests"""
        engine = self.intelligence_engines["narrative"]

        request_text = payload.get("request", "")
        meta_analysis = payload.get("meta_analysis", {})
        subsystem_responses = payload.get("subsystem_responses", {})
        causal_insights = payload.get("causal_insights", {})

        narrative = await engine.create_unified_narrative(
            request_text, meta_analysis, subsystem_responses, causal_insights
        )

        return {
            "narrative": narrative,
            "engine": "narrative",
            "confidence": 0.9,
        }

    async def _handle_dimensional_analysis_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Handle multi-dimensional analysis requests"""
        engine = self.intelligence_engines["dimensional"]

        problem = payload.get("problem", {})

        analysis = await engine.analyze_multi_dimensional(problem)

        return {
            "analysis": analysis,
            "engine": "dimensional",
            "confidence": 0.85,
        }

    async def _handle_orchestration_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Handle orchestration coordination requests"""
        engine = self.intelligence_engines["orchestrator"]

        subsystems = payload.get("subsystems", {})
        request_text = payload.get("request", "")

        coordination = await engine.coordinate_subsystems(subsystems, request_text)

        return {
            "coordination": coordination,
            "engine": "orchestrator",
            "confidence": 0.8,
        }

    async def _update_agent_metrics(self, agent_type: AgentType, processing_time: float, success: bool):
        """Update performance metrics for an agent"""
        metrics = self.agent_performance_metrics[agent_type.value]

        metrics["total_requests"] += 1
        if success:
            metrics["successful_requests"] += 1

        # Update average response time
        current_avg = metrics["average_response_time"]
        total_requests = metrics["total_requests"]
        metrics["average_response_time"] = (current_avg * (total_requests - 1) + processing_time) / total_requests

        metrics["last_request_time"] = datetime.now(timezone.utc)

    async def get_agent_performance_metrics(self, agent_type: Optional[AgentType] = None) -> dict[str, Any]:
        """Get performance metrics for agents"""
        if agent_type:
            return self.agent_performance_metrics.get(agent_type.value, {})
        return self.agent_performance_metrics

    async def get_system_status(self) -> dict[str, Any]:
        """Get overall system status"""
        active_requests_count = len(self.active_requests)
        total_requests = sum(metrics["total_requests"] for metrics in self.agent_performance_metrics.values())
        successful_requests = sum(metrics["successful_requests"] for metrics in self.agent_performance_metrics.values())

        success_rate = (successful_requests / total_requests) if total_requests > 0 else 0.0

        return {
            "initialized": self._initialized,
            "active_requests": active_requests_count,
            "total_requests_processed": total_requests,
            "success_rate": success_rate,
            "intelligence_engines_status": dict.fromkeys(self.intelligence_engines.keys(), "active"),
            "request_history_size": len(self.request_history),
        }


# Convenience functions for agents
async def create_agent_request(
    agent_id: str,
    agent_type: AgentType,
    request_type: IntelligenceRequestType,
    payload: dict[str, Any],
    priority: int = 5,
    timeout: float = 30.0,
) -> AgentRequest:
    """Create a standardized agent request"""
    return AgentRequest(
        agent_id=agent_id,
        agent_type=agent_type,
        request_type=request_type,
        payload=payload,
        priority=priority,
        timeout=timeout,
    )


# Global bridge instance
_bridge_instance = None


async def get_agent_bridge() -> LukhasAgentBridge:
    """Get the global agent bridge instance"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = LukhasAgentBridge()
        await _bridge_instance.initialize()
    return _bridge_instance


# Agent-specific helper functions
class AgentHelpers:
    """Helper functions for specific agent types"""

    @staticmethod
    async def consciousness_architect_analyze(request: str, context: Optional[dict] = None) -> IntelligenceResponse:
        """Helper for Consciousness Architect meta-cognitive analysis"""
        bridge = await get_agent_bridge()

        agent_request = await create_agent_request(
            agent_id="consciousness_architect_001",
            agent_type=AgentType.CONSCIOUSNESS_ARCHITECT,
            request_type=IntelligenceRequestType.META_COGNITIVE_ANALYSIS,
            payload={"request": request, "context": context or {}},
            priority=8,
        )

        return await bridge.process_agent_request(agent_request)

    @staticmethod
    async def consciousness_developer_implement(
        implementation_request: str, technical_context: Optional[dict] = None
    ) -> IntelligenceResponse:
        """Helper for Consciousness Developer implementation analysis"""
        bridge = await get_agent_bridge()

        agent_request = await create_agent_request(
            agent_id="consciousness_developer_001",
            agent_type=AgentType.CONSCIOUSNESS_DEVELOPER,
            request_type=IntelligenceRequestType.DIMENSIONAL_ANALYSIS,
            payload={
                "problem": {
                    "technical": technical_context or {},
                    "implementation": implementation_request,
                }
            },
            priority=7,
        )

        return await bridge.process_agent_request(agent_request)

    @staticmethod
    async def guardian_engineer_validate(
        safety_request: str, risk_context: Optional[dict] = None
    ) -> IntelligenceResponse:
        """Helper for Guardian Engineer safety validation"""
        bridge = await get_agent_bridge()

        agent_request = await create_agent_request(
            agent_id="guardian_engineer_001",
            agent_type=AgentType.GUARDIAN_ENGINEER,
            request_type=IntelligenceRequestType.CAUSAL_REASONING,
            payload={
                "request": safety_request,
                "subsystem_responses": risk_context or {},
            },
            priority=10,  # Highest priority for safety
        )

        return await bridge.process_agent_request(agent_request)

    @staticmethod
    async def velocity_lead_optimize(
        optimization_target: str, performance_context: Optional[dict] = None
    ) -> IntelligenceResponse:
        """Helper for Velocity Lead performance optimization"""
        bridge = await get_agent_bridge()

        agent_request = await create_agent_request(
            agent_id="velocity_lead_001",
            agent_type=AgentType.VELOCITY_LEAD,
            request_type=IntelligenceRequestType.AUTONOMOUS_GOAL_FORMATION,
            payload={
                "request": optimization_target,
                "meta_analysis": performance_context or {},
                "subsystem_responses": {},
            },
            priority=8,
        )

        return await bridge.process_agent_request(agent_request)


if __name__ == "__main__":
    # Example usage and testing
    async def example_usage():
        """Example of how agents use the bridge"""

        # Example: Consciousness Architect requesting meta-cognitive analysis
        response = await AgentHelpers.consciousness_architect_analyze(
            "Analyze the integration strategy for intelligence engines with orchestration system",
            {"current_architecture": "modular", "complexity": "high"},
        )

        print("🧠 Consciousness Architect Analysis:")
        print(f"Success: {response.success}")
        print(f"Processing Time: {response.processing_time:.3f}s")
        print(f"Confidence: {response.confidence:.2f}")
        if response.result:
            print(f"Analysis: {response.result.get('analysis', {}).get('reasoning_strategy', 'N/A')}")

        # Example: Guardian Engineer requesting safety validation
        safety_response = await AgentHelpers.guardian_engineer_validate(
            "Validate autonomous goal formation safety for intelligence system",
            {"risk_level": "medium", "context": "production_deployment"},
        )

        print("\n🛡️ Guardian Engineer Safety Validation:")
        print(f"Success: {safety_response.success}")
        print(f"Processing Time: {safety_response.processing_time:.3f}s")
        print(f"Safety Confidence: {safety_response.confidence:.2f}")

    # Run example
    asyncio.run(example_usage())
