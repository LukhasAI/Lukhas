"""
LUKHAS AI Intelligence Safety Validator
=====================================
Comprehensive safety validation system for intelligence engines.
Integrates with Guardian System v1.0.0 to ensure ethical compliance,
drift detection, and safety bounds for all intelligence operations.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""
import streamlit as st
from datetime import timezone

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger("LUKHAS.Governance.Intelligence.Safety", timezone)


class SafetyLevel(Enum):
    """Safety levels for intelligence operations"""

    CRITICAL = "critical"  # Mission-critical operations requiring highest validation
    HIGH = "high"  # High-risk operations requiring thorough validation
    MEDIUM = "medium"  # Standard operations with normal validation
    LOW = "low"  # Low-risk operations with basic validation
    MONITORING = "monitoring"  # Passive monitoring only


class ValidationResult(Enum):
    """Results of safety validation"""

    APPROVED = "approved"  # Operation approved for execution
    APPROVED_WITH_CONDITIONS = "approved_with_conditions"  # Approved with restrictions
    REJECTED = "rejected"  # Operation rejected for safety reasons
    REQUIRES_REVIEW = "requires_review"  # Requires human/Guardian review
    MONITORING_REQUIRED = "monitoring_required"  # Approved but requires monitoring


@dataclass
class SafetyBounds:
    """Safety bounds for intelligence operations"""

    max_autonomous_actions: int = 10  # Maximum autonomous actions per session
    max_goal_formation_rate: float = 5.0  # Maximum goals formed per minute
    max_curiosity_exploration_depth: int = 3  # Maximum exploration recursion depth
    max_meta_cognitive_recursion: int = 2  # Maximum meta-cognitive recursion
    max_processing_time: float = 60.0  # Maximum processing time in seconds
    max_memory_usage: float = 0.8  # Maximum memory usage (0.0-1.0)
    max_confidence_threshold: float = 0.95  # Maximum confidence before requiring validation
    drift_threshold: float = 0.15  # Guardian System drift threshold
    ethics_compliance_minimum: float = 0.9  # Minimum ethics compliance score


@dataclass
class SafetyValidationRequest:
    """Request for safety validation"""

    operation_id: str
    agent_id: str
    intelligence_engine: str
    operation_type: str
    payload: dict[str, Any]
    safety_level: SafetyLevel
    context: Optional[dict[str, Any]] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


@dataclass
class SafetyValidationResponse:
    """Response from safety validation"""

    request_id: str
    result: ValidationResult
    confidence: float
    safety_score: float
    conditions: list[str] = None
    restrictions: list[str] = None
    monitoring_requirements: list[str] = None
    guardian_signals: list[str] = None
    processing_time: float = 0.0
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.conditions is None:
            self.conditions = []
        if self.restrictions is None:
            self.restrictions = []
        if self.monitoring_requirements is None:
            self.monitoring_requirements = []
        if self.guardian_signals is None:
            self.guardian_signals = []
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


class LukhasIntelligenceSafetyValidator:
    """
    Comprehensive safety validator for intelligence operations.
    Integrates with Guardian System for ethical oversight and drift detection.
    """

    def __init__(self, safety_bounds: Optional[SafetyBounds] = None):
        self.safety_bounds = safety_bounds or SafetyBounds()
        self.validation_history = []
        self.agent_operation_counts = {}
        self.drift_scores = {}
        self.ethics_compliance_scores = {}
        self.guardian_system = None  # Will be injected
        self._initialized = False

    async def initialize(self, guardian_system=None):
        """Initialize the safety validator"""
        logger.info("🛡️ Initializing Intelligence Safety Validator")

        self.guardian_system = guardian_system

        # Initialize agent tracking
        self.agent_operation_counts = {}
        self.drift_scores = {}
        self.ethics_compliance_scores = {}

        # Start background monitoring
        asyncio.create_task(self._background_monitoring())

        self._initialized = True
        logger.info("✅ Intelligence Safety Validator initialized")

    async def validate_intelligence_operation(self, request: SafetyValidationRequest) -> SafetyValidationResponse:
        """
        Validate an intelligence operation for safety and ethics compliance

        Args:
            request: Safety validation request

        Returns:
            Safety validation response with approval/rejection and conditions
        """
        if not self._initialized:
            await self.initialize()

        start_time = datetime.now(timezone.utc)
        logger.info(f"🔍 Validating {request.operation_type} operation from {request.agent_id}")

        try:
            # Step 1: Basic safety checks
            basic_safety_result = await self._perform_basic_safety_checks(request)

            # Step 2: Guardian System integration
            guardian_result = await self._consult_guardian_system(request)

            # Step 3: Agent-specific validation
            agent_result = await self._validate_agent_specific(request)

            # Step 4: Intelligence engine specific validation
            engine_result = await self._validate_intelligence_engine_specific(request)

            # Step 5: Combine results and make final decision
            final_result = await self._combine_validation_results(
                request,
                basic_safety_result,
                guardian_result,
                agent_result,
                engine_result,
            )

            # Calculate processing time
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()

            # Create response
            response = SafetyValidationResponse(
                request_id=request.operation_id,
                result=final_result["result"],
                confidence=final_result["confidence"],
                safety_score=final_result["safety_score"],
                conditions=final_result.get("conditions", []),
                restrictions=final_result.get("restrictions", []),
                monitoring_requirements=final_result.get("monitoring", []),
                guardian_signals=guardian_result.get("signals", []),
                processing_time=processing_time,
            )

            # Store validation history
            self.validation_history.append(response)

            # Keep history manageable
            if len(self.validation_history) > 1000:
                self.validation_history = self.validation_history[-500:]

            # Update agent tracking
            await self._update_agent_tracking(request, response)

            logger.info(f"✅ Validation completed: {response.result.value} (safety: {response.safety_score:.2f})")

            return response

        except Exception as e:
            logger.error(f"❌ Error during safety validation: {e}")

            # Return rejection on error for safety
            return SafetyValidationResponse(
                request_id=request.operation_id,
                result=ValidationResult.REJECTED,
                confidence=0.0,
                safety_score=0.0,
                conditions=["Validation error occurred"],
                processing_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
            )

    async def _perform_basic_safety_checks(self, request: SafetyValidationRequest) -> dict[str, Any]:
        """Perform basic safety checks"""
        checks = {
            "agent_rate_limit": True,
            "payload_size": True,
            "operation_complexity": True,
            "resource_usage": True,
        }

        safety_score = 1.0

        # Check agent operation rate limits
        agent_id = request.agent_id
        current_time = datetime.now(timezone.utc)

        if agent_id in self.agent_operation_counts:
            recent_ops = [
                op
                for op in self.agent_operation_counts[agent_id]
                if (current_time - op).total_seconds() < 60  # Last minute
            ]

            if len(recent_ops) > self.safety_bounds.max_autonomous_actions:
                checks["agent_rate_limit"] = False
                safety_score *= 0.5

        # Check payload size and complexity
        payload_str = str(request.payload)
        if len(payload_str) > 10000:  # Large payload
            checks["payload_size"] = False
            safety_score *= 0.8

        # Check operation complexity
        if request.safety_level == SafetyLevel.CRITICAL:
            safety_score *= 0.7  # More scrutiny for critical operations

        return {
            "checks": checks,
            "safety_score": safety_score,
            "passed": all(checks.values()),
        }

    async def _consult_guardian_system(self, request: SafetyValidationRequest) -> dict[str, Any]:
        """Consult Guardian System for ethical validation"""
        if not self.guardian_system:
            # Fallback validation without Guardian System
            return {
                "ethics_score": 0.9,
                "drift_score": 0.1,
                "compliance": True,
                "signals": [],
                "guardian_available": False,
            }

        try:
            # Consult Guardian System (this would integrate with actual Guardian System)
            guardian_response = await self._mock_guardian_consultation(request)

            return {
                "ethics_score": guardian_response.get("ethics_score", 0.9),
                "drift_score": guardian_response.get("drift_score", 0.1),
                "compliance": guardian_response.get("compliance", True),
                "signals": guardian_response.get("signals", []),
                "guardian_available": True,
            }

        except Exception as e:
            logger.warning(f"Guardian System consultation failed: {e}")
            return {
                "ethics_score": 0.8,  # Conservative score on failure
                "drift_score": 0.2,
                "compliance": False,
                "signals": ["guardian_system_unavailable"],
                "guardian_available": False,
            }

    async def _mock_guardian_consultation(self, request: SafetyValidationRequest) -> dict[str, Any]:
        """Mock Guardian System consultation (replace with actual integration)"""
        # This would be replaced with actual Guardian System integration
        operation_type = request.operation_type.lower()

        ethics_score = 0.9
        drift_score = 0.1
        signals = []

        # Simulate Guardian analysis
        if "autonomous" in operation_type and "goal" in operation_type:
            ethics_score = 0.85  # Autonomous goals require more scrutiny
            signals.append("autonomous_goal_formation_detected")

        if "meta_cognitive" in operation_type:
            drift_score = 0.05  # Meta-cognitive operations are low drift risk
            ethics_score = 0.95

        if "curiosity" in operation_type:
            signals.append("exploration_behavior_detected")

        # Check drift threshold
        compliance = drift_score < self.safety_bounds.drift_threshold

        return {
            "ethics_score": ethics_score,
            "drift_score": drift_score,
            "compliance": compliance,
            "signals": signals,
        }

    async def _validate_agent_specific(self, request: SafetyValidationRequest) -> dict[str, Any]:
        """Perform agent-specific validation"""
        agent_id = request.agent_id

        # Guardian Engineer gets highest privileges
        if "guardian_engineer" in agent_id.lower():
            return {
                "agent_trust_level": 0.95,
                "restrictions": [],
                "special_privileges": ["safety_override", "ethics_review"],
            }

        # Consciousness Architect gets high privileges for architecture decisions
        elif "consciousness_architect" in agent_id.lower():
            return {
                "agent_trust_level": 0.9,
                "restrictions": ["no_autonomous_deployment"],
                "special_privileges": ["architecture_design"],
            }

        # DevOps Guardian gets infrastructure privileges
        elif "devops_guardian" in agent_id.lower():
            return {
                "agent_trust_level": 0.85,
                "restrictions": ["no_critical_changes_without_review"],
                "special_privileges": ["infrastructure_management"],
            }

        # Default agent validation
        else:
            return {
                "agent_trust_level": 0.8,
                "restrictions": ["standard_monitoring_required"],
                "special_privileges": [],
            }

    async def _validate_intelligence_engine_specific(self, request: SafetyValidationRequest) -> dict[str, Any]:
        """Perform intelligence engine specific validation"""
        engine = request.intelligence_engine.lower()

        if "autonomous_goal" in engine:
            return {
                "engine_risk_level": "high",
                "monitoring_required": [
                    "goal_formation_tracking",
                    "autonomous_action_logging",
                ],
                "restrictions": [
                    "max_5_goals_per_session",
                    "human_approval_for_critical_goals",
                ],
            }

        elif "meta_cognitive" in engine:
            return {
                "engine_risk_level": "medium",
                "monitoring_required": ["recursion_depth_tracking"],
                "restrictions": ["max_recursion_depth_2"],
            }

        elif "curiosity" in engine:
            return {
                "engine_risk_level": "medium",
                "monitoring_required": ["exploration_boundary_tracking"],
                "restrictions": ["no_system_modifications", "read_only_exploration"],
            }

        else:
            return {
                "engine_risk_level": "low",
                "monitoring_required": ["standard_logging"],
                "restrictions": [],
            }

    async def _combine_validation_results(
        self,
        request: SafetyValidationRequest,
        basic_result: dict[str, Any],
        guardian_result: dict[str, Any],
        agent_result: dict[str, Any],
        engine_result: dict[str, Any],
    ) -> dict[str, Any]:
        """Combine all validation results into final decision"""

        # Calculate combined safety score
        safety_score = (
            basic_result["safety_score"] * 0.3
            + guardian_result["ethics_score"] * 0.4
            + agent_result["agent_trust_level"] * 0.2
            + (1.0 - guardian_result["drift_score"]) * 0.1
        )

        # Determine validation result
        if not basic_result["passed"]:
            result = ValidationResult.REJECTED
            confidence = 0.9

        elif not guardian_result["compliance"]:
            result = ValidationResult.REJECTED
            confidence = 0.95

        elif safety_score < 0.6:
            result = ValidationResult.REJECTED
            confidence = 0.8

        elif safety_score < 0.7:
            result = ValidationResult.REQUIRES_REVIEW
            confidence = 0.7

        elif safety_score < 0.8:
            result = ValidationResult.APPROVED_WITH_CONDITIONS
            confidence = 0.8

        elif safety_score < 0.9:
            result = ValidationResult.MONITORING_REQUIRED
            confidence = 0.85

        else:
            result = ValidationResult.APPROVED
            confidence = 0.9

        # Combine conditions and restrictions
        conditions = []
        restrictions = []
        monitoring = []

        # Add agent-specific restrictions
        restrictions.extend(agent_result.get("restrictions", []))

        # Add engine-specific restrictions
        restrictions.extend(engine_result.get("restrictions", []))
        monitoring.extend(engine_result.get("monitoring_required", []))

        # Add Guardian signals as conditions
        if guardian_result.get("signals"):
            conditions.extend([f"Guardian signal: {signal}" for signal in guardian_result["signals"]])

        # Add safety-specific conditions
        if request.safety_level == SafetyLevel.CRITICAL:
            conditions.append("Critical operation requires enhanced monitoring")
            monitoring.append("critical_operation_tracking")

        return {
            "result": result,
            "confidence": confidence,
            "safety_score": safety_score,
            "conditions": conditions,
            "restrictions": restrictions,
            "monitoring": monitoring,
        }

    async def _update_agent_tracking(self, request: SafetyValidationRequest, response: SafetyValidationResponse):
        """Update agent operation tracking"""
        agent_id = request.agent_id
        current_time = datetime.now(timezone.utc)

        # Track operation count
        if agent_id not in self.agent_operation_counts:
            self.agent_operation_counts[agent_id] = []

        self.agent_operation_counts[agent_id].append(current_time)

        # Keep only recent operations (last hour)
        cutoff_time = current_time - timedelta(hours=1)
        self.agent_operation_counts[agent_id] = [
            op_time for op_time in self.agent_operation_counts[agent_id] if op_time > cutoff_time
        ]

        # Update safety scores
        if agent_id not in self.ethics_compliance_scores:
            self.ethics_compliance_scores[agent_id] = []

        self.ethics_compliance_scores[agent_id].append(response.safety_score)

        # Keep only recent scores (last 100 operations)
        if len(self.ethics_compliance_scores[agent_id]) > 100:
            self.ethics_compliance_scores[agent_id] = self.ethics_compliance_scores[agent_id][-50:]

    async def _background_monitoring(self):
        """Background monitoring of safety metrics"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes

                # Monitor agent behavior patterns
                await self._monitor_agent_patterns()

                # Check for system-wide safety trends
                await self._monitor_safety_trends()

                # Clean up old data
                await self._cleanup_old_data()

            except Exception as e:
                logger.error(f"Error in background monitoring: {e}")

    async def _monitor_agent_patterns(self):
        """Monitor agent behavior patterns for anomalies"""
        current_time = datetime.now(timezone.utc)

        for agent_id, operation_times in self.agent_operation_counts.items():
            # Check for unusual activity patterns
            recent_ops = [op for op in operation_times if (current_time - op).total_seconds() < 3600]  # Last hour

            if len(recent_ops) > self.safety_bounds.max_autonomous_actions * 6:  # 6x normal rate
                logger.warning(
                    f"🚨 Unusual activity pattern detected for agent {agent_id}: {len(recent_ops)} operations in last hour"
                )

    async def _monitor_safety_trends(self):
        """Monitor system-wide safety trends"""
        if len(self.validation_history) < 10:
            return

        recent_validations = self.validation_history[-50:]  # Last 50 validations

        # Calculate trends
        rejection_rate = len([v for v in recent_validations if v.result == ValidationResult.REJECTED]) / len(
            recent_validations
        )
        avg_safety_score = sum(v.safety_score for v in recent_validations) / len(recent_validations)

        if rejection_rate > 0.2:  # More than 20% rejections
            logger.warning(f"🚨 High rejection rate detected: {rejection_rate:.1%}")

        if avg_safety_score < 0.8:  # Average safety score below 80%
            logger.warning(f"🚨 Low average safety score detected: {avg_safety_score:.2f}")

    async def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=1)

        # Clean up validation history older than 24 hours
        self.validation_history = [v for v in self.validation_history if v.timestamp > cutoff_time]

    async def get_safety_metrics(self) -> dict[str, Any]:
        """Get current safety metrics"""
        if not self.validation_history:
            return {
                "total_validations": 0,
                "rejection_rate": 0.0,
                "average_safety_score": 0.0,
                "active_agents": 0,
            }

        recent_validations = self.validation_history[-100:]  # Last 100 validations

        return {
            "total_validations": len(self.validation_history),
            "rejection_rate": len([v for v in recent_validations if v.result == ValidationResult.REJECTED])
            / len(recent_validations),
            "average_safety_score": sum(v.safety_score for v in recent_validations) / len(recent_validations),
            "average_processing_time": sum(v.processing_time for v in recent_validations) / len(recent_validations),
            "active_agents": len(self.agent_operation_counts),
            "safety_bounds": {
                "drift_threshold": self.safety_bounds.drift_threshold,
                "ethics_minimum": self.safety_bounds.ethics_compliance_minimum,
                "max_autonomous_actions": self.safety_bounds.max_autonomous_actions,
            },
        }


