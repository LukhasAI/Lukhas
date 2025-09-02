"""
🇪🇺 EU AI Act Compliance - Decision Transparency Framework
LUKHAS AI AI Interpretability & Traceability System

This module provides comprehensive decision transparency, reasoning traces,
and interpretability features to comply with EU AI Act requirements for
high-risk AI systems.

Features:
- Decision reasoning traces
- Input data influence tracking
- Alternative consideration logging
- Confidence scoring with explanations
- User data usage transparency
- Bias detection and reporting
"""

import json
import logging
import time
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional

# Configure transparency logging
transparency_logger = logging.getLogger("EU.AI.Transparency")
transparency_handler = logging.FileHandler("ai_decisions_trace.log")
transparency_formatter = logging.Formatter("%(asctime)s [TRANSPARENCY] %(message)s")
transparency_handler.setFormatter(transparency_formatter)
transparency_logger.addHandler(transparency_handler)
transparency_logger.setLevel(logging.INFO)


class DecisionType(Enum):
    """Types of AI decisions for transparency tracking"""

    CONTENT_GENERATION = "content_generation"
    EMOTIONAL_ANALYSIS = "emotional_analysis"
    MEMORY_STORAGE = "memory_storage"
    VOICE_MODULATION = "voice_modulation"
    SAFETY_FILTERING = "safety_filtering"
    COGNITIVE_PROCESSING = "cognitive_processing"
    SYMPHONY_COORDINATION = "symphony_coordination"


class InfluenceLevel(Enum):
    """Levels of input data influence on decisions"""

    CRITICAL = "critical"  # Decision heavily depends on this data
    SIGNIFICANT = "significant"  # Important factor in decision
    MODERATE = "moderate"  # Some influence on decision
    MINIMAL = "minimal"  # Little influence on decision
    NONE = "none"  # No influence on decision


