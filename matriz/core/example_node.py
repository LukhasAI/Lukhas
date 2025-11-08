#!/usr/bin/env python3
"""
Example MATRIZ Cognitive Node Implementation

This demonstrates how to implement the CognitiveNode interface
to create a simple mathematical reasoning node that emits
complete MATRIZ format nodes.
"""

import re
import time
from typing import Any

from matriz.core.node_interface import CognitiveNode, NodeState, NodeTrigger


class MathReasoningNode(CognitiveNode):
    """
    Example cognitive node that performs basic mathematical reasoning.

    This node demonstrates:
    1. Processing mathematical expressions
    2. Creating complete MATRIZ format nodes
    3. Self-validation of outputs
    4. Reflection on processing quality
    """

    def __init__(self, tenant: str = "default"):
        super().__init__(
            node_name="math_reasoning",
            capabilities=["arithmetic", "basic_algebra", "expression_evaluation"],
            tenant=tenant,
        )
        self.supported_operations = ["+", "-", "*", "/", "**", "(", ")"]

    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Process mathematical expressions and return results with MATRIZ node.

        Args:
            input_data: Dict with 'query' containing mathematical expression

        Returns:
            Dict with answer, confidence, matriz_node, and processing_time
        """
        start_time = time.time()

        query = input_data.get("query", "")
        trigger_node_id = input_data.get("trigger_node_id")
        trace_id = input_data.get("trace_id", self.get_deterministic_hash(input_data))

        # Extract mathematical expression
        expression = self._extract_math_expression(query)

        if not expression:
            # Create low-confidence node for non-math queries
            state = NodeState(
                confidence=0.1,
                salience=0.2,
                valence=-0.3,  # Slightly negative - couldn't help
            )

            matriz_node = self.create_matriz_node(
                node_type="DECISION",
                state=state,
                trace_id=trace_id,
                additional_data={
                    "query": query,
                    "error": "No mathematical expression found",
                    "expression": None,
                    "result": None,
                },
            )

            return {
                "answer": "I could not find a mathematical expression to evaluate.",
                "confidence": 0.1,
                "matriz_node": matriz_node,
                "processing_time": time.time() - start_time,
            }

        # Evaluate the expression
        try:
            result = self._safe_eval(expression)
            confidence = 0.95  # High confidence for successful evaluation
            valence = 0.8  # Positive - successfully helped

            state = NodeState(
                confidence=confidence,
                salience=0.9,
                valence=valence,
                utility=0.8,  # High utility for providing answer
            )

            # Create reflection on successful processing
            reflection = self.create_reflection(
                reflection_type="affirmation",
                cause="Successfully evaluated mathematical expression",
                new_state={"confidence": confidence, "result": result},
            )

            # Create a trigger if there was a causal node
            triggers = []
            if trigger_node_id:
                trigger = NodeTrigger(
                    event_type="computation_request",
                    timestamp=int(time.time() * 1000),
                    trigger_node_id=trigger_node_id,
                    effect="invoke_computation",
                )
                triggers.append(trigger)

            matriz_node = self.create_matriz_node(
                node_type="COMPUTATION",
                state=state,
                trace_id=trace_id,
                reflections=[reflection],
                triggers=triggers,
                additional_data={
                    "query": query,
                    "expression": expression,
                    "result": result,
                    "evaluation_method": "safe_eval",
                },
            )

            answer = f"The result is {result}"

        except Exception as e:
            # Handle evaluation errors
            confidence = 0.2
            valence = -0.6  # Negative - failed to help

            state = NodeState(
                confidence=confidence,
                salience=0.7,
                valence=valence,
                risk=0.8,  # High risk due to error
            )

            # Create reflection on failure
            reflection = self.create_reflection(
                reflection_type="regret",
                cause=f"Failed to evaluate expression: {e!s}",
                old_state={"expression": expression},
                new_state={"error": str(e)},
            )

            matriz_node = self.create_matriz_node(
                node_type="DECISION",
                state=state,
                trace_id=trace_id,
                reflections=[reflection],
                additional_data={
                    "query": query,
                    "expression": expression,
                    "error": str(e),
                    "result": None,
                },
            )

            answer = f"I couldn't evaluate the expression '{expression}': {e!s}"

        processing_time = time.time() - start_time

        return {
            "answer": answer,
            "confidence": confidence,
            "matriz_node": matriz_node,
            "processing_time": processing_time,
        }

    def validate_output(self, output: dict[str, Any]) -> bool:
        """
        Validate the mathematical reasoning output.

        Checks:
        1. Required fields present
        2. MATRIZ node is valid
        3. Mathematical result is reasonable (if present)
        4. Confidence matches result quality
        """
        try:
            # Check required fields
            required_fields = ["answer", "confidence", "matriz_node", "processing_time"]
            for field in required_fields:
                if field not in output:
                    return False

            # Validate MATRIZ node
            if not self.validate_matriz_node(output["matriz_node"]):
                return False

            # Check confidence range
            confidence = output["confidence"]
            if not (0 <= confidence <= 1):
                return False

            # Check if mathematical result is present and valid
            matriz_node = output["matriz_node"]
            result = matriz_node["state"].get("result")

            if result is not None:
                # If we have a result, confidence should be reasonably high
                if confidence < 0.5:
                    return False

                # Result should be a number
                if not isinstance(result, (int, float)):
                    return False
            else:
                # If no result, confidence should be low
                if confidence > 0.5:
                    return False

            return True

        except Exception:
            return False

    def _extract_math_expression(self, query: str) -> str:
        """Extract mathematical expression from natural language query"""
        # Simple regex to find mathematical expressions
        math_pattern = r"[0-9+\-*/().\s]+"

        # Look for patterns like "what is 2+2" or "calculate 3*4"
        query_lower = query.lower()

        if any(word in query_lower for word in ["calculate", "what is", "solve", "evaluate"]):
            # Find the mathematical part
            matches = re.findall(math_pattern, query)
            if matches:
                # Take the longest match that contains operators
                for match in sorted(matches, key=len, reverse=True):
                    if any(op in match for op in ["+", "-", "*", "/", "(", ")"]):
                        return match.strip()

        # If no natural language cues, check if the whole query looks mathematical
        if re.match(r"^[0-9+\-*/().\s]+$", query.strip()):
            return query.strip()

        return ""

    def _safe_eval(self, expression: str) -> float:
        """
        Safely evaluate mathematical expression.

        This uses a restricted evaluation that only allows
        basic mathematical operations.
        """
        # Remove spaces
        expression = expression.replace(" ", "")

        # Validate expression only contains allowed characters
        allowed_chars = set("0123456789+-*/().")
        if not all(c in allowed_chars for c in expression):
            raise ValueError("Expression contains invalid characters")

        # Validate parentheses are balanced
        if expression.count("(") != expression.count(")"):
            raise ValueError("Unbalanced parentheses")

        # Use eval with restricted environment
        try:
            # Create safe environment with only math operations
            safe_dict = {"__builtins__": {}, "__name__": "__main__", "__doc__": None}

            result = eval(expression, safe_dict)

            # Ensure result is a number
            if not isinstance(result, (int, float)):
                raise ValueError("Result is not a number")

            return float(result)

        except ZeroDivisionError:
            raise ValueError("Division by zero")  # TODO[T4-ISSUE]: {"code": "B904", "ticket": "GH-1031", "owner": "consciousness-team", "status": "planned", "reason": "Exception re-raise pattern - needs review for proper chaining (raise...from)", "estimate": "15m", "priority": "medium", "dependencies": "none", "id": "matriz_core_example_node_py_L264"}
        except Exception as e:
            raise ValueError(f"Invalid expression: {e!s}")  # TODO[T4-ISSUE]: {"code": "B904", "ticket": "GH-1031", "owner": "consciousness-team", "status": "planned", "reason": "Exception re-raise pattern - needs review for proper chaining (raise...from)", "estimate": "15m", "priority": "medium", "dependencies": "none", "id": "matriz_core_example_node_py_L267"}


# Example usage and testing
if __name__ == "__main__":
    # Create the math node
    math_node = MathReasoningNode()

    # Test cases
    test_queries = [
        "What is 2 + 2?",
        "Calculate 15 * 3",
        "Solve (10 + 5) / 3",
        "Hello, how are you?",  # Non-math query
        "What is 1/0?",  # Error case
    ]

    print("MATRIZ Math Reasoning Node Test")
    print("=" * 40)

    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}: {query}")

        result = math_node.process({"query": query})

        print(f"Answer: {result['answer']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Processing time: {result['processing_time']:.4f}s")
        print(f"Valid: {math_node.validate_output(result)}")

        # Show MATRIZ node structure
        matriz_node = result["matriz_node"]
        print(f"MATRIZ Node ID: {matriz_node['id']}")
        print(f"Node Type: {matriz_node['type']}")
        print(
            f"State: confidence={matriz_node['state']['confidence']:.2f}, "
            f"salience={matriz_node['state']['salience']:.2f}"
        )

        if matriz_node["reflections"]:
            reflection = matriz_node["reflections"][0]
            print(f"Reflection: {reflection['reflection_type']} - {reflection['cause']}")

    print(f"\nProcessing History: {len(math_node.get_trace())} nodes created")
