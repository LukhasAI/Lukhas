import time
from typing import Any, Dict, List

from matriz.core.node_interface import CognitiveNode, NodeState


class MetacognitiveReasoningNode(CognitiveNode):
    """
    Performs metacognitive reasoning to monitor and evaluate the quality of thought processes.
    This node conforms to the modern MATRIZ CognitiveNode interface.
    """

    def __init__(self, tenant: str = "default"):
        super().__init__(
            node_name="metacognitive_reasoning",
            capabilities=["metacognition", "self_reflection", "bias_detection"],
            tenant=tenant,
        )

    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Monitors and evaluates the quality of a reasoning process.

        Args:
            input_data: A dictionary containing:
                - 'reasoning_trace': A trace of the reasoning steps.
                - 'conclusions': The conclusions that were reached.
                - 'evidence': The evidence that was used.

        Returns:
            A dictionary containing the answer, confidence, a MATRIZ node, and processing time.
        """
        start_time = time.time()

        trace = input_data.get("reasoning_trace", [])
        conclusions = input_data.get("conclusions", [])
        evidence = input_data.get("evidence", [])
        trace_id = input_data.get("trace_id", self.get_deterministic_hash(input_data))

        if not trace:
            confidence = 0.1
            answer = "Metacognitive reasoning requires a reasoning trace to analyze."
            state = NodeState(confidence=confidence, salience=0.3)
            matriz_node = self.create_matriz_node(
                node_type="DECISION",
                state=state,
                trace_id=trace_id,
                additional_data={"error": "Missing reasoning_trace."}
            )
        else:
            assessment = self._assess_reasoning_quality(trace, conclusions, evidence)
            calibration = self._calibrate_confidence(assessment, trace)
            recommendations = self._generate_recommendations(assessment)

            confidence = assessment["confidence"]
            answer = f"Metacognitive assessment complete. Detected {len(assessment['biases_detected'])} potential biases."

            state = NodeState(confidence=confidence, salience=0.9, utility=0.8)
            matriz_node = self.create_matriz_node(
                node_type="AWARENESS",
                state=state,
                trace_id=trace_id,
                additional_data={
                    "assessment": assessment,
                    "confidence_calibration": calibration,
                    "recommendations": recommendations,
                }
            )

        processing_time = time.time() - start_time

        return {
            "answer": answer,
            "confidence": confidence,
            "matriz_node": matriz_node,
            "processing_time": processing_time,
        }

    def validate_output(self, output: dict[str, Any]) -> bool:
        """Validates the output of the metacognitive reasoning node."""
        if not all(k in output for k in ["answer", "confidence", "matriz_node", "processing_time"]):
            return False
        if not (0 <= output["confidence"] <= 1):
            return False
        if not self.validate_matriz_node(output["matriz_node"]):
            return False
        return True

    def _assess_reasoning_quality(self, trace: List[dict], conclusions: List[str], evidence: List[str]) -> dict:
        """Assesses the quality of the reasoning process."""
        confidence = self._assess_confidence(trace, evidence)
        completeness = self._assess_completeness(trace, conclusions)
        coherence = self._assess_coherence(trace, conclusions)
        biases = self._detect_biases(trace, evidence)
        improvements = self._suggest_improvements(confidence, completeness, coherence, biases)

        return {
            "process_name": "reasoning",
            "confidence": confidence,
            "completeness": completeness,
            "coherence": coherence,
            "biases_detected": biases,
            "improvements": improvements,
        }

    def _assess_confidence(self, trace: List[dict], evidence: List[str]) -> float:
        """Assesses the confidence in the reasoning."""
        return (min(1.0, len(evidence) * 0.2) + min(1.0, len(trace) * 0.1)) / 2

    def _assess_completeness(self, trace: List[dict], conclusions: List[str]) -> float:
        """Assesses the completeness of the reasoning."""
        alternatives = sum(1 for step in trace if "alternative" in step.get("type", "").lower())
        if not conclusions:
            return 0.5
        addressed = sum(1 for conc in conclusions if any(conc in str(step) for step in trace))
        coverage = addressed / len(conclusions) if conclusions else 0.0
        return (coverage + min(1.0, alternatives * 0.3)) / 2

    def _assess_coherence(self, trace: List[dict], conclusions: List[str]) -> float:
        """Assesses the logical coherence of the reasoning."""
        coherent_steps = sum(1 for i in range(1, len(trace)) if self._follows_logically(trace[i-1], trace[i]))
        return coherent_steps / max(1, len(trace) - 1) if len(trace) > 1 else 1.0

    def _follows_logically(self, step1: dict, step2: dict) -> bool:
        """Checks if step2 follows logically from step1."""
        return step1.get("output") in str(step2.get("input", ""))

    def _detect_biases(self, trace: List[dict], evidence: List[str]) -> List[str]:
        """Detects cognitive biases in the reasoning."""
        biases = []
        if evidence and sum(1 for e in evidence if "confirm" in e.lower() and "disconfirm" not in e.lower()) / len(evidence) > 0.8:
            biases.append("confirmation_bias")
        if trace and len(trace) > 3 and sum(s.get("weight", 0.5) for s in trace[-3:]) / 3 > 0.8:
            biases.append("availability_bias")
        if trace and len(trace) > 2 and trace[0].get("weight", 0.5) >= 0.9:
            biases.append("anchoring_bias")
        return biases

    def _suggest_improvements(self, confidence: float, completeness: float, coherence: float, biases: List[str]) -> List[str]:
        """Suggests improvements to the reasoning process."""
        improvements = []
        if confidence < 0.5: improvements.append("Gather more evidence.")
        if completeness < 0.6: improvements.append("Consider alternative explanations.")
        if coherence < 0.7: improvements.append("Ensure logical consistency.")
        if "confirmation_bias" in biases: improvements.append("Seek disconfirming evidence.")
        return improvements

    def _calibrate_confidence(self, assessment: dict, trace: List[dict]) -> Dict[str, Any]:
        """Calibrates the confidence levels."""
        stated_confidence = assessment["confidence"]
        actual_quality = (assessment["completeness"] + assessment["coherence"]) / 2
        calibration_error = abs(stated_confidence - actual_quality)

        status = "well_calibrated"
        if stated_confidence > actual_quality + 0.2: status = "overconfident"
        elif stated_confidence < actual_quality - 0.2: status = "underconfident"

        return {"stated_confidence": stated_confidence, "actual_quality": actual_quality, "calibration_error": calibration_error, "status": status}

    def _generate_recommendations(self, assessment: dict) -> List[str]:
        """Generates actionable recommendations."""
        recs = ["Continue monitoring reasoning quality."] + assessment["improvements"]
        for bias in assessment["biases_detected"]:
            recs.append(f"Mitigate {bias} by seeking diverse perspectives.")
        return recs
