#!/usr/bin/env python3
"""
MATRIZ Validation Node

A production-ready cognitive node for validating outputs from other nodes that provides:
- Mathematical correctness validation
- Fact accuracy verification
- Logical consistency checking
- Multi-strategy validation approach
- Complete MATRIZ format node emission with type "VALIDATION"
- Confidence scoring for validation results
- Full traceability and audit support

This node validates outputs from other cognitive nodes to ensure accuracy, consistency,
and reliability across the MATRIZ-AGI system. It supports multiple validation strategies
and provides detailed confidence assessments.
"""

import ast
import math
import operator
import re
import time
from typing import Any, Union

from ..core.node_interface import (
    CognitiveNode,
    NodeState,
    NodeTrigger,
)


class ValidatorNode(CognitiveNode):
    """
    Production-ready validation node for MATRIZ-AGI system.

    Features:
    - Mathematical expression validation and verification
    - Fact accuracy checking against known knowledge
    - Logical consistency analysis
    - Multiple validation strategies with confidence scoring
    - Complete MATRIZ format node emission with type "VALIDATION"
    - Full audit trail and traceability
    - Cross-validation with multiple approaches

    Validation Categories:
    - Mathematical: Arithmetic accuracy, expression correctness
    - Factual: Knowledge base verification, consistency checks
    - Logical: Reasoning validation, consistency analysis
    - Structural: Format and schema validation
    """

    def __init__(self, tenant: str = "default"):
        """
        Initialize the validation node.

        Args:
            tenant: Tenant identifier for multi-tenancy
        """
        super().__init__(
            node_name="matriz_validator_node",
            capabilities=[
                "mathematical_validation",
                "fact_verification",
                "logical_consistency_checking",
                "output_validation",
                "confidence_assessment",
                "cross_validation",
            ],
            tenant=tenant,
        )

        # Validation thresholds
        self.validation_thresholds = {
            "mathematical_accuracy": 0.95,
            "fact_accuracy": 0.90,
            "logical_consistency": 0.85,
            "format_compliance": 0.99,
        }

        # Confidence weights for different validation types
        self.confidence_weights = {
            "mathematical": 0.95,  # High confidence in math validation
            "factual": 0.85,  # Good confidence in fact checking
            "logical": 0.80,  # Moderate confidence in logic validation
            "structural": 0.99,  # Very high confidence in structure validation
            "cross_validation_bonus": 0.10,  # Bonus for multiple validation agreement
        }

        # Mathematical operators for expression validation
        self.math_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }

        # Known facts for verification
        self.known_facts = self._build_validation_knowledge_base()

    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate outputs from other cognitive nodes.

        Args:
            input_data: Dict containing:
                - 'target_output': Output from another node to validate
                - 'validation_type': Type of validation to perform (optional)
                - 'trace_id': Optional execution trace ID
                - 'context': Optional additional context

        Returns:
            Dict containing:
                - 'answer': Validation result summary
                - 'confidence': Overall validation confidence (0.0-1.0)
                - 'matriz_node': Complete MATRIZ format node with type "VALIDATION"
                - 'processing_time': Processing duration in seconds
        """
        start_time = time.time()

        # Extract and validate input
        target_output = input_data.get("target_output", {})
        validation_type = input_data.get("validation_type", "comprehensive")
        trace_id = input_data.get("trace_id", self.get_deterministic_hash(input_data))
        context = input_data.get("context", {})

        # Create initial trigger
        trigger = NodeTrigger(
            event_type="output_validation_request",
            timestamp=int(time.time() * 1000),
            effect="validation_analysis",
        )

        if not target_output:
            return self._create_error_response(
                "No target output provided for validation",
                input_data,
                trace_id,
                start_time,
                [trigger],
            )

        # Perform validation based on type
        try:
            validation_results = self._perform_validation(target_output, validation_type, context)

            # Calculate overall confidence and create summary
            overall_confidence = self._calculate_overall_confidence(validation_results)
            validation_summary = self._create_validation_summary(validation_results)

            # Determine validation status - must pass all critical validations
            critical_failures = self._check_critical_failures(validation_results)
            is_valid = overall_confidence >= 0.7 and not critical_failures

            # Create state based on validation results
            state = NodeState(
                confidence=overall_confidence,
                salience=min(
                    0.9, 0.6 + (1 - overall_confidence) * 0.3
                ),  # Higher salience for concerning results
                valence=(0.7 if is_valid else -0.3),  # Positive if valid, negative if invalid
                utility=0.9,  # High utility for validation results
                novelty=max(0.1, 1 - overall_confidence),  # Higher novelty for unexpected results
                arousal=min(
                    0.8, 0.3 + (1 - overall_confidence) * 0.5
                ),  # Higher arousal for concerning results
                risk=max(0.1, 1 - overall_confidence),  # Higher risk for low confidence validation
            )

            # Create appropriate reflection
            reflection_type = "affirmation" if is_valid else "regret"
            reflection_cause = f"Validation {'passed' if is_valid else 'failed'} with confidence {overall_confidence:.3f}"

            reflection = self.create_reflection(
                reflection_type=reflection_type,
                cause=reflection_cause,
                new_state={
                    "validation_results": validation_results,
                    "overall_confidence": overall_confidence,
                    "is_valid": is_valid,
                    "validation_type": validation_type,
                },
            )

            # Create MATRIZ node for validation
            matriz_node = self.create_matriz_node(
                node_type="VALIDATION",
                state=state,
                trace_id=trace_id,
                triggers=[trigger],
                reflections=[reflection],
                additional_data={
                    "target_output": target_output,
                    "validation_type": validation_type,
                    "validation_results": validation_results,
                    "overall_confidence": overall_confidence,
                    "is_valid": is_valid,
                    "validation_summary": validation_summary,
                    "validation_strategies_used": list(validation_results.keys()),
                    "context": context,
                    "deterministic_hash": self.get_deterministic_hash(
                        {
                            "target_output": target_output,
                            "validation_type": validation_type,
                        }
                    ),
                },
            )

            answer = f"Validation {'PASSED' if is_valid else 'FAILED'}: {validation_summary}"

        except Exception as e:
            return self._create_error_response(
                f"Validation error: {e!s}",
                input_data,
                trace_id,
                start_time,
                [trigger],
            )

        processing_time = time.time() - start_time

        return {
            "answer": answer,
            "confidence": overall_confidence,
            "matriz_node": matriz_node,
            "processing_time": processing_time,
        }

    def validate_output(self, output: dict[str, Any]) -> bool:
        """
        Validate the validation node's own output.

        Validates:
        1. Required fields presence and types
        2. MATRIZ node schema compliance with type "VALIDATION"
        3. Validation result structure and consistency
        4. Confidence score validity
        5. Processing metadata completeness

        Args:
            output: Output from process() method

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required top-level fields
            required_fields = ["answer", "confidence", "matriz_node", "processing_time"]
            for field in required_fields:
                if field not in output:
                    return False

            # Validate field types
            if not isinstance(output["answer"], str):
                return False
            if not isinstance(output["confidence"], (int, float)):
                return False
            if not isinstance(output["processing_time"], (int, float)):
                return False

            # Validate confidence range
            confidence = output["confidence"]
            if not (0 <= confidence <= 1):
                return False

            # Validate MATRIZ node
            matriz_node = output["matriz_node"]
            if not self.validate_matriz_node(matriz_node):
                return False

            # Check node type is VALIDATION
            if matriz_node.get("type") != "VALIDATION":
                return False

            # Validate validation-specific fields
            state = matriz_node.get("state", {})

            # Check for validation results
            if "validation_results" not in state:
                return False

            validation_results = state["validation_results"]
            if not isinstance(validation_results, dict):
                return False

            # Check overall confidence consistency
            if "overall_confidence" not in state:
                return False

            state_confidence = state["overall_confidence"]
            if not isinstance(state_confidence, (int, float)):
                return False
            if abs(state_confidence - confidence) > 0.001:  # Allow small floating point differences
                return False

            # Check validation status
            if "is_valid" not in state:
                return False
            if not isinstance(state["is_valid"], bool):
                return False

            # Validate answer format
            answer = output["answer"]
            if not (
                answer.startswith("Validation PASSED:")
                or answer.startswith("Validation FAILED:")
                or answer.startswith("Error:")
            ):
                return False

            # Validate provenance
            provenance = matriz_node.get("provenance", {})
            expected_capabilities = [
                "mathematical_validation",
                "fact_verification",
                "logical_consistency_checking",
            ]
            if not any(cap in provenance.get("capabilities", []) for cap in expected_capabilities):
                return False

            return True

        except Exception:
            return False

    def _perform_validation(
        self,
        target_output: dict[str, Any],
        validation_type: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Perform comprehensive validation of target output.

        Args:
            target_output: Output to validate
            validation_type: Type of validation to perform
            context: Additional context for validation

        Returns:
            Dict containing validation results for each strategy
        """
        validation_results = {}

        # Always perform structural validation
        validation_results["structural"] = self._validate_structure(target_output)

        # Determine what type of content we're validating
        answer = target_output.get("answer", "")
        matriz_node = target_output.get("matriz_node", {})
        node_type = matriz_node.get("type", "")

        # Mathematical validation for COMPUTATION nodes or mathematical content
        if (
            validation_type in ["comprehensive", "mathematical"]
            or node_type == "COMPUTATION"
            or self._contains_mathematical_content(answer)
        ):
            validation_results["mathematical"] = self._validate_mathematical_content(target_output)

        # Factual validation for MEMORY nodes or factual content
        if (
            validation_type in ["comprehensive", "factual"]
            or node_type == "MEMORY"
            or self._contains_factual_content(answer)
        ):
            validation_results["factual"] = self._validate_factual_content(target_output)

        # Logical consistency validation
        if validation_type in ["comprehensive", "logical"]:
            validation_results["logical"] = self._validate_logical_consistency(target_output)

        # Cross-validation if multiple strategies were used
        if len(validation_results) > 2:  # More than just structural + one other
            validation_results["cross_validation"] = self._perform_cross_validation(
                validation_results
            )

        return validation_results

    def _validate_structure(self, target_output: dict[str, Any]) -> dict[str, Any]:
        """
        Validate the structural integrity of the target output.

        Args:
            target_output: Output to validate structurally

        Returns:
            Dict containing structural validation results
        """
        try:
            issues = []
            confidence = 1.0

            # Check required fields
            required_fields = ["answer", "confidence", "matriz_node", "processing_time"]
            for field in required_fields:
                if field not in target_output:
                    issues.append(f"Missing required field: {field}")
                    confidence -= 0.2

            # Check field types
            if "answer" in target_output and not isinstance(target_output["answer"], str):
                issues.append("Answer field is not a string")
                confidence -= 0.1

            if "confidence" in target_output:
                conf = target_output["confidence"]
                if not isinstance(conf, (int, float)) or not (0 <= conf <= 1):
                    issues.append("Invalid confidence value")
                    confidence -= 0.2

            # Validate MATRIZ node structure
            if "matriz_node" in target_output:
                matriz_node = target_output["matriz_node"]
                if not isinstance(matriz_node, dict):
                    issues.append("MATRIZ node is not a dictionary")
                    confidence -= 0.3
                else:
                    # Check MATRIZ node required fields
                    matriz_required = [
                        "version",
                        "id",
                        "type",
                        "state",
                        "timestamps",
                        "provenance",
                    ]
                    for field in matriz_required:
                        if field not in matriz_node:
                            issues.append(f"MATRIZ node missing field: {field}")
                            confidence -= 0.1

            confidence = max(0.0, confidence)
            is_valid = confidence >= self.validation_thresholds["format_compliance"]

            return {
                "strategy": "structural",
                "confidence": confidence,
                "is_valid": is_valid,
                "issues": issues,
                "details": {
                    "required_fields_present": len(
                        [f for f in required_fields if f in target_output]
                    ),
                    "total_required_fields": len(required_fields),
                    "matriz_node_valid": "matriz_node" in target_output
                    and isinstance(target_output["matriz_node"], dict),
                },
            }

        except Exception as e:
            return {
                "strategy": "structural",
                "confidence": 0.0,
                "is_valid": False,
                "issues": [f"Structural validation error: {e!s}"],
                "details": {},
            }

    def _validate_mathematical_content(self, target_output: dict[str, Any]) -> dict[str, Any]:
        """
        Validate mathematical accuracy of the target output.

        Args:
            target_output: Output containing mathematical content

        Returns:
            Dict containing mathematical validation results
        """
        try:
            issues = []
            confidence = 0.95
            answer = target_output.get("answer", "")
            matriz_node = target_output.get("matriz_node", {})
            state = matriz_node.get("state", {})

            # Extract mathematical expression and result if available
            expression = state.get("expression", "")
            result = state.get("result", None)

            if expression and result is not None:
                # Validate the mathematical computation
                try:
                    # Re-evaluate the expression to verify correctness
                    verified_result = self._safe_eval_expression(expression)

                    if isinstance(result, (int, float)) and isinstance(
                        verified_result, (int, float)
                    ):
                        # Compare results with tolerance for floating point
                        tolerance = 1e-10
                        if abs(result - verified_result) <= tolerance:
                            confidence = 0.98
                        else:
                            issues.append(
                                f"Mathematical result mismatch: expected {verified_result}, got {result}"
                            )
                            confidence = 0.2
                    else:
                        issues.append("Unable to verify mathematical result types")
                        confidence = 0.5

                except Exception as e:
                    issues.append(f"Cannot verify mathematical expression: {e!s}")
                    confidence = 0.3

            # Check for mathematical patterns in answer text
            elif self._contains_mathematical_content(answer):
                # Extract numbers and basic operations from answer
                math_confidence = self._verify_answer_mathematics(answer)
                confidence = math_confidence
                if math_confidence < 0.7:
                    issues.append("Mathematical content in answer appears inconsistent")

            else:
                # No clear mathematical content found
                confidence = 0.8  # Neutral confidence when no math to validate
                issues.append("No mathematical content detected for validation")

            is_valid = confidence >= self.validation_thresholds["mathematical_accuracy"]

            return {
                "strategy": "mathematical",
                "confidence": confidence,
                "is_valid": is_valid,
                "issues": issues,
                "details": {
                    "expression": expression,
                    "result": result,
                    "verification_attempted": bool(expression and result is not None),
                    "math_content_detected": self._contains_mathematical_content(answer),
                },
            }

        except Exception as e:
            return {
                "strategy": "mathematical",
                "confidence": 0.0,
                "is_valid": False,
                "issues": [f"Mathematical validation error: {e!s}"],
                "details": {},
            }

    def _validate_factual_content(self, target_output: dict[str, Any]) -> dict[str, Any]:
        """
        Validate factual accuracy of the target output.

        Args:
            target_output: Output containing factual content

        Returns:
            Dict containing factual validation results
        """
        try:
            issues = []
            confidence = 0.85
            answer = target_output.get("answer", "")
            matriz_node = target_output.get("matriz_node", {})
            state = matriz_node.get("state", {})

            # Check if this is a known fact
            question = state.get("question", "")
            if question and answer:
                fact_confidence = self._verify_known_fact(question, answer)
                confidence = fact_confidence

                if fact_confidence < 0.5:
                    issues.append("Answer conflicts with known facts")
                elif fact_confidence < 0.7:
                    issues.append("Answer partially consistent with known facts")

            # Check for factual inconsistencies in the answer
            consistency_issues = self._check_factual_consistency(answer)
            if consistency_issues:
                issues.extend(consistency_issues)
                confidence *= 0.7

            # Verify against knowledge category if available
            category = state.get("knowledge_category", "")
            if category and category != "unknown":
                category_confidence = self._verify_category_consistency(answer, category)
                confidence = (confidence + category_confidence) / 2

            is_valid = confidence >= self.validation_thresholds["fact_accuracy"]

            return {
                "strategy": "factual",
                "confidence": confidence,
                "is_valid": is_valid,
                "issues": issues,
                "details": {
                    "question": question,
                    "answer_text": (answer[:100] + "..." if len(answer) > 100 else answer),
                    "knowledge_category": category,
                    "fact_verification_attempted": bool(question and answer),
                    "consistency_checks_performed": len(consistency_issues) == 0,
                },
            }

        except Exception as e:
            return {
                "strategy": "factual",
                "confidence": 0.0,
                "is_valid": False,
                "issues": [f"Factual validation error: {e!s}"],
                "details": {},
            }

    def _validate_logical_consistency(self, target_output: dict[str, Any]) -> dict[str, Any]:
        """
        Validate logical consistency of the target output.

        Args:
            target_output: Output to validate for logical consistency

        Returns:
            Dict containing logical validation results
        """
        try:
            issues = []
            confidence = 0.80
            answer = target_output.get("answer", "")
            matriz_node = target_output.get("matriz_node", {})

            # Check confidence-answer consistency
            output_confidence = target_output.get("confidence", 0)
            if answer.startswith("Error:") and output_confidence > 0.3:
                issues.append("High confidence for error response is inconsistent")
                confidence -= 0.3
            elif answer == "I don't know the answer to that question." and output_confidence > 0.3:
                issues.append("High confidence for 'don't know' response is inconsistent")
                confidence -= 0.2
            elif (
                not answer.startswith("Error:")
                and not answer.startswith("I don't know")
                and output_confidence < 0.3
            ):
                issues.append("Low confidence for substantive answer is potentially inconsistent")
                confidence -= 0.1

            # Check state consistency within MATRIZ node
            state = matriz_node.get("state", {})
            state_confidence = state.get("confidence", 0)
            if abs(output_confidence - state_confidence) > 0.01:
                issues.append("Confidence mismatch between output and MATRIZ node state")
                confidence -= 0.2

            # Check reflection consistency
            reflections = matriz_node.get("reflections", [])
            if reflections:
                reflection = reflections[0]
                reflection_type = reflection.get("reflection_type", "")

                if output_confidence > 0.7 and reflection_type == "regret":
                    issues.append("High confidence with regret reflection is inconsistent")
                    confidence -= 0.2
                elif output_confidence < 0.3 and reflection_type == "affirmation":
                    issues.append("Low confidence with affirmation reflection is inconsistent")
                    confidence -= 0.2

            # Check for logical contradictions in answer text
            contradiction_issues = self._check_logical_contradictions(answer)
            if contradiction_issues:
                issues.extend(contradiction_issues)
                confidence *= 0.6

            is_valid = confidence >= self.validation_thresholds["logical_consistency"]

            return {
                "strategy": "logical",
                "confidence": confidence,
                "is_valid": is_valid,
                "issues": issues,
                "details": {
                    "confidence_consistency_checked": True,
                    "reflection_consistency_checked": len(reflections) > 0,
                    "contradiction_analysis_performed": True,
                    "output_confidence": output_confidence,
                    "state_confidence": state_confidence,
                },
            }

        except Exception as e:
            return {
                "strategy": "logical",
                "confidence": 0.0,
                "is_valid": False,
                "issues": [f"Logical validation error: {e!s}"],
                "details": {},
            }

    def _perform_cross_validation(self, validation_results: dict[str, Any]) -> dict[str, Any]:
        """
        Perform cross-validation analysis across multiple validation strategies.

        Args:
            validation_results: Results from individual validation strategies

        Returns:
            Dict containing cross-validation results
        """
        try:
            # Exclude cross_validation from analysis to avoid recursion
            strategies = {k: v for k, v in validation_results.items() if k != "cross_validation"}

            if len(strategies) < 2:
                return {
                    "strategy": "cross_validation",
                    "confidence": 0.5,
                    "is_valid": True,
                    "issues": ["Insufficient strategies for cross-validation"],
                    "details": {"strategies_analyzed": list(strategies.keys())},
                }

            # Calculate agreement between strategies
            validities = [result["is_valid"] for result in strategies.values()]
            confidences = [result["confidence"] for result in strategies.values()]

            # Check for agreement
            all_agree_valid = all(validities)
            all_agree_invalid = not any(validities)
            partial_agreement = not all_agree_valid and not all_agree_invalid

            issues = []
            if partial_agreement:
                issues.append("Validation strategies disagree on validity")

            # Check confidence variance
            confidence_variance = max(confidences) - min(confidences)
            if confidence_variance > 0.4:
                issues.append(
                    f"High confidence variance across strategies: {confidence_variance:.3f}"
                )

            # Calculate cross-validation confidence
            if all_agree_valid or all_agree_invalid:
                base_confidence = 0.9
            else:
                base_confidence = 0.5  # Lower confidence when strategies disagree

            # Adjust based on individual strategy confidences
            avg_confidence = sum(confidences) / len(confidences)
            cross_confidence = (base_confidence + avg_confidence) / 2

            return {
                "strategy": "cross_validation",
                "confidence": cross_confidence,
                "is_valid": cross_confidence >= 0.7,
                "issues": issues,
                "details": {
                    "strategies_analyzed": list(strategies.keys()),
                    "agreement_level": (
                        "full" if (all_agree_valid or all_agree_invalid) else "partial"
                    ),
                    "confidence_variance": confidence_variance,
                    "average_confidence": avg_confidence,
                },
            }

        except Exception as e:
            return {
                "strategy": "cross_validation",
                "confidence": 0.0,
                "is_valid": False,
                "issues": [f"Cross-validation error: {e!s}"],
                "details": {},
            }

    def _calculate_overall_confidence(self, validation_results: dict[str, Any]) -> float:
        """
        Calculate overall confidence from individual validation results.

        Args:
            validation_results: Results from all validation strategies

        Returns:
            Overall confidence score (0.0-1.0)
        """
        if not validation_results:
            return 0.0

        weighted_confidence = 0.0
        total_weight = 0.0

        for strategy, result in validation_results.items():
            confidence = result.get("confidence", 0.0)
            weight = self.confidence_weights.get(strategy, 0.5)

            weighted_confidence += confidence * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        base_confidence = weighted_confidence / total_weight

        # Apply cross-validation bonus if available
        if "cross_validation" in validation_results:
            cross_result = validation_results["cross_validation"]
            if cross_result.get("is_valid", False):
                base_confidence += self.confidence_weights["cross_validation_bonus"]

        return min(1.0, base_confidence)

    def _check_critical_failures(self, validation_results: dict[str, Any]) -> bool:
        """
        Check if there are critical failures that should cause overall validation to fail.

        Args:
            validation_results: Results from all validation strategies

        Returns:
            True if there are critical failures, False otherwise
        """
        # Structural validation is always critical
        if "structural" in validation_results:
            if not validation_results["structural"].get("is_valid", False):
                return True

        # Mathematical validation is critical for COMPUTATION nodes
        if "mathematical" in validation_results:
            math_result = validation_results["mathematical"]
            if not math_result.get("is_valid", False):
                # Check if this was a serious mathematical error
                if math_result.get("confidence", 0) < 0.5:
                    return True

        # Logical consistency failures with very low confidence are critical
        if "logical" in validation_results:
            logical_result = validation_results["logical"]
            if not logical_result.get("is_valid", False):
                if logical_result.get("confidence", 0) < 0.5:
                    return True

        return False

    def _create_validation_summary(self, validation_results: dict[str, Any]) -> str:
        """
        Create a human-readable summary of validation results.

        Args:
            validation_results: Results from all validation strategies

        Returns:
            Human-readable validation summary
        """
        if not validation_results:
            return "No validation performed"

        passed_strategies = []
        failed_strategies = []

        for strategy, result in validation_results.items():
            if result.get("is_valid", False):
                passed_strategies.append(strategy)
            else:
                failed_strategies.append(strategy)

        summary_parts = []

        if passed_strategies:
            summary_parts.append(f"Passed: {', '.join(passed_strategies)}")

        if failed_strategies:
            summary_parts.append(f"Failed: {', '.join(failed_strategies)}")

        # Add key issues
        all_issues = []
        for result in validation_results.values():
            all_issues.extend(result.get("issues", []))

        if all_issues:
            key_issues = all_issues[:3]  # Show top 3 issues
            summary_parts.append(f"Issues: {'; '.join(key_issues)}")

        return " | ".join(summary_parts) if summary_parts else "No issues detected"

    def _contains_mathematical_content(self, text: str) -> bool:
        """Check if text contains mathematical content."""
        if not text:
            return False

        # Look for mathematical patterns
        math_patterns = [
            r"\d+\s*[+\-*/]\s*\d+",  # Basic arithmetic
            r"\d+\s*\*\*\s*\d+",  # Exponents
            r"=\s*\d+",  # Equals with number
            r"result\s+is\s+\d+",  # Result statement
            r"answer\s+is\s+\d+",  # Answer statement
        ]

        return any(re.search(pattern, text, re.IGNORECASE) for pattern in math_patterns)

    def _contains_factual_content(self, text: str) -> bool:
        """Check if text contains factual content."""
        if not text:
            return False

        # Look for factual patterns
        factual_patterns = [
            r"capital of \w+",
            r"president of \w+",
            r"largest \w+",
            r"smallest \w+",
            r"when did \w+",
            r"who was \w+",
            r"what is \w+",
            r"how many \w+",
        ]

        for pattern in factual_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    def _safe_eval_expression(self, expression: str) -> Union[float, int]:
        """Safely evaluate a mathematical expression."""
        try:
            # Simple validation and evaluation
            if not expression or len(expression) > 200:
                raise ValueError("Invalid expression")

            # Replace constants
            expr = expression.lower()
            math_constants = {"pi": math.pi, "e": math.e, "tau": math.tau}
            for const, value in math_constants.items():
                expr = expr.replace(const, str(value))

            # Parse and evaluate safely
            parsed = ast.parse(expr, mode="eval")
            result = self._eval_ast_node(parsed.body)

            if isinstance(result, float) and result.is_integer():
                return int(result)
            return result

        except Exception:
            raise ValueError("Cannot evaluate expression")

    def _eval_ast_node(self, node: ast.AST) -> Union[float, int]:
        """Recursively evaluate AST node safely."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            left = self._eval_ast_node(node.left)
            right = self._eval_ast_node(node.right)
            op_func = self.math_operators.get(type(node.op))
            if not op_func:
                raise ValueError("Unsupported operation")
            return op_func(left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_ast_node(node.operand)
            op_func = self.math_operators.get(type(node.op))
            if not op_func:
                raise ValueError("Unsupported unary operation")
            return op_func(operand)
        else:
            raise ValueError("Unsupported node type")

    def _verify_answer_mathematics(self, answer: str) -> float:
        """Verify mathematical content in answer text."""
        try:
            # Extract mathematical expressions and verify them
            numbers = re.findall(r"\d+(?:\.\d+)?", answer)
            if len(numbers) < 2:
                return 0.8  # Neutral confidence if minimal math content

            # Look for simple arithmetic expressions
            expr_match = re.search(
                r"(\d+(?:\.\d+)?)\s*([+\-*/])\s*(\d+(?:\.\d+)?)\s*=\s*(\d+(?:\.\d+)?)",
                answer,
            )
            if expr_match:
                left, op, right, result = expr_match.groups()
                try:
                    expected = {
                        "+": float(left) + float(right),
                        "-": float(left) - float(right),
                        "*": float(left) * float(right),
                        "/": float(left) / float(right) if float(right) != 0 else None,
                    }.get(op)

                    if expected is not None and abs(expected - float(result)) < 1e-10:
                        return 0.95
                    else:
                        return 0.2
                except Exception:
                    return 0.5

            return 0.7  # Default confidence for mathematical content

        except Exception:
            return 0.5

    def _verify_known_fact(self, question: str, answer: str) -> float:
        """Verify answer against known facts."""
        try:
            question_lower = question.lower().strip()
            answer_lower = answer.lower().strip()

            # Check against known facts
            for known_q, known_data in self.known_facts.items():
                if self._questions_similar(question_lower, known_q):
                    known_answer = known_data["answer"].lower()
                    if self._answers_consistent(answer_lower, known_answer):
                        return known_data.get("certainty", 0.9)
                    else:
                        return 0.1  # Answer conflicts with known fact

            return 0.6  # Neutral confidence when fact is unknown

        except Exception:
            return 0.5

    def _questions_similar(self, q1: str, q2: str) -> bool:
        """Check if two questions are asking the same thing."""
        import difflib

        return difflib.SequenceMatcher(None, q1, q2).ratio() > 0.7

    def _answers_consistent(self, answer: str, known_answer: str) -> bool:
        """Check if answer is consistent with known answer."""

        # Extract key terms from both answers
        def extract_key_terms(text):
            words = re.findall(r"\b\w+\b", text.lower())
            return {word for word in words if len(word) > 2}

        answer_terms = extract_key_terms(answer)
        known_terms = extract_key_terms(known_answer)

        # Check for significant overlap
        overlap = len(answer_terms & known_terms)
        union = len(answer_terms | known_terms)

        return overlap / union > 0.5 if union > 0 else False

    def _check_factual_consistency(self, answer: str) -> list[str]:
        """Check for obvious factual inconsistencies in answer."""
        issues = []

        # Check for contradictory statements
        contradictions = [
            (
                r"the largest.*is.*smallest",
                "Claims something is both largest and smallest",
            ),
            (r"never.*always", "Contains contradictory temporal claims"),
            (r"impossible.*possible", "Contains contradictory possibility claims"),
        ]

        for pattern, issue in contradictions:
            if re.search(pattern, answer, re.IGNORECASE):
                issues.append(issue)

        return issues

    def _verify_category_consistency(self, answer: str, category: str) -> float:
        """Verify answer is consistent with its category."""
        category_keywords = {
            "geography": [
                "country",
                "city",
                "capital",
                "continent",
                "ocean",
                "mountain",
            ],
            "history": ["year", "century", "war", "battle", "revolution", "empire"],
            "science": ["element", "molecule", "planet", "speed", "mass", "energy"],
            "mathematics": ["number", "equation", "formula", "calculate", "result"],
        }

        if category not in category_keywords:
            return 0.7  # Neutral confidence for unknown categories

        keywords = category_keywords[category]
        answer_lower = answer.lower()

        matches = sum(1 for keyword in keywords if keyword in answer_lower)
        return min(0.9, 0.5 + (matches / len(keywords)) * 0.4)

    def _check_logical_contradictions(self, answer: str) -> list[str]:
        """Check for logical contradictions in answer text."""
        issues = []

        # Check for obvious logical contradictions
        if re.search(r"both.*and.*not", answer, re.IGNORECASE):
            issues.append("Contains potential logical contradiction")

        if re.search(r"always.*never", answer, re.IGNORECASE):
            issues.append("Contains contradictory temporal claims")

        if re.search(r"all.*none", answer, re.IGNORECASE):
            issues.append("Contains contradictory universal claims")

        return issues

    def _build_validation_knowledge_base(self) -> dict[str, dict]:
        """Build knowledge base for fact validation."""
        return {
            "what is the capital of france": {
                "answer": "The capital of France is Paris.",
                "certainty": 1.0,
                "category": "geography",
            },
            "what is the capital of japan": {
                "answer": "The capital of Japan is Tokyo.",
                "certainty": 1.0,
                "category": "geography",
            },
            "what is 2 + 2": {
                "answer": "4",
                "certainty": 1.0,
                "category": "mathematics",
            },
            "what is the speed of light": {
                "answer": "The speed of light in a vacuum is approximately 299,792,458 meters per second.",
                "certainty": 1.0,
                "category": "science",
            },
            "how many planets are in our solar system": {
                "answer": "There are 8 planets in our solar system.",
                "certainty": 1.0,
                "category": "science",
            },
        }

    def _create_error_response(
        self,
        error_message: str,
        input_data: dict[str, Any],
        trace_id: str,
        start_time: float,
        triggers: list[NodeTrigger],
    ) -> dict[str, Any]:
        """Create standardized error response with MATRIZ node."""
        confidence = 0.1

        state = NodeState(
            confidence=confidence,
            salience=0.4,
            valence=-0.7,  # Negative - validation failed
            risk=0.9,  # High risk due to validation error
            utility=0.2,  # Low utility - no validation performed
        )

        reflection = self.create_reflection(
            reflection_type="regret",
            cause=f"Validation process failed: {error_message}",
            new_state={"error": error_message},
        )

        matriz_node = self.create_matriz_node(
            node_type="VALIDATION",
            state=state,
            trace_id=trace_id,
            triggers=triggers,
            reflections=[reflection],
            additional_data={
                "error": error_message,
                "validation_type": "failed",
                "validation_results": {},
                "overall_confidence": confidence,
                "is_valid": False,
                "context": input_data.get("context", {}),
            },
        )

        processing_time = time.time() - start_time

        return {
            "answer": f"Error: {error_message}",
            "confidence": confidence,
            "matriz_node": matriz_node,
            "processing_time": processing_time,
        }


# Example usage and testing
if __name__ == "__main__":
    # Create the validator node
    validator_node = ValidatorNode()

    # Test cases with different types of outputs to validate
    test_cases = [
        {
            "name": "Valid Math Output",
            "target_output": {
                "answer": "The result is 8",
                "confidence": 0.95,
                "matriz_node": {
                    "version": 1,
                    "id": "test-math-node",
                    "type": "COMPUTATION",
                    "state": {
                        "confidence": 0.95,
                        "salience": 0.7,
                        "expression": "2 + 6",
                        "result": 8,
                        "result_type": "int",
                    },
                    "timestamps": {"created_ts": int(time.time() * 1000)},
                    "provenance": {
                        "producer": "test.math_node",
                        "capabilities": ["mathematical_computation"],
                        "tenant": "default",
                        "trace_id": "test-trace",
                        "consent_scopes": ["cognitive_processing"],
                    },
                    "links": [],
                    "evolves_to": [],
                    "triggers": [],
                    "reflections": [],
                },
                "processing_time": 0.001,
            },
            "validation_type": "mathematical",
            "expected_result": "PASSED",
        },
        {
            "name": "Invalid Math Output",
            "target_output": {
                "answer": "The result is 10",
                "confidence": 0.95,
                "matriz_node": {
                    "version": 1,
                    "id": "test-math-node-invalid",
                    "type": "COMPUTATION",
                    "state": {
                        "confidence": 0.95,
                        "salience": 0.7,
                        "expression": "2 + 6",
                        "result": 10,  # Wrong result!
                        "result_type": "int",
                    },
                    "timestamps": {"created_ts": int(time.time() * 1000)},
                    "provenance": {
                        "producer": "test.math_node",
                        "capabilities": ["mathematical_computation"],
                        "tenant": "default",
                        "trace_id": "test-trace",
                        "consent_scopes": ["cognitive_processing"],
                    },
                    "links": [],
                    "evolves_to": [],
                    "triggers": [],
                    "reflections": [],
                },
                "processing_time": 0.001,
            },
            "validation_type": "mathematical",
            "expected_result": "FAILED",
        },
        {
            "name": "Valid Fact Output",
            "target_output": {
                "answer": "The capital of France is Paris.",
                "confidence": 0.95,
                "matriz_node": {
                    "version": 1,
                    "id": "test-fact-node",
                    "type": "MEMORY",
                    "state": {
                        "confidence": 0.95,
                        "salience": 0.8,
                        "question": "What is the capital of France?",
                        "answer": "The capital of France is Paris.",
                        "knowledge_category": "geography",
                    },
                    "timestamps": {"created_ts": int(time.time() * 1000)},
                    "provenance": {
                        "producer": "test.fact_node",
                        "capabilities": ["factual_knowledge_retrieval"],
                        "tenant": "default",
                        "trace_id": "test-trace",
                        "consent_scopes": ["cognitive_processing"],
                    },
                    "links": [],
                    "evolves_to": [],
                    "triggers": [],
                    "reflections": [],
                },
                "processing_time": 0.002,
            },
            "validation_type": "factual",
            "expected_result": "PASSED",
        },
        {
            "name": "Inconsistent Confidence Output",
            "target_output": {
                "answer": "Error: No expression provided",
                "confidence": 0.95,  # High confidence for error is inconsistent
                "matriz_node": {
                    "version": 1,
                    "id": "test-inconsistent-node",
                    "type": "COMPUTATION",
                    "state": {
                        "confidence": 0.95,
                        "salience": 0.3,
                        "error": "No expression provided",
                    },
                    "timestamps": {"created_ts": int(time.time() * 1000)},
                    "provenance": {
                        "producer": "test.math_node",
                        "capabilities": ["mathematical_computation"],
                        "tenant": "default",
                        "trace_id": "test-trace",
                        "consent_scopes": ["cognitive_processing"],
                    },
                    "links": [],
                    "evolves_to": [],
                    "triggers": [],
                    "reflections": [{"reflection_type": "regret", "cause": "Failed to process"}],
                },
                "processing_time": 0.001,
            },
            "validation_type": "logical",
            "expected_result": "FAILED",
        },
        {
            "name": "Malformed Output",
            "target_output": {
                "answer": "Some answer",
                # Missing confidence field
                "matriz_node": {
                    "version": 1,
                    "id": "test-malformed-node",
                    # Missing type field
                    "state": {"confidence": 0.5, "salience": 0.5},
                    "timestamps": {"created_ts": int(time.time() * 1000)},
                    "provenance": {
                        "producer": "test.node",
                        "capabilities": ["test"],
                        "tenant": "default",
                        "trace_id": "test-trace",
                        "consent_scopes": ["cognitive_processing"],
                    },
                    "links": [],
                    "evolves_to": [],
                    "triggers": [],
                    "reflections": [],
                },
                "processing_time": 0.001,
            },
            "validation_type": "structural",
            "expected_result": "FAILED",
        },
    ]

    print("MATRIZ Validation Node Test")
    print("=" * 50)

    success_count = 0
    total_tests = len(test_cases)

    for i, test_case in enumerate(test_cases, 1):
        name = test_case["name"]
        target_output = test_case["target_output"]
        validation_type = test_case["validation_type"]
        expected_result = test_case["expected_result"]

        print(f"\nTest {i:2d}: {name}")
        print("-" * 40)

        try:
            # Perform validation
            result = validator_node.process(
                {
                    "target_output": target_output,
                    "validation_type": validation_type,
                    "context": {"test_case": i},
                }
            )

            # Validate output
            is_valid = validator_node.validate_output(result)

            print(f"Answer: {result['answer']}")
            print(f"Confidence: {result['confidence']:.3f}")
            print(f"Processing time: {result['processing_time']:.6f}s")
            print(f"Output valid: {is_valid}")

            # Check if result matches expected outcome
            actual_result = (
                "PASSED" if result["answer"].startswith("Validation PASSED:") else "FAILED"
            )
            result_matches = actual_result == expected_result

            print(f"Expected: {expected_result}, Got: {actual_result}, Match: {result_matches}")

            # Show MATRIZ node details
            matriz_node = result["matriz_node"]
            print(f"MATRIZ Node ID: {matriz_node['id'][:8]}...")
            print(f"Node Type: {matriz_node['type']}")

            state = matriz_node["state"]
            print(
                f"State: conf={state['confidence']:.3f}, sal={state['salience']:.3f}, valid={state['is_valid']}"
            )

            # Show validation details
            validation_results = state.get("validation_results", {})
            print(f"Validation strategies: {list(validation_results.keys())}")

            for strategy, strategy_result in validation_results.items():
                print(
                    f"  {strategy}: conf={strategy_result['confidence']:.3f}, valid={strategy_result['is_valid']}"
                )

            if state.get("validation_summary"):
                print(f"Summary: {state['validation_summary']}")

            # Check reflections
            if matriz_node["reflections"]:
                reflection = matriz_node["reflections"][0]
                print(
                    f"Reflection: {reflection['reflection_type']} - {reflection['cause'][:50]}..."
                )

            if is_valid and result_matches:
                success_count += 1
                print("✓ PASS")
            else:
                print("✗ FAIL")

        except Exception as e:
            print(f"✗ EXCEPTION: {e!s}")

    print("\n" + "=" * 50)
    print(
        f"Test Results: {success_count}/{total_tests} passed ({success_count / total_tests * 100:.1f}%)"
    )
    print(f"Processing History: {len(validator_node.get_trace())} MATRIZ nodes created")

    # Show validation capabilities
    print("\nValidator Capabilities:")
    for capability in validator_node.capabilities:
        print(f"  - {capability}")

    print("\nValidation Thresholds:")
    for threshold_type, threshold_value in validator_node.validation_thresholds.items():
        print(f"  {threshold_type}: {threshold_value}")

    print(f"\nKnowledge Base Size: {len(validator_node.known_facts)} known facts")
