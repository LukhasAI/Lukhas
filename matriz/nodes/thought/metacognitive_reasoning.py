#!/usr/bin/env python3
"""
MATRIZ Metacognitive Reasoning Node

Performs metacognitive reasoning: monitoring and evaluating own thought processes.
Implements self-reflection, bias detection, and reasoning quality assessment.

Example: "My reasoning was overconfident because I only considered supporting evidence"
"""

import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List

from matriz.core.node_interface import CognitiveNode, NodeState, NodeTrigger


@dataclass
class MetacognitiveAssessment:
    """Assessment of cognitive process quality."""
    process_name: str
    confidence: float  # How confident are we?
    completeness: float  # Did we consider everything?
    coherence: float  # Do conclusions follow logically?
    biases_detected: List[str]  # Cognitive biases detected
    improvements: List[str]  # Suggestions for improvement


class MetacognitiveReasoningNode(CognitiveNode):
    """
    Performs metacognitive reasoning: thinking about thinking.

    Capabilities:
    - Reasoning quality assessment
    - Cognitive bias detection
    - Confidence calibration
    - Improvement recommendations
    """

    def __init__(self, tenant: str = "default"):
        super().__init__(
            node_name="matriz_metacognitive_reasoning",
            capabilities=[
                "self_reflection",
                "bias_detection",
                "confidence_calibration",
                "governed_trace"
            ],
            tenant=tenant
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform metacognitive assessment.

        Args:
            input_data: Dict containing:
                - reasoning_trace: Trace of reasoning steps
                - conclusions: Conclusions reached
                - evidence: Evidence used

        Returns:
            Dict with assessment, calibration, recommendations, and MATRIZ node
        """
        start_time = time.time()

        trace = input_data.get("reasoning_trace", [])
        conclusions = input_data.get("conclusions", [])
        evidence = input_data.get("evidence", [])

        # Assess reasoning quality
        assessment = self._assess_reasoning_quality(trace, conclusions, evidence)

        # Calibrate confidence
        calibration = self._calibrate_confidence(assessment, trace)

        # Generate recommendations
        recommendations = self._generate_recommendations(assessment)

        # Overall confidence in assessment
        confidence = (assessment.confidence + assessment.completeness + assessment.coherence) / 3

        # Create NodeState
        state = NodeState(
            confidence=confidence,
            salience=min(1.0, 0.7 + len(assessment.biases_detected) * 0.1),
            novelty=min(1.0, 0.3 + len(assessment.improvements) * 0.1),
            utility=min(1.0, 0.8 + len(recommendations) * 0.05)
        )

        # Create trigger
        trigger = NodeTrigger(
            event_type="metacognitive_assessment_request",
            timestamp=int(time.time() * 1000)
        )

        # Build MATRIZ node
        matriz_node = {
            "id": str(uuid.uuid4()),
            "type": "AWARENESS",
            "state": {
                "confidence": state.confidence,
                "salience": state.salience,
                "novelty": state.novelty,
                "utility": state.utility
            },
            "triggers": [{
                "event_type": trigger.event_type,
                "timestamp": trigger.timestamp
            }],
            "metadata": {
                "node_name": self.node_name,
                "tenant": self.tenant,
                "capabilities": self.capabilities,
                "processing_time": time.time() - start_time,
                "trace_length": len(trace),
                "conclusion_count": len(conclusions)
            },
            "assessment": {
                "process_name": assessment.process_name,
                "confidence": assessment.confidence,
                "completeness": assessment.completeness,
                "coherence": assessment.coherence,
                "biases_detected": assessment.biases_detected,
                "improvements": assessment.improvements
            },
            "confidence_calibration": calibration,
            "recommendations": recommendations
        }

        return {
            "answer": {
                "assessment": matriz_node["assessment"],
                "confidence_calibration": calibration,
                "recommendations": recommendations
            },
            "confidence": confidence,
            "matriz_node": matriz_node,
            "processing_time": time.time() - start_time
        }

    def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate output structure."""
        required = ["answer", "confidence", "matriz_node", "processing_time"]
        if not all(k in output for k in required):
            return False

        if not 0.0 <= output["confidence"] <= 1.0:
            return False

        if "assessment" not in output["answer"]:
            return False

        return True

    def _assess_reasoning_quality(
        self,
        trace: List[dict],
        conclusions: List[str],
        evidence: List[str]
    ) -> MetacognitiveAssessment:
        """Assess quality of reasoning process."""
        # Assess confidence
        confidence = self._assess_confidence(trace, evidence)

        # Assess completeness
        completeness = self._assess_completeness(trace, conclusions)

        # Assess coherence
        coherence = self._assess_coherence(trace, conclusions)

        # Detect biases
        biases = self._detect_biases(trace, evidence)

        # Generate improvement suggestions
        improvements = self._suggest_improvements(
            confidence,
            completeness,
            coherence,
            biases
        )

        return MetacognitiveAssessment(
            process_name="reasoning",
            confidence=confidence,
            completeness=completeness,
            coherence=coherence,
            biases_detected=biases,
            improvements=improvements
        )

    def _assess_confidence(self, trace: List[dict], evidence: List[str]) -> float:
        """Assess confidence in reasoning."""
        # More evidence = higher confidence
        evidence_score = min(1.0, len(evidence) * 0.2)

        # Longer trace = more thorough = higher confidence
        trace_score = min(1.0, len(trace) * 0.1)

        return (evidence_score + trace_score) / 2

    def _assess_completeness(self, trace: List[dict], conclusions: List[str]) -> float:
        """Assess completeness of reasoning."""
        # Did we consider alternatives?
        alternatives_considered = sum(
            1 for step in trace
            if "alternative" in str(step.get("type", "")).lower()
        )

        # Did we address all conclusions?
        if not conclusions:
            return 0.5  # Neutral

        addressed = sum(
            1 for conclusion in conclusions
            if any(conclusion in str(step) for step in trace)
        )

        coverage = addressed / len(conclusions) if conclusions else 0.0

        # Combine scores
        return (coverage + min(1.0, alternatives_considered * 0.3)) / 2

    def _assess_coherence(self, trace: List[dict], conclusions: List[str]) -> float:
        """Assess logical coherence of reasoning."""
        # Check for logical consistency
        if len(trace) <= 1:
            return 1.0

        coherent_steps = 0
        for i in range(1, len(trace)):
            if self._follows_logically(trace[i-1], trace[i]):
                coherent_steps += 1

        coherence = coherent_steps / max(1, len(trace) - 1) if len(trace) > 1 else 1.0

        return coherence

    def _follows_logically(self, step1: dict, step2: dict) -> bool:
        """Check if step2 follows logically from step1."""
        # Simplified: check if step2 references step1 output
        output1 = str(step1.get("output", ""))
        input2 = str(step2.get("input", ""))

        return output1 and input2 and output1 in input2

    def _detect_biases(self, trace: List[dict], evidence: List[str]) -> List[str]:
        """Detect cognitive biases in reasoning."""
        biases = []

        # Confirmation bias: only considering supporting evidence
        if evidence:
            supporting = sum(1 for e in evidence if "confirm" in e.lower() or "support" in e.lower())
            if supporting / len(evidence) > 0.8:
                biases.append("confirmation_bias")

        # Availability bias: recent evidence weighted too heavily
        if trace and len(trace) > 3:
            recent_steps = trace[-3:]
            recent_weight = sum(s.get("weight", 0.5) for s in recent_steps) / 3
            if recent_weight > 0.8:
                biases.append("availability_bias")

        # Anchoring bias: first evidence anchors all reasoning
        if trace and len(trace) > 2:
            first_weight = trace[0].get("weight", 0.5)
            if first_weight > 0.9:
                biases.append("anchoring_bias")

        return biases

    def _suggest_improvements(
        self,
        confidence: float,
        completeness: float,
        coherence: float,
        biases: List[str]
    ) -> List[str]:
        """Suggest improvements to reasoning."""
        improvements = []

        if confidence < 0.5:
            improvements.append("Gather more evidence to support conclusions")

        if completeness < 0.6:
            improvements.append("Consider alternative explanations")
            improvements.append("Address all aspects of the problem")

        if coherence < 0.7:
            improvements.append("Ensure logical consistency between steps")

        if "confirmation_bias" in biases:
            improvements.append("Actively seek disconfirming evidence")

        if "availability_bias" in biases:
            improvements.append("Weight evidence by quality, not recency")

        if "anchoring_bias" in biases:
            improvements.append("Re-evaluate initial assumptions")

        return improvements

    def _calibrate_confidence(
        self,
        assessment: MetacognitiveAssessment,
        trace: List[dict]
    ) -> Dict[str, Any]:
        """Calibrate confidence levels."""
        stated_confidence = assessment.confidence
        actual_quality = (
            assessment.completeness + assessment.coherence
        ) / 2

        calibration_error = abs(stated_confidence - actual_quality)

        if stated_confidence > actual_quality + 0.2:
            calibration_status = "overconfident"
        elif stated_confidence < actual_quality - 0.2:
            calibration_status = "underconfident"
        else:
            calibration_status = "well_calibrated"

        return {
            "stated_confidence": stated_confidence,
            "actual_quality": actual_quality,
            "calibration_error": calibration_error,
            "status": calibration_status
        }

    def _generate_recommendations(
        self,
        assessment: MetacognitiveAssessment
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Add general recommendation
        recommendations.append("Continue monitoring reasoning quality")

        # Add specific improvements
        recommendations.extend(assessment.improvements)

        # Add bias mitigation strategies
        for bias in assessment.biases_detected:
            recommendations.append(f"Mitigate {bias} by seeking diverse perspectives")

        return recommendations