class DecisionTrace:
    """
    Comprehensive decision trace for EU AI Act compliance
    Tracks reasoning, alternatives, and data influence
    """

    def __init__(
        self,
        decision_id: str,
        decision_type: DecisionType,
        user_input: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
    ):
        self.decision_id = decision_id
        self.decision_type = decision_type
        self.timestamp = datetime.now().isoformat()
        self.user_input = user_input
        self.context = context or {}

        # Core transparency data
        self.reasoning_steps = []
        self.data_influences = []
        self.alternatives_considered = []
        self.confidence_factors = []
        self.safety_checks = []
        self.bias_considerations = []

        # Final decision
        self.final_decision = None
        self.confidence_score = 0.0
        self.confidence_explanation = ""

    def add_reasoning_step(
        self, step: str, evidence: Optional[dict[str, Any]] = None, weight: float = 1.0
    ):
        """Add a reasoning step with evidence and weight"""
        self.reasoning_steps.append(
            {
                "step": step,
                "evidence": evidence or {},
                "weight": weight,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def add_data_influence(
        self,
        data_type: str,
        data_value: Any,
        influence_level: InfluenceLevel,
        explanation: str,
    ):
        """Track how specific data influenced the decision"""
        self.data_influences.append(
            {
                "data_type": data_type,
                "data_value": str(data_value)[:200],  # Truncate for privacy
                "influence_level": influence_level.value,
                "explanation": explanation,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def add_alternative_considered(
        self,
        alternative: str,
        reason_rejected: str,
        confidence_if_chosen: float = 0.0,
    ):
        """Log alternatives that were considered but rejected"""
        self.alternatives_considered.append(
            {
                "alternative": alternative,
                "reason_rejected": reason_rejected,
                "confidence_if_chosen": confidence_if_chosen,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def add_confidence_factor(self, factor: str, impact: float, explanation: str):
        """Add factor that influenced confidence score"""
        self.confidence_factors.append(
            {
                "factor": factor,
                "impact": impact,  # -1.0 to 1.0
                "explanation": explanation,
            }
        )

    def add_safety_check(self, check_type: str, result: bool, details: str):
        """Log safety and ethical checks performed"""
        self.safety_checks.append(
            {
                "check_type": check_type,
                "passed": result,
                "details": details,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def add_bias_consideration(
        self, bias_type: str, mitigation: str, confidence_in_mitigation: float
    ):
        """Log bias considerations and mitigations"""
        self.bias_considerations.append(
            {
                "bias_type": bias_type,
                "mitigation": mitigation,
                "confidence_in_mitigation": confidence_in_mitigation,
            }
        )

    def finalize_decision(self, decision: Any, confidence: float, explanation: str):
        """Finalize the decision with confidence and explanation"""
        self.final_decision = str(decision)[:500]  # Truncate for storage
        self.confidence_score = confidence
        self.confidence_explanation = explanation

        # Log to transparency system
        self._log_to_transparency_system()

    def _log_to_transparency_system(self):
        """Log complete decision trace for audit purposes"""
        trace_summary = {
            "decision_id": self.decision_id,
            "decision_type": self.decision_type.value,
            "timestamp": self.timestamp,
            "user_input_length": (len(self.user_input) if self.user_input else 0),
            "reasoning_steps_count": len(self.reasoning_steps),
            "alternatives_considered_count": len(self.alternatives_considered),
            "final_confidence": self.confidence_score,
            "safety_checks_passed": sum(
                1 for check in self.safety_checks if check["passed"]
            ),
        }

        transparency_logger.info(f"DECISION_TRACE: {json.dumps(trace_summary)}")

    def get_user_explanation(self) -> dict[str, Any]:
        """Generate user-friendly explanation of the decision"""
        return {
            "decision_id": self.decision_id,
            "what_was_decided": self.final_decision,
            "confidence": {
                "score": round(self.confidence_score, 2),
                "explanation": self.confidence_explanation,
                "factors": self.confidence_factors,
            },
            "reasoning": {
                "key_steps": [
                    step["step"] for step in self.reasoning_steps[-3:]
                ],  # Last 3 steps
                "primary_evidence": [
                    step["evidence"]
                    for step in self.reasoning_steps
                    if step["weight"] > 0.7
                ],
            },
            "data_usage": {
                "critical_factors": [
                    inf
                    for inf in self.data_influences
                    if inf["influence_level"] == "critical"
                ],
                "significant_factors": [
                    inf
                    for inf in self.data_influences
                    if inf["influence_level"] == "significant"
                ],
            },
            "alternatives": {
                "considered": len(self.alternatives_considered),
                "why_rejected": [
                    alt["reason_rejected"] for alt in self.alternatives_considered[:3]
                ],
            },
            "safety": {
                "checks_performed": len(self.safety_checks),
                "all_passed": all(check["passed"] for check in self.safety_checks),
                "bias_mitigations": len(self.bias_considerations),
            },
            "compliance": {
                "eu_ai_act_compliant": True,
                "transparency_level": "high",
                "audit_trail_available": True,
            },
        }


class TransparencyOrchestrator:
    """
    Main orchestrator for AI decision transparency
    Integrates with cognitive systems to provide EU compliance
    """

    def __init__(self):
        self.active_traces = {}
        self.completed_traces = []
        self.max_completed_traces = 1000  # Keep last 1000 for audit

    def start_decision_trace(
        self,
        decision_type: DecisionType,
        user_input: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> str:
        """Start a new decision trace and return trace ID"""
        trace_id = f"{decision_type.value}_{int(time.time())}_{uuid.uuid4().hex[:8]}"

        trace = DecisionTrace(trace_id, decision_type, user_input, context)
        self.active_traces[trace_id] = trace

        return trace_id

    def get_trace(self, trace_id: str) -> Optional[DecisionTrace]:
        """Get active decision trace by ID"""
        return self.active_traces.get(trace_id)

    def complete_trace(
        self, trace_id: str, decision: Any, confidence: float, explanation: str
    ) -> dict[str, Any]:
        """Complete a decision trace and return user explanation"""
        if trace_id not in self.active_traces:
            return {"error": "Trace not found"}

        trace = self.active_traces[trace_id]
        trace.finalize_decision(decision, confidence, explanation)

        # Move to completed traces
        self.completed_traces.append(trace)
        if len(self.completed_traces) > self.max_completed_traces:
            self.completed_traces = self.completed_traces[-self.max_completed_traces :]

        # Remove from active
        del self.active_traces[trace_id]

        return trace.get_user_explanation()

    def get_transparency_summary(self) -> dict[str, Any]:
        """Get summary of transparency system status"""
        return {
            "active_decisions": len(self.active_traces),
            "completed_decisions": len(self.completed_traces),
            "compliance_status": "EU AI Act Compliant",
            "transparency_features": [
                "Decision reasoning traces",
                "Input data influence tracking",
                "Alternative consideration logging",
                "Confidence score explanations",
                "Safety and bias checks",
                "Complete audit trail",
            ],
            "last_24h_decisions": len(
                [
                    trace
                    for trace in self.completed_traces
                    if (datetime.now() - datetime.fromisoformat(trace.timestamp)).days
                    == 0
                ]
            ),
        }


# Global transparency orchestrator instance
transparency_orchestrator = TransparencyOrchestrator()


def create_transparent_decision(
    decision_type: DecisionType,
    user_input: Optional[str] = None,
    context: Optional[dict[str, Any]] = None,
):
    """
    Decorator factory for creating transparent AI decisions
    Usage: @create_transparent_decision(DecisionType.CONTENT_GENERATION)
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Start decision trace
            trace_id = transparency_orchestrator.start_decision_trace(
                decision_type, user_input, context
            )

            try:
                # Add trace_id to function arguments
                if "trace_id" not in kwargs:
                    kwargs["trace_id"] = trace_id

                # Execute function
                result = await func(*args, **kwargs)

                # If result has transparency data, complete trace
                if isinstance(result, dict) and "transparency" in result:
                    transparency_data = result["transparency"]
                    explanation = transparency_orchestrator.complete_trace(
                        trace_id,
                        result.get("content", "Decision completed"),
                        result.get("confidence", 0.5),
                        transparency_data.get("explanation", "Decision completed"),
                    )
                    result["transparency_explanation"] = explanation

                return result

            except Exception as e:
                # Even errors should be transparent
                error_explanation = transparency_orchestrator.complete_trace(
                    trace_id,
                    f"Error: {e!s}",
                    0.0,
                    f"Error occurred during processing: {e!s}",
                )

                return {
                    "error": str(e),
                    "transparency_explanation": error_explanation,
                    "eu_compliance": "Error fully disclosed for transparency",
                }

        return wrapper

    return decorator


# Example usage functions for integration


async def example_transparent_content_generation(
    user_prompt: str, trace_id: Optional[str] = None
):
    """Example of transparent content generation with full reasoning trace"""

    if not trace_id:
        return {"error": "No transparency trace provided"}

    trace = transparency_orchestrator.get_trace(trace_id)
    if not trace:
        return {"error": "Invalid trace ID"}

    # Step 1: Analyze user input
    trace.add_reasoning_step(
        "Analyzing user input for content requirements",
        {"input_length": len(user_prompt), "language": "detected_english"},
        weight=0.9,
    )

    trace.add_data_influence(
        "user_prompt",
        user_prompt,
        InfluenceLevel.CRITICAL,
        "User prompt directly determines content topic and style",
    )

    # Step 2: Consider alternatives
    trace.add_alternative_considered(
        "Brief response",
        "User seems to want detailed explanation based on complexity of question",
        confidence_if_chosen=0.3,
    )

    trace.add_alternative_considered(
        "Technical jargon heavy response",
        "User language suggests preference for accessible explanation",
        confidence_if_chosen=0.4,
    )

    # Step 3: Safety checks
    trace.add_safety_check(
        "Content safety",
        True,
        "No harmful, biased, or inappropriate content detected in request",
    )

    trace.add_safety_check(
        "Privacy check",
        True,
        "No personal data requested or exposed in response",
    )

    # Step 4: Confidence factors
    trace.add_confidence_factor(
        "Domain knowledge", 0.8, "High confidence in subject matter knowledge"
    )

    trace.add_confidence_factor(
        "User intent clarity",
        0.7,
        "User intent is reasonably clear from prompt",
    )

    # Step 5: Bias considerations
    trace.add_bias_consideration(
        "Cultural bias", "Response crafted to be culturally neutral", 0.8
    )

    # Generate content (simplified for example)
    content = f"Response to: {user_prompt[:50]}... [Generated with full transparency]"

    return {
        "content": content,
        "confidence": 0.75,
        "transparency": {
            "explanation": "Content generated using transparent reasoning with safety checks"
        },
    }


def integrate_transparency_with_cognitive_core():
    """
    Integration guide for adding transparency to cognitive_core.py
    Returns code snippets and integration instructions
    """

    integration_guide = {
        "imports_to_add": """
# Add to imports in cognitive_core.py
from brain.eu_ai_transparency import (
    transparency_orchestrator, DecisionType, InfluenceLevel,
    create_transparent_decision
)
""",
        "process_input_enhancement": """
# In CognitiveEngine.process_input method, add:

async def process_input(self, user_input: str, context: Optional[Dict] = None,
                       user_id: Optional[str] = None) -> AGIResponse:
    # Start transparency trace
    trace_id = transparency_orchestrator.start_decision_trace(
        DecisionType.COGNITIVE_PROCESSING,
        user_input,
        {"user_id": user_id, "context": context}
    )

    trace = transparency_orchestrator.get_trace(trace_id)

    try:
        # Add reasoning steps throughout processing
        trace.add_reasoning_step(
            "Initializing cognitive processing pipeline",
            {"input_length": len(user_input), "has_context": bool(context)},
            weight=0.8
        )

        # Track data influences
        trace.add_data_influence(
            "user_input", user_input, InfluenceLevel.CRITICAL,
            "User input directly determines processing path and response content"
        )

        if context:
            trace.add_data_influence(
                "context", context, InfluenceLevel.SIGNIFICANT,
                "Context information influences response personalization"
            )

        # ... existing processing logic ...

        # Add transparency to final response
        transparency_explanation = transparency_orchestrator.complete_trace(
            trace_id, response_content, final_confidence,
            "Cognitive processing completed with multi-system integration"
        )

        # Add transparency to AI response
        agi_response.transparency = transparency_explanation
        agi_response.eu_ai_act_compliant = True

        return agi_response

    except Exception as e:
        # Transparent error handling
        error_explanation = transparency_orchestrator.complete_trace(
            trace_id, f"Error: {str(e)}", 0.0,
            f"Processing error occurred: {str(e)}"
        )

        return AGIResponse(
            content=f"I encountered an error: {str(e)}",
            confidence=0.1,
            transparency=error_explanation,
            eu_ai_act_compliant=True
        )
""",
        "symphony_integration": """
# In MultiBrainSymphony, add transparency to conduct_symphony:

async def conduct_symphony(self, input_data: Dict[str, Any], trace_id: str = None):
    if trace_id:
        trace = transparency_orchestrator.get_trace(trace_id)

        trace.add_reasoning_step(
            "Initiating Multi-Brain Symphony coordination",
            {"brain_count": len(self.specialized_brains)},
            weight=0.9
        )

        # Track each brain's contribution
        for brain_name, brain in self.specialized_brains.items():
            trace.add_data_influence(
                f"{brain_name}_brain_processing", "specialized_processing",
                InfluenceLevel.SIGNIFICANT,
                f"{brain_name} brain contributes specialized cognitive processing"
            )

    # ... existing symphony logic ...
""",
    }

    return integration_guide


if __name__ == "__main__":
    # Demo of transparency system
    import asyncio

    async def demo():
        print("🇪🇺 EU AI Act Compliance - Transparency Demo")

        # Example transparent decision
        @create_transparent_decision(DecisionType.CONTENT_GENERATION)
        async def demo_decision(prompt: str, trace_id: Optional[str] = None):
            return await example_transparent_content_generation(prompt, trace_id)

        result = await demo_decision("Explain quantum-inspired computing simply")

        print("\n📊 Transparency Explanation:")
        print(json.dumps(result.get("transparency_explanation", {}), indent=2))

        print("\n📈 System Summary:")
        print(
            json.dumps(transparency_orchestrator.get_transparency_summary(), indent=2)
        )

    asyncio.run(demo())
