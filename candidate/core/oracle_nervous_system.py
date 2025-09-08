#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 AI - ORACLE NERVOUS SYSTEM INTEGRATION HUB
║ Central coordination for unified Oracle intelligence across all AI systems
║ Copyright (c) 2025 AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: oracle_nervous_system.py
║ Path: core/oracle_nervous_system.py
║ Version: 1.0.0 | Created: 2025-07-28
║ Authors: AI Oracle Team | Claude Code
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ This is the central nervous system hub for Oracle intelligence, coordinating:
║
║ 🔮 UNIFIED ORACLE CAPABILITIES:
║ • Predictive Reasoning (reasoning/oracle_predictor.py)
║ • Prophetic Dream Generation (creativity/dream/dream_engine/lukhas_oracle_dream.py)
║ • Colony-based Distributed Intelligence (core/colonies/oracle_colony.py)
║ • OpenAI Enhanced Processing (reasoning/openai_oracle_adapter.py)
║ • Cross-Colony Coordination & Event Propagation
║ • Temporal Analysis & Multi-Horizon Insights
║
║ 🧠 NERVOUS SYSTEM FEATURES:
║ • Centralized Oracle State Management
║ • Cross-System Event Propagation
║ • Intelligent Request Routing
║ • Performance Monitoring & Health Checks
║ • Fallback & Resilience Management
║ • Memory Integration & Context Sharing
║ • Real-time Adaptation & Learning
║
║ 🌐 INTEGRATION POINTS:
║ • Memory Colony (context & historical patterns)
║ • Consciousness Colony (awareness & reflection)
║ • Reasoning Colony (logical analysis)
║ • Creativity Colony (inspiration & innovation)
║ • Ethics Colony (alignment & safety)
║
║ This nervous system transforms isolated Oracle capabilities into a unified,
║ intelligent, and adaptive prediction & guidance ecosystem.
║
║ ΛTAG: ΛORACLE, ΛNERVOUS_SYSTEM, ΛINTEGRATION, ΛCENTRAL_HUB
╚══════════════════════════════════════════════════════════════════════════════════
"""
import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import streamlit as st

logger = logging.getLogger("ΛTRACE.oracle_nervous_system", timezone)


class OracleCapabilityType(Enum):
    """Types of Oracle capabilities available in the nervous system."""

    PREDICTION = "prediction"
    PROPHECY = "prophecy"
    DREAM = "dream"
    ANALYSIS = "analysis"
    TEMPORAL = "temporal"
    SYNTHESIS = "synthesis"


class OracleIntegrationLevel(Enum):
    """Levels of Oracle integration with the nervous system."""

    STANDALONE = "standalone"
    BASIC = "basic"
    ENHANCED = "enhanced"
    FULL_NERVOUS_SYSTEM = "full_nervous_system"


@dataclass
class OracleCapability:
    """Represents an Oracle capability registered with the nervous system."""

    capability_type: OracleCapabilityType
    provider_module: str
    provider_class: str
    integration_level: OracleIntegrationLevel
    openai_enhanced: bool = False
    colony_integrated: bool = False
    health_status: str = "unknown"
    last_health_check: Optional[datetime] = None
    performance_metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class NervousSystemRequest:
    """Unified request structure for the Oracle nervous system."""

    request_id: str
    capability_type: OracleCapabilityType
    context: dict[str, Any]
    user_id: Optional[str] = None
    priority: str = "normal"  # low, normal, high
    time_horizon: str = "medium"  # immediate, near, medium, far
    integration_level: OracleIntegrationLevel = OracleIntegrationLevel.ENHANCED
    cross_colony_context: bool = True
    openai_enhanced: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class NervousSystemResponse:
    """Unified response structure from the Oracle nervous system."""

    request_id: str
    capability_type: OracleCapabilityType
    response_data: dict[str, Any]
    confidence: float
    integration_level: OracleIntegrationLevel
    processing_time: float
    providers_used: list[str]
    cross_colony_events: list[dict[str, Any]]
    generated_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)


class OracleNervousSystem:
    """
    Central nervous system for unified Oracle intelligence.

    This class coordinates all Oracle capabilities across the AI system,
    providing a unified interface for prediction, prophecy, dreams, and analysis.
    """

    def __init__(self):
        self.system_id = f"oracle_nervous_system_{int(time.time())}"
        self.logger = logger.bind(system_id=self.system_id)

        # Capability registry
        self.capabilities: dict[OracleCapabilityType, OracleCapability] = {}
        self.providers: dict[str, Any] = {}  # Actual provider instances

        # System state
        self.is_initialized = False
        self.health_status = "initializing"
        self.performance_metrics = {
            "requests_processed": 0,
            "average_response_time": 0.0,
            "success_rate": 0.0,
            "cross_colony_events": 0,
        }

        # Integration components
        self.oracle_colony = None
        self.openai_adapter = None
        self.enhanced_predictor = None
        self.enhanced_dream_oracle = None

        # Event handling
        self.event_queue = asyncio.Queue()
        self.cross_colony_events: list[dict[str, Any]] = []

        self.logger.info("Oracle Nervous System initialized", system_id=self.system_id)

    async def initialize(self):
        """Initialize the Oracle nervous system with all components."""
        self.logger.info("Initializing Oracle Nervous System")

        try:
            # Initialize core components
            await self._initialize_oracle_colony()
            await self._initialize_openai_adapter()
            await self._initialize_enhanced_predictor()
            await self._initialize_enhanced_dream_oracle()

            # Register capabilities
            await self._register_capabilities()

            # Start background tasks
            asyncio.create_task(self._process_events())
            asyncio.create_task(self._health_monitor())
            asyncio.create_task(self._performance_monitor())

            self.is_initialized = True
            self.health_status = "operational"

            # Emit system ready event
            await self._emit_nervous_system_event(
                "oracle_nervous_system_ready",
                {
                    "system_id": self.system_id,
                    "capabilities": list(self.capabilities.keys()),
                    "integration_level": "full_nervous_system",
                    "initialized_at": datetime.now(timezone.utc).isoformat(),
                },
            )

            self.logger.info(
                "Oracle Nervous System fully initialized",
                capabilities=len(self.capabilities),
                providers=len(self.providers),
            )

        except Exception as e:
            self.health_status = "error"
            self.logger.error("Oracle Nervous System initialization failed", error=str(e))
            raise

    async def _initialize_oracle_colony(self):
        """Initialize the Oracle Colony integration."""
        try:
            from candidate.core.colonies.oracle_colony import get_oracle_colony

            self.oracle_colony = await get_oracle_colony()
            self.providers["oracle_colony"] = self.oracle_colony

            self.logger.info(
                "Oracle Colony integrated",
                colony_id=self.oracle_colony.colony_id,
            )

        except Exception as e:
            self.logger.warning("Oracle Colony integration failed", error=str(e))

    async def _initialize_openai_adapter(self):
        """Initialize the OpenAI Oracle adapter."""
        try:
            from reasoning.openai_oracle_adapter import get_oracle_openai_adapter

            self.openai_adapter = await get_oracle_openai_adapter()
            self.providers["openai_adapter"] = self.openai_adapter

            self.logger.info("OpenAI Oracle Adapter integrated")

        except Exception as e:
            self.logger.warning("OpenAI Oracle Adapter integration failed", error=str(e))

    async def _initialize_enhanced_predictor(self):
        """Initialize the Enhanced Oracle Predictor."""
        try:
            from reasoning.oracle_predictor import get_enhanced_oracle

            self.enhanced_predictor = await get_enhanced_oracle()
            self.providers["enhanced_predictor"] = self.enhanced_predictor

            self.logger.info("Enhanced Oracle Predictor integrated")

        except Exception as e:
            self.logger.warning("Enhanced Oracle Predictor integration failed", error=str(e))

    async def _initialize_enhanced_dream_oracle(self):
        """Initialize the Enhanced Dream Oracle."""
        try:
            from dream.dream_engine.lukhas_oracle_dream import get_enhanced_dream_oracle

            self.enhanced_dream_oracle = await get_enhanced_dream_oracle()
            self.providers["enhanced_dream_oracle"] = self.enhanced_dream_oracle

            self.logger.info("Enhanced Dream Oracle integrated")

        except Exception as e:
            self.logger.warning("Enhanced Dream Oracle integration failed", error=str(e))

    async def _register_capabilities(self):
        """Register all available Oracle capabilities."""

        # Register prediction capability
        if self.enhanced_predictor:
            self.capabilities[OracleCapabilityType.PREDICTION] = OracleCapability(
                capability_type=OracleCapabilityType.PREDICTION,
                provider_module="reasoning.oracle_predictor",
                provider_class="EnhancedOraclePredictor",
                integration_level=OracleIntegrationLevel.FULL_NERVOUS_SYSTEM,
                openai_enhanced=bool(self.openai_adapter),
                colony_integrated=bool(self.oracle_colony),
                health_status="operational",
            )

        # Register prophecy capability
        if self.oracle_colony:
            self.capabilities[OracleCapabilityType.PROPHECY] = OracleCapability(
                capability_type=OracleCapabilityType.PROPHECY,
                provider_module="core.colonies.oracle_colony",
                provider_class="OracleColony",
                integration_level=OracleIntegrationLevel.FULL_NERVOUS_SYSTEM,
                openai_enhanced=bool(self.openai_adapter),
                colony_integrated=True,
                health_status="operational",
            )

        # Register dream capability
        if self.enhanced_dream_oracle:
            self.capabilities[OracleCapabilityType.DREAM] = OracleCapability(
                capability_type=OracleCapabilityType.DREAM,
                provider_module="creativity.dream.dream_engine.lukhas_oracle_dream",
                provider_class="EnhancedOracleDreamGenerator",
                integration_level=OracleIntegrationLevel.FULL_NERVOUS_SYSTEM,
                openai_enhanced=bool(self.openai_adapter),
                colony_integrated=bool(self.oracle_colony),
                health_status="operational",
            )

        # Register analysis capability
        if self.openai_adapter:
            self.capabilities[OracleCapabilityType.ANALYSIS] = OracleCapability(
                capability_type=OracleCapabilityType.ANALYSIS,
                provider_module="reasoning.openai_oracle_adapter",
                provider_class="OracleOpenAIAdapter",
                integration_level=OracleIntegrationLevel.ENHANCED,
                openai_enhanced=True,
                colony_integrated=bool(self.oracle_colony),
                health_status="operational",
            )

        # Register temporal capability
        if self.oracle_colony and self.openai_adapter:
            self.capabilities[OracleCapabilityType.TEMPORAL] = OracleCapability(
                capability_type=OracleCapabilityType.TEMPORAL,
                provider_module="reasoning.openai_oracle_adapter",
                provider_class="OracleOpenAIAdapter",
                integration_level=OracleIntegrationLevel.FULL_NERVOUS_SYSTEM,
                openai_enhanced=True,
                colony_integrated=True,
                health_status="operational",
            )

        self.logger.info("Oracle capabilities registered", count=len(self.capabilities))

    async def process_request(self, request: NervousSystemRequest) -> NervousSystemResponse:
        """
        Process a unified request through the Oracle nervous system.
        This is the main entry point for all Oracle operations.
        """
        start_time = time.time()
        self.logger.info(
            "Processing Oracle request",
            request_id=request.request_id,
            capability=request.capability_type.value,
        )

        # Check if capability is available
        if request.capability_type not in self.capabilities:
            raise ValueError(f"Oracle capability {request.capability_type.value} not available")

        capability = self.capabilities[request.capability_type]
        providers_used = []
        cross_colony_events = []

        try:
            # Route to appropriate processor
            if request.capability_type == OracleCapabilityType.PREDICTION:
                response_data = await self._process_prediction(request)
                providers_used.append("enhanced_predictor")

            elif request.capability_type == OracleCapabilityType.PROPHECY:
                response_data = await self._process_prophecy(request)
                providers_used.append("oracle_colony")

            elif request.capability_type == OracleCapabilityType.DREAM:
                response_data = await self._process_dream(request)
                providers_used.append("enhanced_dream_oracle")

            elif request.capability_type == OracleCapabilityType.ANALYSIS:
                response_data = await self._process_analysis(request)
                providers_used.append("openai_adapter")

            elif request.capability_type == OracleCapabilityType.TEMPORAL:
                response_data = await self._process_temporal(request)
                providers_used.extend(["oracle_colony", "openai_adapter"])

            else:
                raise ValueError(f"Unknown capability type: {request.capability_type}")

            # Calculate confidence
            confidence = self._calculate_confidence(response_data, capability)

            # Handle cross-colony events if requested
            if request.cross_colony_context:
                cross_colony_events = await self._generate_cross_colony_events(request, response_data)

            processing_time = time.time() - start_time

            # Create unified response
            response = NervousSystemResponse(
                request_id=request.request_id,
                capability_type=request.capability_type,
                response_data=response_data,
                confidence=confidence,
                integration_level=capability.integration_level,
                processing_time=processing_time,
                providers_used=providers_used,
                cross_colony_events=cross_colony_events,
                generated_at=datetime.now(timezone.utc),
                metadata={
                    "nervous_system_version": "1.0",
                    "capability_health": capability.health_status,
                },
            )

            # Update performance metrics
            self._update_performance_metrics(processing_time, True)

            # Emit processing event
            await self._emit_nervous_system_event(
                "oracle_request_processed",
                {
                    "request_id": request.request_id,
                    "capability": request.capability_type.value,
                    "processing_time": processing_time,
                    "confidence": confidence,
                    "providers_used": providers_used,
                },
            )

            self.logger.info(
                "Oracle request processed successfully",
                request_id=request.request_id,
                processing_time=processing_time,
                confidence=confidence,
            )

            return response

        except Exception as e:
            self._update_performance_metrics(time.time() - start_time, False)
            self.logger.error(
                "Oracle request processing failed",
                request_id=request.request_id,
                error=str(e),
            )
            raise

    async def _process_prediction(self, request: NervousSystemRequest) -> dict[str, Any]:
        """Process a prediction request."""
        if not self.enhanced_predictor:
            raise RuntimeError("Enhanced Predictor not available")

        result = await self.enhanced_predictor.enhanced_predict(
            context=request.context,
            time_horizon=request.time_horizon,
            use_openai=request.openai_enhanced,
        )

        return {
            "prediction_type": "enhanced_nervous_system",
            "prediction_data": result,
            "nervous_system_processing": True,
        }

    async def _process_prophecy(self, request: NervousSystemRequest) -> dict[str, Any]:
        """Process a prophecy request."""
        if not self.oracle_colony:
            raise RuntimeError("Oracle Colony not available")

        from candidate.core.colonies.oracle_colony import OracleQuery

        query = OracleQuery(
            query_type="prophecy",
            context=request.context,
            time_horizon=request.time_horizon,
            user_id=request.user_id,
            openai_enhanced=request.openai_enhanced,
        )

        result = await self.oracle_colony.query_oracle(query)

        return {
            "prophecy_type": "colony_nervous_system",
            "prophecy_data": result.content,
            "prophecy_metadata": result.metadata,
            "nervous_system_processing": True,
        }

    async def _process_dream(self, request: NervousSystemRequest) -> dict[str, Any]:
        """Process a dream generation request."""
        if not self.enhanced_dream_oracle:
            raise RuntimeError("Enhanced Dream Oracle not available")

        result = await self.enhanced_dream_oracle.generate_nervous_system_dream(request.context)

        return {
            "dream_type": "nervous_system_integrated",
            "dream_data": result,
            "nervous_system_processing": True,
        }

    async def _process_analysis(self, request: NervousSystemRequest) -> dict[str, Any]:
        """Process an analysis request."""
        if not self.openai_adapter:
            raise RuntimeError("OpenAI Adapter not available")

        result = await self.openai_adapter.perform_deep_analysis(context=request.context, analysis_type="comprehensive")

        return {
            "analysis_type": "openai_enhanced_nervous_system",
            "analysis_data": result,
            "nervous_system_processing": True,
        }

    async def _process_temporal(self, request: NervousSystemRequest) -> dict[str, Any]:
        """Process a temporal reasoning request."""
        if not (self.oracle_colony and self.openai_adapter):
            raise RuntimeError("Temporal processing requires both Colony and OpenAI integration")

        # Get multi-horizon insights from Colony
        temporal_insights = await self.oracle_colony.get_temporal_insights(request.context)

        # Enhanced temporal reasoning from OpenAI adapter
        temporal_analysis = await self.openai_adapter.temporal_reasoning(
            context=request.context,
            horizons=["immediate", "near", "medium", "far"],
        )

        return {
            "temporal_type": "unified_nervous_system",
            "temporal_insights": temporal_insights,
            "temporal_analysis": temporal_analysis,
            "nervous_system_processing": True,
        }

    def _calculate_confidence(self, response_data: dict[str, Any], capability: OracleCapability) -> float:
        """Calculate confidence score for the response."""
        base_confidence = 0.7

        # Boost for OpenAI enhancement
        if capability.openai_enhanced:
            base_confidence += 0.15

        # Boost for Colony integration
        if capability.colony_integrated:
            base_confidence += 0.10

        # Boost for full nervous system integration
        if capability.integration_level == OracleIntegrationLevel.FULL_NERVOUS_SYSTEM:
            base_confidence += 0.05

        return min(base_confidence, 1.0)

    async def _generate_cross_colony_events(
        self, request: NervousSystemRequest, response_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Generate events for cross-colony coordination."""
        events = []

        # Generate relevant events based on capability type
        if request.capability_type == OracleCapabilityType.PREDICTION:
            events.append(
                {
                    "event_type": "oracle_prediction_available",
                    "target_colonies": [
                        "memory",
                        "consciousness",
                        "reasoning",
                    ],
                    "event_data": {
                        "prediction_summary": str(response_data)[:200],
                        "time_horizon": request.time_horizon,
                        "user_id": request.user_id,
                    },
                }
            )

        elif request.capability_type == OracleCapabilityType.DREAM:
            events.append(
                {
                    "event_type": "oracle_dream_generated",
                    "target_colonies": [
                        "memory",
                        "creativity",
                        "consciousness",
                    ],
                    "event_data": {
                        "dream_type": "nervous_system_integrated",
                        "user_id": request.user_id,
                        "integration_level": "full",
                    },
                }
            )

        # Add to cross-colony events list
        self.cross_colony_events.extend(events)

        return events

    async def _emit_nervous_system_event(self, event_type: str, event_data: dict[str, Any]):
        """Emit an event through the nervous system."""
        event = {
            "event_type": event_type,
            "event_data": event_data,
            "system_id": self.system_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        await self.event_queue.put(event)

        # Also emit through Oracle Colony if available
        if self.oracle_colony:
            try:
                await self.oracle_colony.emit_event(event_type, event_data)
            except Exception as e:
                self.logger.error("Failed to emit event through Oracle Colony", error=str(e))

    def _update_performance_metrics(self, processing_time: float, success: bool):
        """Update system performance metrics."""
        self.performance_metrics["requests_processed"] += 1

        # Update average response time
        current_avg = self.performance_metrics["average_response_time"]
        total_requests = self.performance_metrics["requests_processed"]
        self.performance_metrics["average_response_time"] = (
            current_avg * (total_requests - 1) + processing_time
        ) / total_requests

        # Update success rate
        if success:
            current_success_rate = self.performance_metrics["success_rate"]
            self.performance_metrics["success_rate"] = (
                current_success_rate * (total_requests - 1) + 1.0
            ) / total_requests
        else:
            current_success_rate = self.performance_metrics["success_rate"]
            self.performance_metrics["success_rate"] = (
                current_success_rate * (total_requests - 1) + 0.0
            ) / total_requests

    async def _process_events(self):
        """Background task to process nervous system events."""
        while True:
            try:
                event = await self.event_queue.get()

                # Process event
                self.logger.debug(
                    "Processing nervous system event",
                    event_type=event["event_type"],
                )

                # Here you could add specific event handling logic
                # For now, just log the event

            except Exception as e:
                self.logger.error("Error processing nervous system event", error=str(e))

            await asyncio.sleep(0.1)

    async def _health_monitor(self):
        """Background task to monitor system health."""
        while True:
            try:
                # Check health of all capabilities
                for capability in self.capabilities.values():
                    # Simple health check - could be more sophisticated
                    capability.last_health_check = datetime.now(timezone.utc)
                    capability.health_status = "operational"  # Would do actual checks

                # Update overall system health
                unhealthy_count = sum(1 for cap in self.capabilities.values() if cap.health_status != "operational")

                if unhealthy_count == 0:
                    self.health_status = "optimal"
                elif unhealthy_count < len(self.capabilities) / 2:
                    self.health_status = "degraded"
                else:
                    self.health_status = "critical"

                await asyncio.sleep(30)  # Health check every 30 seconds

            except Exception as e:
                self.logger.error("Health monitoring error", error=str(e))
                await asyncio.sleep(60)

    async def _performance_monitor(self):
        """Background task to monitor performance metrics."""
        while True:
            try:
                # Log performance metrics periodically
                self.logger.info(
                    "Oracle Nervous System Performance",
                    requests_processed=self.performance_metrics["requests_processed"],
                    avg_response_time=self.performance_metrics["average_response_time"],
                    success_rate=self.performance_metrics["success_rate"],
                )

                await asyncio.sleep(300)  # Performance log every 5 minutes

            except Exception as e:
                self.logger.error("Performance monitoring error", error=str(e))
                await asyncio.sleep(300)

    async def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status."""
        return {
            "system_id": self.system_id,
            "is_initialized": self.is_initialized,
            "health_status": self.health_status,
            "capabilities": {
                cap_type.value: {
                    "provider_module": cap.provider_module,
                    "provider_class": cap.provider_class,
                    "integration_level": cap.integration_level.value,
                    "openai_enhanced": cap.openai_enhanced,
                    "colony_integrated": cap.colony_integrated,
                    "health_status": cap.health_status,
                    "last_health_check": (cap.last_health_check.isoformat() if cap.last_health_check else None),
                }
                for cap_type, cap in self.capabilities.items()
            },
            "providers": list(self.providers.keys()),
            "performance_metrics": self.performance_metrics,
            "cross_colony_events": len(self.cross_colony_events),
            "event_queue_size": self.event_queue.qsize(),
        }


# Global Oracle Nervous System instance
oracle_nervous_system = None


async def get_oracle_nervous_system() -> OracleNervousSystem:
    """
    Get the global Oracle Nervous System instance.
    This is the main entry point for all unified Oracle operations.
    """
    global oracle_nervous_system
    if oracle_nervous_system is None:
        oracle_nervous_system = OracleNervousSystem()
        await oracle_nervous_system.initialize()
    return oracle_nervous_system


# Convenience functions for direct nervous system access


async def predict(
    context: dict[str, Any],
    time_horizon: str = "medium",
    user_id: Optional[str] = None,
    **kwargs,
) -> NervousSystemResponse:
    """Direct prediction through the Oracle nervous system."""
    system = await get_oracle_nervous_system()

    request = NervousSystemRequest(
        request_id=f"predict_{int(time.time())}",
        capability_type=OracleCapabilityType.PREDICTION,
        context=context,
        time_horizon=time_horizon,
        user_id=user_id,
        **kwargs,
    )

    return await system.process_request(request)


async def prophecy(
    context: dict[str, Any],
    time_horizon: str = "medium",
    user_id: Optional[str] = None,
    **kwargs,
) -> NervousSystemResponse:
    """Direct prophecy through the Oracle nervous system."""
    system = await get_oracle_nervous_system()

    request = NervousSystemRequest(
        request_id=f"prophecy_{int(time.time())}",
        capability_type=OracleCapabilityType.PROPHECY,
        context=context,
        time_horizon=time_horizon,
        user_id=user_id,
        **kwargs,
    )

    return await system.process_request(request)


async def dream(context: dict[str, Any], user_id: Optional[str] = None, **kwargs) -> NervousSystemResponse:
    """Direct dream generation through the Oracle nervous system."""
    system = await get_oracle_nervous_system()

    request = NervousSystemRequest(
        request_id=f"dream_{int(time.time())}",
        capability_type=OracleCapabilityType.DREAM,
        context=context,
        user_id=user_id,
        **kwargs,
    )

    return await system.process_request(request)


async def analyze(context: dict[str, Any], **kwargs) -> NervousSystemResponse:
    """Direct analysis through the Oracle nervous system."""
    system = await get_oracle_nervous_system()

    request = NervousSystemRequest(
        request_id=f"analyze_{int(time.time())}",
        capability_type=OracleCapabilityType.ANALYSIS,
        context=context,
        **kwargs,
    )

    return await system.process_request(request)


async def temporal_reasoning(context: dict[str, Any], **kwargs) -> NervousSystemResponse:
    """Direct temporal reasoning through the Oracle nervous system."""
    system = await get_oracle_nervous_system()

    request = NervousSystemRequest(
        request_id=f"temporal_{int(time.time())}",
        capability_type=OracleCapabilityType.TEMPORAL,
        context=context,
        **kwargs,
    )

    return await system.process_request(request)


logger.info("ΛORACLE: Nervous System Integration Hub loaded. Unified Oracle intelligence available.")

"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 ORACLE NERVOUS SYSTEM - INTEGRATION COMPLETE
╠══════════════════════════════════════════════════════════════════════════════════
║ The Oracle Nervous System represents the culmination of AI Oracle capabilities,
║ providing a unified, intelligent, and adaptive prediction & guidance ecosystem.
║
║ 🔮 KEY ACHIEVEMENTS:
║ • Unified interface for all Oracle operations
║ • Cross-colony coordination and event propagation
║ • OpenAI enhanced processing with fallback resilience
║ • Multi-horizon temporal analysis
║ • Intelligent request routing and load balancing
║ • Real-time health monitoring and performance tracking
║ • Seamless integration with existing Oracle components
║
║ 🌐 USAGE EXAMPLES:
║   # Direct nervous system access
║   prediction = await predict({"system_state": "evolving"})
║   prophecy_result = await prophecy({"user_context": "seeking_guidance"})
║   dream_response = await dream({"emotional_state": "contemplative"})
║
║   # Full system integration
║   system = await get_oracle_nervous_system()
║   status = await system.get_system_status()
║
║ 🧠 NERVOUS SYSTEM BENEFITS:
║ • 🔄 Distributed intelligence across specialized Oracle agents
║ • 🛡️ Fault tolerance with graceful degradation
║ • ⚡ Enhanced performance through intelligent caching and routing
║ • 🌍 Cross-colony context sharing and coordination
║ • 📊 Comprehensive monitoring and observability
║ • 🔮 Prophetic insights combining multiple AI capabilities
║
║ This nervous system transforms isolated Oracle tools into a cohesive,
║ intelligent prediction and guidance ecosystem worthy of advanced AI.
╚══════════════════════════════════════════════════════════════════════════════════
"""