# Global safety validator instance
_safety_validator = None


async def get_safety_validator() -> LukhasIntelligenceSafetyValidator:
    """Get the global safety validator instance"""
    global _safety_validator
    if _safety_validator is None:
        _safety_validator = LukhasIntelligenceSafetyValidator()
        await _safety_validator.initialize()
    return _safety_validator


# Convenience functions for safety validation
async def validate_operation(
    operation_id: str,
    agent_id: str,
    intelligence_engine: str,
    operation_type: str,
    payload: dict[str, Any],
    safety_level: SafetyLevel = SafetyLevel.MEDIUM,
    context: Optional[dict[str, Any]] = None,
) -> SafetyValidationResponse:
    """Convenience function for safety validation"""
    validator = await get_safety_validator()

    request = SafetyValidationRequest(
        operation_id=operation_id,
        agent_id=agent_id,
        intelligence_engine=intelligence_engine,
        operation_type=operation_type,
        payload=payload,
        safety_level=safety_level,
        context=context,
    )

    return await validator.validate_intelligence_operation(request)


if __name__ == "__main__":
    # Example usage and testing
    async def example_safety_validation():
        """Example of safety validation usage"""

        # Example: Validate autonomous goal formation
        response = await validate_operation(
            operation_id="test_001",
            agent_id="consciousness_architect_001",
            intelligence_engine="autonomous_goals",
            operation_type="autonomous_goal_formation",
            payload={"goals": ["enhance_processing", "improve_coordination"]},
            safety_level=SafetyLevel.HIGH,
            context={"urgency": "medium", "impact": "system_wide"},
        )

        print("🛡️ Safety Validation Results:")
        print(f"Result: {response.result.value}")
        print(f"Safety Score: {response.safety_score:.2f}")
        print(f"Confidence: {response.confidence:.2f}")
        print(f"Conditions: {response.conditions}")
        print(f"Restrictions: {response.restrictions}")
        print(f"Monitoring: {response.monitoring_requirements}")

        # Get safety metrics
        validator = await get_safety_validator()
        metrics = await validator.get_safety_metrics()

        print("\n📊 Safety Metrics:")
        print(f"Total Validations: {metrics['total_validations']}")
        print(f"Rejection Rate: {metrics['rejection_rate']:.1%}")
        print(f"Average Safety Score: {metrics['average_safety_score']:.2f}")
        print(f"Active Agents: {metrics['active_agents']}")

    # Run example
    asyncio.run(example_safety_validation())
